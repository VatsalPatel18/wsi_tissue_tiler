import argparse
from slide_processor import SlideProcessor

def main():
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

    processor = SlideProcessor(
        tile_size=args.tile_size,
        overlap=args.overlap,
        tissue_threshold=args.tissue_threshold,
        max_workers=args.max_workers
    )
    processor.process_one_slide(args.svs_file_path, output_dir=args.output_dir)

if __name__ == '__main__':
    main()
