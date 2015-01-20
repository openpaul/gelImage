# gelImage
This code enables a user to simply annotate gel images. It is designed to make quick annotations of agarose gels or sds-PAGE's possible.
It is not a fully working annotation software. If does not have any features for so called
"eye candy". It is slow and has serveral limitations. Feel free to contribute code.

## How to use it:
First install python 2.x: https://wiki.python.org/moin/BeginnersGuide/Download and Cairo, PIL, wxpython.
This shuld be easy on GNU/Linux. 

I only testet it on Xubuntu 14.10. A short test on windows resulted in a various errors.

As you run the script in Python a window should open. A workflow could look like this:

- open file (CTRL+S)
- invert image (CTRL+I)
- rotate image sligthly
- crop image
- add a ladder
 - click on the visible bands of the ladder to make lines appear
- add labels
 - click on the positions where to show the label (only horizontal for now)

![Screenshot gelImage](https://raw.githubusercontent.com/openpaul/gelImage/master/screenshot.png)

## Version info:
Features and limitations:

works:
- open image (png, TIF)
- invert image
- rotate image [buggy but works]
- crop image (very slow!)
- save image as png
- export only selection
- add and remove ladders
- draw lines to ladder bands
- add labels
- select various ladders

not yet implemented or not working:
- work with large images (larger than screen)
- 2D gels
 - vertical labels
 - horizontal ladders
- performance