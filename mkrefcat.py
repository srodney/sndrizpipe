#! /usr/bin/env python
# S.Rodney 2014.05.06

def convertToRefcat( incatfile, refcatfile, fluxcol=None,
                     clobber=False, verbose=False ):
    """ Read in the catalog incatfile and write out as a tweakreg reference
    catalog called refcatfile.
    The file incatfile may be in any of the formats recognized by the
    astropy.io.ascii  library (e.g. ascii text, sextractor), but it must
    have a list of column names, including at least the RA and Dec columns.

    The argument fluxcol can be used to give the column name for a single
    column of measured source fluxes to be written out as a third column
    in the output tweakreg reference catalog file.
    """
    import os
    from astropy.io import ascii
    import exceptions
    incat = ascii.read( incatfile )

    if os.path.exists( refcatfile ) and not clobber :
        print("Tweakreg reference catalog %s exists. Not clobbering."%refcatfile)
        return
    if verbose :
        print("Converting input catalog %s into tweakreg ref cat %s"%(incatfile, refcatfile))

    gotracol = False
    for racol in ['X_WORLD','RA','ra','R.A.','ALPHA_J2000','ALPHA', 'Ra']:
        if racol in incat.colnames :
            gotracol = True
            break
    gotdeccol = False
    for deccol in ['Y_WORLD','DEC','dec','Dec','Decl','DELTA_J2000','DELTA']:
        if deccol in incat.colnames :
            gotdeccol = True
            break
    if not (gotracol and gotdeccol) :
        raise exceptions.RuntimeError(
            "Can't read RA, Dec columns from catalog %s"%incatfile )


    if fluxcol :
        if fluxcol not in incat.colnames :
            raise exceptions.RuntimeError(
                "There is no column %s in %s."%(fluxcol, incatfile) )
        savecolnames = [racol,deccol,fluxcol]
        outcolnames = ['RA','DEC','FLUX']
    else :
        savecolnames = [racol,deccol]
        outcolnames = ['RA','DEC']

    removelist = [ colname for colname in incat.colnames
                   if colname not in savecolnames ]
    incat.remove_columns( removelist )
    for incol,outcol in zip( savecolnames, outcolnames):
        if outcol not in incat.colnames :
            incat.rename_column( incol, outcol )

    incat.write( refcatfile, format='ascii.commented_header' )

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert a source catalog into the format required '
                    'for use as a tweakreg reference catalog.')

    # Required positional argument
    parser.add_argument('incatfile', help='Input catalog. May be in any format recognized by astropy.')
    parser.add_argument('refcatfile', help='Output reference catalog file name.')
    parser.add_argument('--fluxcol', default=None, help='Name of the input catalog column containing fluxes or magnitudes, to be used by tweakreg for limiting detected source lists.')
    parser.add_argument('--clobber', default=False, action='store_true', help='Clobber existing reference catalog if it exists. [False]')
    parser.add_argument('--verbose', default=False, action='store_true', help='Turn on verbose output. [False]')

    argv = parser.parse_args()
    convertToRefcat( argv.incatfile, argv.refcatfile, fluxcol=argv.fluxcol,
                     clobber=argv.clobber, verbose=argv.verbose )

if __name__=='__main__' :
    main()