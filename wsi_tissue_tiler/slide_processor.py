import numpy as np
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import PIL
import matplotlib.pyplot as plt
import os
import openslide
from openslide import OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
from concurrent.futures import ProcessPoolExecutor
import math
import tqdm

class SlideProcessor:
    def __init__(self, tile_size=1024, overlap=0, tissue_threshold=0.65, max_workers=60,CINFO=None,output_dir=None):
        self.tile_size = tile_size
        self.overlap = overlap
        self.tissue_threshold = tissue_threshold
        self.max_workers = max_workers
        self.output_dir = output_dir


    def fetch_tile(self, tile_index, generator):
        """ Fetch a single tile given a tile index and the tile generator. """
        tile_size, overlap, zoom_level, col, row = tile_index
        tile = np.asarray(generator.get_tile(zoom_level, (col, row)))
        return (col, row), tile

    def get_tiles(self, filtered_tiles, tile_indices, generator):
        """ Retrieve tiles in parallel and return them as a dictionary with (col, row) keys. """
        tiles = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.fetch_tile, ti, generator) for ti in tile_indices if (ti[3], ti[4]) in filtered_tiles]
            
            for future in futures:
                key, tile = future.result()
                if tile.shape == (self.tile_size,self.tile_size,3):
                    tiles[key] = tile        
        
        return tiles
    
    def save_tiles(self, tiles,tissue_tiles):
        """ Save tiles to the specified output directory, each tile will be saved as a JPEG file. """
        """ The tissue tiles are processed tissue tiles, ideally of the shape of (3,224,224) and float values """ 
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        for col, row in tissue_tiles.keys():
            img = PIL.Image.fromarray(tiles[(col,row)])
            file_path = os.path.join(self.output_dir, f'tile_{col}_{row}.jpeg')
            img.save(file_path)
            print(f"Saved tile to {file_path}")

    def process_one_slide(self, file_loc,to_save=False,save_dir=None):
        f2p = file_loc
        
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
        
        x_info = tile_indices.copy()

        all_x_info = [x[-2:] for x in x_info ]
        tiles = self.get_tiles(all_x_info, tile_indices, generator) 
        
        return tiles
