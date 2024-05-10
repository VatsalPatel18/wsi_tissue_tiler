import torch
import numpy as np
import argparse
from slide_processor import SlideProcessor
from TissueIdentifier import TissueIdentifier
from transformers import CLIPImageProcessor

def main(svs_file_path, tile_size, output_dir, max_workers):
    processor = SlideProcessor(tile_size=tile_size, overlap=0,,output_dir=output_dir, max_workers=max_workers)
    tiles = processor.process_one_slide(svs_file_path)
    
    clip_processor = CLIPImageProcessor.from_pretrained("./clip_img_processor")
    tc = TissueIdentifier('./tissue_identifier.pth',clip_processor)
    tissue_tiles = tc.process_and_identify(tiles)
    
    processor.save_tiles(tissue_tiles)

    return 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Process a single whole slide image.')
    parser.add_argument('-i', '--svs_file_path', type=str, required=True,
                        help='Path to the whole slide image file.')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Directory to save the processed tiles.')
    parser.add_argument('-t', '--tile_size', type=int, default=1024,
                        help='Size of the tile (default: 1024).')
    parser.add_argument('-v', '--overlap', type=int, default=0,
                        help='Overlap of tiles (default: 0).')
    parser.add_argument('-th', '--tissue_threshold', type=float, default=0.65,
                        help='Threshold for tissue detection (default: 0.65).')
    parser.add_argument('-w', '--max_workers', type=int, default=30,
                        help='Maximum number of worker threads/processes (default: 30).')
    args = parser.parse_args()

    result = main(args.svs_file_path, args.tile_size, args.output_dir, args.max_workers)
    print(f"Predicted value: {result}")