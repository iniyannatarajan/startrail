#!/usr/bin/env python

import os, sys
import numpy as np
import argparse
from PIL import Image

def compute_darkframe(darkframedir):
    print('Computing median darkframe...')
    files = os.listdir(darkframedir)
    darkframes = [name for name in files if name[-4:] in [".jpg", ".JPG"]]
    width, height = Image.open(os.path.join(darkframedir,darkframes[0])).size

    dflist = []
    for df in darkframes:
        dflist.append(np.array(Image.open(os.path.join(darkframedir, df)), dtype=np.float))
    darkframe = np.uint8(np.median(dflist, 0))

    return darkframe

def main():
    # Parse the input arguments
    parser = argparse.ArgumentParser(description="Stack images to create star trails")
    parser.add_argument('imagedir', type=str)
    parser.add_argument('-d', '--darkframedir', type=str, default=None)
    parser.add_argument('-o', '--outfile', type=str, default='startrail.jpg')
    args = parser.parse_args()

    imagedir = args.imagedir
    darkframedir = args.darkframedir
    outfile = args.outfile

    if not os.path.isdir(imagedir):
        print('Input image directory not found. Exiting...')
        sys.exit(1)
    if darkframedir and not os.path.isdir(darkframedir):
        print('Input darkframe directory not found. Exiting...')
        sys.exit(1)

    files = os.listdir(imagedir)
    images = [name for name in files if name[-4:] in [".jpg", ".JPG"]]
    width, height = Image.open(os.path.join(imagedir, images[0])).size

    if darkframedir:
        darkframe = compute_darkframe(darkframedir)
    else:
        print('No darkframes given. Will not correct images.')

    print('Processing images...')
    stack = np.zeros((height, width, 3), np.float)
    for image in images:
        imarray = np.array(Image.open(os.path.join(imagedir, image)), dtype = np.float)
        if darkframedir:
            imarray -= darkframe
        stack = np.maximum(stack, imarray) # Brighten instead of add (courtesy: Tobias Westmeier's blog)

    stack = np.array(np.round(stack), dtype=np.uint8)
    output = Image.fromarray(stack, mode="RGB")
    output.save(outfile, "JPEG")

if __name__ == '__main__':
    ret = main()
    sys.exit(ret)
