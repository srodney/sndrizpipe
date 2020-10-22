sndrizpipe
=========

Image registration, combination and subtraction with astrodrizzle+tweakreg.
Aimed at simple processing of supernova imaging from HST.

Cite it using the v1.0 DOI : ![v1.0 DOI](https://zenodo.org/badge/4159/srodney/sndrizpipe.png)

---------
Dependencies
--------

Requires drizzlepac from STScI.  Recommended installation method: use
the AstroConda package, which provides python, numpy, pyraf, drizzlepac,
etc., with mutually compatible versions.  Maintained by STScI.
   
https://astroconda.readthedocs.io/en/latest/

---------
Environment variables
--------

You must set up some environment variables before running sndrizpipe, using either setenv or export or the equivalent (depending on your shell type).    Here is an example of how I've set this up in my .zshrc file: 

```
# ============================================================
#  IRAF cdbs directories : 


export CDBS=$HOME/Dropbox/cdbs/
export iref=$CDBS/iref/
export jref=$CDBS/jref/
export mtab=$CDBS/mtab/
export cracscomp=$CDBS/comp/acs/
export crotacomp=$CDBS/comp/ota/
export crwfc3comp=$CDBS/comp/wfc3/
export crnicmoscomp=$CDBS/comp/nicmos/
export crrefer=$CDBS/
export PYSYN_CDBS=$CDBS/
```

Directory Setup
---------

This pipeline is designed to process multi-epoch data for a single
target.  The target name is used to define where the input flt files
are stored, and then becomes the prefix for sub-directories and output
image products. 

In your working directory, make a `<name>.flt` directory to hold all the
pristine straight-from-the-archive flt files.  

For a list of options :

    sndrizpipe --help

if you don't give `--ra --dec` then the center position of the first image will be used.

use `--imsize` to give the width and height of the final output image in arcsec

if you don't set `--pixscale` and `--pixfrac` then the defaults are designed
 for 2-exposure image sets (i.e.  0.09" per pixel for IR, 0.04" for ACS)


Defining epochs
---------

The first time you run sndrizpipe it will sort the flt files from the
`<name>.flt` dir into epochs and generate a file `<name>_epochs.txt`
containing the sorted list of exposures.  Subsequent runs will adopt the
epochs sorting in that file, if present.

You must specify `--mjdmin` and/or `--mjdmax` to get images sorted into
epoch 0.  If present, epoch 0 is assumed to be the template epoch for
differencing.

Without `--mjdmin` or `--mjdmax` you will get epochs 1,2,...
and you then need to specify `--tempepoch 1` or `--tempepoch 2` to tell the
pipeline which epoch is the template.

FLT files that do not include the given target ra,dec will be sorted into
epoch -1.  That epoch never gets any further processing.

You can generate and check the `<name>_epochs.txt` file by first running
without any  `--do`  commands.   For example:

    sndrizpipe --ra 189.156538   --dec 62.309147 --mjdmin 56010 --mjdmax 56300 colfax

If you want to remake the epochs list, just delete the `<name>_epochs.txt`
file and re-run.

The command-line options for the 6 processing stages are:

1.  `--dosetup`    copy flt files into epoch subdirs
2.  `--dorefim`    build the WCS ref image
3.  `--dodriz1`    first astrodrizzle pass (pre-registration)
4.  `--doreg`      run tweakreg to align with refimage
5.  `--dodriz2`    second astrodrizzle pass (registered)
6.  `--dodiff`     subtract and mask to make diff images
*   `--doall`      Run all necessary processing stages


(1) Copy FLTs to sub-directories
--------

Each epoch gets a sub-directory called `<name>.e00`, `<name>.e01`, etc.

All filters go into the same subdir. The FLT files are copied into the
sub-directory (so the originals in `<name>.flt` remain pristine).
Subsequent astrodrizzle and tweakreg stages will make further copies and
modifications to those FLTs within the subdirs.

(2) WCS Ref image construction
--------

The pipeline makes a reference image that is subsequently used with
TweakReg to set a common WCS for all epochs and filters and cameras.
If you are going to have parallel processes for the same target then
you have to make this reference image first, before you start parallel
processing, because each parallel process will try to generate the
same ref image as the first step.

If you don't specify `--refepoch, --reffilter,` and `--refvisit` then the
defaults are first epoch, first filter, deepest available visit.
You can specify 1, 2 or all 3 of those refimage constraints, or none.

When possible, you should choose a filter, epoch and visit that put
the target near the center of the field, and will provide a deep,
CR-clean image with lots of sources for registration.  WFC3-IR is
good when available.  In principle you could use a cutout from a deep
mosaic image, though at present there is no tool for generating that. 

(3) First drizzle pass
--------

The first astrodrizzle pass operates on each HST visit separately. All files
within the visit and from the same filter are drizzled together into the
natural rotation frame (i.e. adopting the HST orientation instead of putting
north up and east to the left). If the `--drizcr` flag is set,
then this pass will also set new cosmic ray flags in the FLT data quality arrays.  Otherwise, the CR flagging from the HST
archive is left in place.  This first pass will set the output pixel scale
automatically based on the number of FLT files in each filter+visit group.
By improving the PSF sampling, this can sometimes deliver better CR
rejection than the automated pipeline, if you have more than 2
exposures.

The output products from this stage have the suffix `_nat_drz_sci.fits` (or
`_nat_drc_sci.fits` for CTE-corrected ACS and UVIS files.)


(4) Registration
--------

Each FLT file is registered to the WCS ref image with tweakreg. Tweakreg
finds sources in the natural-rotation drizzled image products and compares
them to a source catalog drawn from the WCS refimage. Using the
`--interactive` mode, the user can see tweakreg 2D
histograms and residual plots, and can modify the tweakreg parameters
on-the-fly.

When registrations go really awry, the current best practice is to just wipe
out all the affected products and restart from the top.  A future version
will provide a more efficient option to restart only the registration stage.

The user may provide a reference catalog using the `--refcat` option,
in which case the tweakreg registration will only use detected sources that
have a match in that catalog.  The reference catalog must have `RA` and
`DEC` as the first two columns, and may optionally include a third `FLUX`
column.   An existing catalog in Sextractor or commented_header format can
be converted to this tweakreg format using `mkrefcat.py` as follows:

    mkrefcat.py incatfile outcatfile

Use `mkrefcat.py --help` for more options.


(5) Second (final) drizzle pass
--------

After the WCS parameters in the FLT file headers have been updated,
the final astrodrizzle run will create drizzled image products,
rotated with north up and east to the left.  All filters from each camera
are drizzled to the same pixel scale and all output images have the same
image size in arcseconds.   To explicitly specify a different pixel scale
for the different cameras, the corresponding filters and epochs should be
run with separate processes, and different values given for `--pixscale` and
 `--pixfrac`.

ACS or UVIS images that started as CTE-corrected flt files (`_flc.fits`)  will
 end as `reg_drc_sci.fits`, and IR images will be `reg_drz_sci.fits`.
This stage also produces `drz_wht.fits` files with the inverse variance map
weight images, and `drz_bpx.fits` files with the bad pixel masks.  These
mask out only those pixels that have zero weight in the output `sci.fits`
images (i.e. there was no good pixel from any input image at that location).

(6) Template Subtraction
--------

 If a template image is available, this final stage will generate
`sub_sci.fits` difference images.  These are straight subtractions,
without any psf convolution.  

The accompanying `sub_wht.fits` files are the inverse of the combined
variance from the template and the target epochs, and `sub_bpx.fits`
are the union of the two contributing bad pixel masks.  Applying the
badpix mask to the diff image then produces the final
`sub_masked.fits` product.

In the current version, lots of cruft is left behind in the sub-directories
(intermeidate flt files, ctx.fits, etc). A future version will have a
--docleanup stage to remove them.



### Building and using sndrizpipe with docker

To build sndrizpipe as a docker container run:

```bash
docker build -t sndrizpipe .
```

To run the test, change directorty to the folder with the extracted sndrizpipe/colfax_test.tgz data. Then the docker image can be run with:

```bash
docker run -v$PWD:/work -it --rm sndrizpipe --filters F160W  --doall --mjdmin 56010 --mjdmax 56300 --ra 189.156538 --dec 62.309147  --refcat 'goodsn_mosaic.cat' colfax
```

You can also create a bash/zsh function to seem as if you're running sndrizpipe nativly by adding this to your `.bashrc`/`.zshrc` file:

```bash
sndrizpipe () {
	docker run -v$PWD:/work -it --rm sndrizpipe $@
}
```
