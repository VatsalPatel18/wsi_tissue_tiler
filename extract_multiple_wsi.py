import argparse
from slide_processor_parallel import SlideProcessor

def main():
    parser = argparse.ArgumentParser(description='Process multiple whole slide images from a directory.')
    parser.add_argument('-d', '--directory', type=str, required=True,
                        help='Directory containing whole slide image files.')
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
    processor.parallel_process(base_dir=args.directory, output_dir=args.output_dir)

if __name__ == '__main__':
    main()
