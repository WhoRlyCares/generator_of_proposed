


### File generation
- if `--nograph`, `-b` no opts provided, generates binary noise.
- if `-svg` provided, generates files with random rectangles 

###
Writing png images requires additional libries. By default, comes with wand as wrapper over ImageMagic.

In case imageMagic is not located on target system will try to fall back to Pillow, which is not specified at requirements txt, so will fail if not installed manualy.

If both cases fail will generate plain svgs.