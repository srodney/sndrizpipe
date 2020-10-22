"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Takes the information for a single supernova 
    (the information is from a catalog)
    1) Gets all the hubble data for the single supernova in the wavelengths of interest (band filter)
    2) Mounts the new images from the astroquery mast into \"symlink\" directories
    3) Drizzles the raw hubble images into difference images
    4) Registers a true location for the supernova in the hubble database using a GMM
    5) Makes photometry plots for each difference image using the true location
    6) Turns the photometry information into a light curve
    7) Gets existing lightcurve data from the open supernova catalog for the ID of interest
    8) Puts the new light curve points on a plot with the existing visible light curve points
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
    SuperNovaId
        Type:
            <class 'NoneType'>
        Description:
            None
    SuperNovaRa
        Type:
            <class 'NoneType'>
        Description:
            None
    SuperNovaDec
        Type:
            <class 'NoneType'>
        Description:
            None
    SuperNovaMjd
        Type:
            <class 'NoneType'>
        Description:
            None
    SuperNovaMjdRange
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import os
import glob
import pathlib
import astroquery
import astroquery.mast 
import sndrizpipe
import sndrizpipe.runpipe_cmdline
import pprint
import numpy
import matplotlib
#-------------------------------------------------------------------------------

import Library_FileCopy
import Library_SystemDirectoryCreateSafe
import Library_SystemGetLocalDataDirectory
import Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject
import Library_DateStringNowGMT
import Library_NestedObjectFileRead
import Library_NestedObjectFileWrite
import Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles
import Library_StringFileNameStripLastExtension
import Library_StringFilePathGetFileName
import Library_FitsSubtractionImageHubbleSuperNovaCenterFinder
import Library_HstPhotWrapper
import Library_GeometryEuclidianDistance
import Library_HstPhotometryToLightCurve
#-------------------------------------------------------------------------------
def Main(
    SingleSuperNovaCatalogName = None,
    SingleSuperNovaId= None,
    SingleSuperNovaRa= None,
    SingleSuperNovaDec= None,
    SingleSuperNovaMjd= None,
    SingleSuperNovaMjdRange= None,

    #Optional query arguements
    SingleSuperNovaAllowedFilters = None,
    SingleSuperNovaAllowedInstruments = None,
    SingleSuperNovaAllowedCollections = None,

    #Optional what to do/skip arguements:
    DoAstroquerySearch = None,
    DoAstroqueryDownload = None,
    DoSymlinkMount = None,
    DoDrizzleDiffs = None,
    DoDrizzleDiffFileCopy = None,
    DoCenterFind = None,
    DoPhotometry = None,
    DoLightCurve = None,

    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None


    if DoAstroquerySearch is None:
        DoAstroquerySearch = True
    if DoAstroqueryDownload is None:
        DoAstroqueryDownload = True
    if DoSymlinkMount is None:
        DoSymlinkMount = True
    if DoDrizzleDiffs is None:
        DoDrizzleDiffs = True
    if DoDrizzleDiffFileCopy is None:
        DoDrizzleDiffFileCopy = True
    if DoCenterFind is None:
        DoCenterFind = True
    if DoPhotometry is None:
        DoPhotometry = True


    #Set default filters
    if SingleSuperNovaAllowedInstruments is None:
        SingleSuperNovaAllowedInstruments=[
            'WFPC2/WFC',
            'PC/WFC',
            'ACS/WFC',
            'ACS/HRC',
            'ACS/SBC',
            'WFC3/UVIS',
            'WFC3/IR'
            ]
    if SingleSuperNovaAllowedFilters is None:
        SingleSuperNovaAllowedFilters=[
            'F606W',
            'F625W',
            'F775W',
            'F814W',
            'F850LP',
            'F105W',
            'F110W',
            'F125W',
            'F140W',
            'F160W',
            ]
    if SingleSuperNovaAllowedCollections is None:
        SingleSuperNovaAllowedCollections = [
            'HLA',
            'HST'
            ]


    if (CheckArguments):
        ArgumentErrorMessage = ""
        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #Do some directory management before we perform all the operations of interest:
    CurrentDirectory = os.getcwd()
    DataDirectory = Library_SystemGetLocalDataDirectory.Main()
    SuperNovaCatalogsDataDirectory  = DataDirectory + '/AstronomySuperNovaData/SuperNovaCatalogs/'
    SuperNovaImageDownloadDirectory = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleImages/'
    SuperNovaMetaDataDirectory      = DataDirectory + '/AstronomySuperNovaData/SuperNovaHubbleMetaData/'
    SuperNovaSubMaskedFolderPath    = DataDirectory + '/AstronomySuperNovaData/SuperNovaMaskedSubView/'
    SuperNovaTransientFindingFolderPath = DataDirectory + '/AstronomySuperNovaData/SuperNovaTransientFinder'
    SuperNovaPhotometryFolderPath   = DataDirectory + '/AstronomySuperNovaData/SuperNovaPhotometry/'
    SuperNovaLightCurveFolderPath   = DataDirectory + '/AstronomySuperNovaData/SuperNovaLightCurves'



    #Query the archive for what files exist given the constraints :
    #   Same stuff as in "Example_DataFindHubbleSuperNova"
    if DoAstroquerySearch:
        ProductListResult = Library_DataFindBarbaraMikulskiArchiveProductsHubbleSingleObject.Main(
            ObjectId                = SingleSuperNovaId,
            ObjectRightAscension    = SingleSuperNovaRa,
            ObjectDeclination       = SingleSuperNovaDec,
            QueryRadius             = None, #defaults to 0.03
            ObjectMjd               = SingleSuperNovaMjd,
            QueryDateRange          = SingleSuperNovaMjdRange,
            QuerySubsetColumnNames  = [
                'instrument_name',
                'filters',
                'obs_collection',
                ],
            QuerySubsetColumnsValuesOfInterest = [
                SingleSuperNovaAllowedInstruments, 
                SingleSuperNovaAllowedFilters,
                SingleSuperNovaAllowedCollections,
                ],
            ProductSubsetColumnNames = [
                'productType',
                'productSubGroupDescription',
                'extension',
                ],
            ProductSubsetColumnsValuesOfInterest = [
                ["SCIENCE"],
                ["FLT"],
                ["fits"],
                ],
            ObjectSourceCatalog     = SingleSuperNovaCatalogName,
            ResultFormat            = 'Dictionary',
            )
        SingleObjectMetaData = ProductListResult['SingleObjectMetaData']
        SingleObjectProductListTable = ProductListResult['SingleObjectProductListTable']

        #Count the number of products we have to download
        SingleSuperNovaProductCount = int(SingleObjectMetaData['productcount']) 
        print ('SingleSuperNovaProductCount', SingleSuperNovaProductCount)


        #Create a download directory for the supernova

        SingleSuperNovaDownloadDirectory = SuperNovaImageDownloadDirectory 
        SingleSuperNovaDownloadDirectory +=  '/' + str(SingleSuperNovaId)
        if SingleSuperNovaProductCount > 0:
            Library_SystemDirectoryCreateSafe.Main( Directory = SingleSuperNovaDownloadDirectory )


        #Perform the download and get hubble images onto disk
        if DoAstroqueryDownload and SingleSuperNovaProductCount > 0:
            print ('Starting Download...')
            astroquery.mast.Observations.download_products(
                SingleObjectProductListTable,
                download_dir = SingleSuperNovaDownloadDirectory,
                cache = True,
                )

        #Store the meta-data for the single object 
        #   (do this regardless of download success/failure)
        #   update the previous file for the catalog
        #   its OK to make an entirely new copy of the file
        SingleCatalogAllMetaDataFilePaths = list( sorted( list(glob.iglob(SuperNovaMetaDataDirectory + '/**/*' + SingleSuperNovaCatalogName + '.txt', recursive=True)) ) )
        OldSingleCatalogMetaDataStorageFilePath = SingleCatalogAllMetaDataFilePaths[-1]
        SingleCatalogMetaData = Library_NestedObjectFileRead.Main(
            FilePath =  OldSingleCatalogMetaDataStorageFilePath
            )
        SingleCatalogMetaDataItemCount = len(SingleCatalogMetaData)
        print ( 'SingleCatalogMetaDataItemCount', SingleCatalogMetaDataItemCount)


        #Find the location of any existing meta data in the file:
        SingleCatalogSingleSuperNovaIndex = 0
        for Item in SingleCatalogMetaData:
            if Item['ID'] == SingleSuperNovaId:
                break
            SingleCatalogSingleSuperNovaIndex += 1
        print ( 'SingleCatalogSingleSuperNovaIndex', SingleCatalogSingleSuperNovaIndex)


        #Update the existing object with the new metadata:
        if SingleCatalogSingleSuperNovaIndex < SingleCatalogMetaDataItemCount:
            SingleCatalogMetaData[SingleCatalogSingleSuperNovaIndex] = SingleObjectMetaData
        else:
            SingleCatalogMetaData.append( SingleObjectMetaData )


        #Store the updated information into the meta-data file system:
        NewSingleCatalogMetaDataStorageFilePath =  SuperNovaMetaDataDirectory 
        NewSingleCatalogMetaDataStorageFilePath += '/' +  Library_DateStringNowGMT.Main() 
        NewSingleCatalogMetaDataStorageFilePath += '_MetaData_' + SingleSuperNovaCatalogName + '.txt'
        Library_NestedObjectFileWrite.Main(
            NestedObject    = SingleCatalogMetaData,
            FilePath        = NewSingleCatalogMetaDataStorageFilePath,
            )


    
    #Mount the astroquery files we have stored into a symlink directory:
    #   (same code as in "Example_SymlinkMountHubbleSuperNova")
    SingleSuperNovaHubbleDataFolderName = str(SingleSuperNovaId)
    ProductListDirectory = os.path.realpath( SuperNovaImageDownloadDirectory + '/' +  SingleSuperNovaHubbleDataFolderName + '/mastDownload' )
    SingleSuperNovaSymlinkDirectory = None
    if DoSymlinkMount:
        SingleSuperNovaSymlinkDirectory = Library_BarbaraMikulskiArchiveSymlinkGroupMastDownloadDirectoryFiles.Main(
            ProductListDownloadDirectory= ProductListDirectory
            )
    else:
        SingleSuperNovaSymlinkDirectory = os.path.realpath( SuperNovaImageDownloadDirectory + '/' +  SingleSuperNovaHubbleDataFolderName + '/mastDownloadFilesSymlinks.flt' )
    print ('SingleSuperNovaSymlinkDirectory:', SingleSuperNovaSymlinkDirectory)    




    #Make the drizzle difference images ("")
    if DoDrizzleDiffs:
        RunPipeArgumentDirectory = Library_StringFileNameStripLastExtension.Main( SingleSuperNovaSymlinkDirectory )

        #Change to the directory one level up from the symlink directory, so exposure.py works:
        path = pathlib.Path(SingleSuperNovaSymlinkDirectory)
        parent = path.parent
        os.chdir( parent )

        #Run the actual pipe command:
        os.environ["iref"] = ""
        os.environ["jref"] = ""
        os.environ["sig"] = ""
        try:
            sndrizpipe.runpipe_cmdline.runpipe(
                RunPipeArgumentDirectory, 
                ra = SingleSuperNovaRa,
                dec = SingleSuperNovaDec, 
                mjdmin = SingleSuperNovaMjdRange[0],
                mjdmax = SingleSuperNovaMjdRange[1],
                epochspan = 5,
                pixscale = 0.06,
                pixfrac = 0.8,
                doall=True, 
                tempepoch=1)
        except Exception as ExceptionObject:
            print (ExceptionObject)
            pass

        #Change back to the original directory after the pipe call is done
        os.chdir( CurrentDirectory )



    #Get the list of diff images with a glob and copy them over to the separate directory 
    if DoDrizzleDiffFileCopy:
        SingleSuperNovaDrizzleImagesDirectory = os.path.realpath(SuperNovaImageDownloadDirectory + '/'  + SingleSuperNovaId)
        #print ('SingleSuperNovaDrizzleImagesDirectory', SingleSuperNovaDrizzleImagesDirectory)
        DrizzleDiffImagePaths =  list(glob.iglob( SingleSuperNovaDrizzleImagesDirectory + '/**/*' + 'sub_masked.fits', recursive=True)) 
        #print ('DrizzleDiffImagePaths', DrizzleDiffImagePaths)
        for SourceFilePath in DrizzleDiffImagePaths:
            SourceFileName = Library_StringFilePathGetFileName.Main(  SourceFilePath   )
            TargetFolderPath = SuperNovaSubMaskedFolderPath + '/' + SingleSuperNovaId
            Library_FileCopy.Main(
                SourceFilePath= SourceFilePath,
                TargetFolderPath= TargetFolderPath,
                Overwrite= True,
                )



    #Model the diff images with gaussian mixture models
    #   We can use them to determine optimal translation to minize the difference image peak brightness (for redoing tweakreg)
    #   We can also use them to recenter the photometry calculations
    SaveCentersPath = SuperNovaTransientFindingFolderPath + '/' + SingleSuperNovaId + '/' + 'NewCenters.json'

    NewCenters = []
    if DoCenterFind:
        SingleSuperNovaDrizzleDiffFilePaths = list(glob.iglob(SuperNovaSubMaskedFolderPath + '/' + SingleSuperNovaId + '/**/*sub_masked.fits', recursive=True))
        for SingleSuperNovaDrizzleDiffFilePath in SingleSuperNovaDrizzleDiffFilePaths:
            CenterFinderResult = Library_FitsSubtractionImageHubbleSuperNovaCenterFinder.Main(
                SubtractionImageFilePath= SingleSuperNovaDrizzleDiffFilePath,
                SuperNovaId= SingleSuperNovaId,
                RaCatalog= SingleSuperNovaRa,
                DecCatalog= SingleSuperNovaDec,
                )
            RaHubbleBest    = CenterFinderResult['RaHubbleBest']
            DecHubbleBest   = CenterFinderResult['DecHubbleBest']


            #Extract other information out of the file path:
            SingleSuperNovaDrizzleDiffFileName = Library_StringFilePathGetFileName.Main(  SingleSuperNovaDrizzleDiffFilePath   )
            SingleSuperNovaDrizzleDiffFileNameSplit = SingleSuperNovaDrizzleDiffFileName.split('_')
            SingleSuperNovaDrizzleDiffBand = SingleSuperNovaDrizzleDiffFileNameSplit[1]
            SingleSuperNovaDrizzleDiffEpochs = SingleSuperNovaDrizzleDiffFileNameSplit[2]

            NewCenters.append( {
                'ID' : SingleSuperNovaId,
                'Band' : SingleSuperNovaDrizzleDiffBand,
                'Epochs' : SingleSuperNovaDrizzleDiffEpochs,
                'RaHubbleBest': RaHubbleBest, 
                'DecHubbleBest' : DecHubbleBest,
                } )
        #Save the new centers to file:
        Library_NestedObjectFileWrite.Main(
            NestedObject= NewCenters,
            FilePath= SaveCentersPath,
            )
    else:
        NewCenters = Library_NestedObjectFileRead.Main( SaveCentersPath )


    #Find best new center from all difference images:
    print(NewCenters)
    pprint.pprint(NewCenters)
    CenterDistances = []
    for Center in NewCenters:
        CenterDistance = Library_GeometryEuclidianDistance.Main(
            Point1 = [ SingleSuperNovaRa, SingleSuperNovaDec ],
            Point2 = [Center['RaHubbleBest'], Center['DecHubbleBest'] ]
            )
        CenterDistances.append(CenterDistance)
    BestCenterIndex  = numpy.argmin(numpy.array(CenterDistances))
    BestCenterObject = NewCenters[BestCenterIndex]
    RaHubbleBest     = BestCenterObject['RaHubbleBest']
    DecHubbleBest    = BestCenterObject['DecHubbleBest']
    print ('RaHubbleBest, DecHubbleBest', RaHubbleBest, DecHubbleBest)


    #Do all the photometry:
    if DoPhotometry:
        SingleSuperNovaDrizzleDiffFilePaths = list(glob.iglob(SuperNovaSubMaskedFolderPath + '/' + SingleSuperNovaId + '/**/*sub_masked.fits', recursive=True))
        for SingleSuperNovaDrizzleDiffFilePath in SingleSuperNovaDrizzleDiffFilePaths:

            #Extract other information out of the file path:
            SingleSuperNovaDrizzleDiffFileName = Library_StringFilePathGetFileName.Main(  SingleSuperNovaDrizzleDiffFilePath   )
            SingleSuperNovaDrizzleDiffFileNameSplit = SingleSuperNovaDrizzleDiffFileName.split('_')
            SingleSuperNovaDrizzleDiffBand = SingleSuperNovaDrizzleDiffFileNameSplit[1]
            SingleSuperNovaDrizzleDiffEpochs = SingleSuperNovaDrizzleDiffFileNameSplit[2]

            #Do the photometry, and save the result to a file:
            PhotResult = Library_HstPhotWrapper.Main(
                SubMaskedFilePath = SingleSuperNovaDrizzleDiffFilePath,
                Coodinates = [RaHubbleBest, DecHubbleBest],
                CoodinatesType= 'radec',
                SaveFolderPath = SuperNovaPhotometryFolderPath + '/' + str(SingleSuperNovaId),
                ObjectId = SingleSuperNovaId,
                MakeFigure = True,
                ShowFigure = False,
                OverWrite = True,
                )
            matplotlib.pyplot.close('all')
   

    #Do the light curve:
    if DoLightCurve:
        SuperNovaIdPhotometryFolderPath = SuperNovaPhotometryFolderPath + '/' + SingleSuperNovaId
        LightCurveResult = Library_HstPhotometryToLightCurve.Main(
            SuperNovaId = SingleSuperNovaId,
            SuperNovaIdPhotometryFolderPath= SuperNovaIdPhotometryFolderPath,
            SuperNovaIdLightCurveFolderPath= SuperNovaLightCurveFolderPath ,
            )


    #TODO: Get light curve data from open supernova catalog 


    #TODO: Make a merged light curve plot with both existing visible and NEW IR data:


    return Result 

















