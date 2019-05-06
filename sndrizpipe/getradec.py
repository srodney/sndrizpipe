#! /usr/bin/env python
# S.Rodney
# 2016.12.27
from astropy.io import fits as pyfits
from glob import glob
from os import path
import numpy as np


def mkparser():
    import argparse

    class SmartFormatter(argparse.HelpFormatter):
        def _split_lines(self, text, width):
            # this is the RawTextHelpFormatter._split_lines
            if text.startswith('R|'):
                return text[2:].splitlines()
            return argparse.HelpFormatter._split_lines(self, text, width)

    parser = argparse.ArgumentParser(
        description='Compute the median RA,Dec from a set of FLT files.',
        formatter_class=SmartFormatter)

    # Required positional argument
    parser.add_argument('fltdir',
                        help='Directory containing the flt files.')

    # optional arguments :
    parser.add_argument('--includeflc', action='store_true', default=False,
                        help='Use FLC files. (normally uses only FLTs)')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Verbose output.')
    # TODO: allow user to input a specific list of flt files or
    # a shell string with wildcard characters.

    return(parser)


def main():
    parser = mkparser()
    argv = parser.parse_args()
    verbose = argv.verbose
    if verbose:
        print(('Looking for FLT files in %s' % argv.fltdir))

    if argv.includeflc:
        fltlist = glob(path.join(argv.fltdir, '*fl?.fits'))
    else:
        fltlist = glob(path.join(argv.fltdir, 'i*flt.fits'))

    if verbose:
        print(('Found %i FLT files.' % len(fltlist)))

    targnamelist, ralist, declist = [], [], []
    for fltfile in fltlist:
        if verbose:
            print(('checking %s' % fltfile))

        targnamelist.append(pyfits.getval(fltfile, 'TARGNAME', ext=0))
        ralist.append(pyfits.getval(fltfile, 'CRVAL1', ext=1))
        declist.append(pyfits.getval(fltfile, 'CRVAL2', ext=1))
    #TODO: check that there is not a large variance in RA or DEC
    ra = np.median(ralist)
    dec = np.median(declist)


    targname = ' '.join(np.unique(targnamelist).tolist())
    print(("TARGET=%s" % targname))
    print(("RA=%.6f" % ra))
    print(("DEC=%.6f" % dec))
    return 0



if __name__ == "__main__":
    main()

