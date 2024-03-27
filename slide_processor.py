import numpy as np
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt
import os
import openslide
from PIL import Image
from openslide import OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
import math
import random
from pyspark.ml.linalg import Vectors
import pyspark.sql.functions as F
from scipy.ndimage.morphology import binary_fill_holes
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.morphology import binary_closing, binary_dilation, disk
from concurrent.futures import ProcessPoolExecutor
import tqdm

class SlideProcessor:
    def __init__(self, tile_size=1024, overlap=0, tissue_threshold=0.65, max_workers=30):
        self.tile_size = tile_size
        self.overlap = overlap
        self.tissue_threshold = tissue_threshold
        self.max_workers = max_workers

    def optical_density(self, tile):
        tile = tile.astype(np.float64)
        od = -np.log((tile+1)/240)
        return od

    def keep_tile(self, tile, tissue_threshold=None):
        if tissue_threshold is None:
            tissue_threshold = self.tissue_threshold
            
        if tile.shape[0:2] == (self.tile_size, self.tile_size):
            tile_orig = tile
            tile = rgb2gray(tile)
            tile = 1 - tile
            tile = canny(tile)
            tile = binary_closing(tile, disk(10))
            tile = binary_dilation(tile, disk(10))
            tile = binary_fill_holes(tile)
            percentage = tile.mean()

            check1 = percentage >= tissue_threshold

            tile = self.optical_density(tile_orig)
            beta = 0.15
            tile = np.min(tile, axis=2) >= beta
            tile = binary_closing(tile, disk(2))
            tile = binary_dilation(tile, disk(2))
            tile = binary_fill_holes(tile)
            percentage = tile.mean()

            check2 = percentage >= tissue_threshold

            return check1 and check2
        else:
            return False
        
    def filter_tiles(self, tile_indices, generator):
        filtered_tiles = []
        for i in range(len(tile_indices)):
            tile_size, overlap, zoom_level, col, row = tile_indices[i]
            tile = np.asarray(generator.get_tile(zoom_level, (col, row)))
            if self.keep_tile(tile, self.tissue_threshold):
                filtered_tiles.append((col, row))
        return filtered_tiles


    def get_tiles(self, samples, tile_indices, generator):
        tiles = []
        for i in samples:
            tile_size, overlap, zoom_level, col, row = tile_indices[i]
            tile = np.asarray(generator.get_tile(zoom_level, (col, row)))
            tiles.append((i, tile))
        return tiles
    
    def save_tiles(self, sample_tiles, slide_num, loc='pDataset/rest'):
        for sample in sample_tiles:
            i, tile = sample
            im = Image.fromarray(tile)
            fname = f"{slide_num}_{i}"
            file_path = os.path.join(loc, f"{fname}.jpeg")
            im.save(file_path)

    def get_save_tiles(self, samples, tile_indices, slide_num, generator, file, loc=None):
        if loc is None:
            loc = f'/home/gp7/ml_pni/Dataset/tiles_1024/{file}'

        for i, cord in enumerate(samples):
            x, y = cord
            tile_size, overlap, zoom_level, col, row = tile_indices[i]
            tile = np.asarray(generator.get_tile(zoom_level, (x, y)))
            im = Image.fromarray(tile)
            fname = f"{slide_num}_{x}_{y}"
            file_path = os.path.join(loc, f"{fname}.jpeg")
            im.save(file_path)

    def process_one_slide(self, file, base_dir='HNSC_DS', output_dir='/home/gp7/ml_pni/Dataset/tiles_1024'):
        f2p = os.path.join(base_dir, f'{file}.svs')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        img1 = openslide.open_slide(f2p) 
        generator = DeepZoomGenerator(img1, tile_size=self.tile_size, overlap=self.overlap, limit_bounds=True)
        highest_zoom_level = generator.level_count - 1

        try:
            mag = int(img1.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER])
            offset = math.floor((mag / 20) / 2)
            level = highest_zoom_level - offset
        except (ValueError, KeyError):
            level = highest_zoom_level

        zoom_level = level
        cols, rows = generator.level_tiles[zoom_level]
        tile_indices = [(self.tile_size, self.overlap, zoom_level, col, row) for col in range(cols) for row in range(rows)]
        
        filter_sname = os.path.join(output_dir, f'{file}_info.npy')

        if os.path.exists(filter_sname):
            try:
                filtered_tiles = np.load(filter_sname)
                print(f"Found existing filtered tiles for {file}, skipping tile filtering.")
            except:
                print(f"Error reading {filter_sname}, re-filtering tiles.")
                filtered_tiles = self.filter_tiles(tile_indices, generator)
                np.save(filter_sname, filtered_tiles)
        else:
            print(f"Didn't find existing filtered tiles for {file}, filtering tiles.")
            filtered_tiles = self.filter_tiles(tile_indices, generator)
            np.save(filter_sname, filtered_tiles)
        
        directory = os.path.join(output_dir, file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        existing_files_count = len([f for f in os.listdir(directory) if f.endswith('.jpeg')])
        
        filtered_tiles_count = len(filtered_tiles)
        threshold = 5 
        if abs(existing_files_count - filtered_tiles_count) <= threshold:
            print(f"Found approximately the same number of files as filtered tiles for {file}, skipping tile saving.")
        else:
            print('Now going to save tiles') 
            self.get_save_tiles(filtered_tiles, tile_indices, file, generator, directory)
        
        return file

    def parallel_process(self, files, base_dir='HNSC_DS', output_dir='/home/gp7/ml_pni/Dataset/tiles_1024'):
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(tqdm.tqdm(executor.map(self.process_one_slide, files, [base_dir]*len(files), [output_dir]*len(files)), total=len(files)))
        return results