import os
import argparse
from slide_processor import SlideProcessor
from TissueIdentifier import TissueIdentifier
from transformers import CLIPImageProcessor

def main(svs_directory, tile_size, output_dir, max_workers):
    processor = SlideProcessor(tile_size=tile_size, overlap=0,output_dir=output_dir, max_workers=max_workers)

    clip_processor = CLIPImageProcessor.from_pretrained("./clip_img_processor")
    tc = TissueIdentifier('./tissue_identifier.pth',clip_processor)
    
    files = [os.path.join(svs_directory, f) for f in os.listdir(svs_directory) if f.endswith('.svs')]
    
    for file_path in files:
        print(f"Processing: {file_path}")
        tiles = processor.process_one_slide(file_path)
        tissue_tiles = tc.process_and_identify(tiles)
        name = file_path.rstrip('.svs').split('/')[-1]
        svpath = os.path.join(output_dir,name)
        tc.save_tissue_tensor(tissue_tiles,svpath)

        # tc.save_tissue_pickle(tissue_tiles,name,output_dir)
        # processor.save_tiles(tissue_tiles)
        
    return 

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Process a single whole slide image.')
    parser.add_argument('-d', '--svs_directory', type=str, required=True,
                        help='Directory containing whole slide image files.')
    parser.add_argument('-o', '--output_dir', type=str, required=True,
                        help='Directory to save the processed tiles.')
    parser.add_argument('-t', '--tile_size', type=int, default=1024,
                        help='Size of the tile (default: 1024).')
    parser.add_argument('-v', '--overlap', type=int, default=0,
                        help='Overlap of tiles (default: 0).')
    parser.add_argument('-th', '--tissue_threshold', type=float, default=0.95,
                        help='Threshold for tissue detection (default: 0.95).')
    parser.add_argument('-w', '--max_workers', type=int, default=30,
                        help='Maximum number of worker threads/processes (default: 30).')
    args = parser.parse_args()

    main(args.svs_directory, args.tile_size, args.output_dir, args.max_workers)
