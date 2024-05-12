# WebP Crawler

WebP Crawler is a Python-based GUI application designed to convert all images within a specified directory to WebP (or PNG) format while maintaining the original folder tree structure.
You can choose whether to include subdirectories in the conversion process or not.

## Features

- **Bulk Image Conversion**: Efficiently converts a large number of images.
- **Format Flexibility**: Supports conversion to both WebP and PNG formats.
- **Optional Subdirectory Inclusion**: Choose whether or not to include subfolders in the conversion process.

## Ideal Users

This tool is perfect for those who have a large collection of images and are looking to save disk space without compromising on image quality.

## Usage
WebP Crawler is very easy to use, with a simple GUI:
- Choose the source folder, from which the program will convert the files.
- Choose the destination folder, to which the converted files will be written.
- Choose the quality value of the image, with the "lossless" option being the best quality, sacrificing disk space.
- Choose the image format:
    >WebP: Offers both lossy and lossless compression, typically resulting in smaller file sizes (25-34% smaller than PNG or JPEG).  
    PNG: Uses lossless compression, often resulting in larger file sizes. 
- Choose whether or not to include subfolders in the conversion. If this option is selected, the program will convert every image inside the folder **as well as** in any subfolders it contains.
