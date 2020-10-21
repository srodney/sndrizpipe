"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Makes a smaller centered image from a bigger hubble image
    Does a transient search
    Gets the best peak, and the associated best shift to perform
    make some plots about the search for a new peak in the single image
ARGS:
    CheckArguments
        Type:
            python boolean
        Description:
            if true, checks the arguments with conditions written in the function
            if false, ignores those conditions
    PrintExtra
        Type:
            python integer
        Description:
            if greater than 0, prints addional information about the function
            if 0, function is expected to print nothing to console
            Additional Notes:
                The greater the number, the more output the function will print
                Most functions only use 0 or 1, but some can print more depending on the number
    SubtractionImageFilePath
        Type:
            <class 'NoneType'>
        Description:
            None
    SingleSuperNovaId
        Type:
            <class 'NoneType'>
        Description:
            None
    SingleSuperNovaRa
        Type:
            <class 'NoneType'>
        Description:
            None
    SingleSuperNovaDec
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import numpy
import hstphot
import astropy
import matplotlib
#-------------------------------------------------------------------------------
import Config_NumpyMatplotlibColors
import Library_FitsSubtractionImageFindBrightestTransient
import Library_StringFilePathGetFileName
import Library_SystemGetLocalDataDirectory
import Library_BarbaraMikulskiArchiveSearchProductListMetaDataAuto
import Library_FileWriteText
import Library_JsonDump
import Library_GraphScatterCrossHair
import Library_GraphTwoDimensionDensityColorMap
#-------------------------------------------------------------------------------
def Main(
    SubtractionImageFilePath= None,
    SuperNovaId = None,
    RaCatalog= None,
    DecCatalog= None,

    DoPlotOriginalImage = None,
    DoPlotCenterSquareImage= None,
    DoPlotFull= None,
    ShowPlots= None,

    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None



    if DoPlotOriginalImage is None:
        DoPlotOriginalImage = True
    if DoPlotCenterSquareImage is None:
        DoPlotCenterSquareImage = True
    if DoPlotFull is None:
        DoPlotFull = True
    if ShowPlots is None:
        ShowPlots = False


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Filepath and directory management:
    SingleSubMaskedFilePath = SubtractionImageFilePath
    DataDirectory = Library_SystemGetLocalDataDirectory.Main(    )
    TransientFindingFolderPath = DataDirectory + '/AstronomySuperNovaData/SuperNovaTransientFinder'
    SaveFolderPath = TransientFindingFolderPath + '/' + str(SuperNovaId)
    print ('SaveFolderPath', SaveFolderPath)


    #Search the meta data for RA and DEC of the supernova id of interest:
    SingleSuperNovaIdMetaDataSearchResults = Library_BarbaraMikulskiArchiveSearchProductListMetaDataAuto.Main(
        ConditionDictionary= {'ID': str(SuperNovaId) }
        )

    #Save the metadata search results to file:
    Library_FileWriteText.Main(
        FilePath = SaveFolderPath + '/' + 'catalog_info.json',
        Text = Library_JsonDump.Main( NestedObject= SingleSuperNovaIdMetaDataSearchResults  ),
        OverWrite = True,
        )






    #Get the x,y coordinate associated with the Ra, Dec in the diff image
    Xcatalog, Ycatalog = hstphot.util.radec2xy(SingleSubMaskedFilePath, RaCatalog, DecCatalog )

    #Transform the coordinates to the center square of the image:
    XcatalogSquare = Xcatalog-200
    YcatalogSquare = Ycatalog-200
    XYcatalogSquareNumpyDataset = numpy.array([[XcatalogSquare,YcatalogSquare]])
    print ('XcatalogSquare, YcatalogSquare', XcatalogSquare, YcatalogSquare)

    ImageDataCenterSquare = astropy.io.fits.getdata(SingleSubMaskedFilePath, ext=0)[200:300, 200:300] #[yvals, xvals]
    print ('ImageDataCenterSquare.shape', ImageDataCenterSquare.shape)

    #Get the peak of the most visible transient object in the center square
    FindBrightestTransientResult = Library_FitsSubtractionImageFindBrightestTransient.Main(
        ImageData= ImageDataCenterSquare,
        PrintExtra = True,
        )
    TruePeak = FindBrightestTransientResult['TruePeak']
    print ("TruePeak", TruePeak)
    XhubbleBestSquare, YhubbleBestSquare = TruePeak


    #Transform the coodinates back to the full image:
    XhubbleBest = XhubbleBestSquare + 200
    YhubbleBest = YhubbleBestSquare + 200
    print ('XhubbleBest, YhubbleBest', XhubbleBest, YhubbleBest)

    #Transform back to RA and DEC
    RaHubbleBest, DecHubbleBest = hstphot.util.xy2radec(SingleSubMaskedFilePath, XhubbleBest , YhubbleBest )


    #Make some plots about how we found the coordinates and save them:
    SingleSubMaskedFileName = Library_StringFilePathGetFileName.Main(  SingleSubMaskedFilePath   )
    SavePlotFitPathPrefix = SaveFolderPath + '/' + SingleSubMaskedFileName
    if DoPlotOriginalImage:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.imshow(astropy.io.fits.getdata(SingleSubMaskedFilePath, ext=0), cmap='gray', origin='lower')
        matplotlib.pyplot.colorbar( label = 'diff brightness ')
        matplotlib.pyplot.title("ImageData \n imshow(ImageData) ")
        subplot = matplotlib.pyplot.gca()
        subplot.set_xlabel( 'x' )
        subplot.set_ylabel( 'y' )
        matplotlib.pyplot.savefig( SavePlotFitPathPrefix + '_ImageOriginal.png', bbox_inches='tight' )


    if DoPlotCenterSquareImage:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.imshow(ImageDataCenterSquare, cmap='gray', origin='lower')
        matplotlib.pyplot.colorbar( label = 'diff brightness (re-normed)')
        matplotlib.pyplot.title("ImageData \n imshow(ImageData) ")
        subplot = matplotlib.pyplot.gca()
        subplot.set_xlabel( 'x' )
        subplot.set_ylabel( 'y' )
        #matplotlib.pyplot.draw()
        Library_GraphScatterCrossHair.Main(
            NumpyTwoDimensionalDatasets= [ XYcatalogSquareNumpyDataset, numpy.atleast_2d(TruePeak) ],
            DatasetLabels= ['Catalog SN Location', 'Hubble SN Location'],
            DatasetColors= [Config_NumpyMatplotlibColors.ColorRed,Config_NumpyMatplotlibColors.ColorGreen ],
            LegendSize = 10,
            )
        matplotlib.pyplot.savefig( SavePlotFitPathPrefix + '_ImageCenterSquareWithCrossHair.png', bbox_inches='tight' )


    if DoPlotFull:
        FitFunctionFull  = FindBrightestTransientResult['FitsSubtractionFitObject']['FitFunctionFull']
        FigureDensityFull = Library_GraphTwoDimensionDensityColorMap.Main(  
            Function = FitFunctionFull,        
            DomainMinimumPoint = [0,0],                
            DomainMaximumPoint = [len(ImageDataCenterSquare[0]), len(ImageDataCenterSquare)],
            Xlabel = 'X',  Ylabel = 'Y', Zlabel = 'Z' ,
            PlotThreeDimensional = False,
            Parallelize  = True,
            PlotTitle = 'GMM pomegranate fit (full)',
            ) 
        Library_GraphScatterCrossHair.Main(
            NumpyTwoDimensionalDatasets= [ XYcatalogSquareNumpyDataset, numpy.atleast_2d(TruePeak) ],
            DatasetLabels= ['Catalog SN Location', 'Hubble SN Location'],
            DatasetColors= [Config_NumpyMatplotlibColors.ColorRed,Config_NumpyMatplotlibColors.ColorGreen ],
            LegendSize = 10,
            )
        matplotlib.pyplot.savefig( SavePlotFitPathPrefix + '_ImageCenterSquareGMMfit.png', bbox_inches='tight' )


    if ShowPlots:
        matplotlib.pyplot.show()

    #Now close all the open figures:
    for i in matplotlib.pyplot.get_fignums():
        matplotlib.pyplot.figure(i)
        matplotlib.pyplot.close()
    matplotlib.pyplot.close('all')


    Result = {
        'FindBrightestTransientResult': FindBrightestTransientResult,
        'Xcatalog': Xcatalog,
        'Ycatalog' : Ycatalog,
        'XhubbleBest':XhubbleBest,
        'YhubbleBest':YhubbleBest,
        'RaHubbleBest':float(RaHubbleBest),
        'DecHubbleBest':float(DecHubbleBest),
        }

    return Result 




















