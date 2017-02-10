## gauge2data - record a movie of an analog gauge, get the time-resolved plot

This script can be useful for everybody who uses or repairs old analog instruments of any kind. By means of the [Hough transform](https://en.wikipedia.org/wiki/Hough_transform), it find the angle of the longest line in each video frame. Therefore, if you place a camera or a mobile phone in front of an old instrument and record a video, you can later get the temporal evolution of any quantity displayed by an analog gauge, without tapping any wire in the instrument and without exporting data from a digital oscilloscope. It may be useful to switch to the timelapse function of the camera/phone, but in this case you want to remember what is its frames-per-second rate for later scaling of the x-axis.

#### Input
An example: Assume you have recorded the 720x480 video that follows, with 0.1 FPS. (For this README, a thumbnail was created with smaller size and converted to gif.)
<!---  commands to generate it: 
ffmpeg -i test.3gp -filter:v scale=240:-1 -vf "fps=15,scale=320:-1:flags=lanczos,palettegen" -y  palette.png
ffmpeg -v warning -i test.3gp -i palette.png -lavfi "fps=15,scale=320:-1:flags=lanczos [x]; [x][1:v] paletteuse" -y out.gif
 -->
![Resized input](input_resized.gif)

Technical limitations: whole raw video stream, frame by frame, are loaded into the memory, no matter what decimation or frameskipping is selected. This takes a long time and limits the size of videos in the lower 10s MB range. More efficient file input (e.g. by some options to the ffmpeg filters) should be used in the future.

#### Conversion
To get reasonable results, all unwanted long straight lines should be cropped, including the gauge boundaries. To this end, specify the `-topcrop`, `-bottomcrop`, `-leftcrop`, `-rightcrop` parameters as numbers from 0 (no crop) up to 1 (would crop the whole image).

By default, the internal "Otsu" black/white thresholding algorithm should work well, but if needed, you can tune the `adjustthreshold` parameter, or in special cases you can also try to use simple thresholding by a given value (the `-hardthreshold` option).

The correct command used here is:
```

```
It takes few tens of seconds to 

For visual debugging, enable the option `-visual 1` to see  the pre-processed images that are passed to the Hough transform.

#### Data calibration
Finally, you will want to calibrate the gauge, i.e. to assign the resolved angles to actual values. By default, _gauge2data_ picks five equidistant angles, shows the corresponding images and asks you for the actual value readout. You can change the number of the calibration points by the option `-calibrate`; set it to zero to output plain, non-calibrated, angles.

#### Result
![The results](penning_example.png)

The result is in two-column ASCII file and can be easily plotted e.g. using the [plotcommander program](https://github.com/FilipDominec/plotcommander).


## Installation and compatibility
The program was tested on Ubuntu 16.10, needing the following dependencies:

```
apt install ffmpeg python3-scipy python3-skimage python3-skimage-lib python3-matplotlib
```

If you can not run it, and need to convert just few files, feel free to contact the author personally. 

## Command-line parameters
```
usage: gauge2data.py [-h] [-input INPUT] [-output OUTPUT] [-topcrop TOPCROP]
                     [-bottomcrop BOTTOMCROP] [-leftcrop LEFTCROP]
                     [-rightcrop RIGHTCROP] [-fps FPS] [-decim DECIM]
                     [-skipframes SKIPFRAMES] [-BPP BPP]
                     [-adjustthreshold ADJUSTTHRESHOLD]
                     [-hardthreshold HARDTHRESHOLD] [-visual VISUAL]
                     [-calibrate CALIBRATE]

Convert a (timelapse) video of an analog gauge to a data series

optional arguments:
  -h, --help            show this help message and exit
  -input INPUT          input file name (may be any format accepted by ffmpeg)
  -output OUTPUT        output file name (stdout if left empty)
  -topcrop TOPCROP      crop from top (from 0 to 1)
  -bottomcrop BOTTOMCROP
                        crop from bottom (from 0 to 1)
  -leftcrop LEFTCROP    crop from left (from 0 to 1)
  -rightcrop RIGHTCROP  crop from right (from 0 to 1)
  -fps FPS              frames per second; use 24 for real-time video, and
                        e.g. 0.1 for timelapse with 10 second period
  -decim DECIM          decimate images for faster processing, set to 0
  -skipframes SKIPFRAMES
                        process every n-th frame only
  -BPP BPP              bytes per pixel
  -adjustthreshold ADJUSTTHRESHOLD
                        adjusting the Otsu threshold of white background
                        (Hough transform works the best with flat background)
  -hardthreshold HARDTHRESHOLD
                        if set positive, defines a hard brightness value of
                        thresholding
  -visual VISUAL        shows the line-detection results on each processed
                        frame
  -calibrate CALIBRATE  if nonzero, enables interactive calibration on the
                        selected values; otherwise angles are output
```



