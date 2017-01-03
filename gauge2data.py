#!/usr/bin/env python3
#-*- coding: utf-8 -*-

## Based on https://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/
## For example, this works:      ffmpeg -ss 00:00:05 -i test.3gp -ss 1 -f image2pipe -pix_fmt rgb24 -vcodec rawvideo - 

## Import common moduli
import matplotlib, sys, os, time
import matplotlib.pyplot as plt
import numpy as np
import subprocess as sp

from skimage.transform import (hough_line, hough_line_peaks, probabilistic_hough_line)
from skimage.feature import canny
from skimage import data

import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-i',         type=str,  help='input file name (may be any format accepted by ffmpeg)')
parser.add_argument('--fps',        type=float, default=24, help='frames per second; use 24 for real-time video, and e.g. 0.1 for timelapse with 10 second period')
parser.add_argument('--decim',      type=int, default=2, help='decimate images for faster processing')
parser.add_argument('--bpp',        type=int, default=3, help='bytes per pixel')
parser.add_argument('--croptop',    type=float, default=0.0, help='crop from top (from 0 to 1)')
parser.add_argument('--cropbottom', type=float, default=1.0, help='crop from bottom (from 0 to 1)')
parser.add_argument('--cropleft',   type=float, default=0.0, help='crop from left (from 0 to 1)')
parser.add_argument('--cropright',  type=float, default=1.0, help='crop from right (from 0 to 1)')
parser.add_argument('--threshold',  type=float, default=1.2, help='adjusting the Otsu threshold of white background (Hough transform works the best with flat background)')
parser.add_argument('--thresholdhard',  type=float, default=-1, help='if set positive, defines a hard brightness value of  threshold ')
parser.add_argument('--visual',     type=float, default=0, help='shows the line-detection results on each processed frame')

args = parser.parse_args()

os_ext = '' if os.name == 'posix' else '.exe' # on Linux, or Windows

input_file_name = args.i # 'test.3gp' if len(sys.argv)==1 else sys.argv[1]
bpp = 3   ## still, only the first (red?) channel will be used here
#visual = True

# You can get informations on a file (frames size, number of frames per second, etc.) by calling
ffoutput = sp.check_output(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'default=noprint_wrappers=1:nokey=1', 'test.3gp'])
xres, yres = [int(s) for s in ffoutput.split()]

# You can get informations on a file (frames size, number of frames per second, etc.) by calling
command = ['ffmpeg'+os_ext, '-ss', '00:00:00', '-i', input_file_name, '-f', 'image2pipe', '-pix_fmt', 'rgb24',
           '-vcodec','rawvideo', '-loglevel', 'error', '-']
ffoutput = sp.check_output(command)
raw_stream =  np.fromstring(ffoutput, dtype='uint8') # transform the byte read into a numpy array
framesize = xres*yres*bpp
framenumber = (len(raw_stream) / framesize)
#print("Data input contains %f frames" % framenumber )
print("#time(s)\tangle" % framenumber )
for nframe in range(int(framenumber)):
    image = raw_stream[framesize*nframe:framesize*(nframe+1)].reshape(yres,xres,bpp)[:,:,1]   ## process three-byte array to monochrome image

    ## crop and decimate
    image = image[int(yres*args.croptop):int(yres*args.cropbottom):args.decim, int(xres*args.cropleft):int(xres*args.cropright):args.decim] 

    if args.thresholdhard < 0:
        from skimage import filters                 ## automatic background removal using the Otsu thresholding
        val = filters.threshold_otsu(image)
        mask = image < (val*args.threshold)
        image = image*0
        image[mask] = 255
    else:
        image = 256-image                   ## take a negative
        image[image<((1-args.thresholdhard)*256)] = 0    ## thresholding is necessary for Hough to work

    # Find the longest line in probabilistic Hough
    lines = probabilistic_hough_line(image, threshold=10, line_length=5, line_gap=3)
    maxlength=-1
    if args.visual:
        fig, ax1 = plt.subplots(1, 1, figsize=(6,4))
        ax1.imshow(image, cmap=plt.cm.gray)

    for line in lines:      
        p0, p1 = line
        try:
            length = ((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)**.5
            if length > maxlength:
                angle = np.arctan(-(p0[0] - p1[0]) / (p0[1] - p1[1]))
                lengths_angles_lines = [length, angle, line]
                maxlength = length
        except ZeroDivisionError:
            pass

    length, angle, (p0, p1) = lengths_angles_lines
    if args.visual:
        ax1.plot((p0[0], p1[0]), (p0[1], p1[1]), c='r')
        plt.show()
    #print("frame n. %d was found with angle %f deg" % (nframe, angle/np.pi*180))
    print("%d\t%f" % (nframe/args.fps, angle/np.pi*180))



