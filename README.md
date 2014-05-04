sndrizpipe
=========

Image registration, combination and subtraction with astrodrizzle+tweakreg.  Aimed at simple processing of supernova imaging from HST.

Requires drizzlepac from STScI.   
Recommended installation method:
   use the Ureka package, which provides python, numpy, pyraf, drizzlepac, etc., with mutually compatible versions, bundled and maintained by STScI/Gemini.
   
http://ssb.stsci.edu/ureka/   

---------

WFC3 UVIS CTE correction functions are from Jay Anderson
 (via   http://www.stsci.edu/hst/wfc3/tools/cte_tools)

To compile, use g77 or gfortran:


gfortran wfc3uv_ctereverse.F -o wfc3uv_ctereverse.e

gfortran wfc3uv_ctereverse_wSUB.F -o wfc3uv_ctereverse_wSUB.e

gfortran wfc3uv_ctereverse_parallel.F -o wfc3uv_ctereverse_parallel.e -fopenmp


(the first is for full-frame, the second for sub-arrays, the third uses parallel processing)


