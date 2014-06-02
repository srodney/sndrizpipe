#! /usr/bin/env python
# S.Rodney 2014.05.06

def writeDS9reg( catalog, regfile, color='green', shape='diamond',
                 linewidth=1 ):
    """ Write out a DS9 region file from the given catalog
    catalog may be a file name or an astropy table object.
    """
    from astropy.coordinates import ICRS
    from astropy import units as u
    from astropy.io import ascii

    if isinstance(catalog,basestring) :
        catalog = ascii.read( catalog )

    fout = open(regfile,'w')
    print>>fout,"# Region file format: DS9 version 5.4"
    print>>fout,'global color=%s font="times 16 bold" select=1 edit=1 move=0 delete=1 include=1 fixed=0 width=%i'%(color,linewidth)

    for row in catalog :
        RA = row['RA']
        DEC = row['DEC']
        if ':' in str(RA) :
            coord = ICRS( ra=RA,dec=DEC, unit=(u.hour,u.degree) )
        else :
            coord = ICRS( ra=RA, dec=DEC, unit=(u.degree,u.degree) )

        xstr  = coord.ra.to_string( unit=u.hour,decimal=False, pad=True,sep=':', precision=2 )
        ystr  = coord.dec.to_string( unit=u.degree, decimal=False, pad=True, alwayssign=True, sep=':', precision=1 )
        print>>fout,'point  %s  %s  # point=%s'%( xstr, ystr, shape )
    fout.close()

def convertToRefcat( incatfile, refcatfile, fluxcol=None, magcol=None,
                     ds9regfile=False, clobber=False, verbose=False ):
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
    import numpy as np
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
    elif magcol :
        if magcol not in incat.colnames :
            raise exceptions.RuntimeError(
                "There is no column %s in %s."%(magcol, incatfile) )
        savecolnames = [racol,deccol,magcol]
        # convert from mags to flux using an arbitrary zpt = 25
        igoodmags = np.where( (incat[magcol]>-9) & (incat[magcol]<99) )
        incat[magcol][igoodmags] = 10**(-0.4*(incat[magcol][igoodmags]-25))
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
    if ds9regfile :
        writeDS9reg( incat, ds9regfile )

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Convert a source catalog into the format required '
                    'for use as a tweakreg reference catalog.'
                    '(Requires astropy)' )

    # Required positional argument
    parser.add_argument('incatfile', help='Input catalog. May be in any format'
                                          'recognized by astropy.')
    parser.add_argument('refcatfile', help='Output reference catalog file name')
    parser.add_argument('--fluxcol', default=None,
                        help='Name of the input catalog column containing '
                             'fluxes, to be used by tweakreg '
                             'for limiting detected source lists.')
    parser.add_argument('--magcol', default=None,
                        help='Name of the input catalog column containing '
                             'magnitudes, to be converted to fluxes and then'
                             'used by tweakreg for limiting source lists.')
    parser.add_argument('--ds9reg', type=str, metavar='X.reg',
                        help='Write out a ds9 region file.' )
    parser.add_argument('--clobber', default=False, action='store_true',
                        help='Clobber existing reference catalog if it exists. [False]')
    parser.add_argument('--verbose', default=False, action='store_true',
                        help='Turn on verbose output. [False]')

    argv = parser.parse_args()
    convertToRefcat( argv.incatfile, argv.refcatfile, fluxcol=argv.fluxcol,
                     magcol=argv.magcol, ds9regfile=argv.ds9reg,
                     clobber=argv.clobber, verbose=argv.verbose )

if __name__=='__main__' :
    main()