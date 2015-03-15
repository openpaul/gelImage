# gelImage
This code enables a user to simply annotate gel images. It is designed to make quick annotations of agarose gels or sds-PAGE's possible.
It is not a fully working annotation software! If does not have any features for so called
"eye candy". It is slow and has serveral limitations. Feel free to contribute code.

## How to use it:
First install python 2.7.x: https://wiki.python.org/moin/BeginnersGuide/Download and Cairo, PIL, wxpython.
This shuld be easy on GNU/Linux. 

I only testet it on Xubuntu 14.10. A short test on windows resulted in a various errors.

As you run the script in Python a window should open. A workflow could look like this:

- open file (CTRL+S)
- invert image (CTRL+I)
- rotate image sligthly (CTRL+R)
- crop image (CTRL+K)
- add a ladder (CTRL+L)
 - click on the visible bands of the ladder to make lines appear
- add labels (CTRL+J)
 - click on the positions where to show the label (only horizontal for now)

![Screenshot gelImage](https://raw.githubusercontent.com/openpaul/gelImage/master/screenshot.png)

## Version info:
Features and limitations:

works:
- open image (png, TIFF (also 16 bit))
- invert image
- rotate image [buggy but works]
- crop image (very slow and buggy)
- save image as svg
- export only selection as png
- add and remove ladders
- draw lines to ladder bands
- add labels
 - add custom labels and rotate them
- select various ladders

not yet implemented or not working:
- work with large images (larger than screen)
- 2D gels
 - vertical labels
 - horizontal ladders
- performance
 - is bad because I use cairo lib for drawing. This libary produces nice svg-graphics but is not very performant