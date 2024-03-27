# WSI Tissue Tiler

This project processes whole slide images (WSI) to extract tissue tiles using parallel processing. It utilizes the `SlideProcessor` class to handle the image processing efficiently.

## Getting Started

These instructions will guide you through the setup and execution of the WSI Tissue Tiler, including the use of the Docker container.

### Prerequisites

- Docker
- Python 3.8 or later
- Git

## Method 1: Using Docker

If you want to start quickly, you can pull the ready-made Docker image and run it.

### Using Pre-Built Docker

Pull the Docker image from Docker Hub with the following command:

```bash
docker pull vatsalpatel18/wsi_tissue_tiler:latest
```
## Method 2: Manual Setup

### Clone the Repository
First, clone this repository to your local machine:
```bash
git clone git@github.com:VatsalPatel18/wsi_tissue_tiler.git
cd wsi_tissue_tiler
```
### Build and Run Docker Container
Build the Docker Image
```bash
docker build -t wsi_tissue_tiler:latest .
```
Run the Docker container:
For Jupyter lab:
```bash
docker run -p 7878:7878 -v /path/to/WSI:/app/WSI -v /path/to/outputs:/app/outputs wsi_tissue_tiler
```
For Unix Systems:
```bash
docker run -v /path/to/WSI:/app/WSI -v /path/to/outputs:/app/outputs wsi_tissue_tiler process_wsi -d /app/WSI -o /app/outputs -w 60
```
Replace /path/to/WSI and /path/to/outputs with the actual paths to your data and output directories on your host machine.

### Parameters
-d, --directory: Directory containing whole slide image files.
-o, --output_dir: Directory to save the processed tiles.
-t, --tile_size: Size of the tile (default: 1024).
-v, --overlap: Overlap of tiles (default: 0).
-th, --tissue_threshold: Threshold for tissue detection (default: 0.65).
-w, --max_workers: Maximum number of worker threads/processes (default: 30).
