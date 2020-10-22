"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Perform a gaussian mixture model fit to an image.
    This is different than performing one on a dataset because
    There are values at every point.
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
    ImageData
        Type:
            <class 'NoneType'>
        Description:
            None
    ImageFilePath
        Type:
            <class 'NoneType'>
        Description:
            None
    ResultFormat
        Type:
            <class 'NoneType'>
        Description:
            None
    Method
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import time
import copy
import numpy
import astropy
import astropy.io
import astropy.io.fits
import astropy.utils
import astropy.utils.data
import matplotlib.pyplot
import Library_GaussianMixtureModel
import Library_OuterProduct
import Library_IndexListToNumpySliceObject
import Library_NumpyArrayNormalize
import Library_GraphScatterPlot
import Config_NumpyMatplotlibColors
#-------------------------------------------------------------------------------
def Main(
    ImageData= None,
    ImageFilePath= None,
    ResultFormat= None,
    Method= None,
    DoWeightsScatterPlot = None,

    HideProgressBar = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if ResultFormat is None:
        ResultFormat = 'Dictionary'

    if HideProgressBar is None:
        HideProgressBar = False

    if ImageData is None and ImageFilePath is not None:
        ImageData = astropy.io.fits.getdata(ImageFilePath, ext=0)

    if DoWeightsScatterPlot is None:
        DoWeightsScatterPlot = False

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #DoFlip: False, DoTranspose: True
    #Here the dataset is a numpy array with a coordinate for each pixel
    #   We interpret [0,0] as the lower left of image
    #ImageData = numpy.flip( ImageData, axis = 0 )  
    #   We inpterpret [x,y] as coordinates in the image data:
    ImageData = ImageData.T


    #Create a list of possible indices for the image data:
    xup, yup = ImageData.shape
    xpossible = range(xup)
    ypossible = range(yup)
    ImagePixelIndexes = Library_OuterProduct.Main(
        ListOfLists= [xpossible, ypossible]
        )
    Dataset = numpy.array(ImagePixelIndexes)

    if PrintExtra:
        print ('xup, yup', xup, yup)
        print ('Dataset.shape', Dataset.shape)



    #Find raw weights and some weights stats
    Weights = ImageData[  Library_IndexListToNumpySliceObject.Main( ImagePixelIndexes  )   ]
    WeightMean = numpy.mean(Weights)
    WeightStd = numpy.std(Weights)


    #Find numpy slice indexes which sasisfy a cut:
    #Subselct the dataset && weights to satisfy cut
    #   UPPER:
    WeightsUpperCut = WeightMean + WeightStd
    NumpySliceWeightsAboveCut = (Weights > WeightsUpperCut)
    DatasetUpper = Dataset[ NumpySliceWeightsAboveCut ]
    WeightsUpper = Weights[ NumpySliceWeightsAboveCut ]
    WeightsIndexesNumpyArrayUpper = numpy.hstack([DatasetUpper, numpy.atleast_2d(WeightsUpper).T  ])


    #   LOWER:
    WeightsLowerCut = WeightMean - WeightStd
    NumpySliceWeightsBelowCut = (Weights < WeightsLowerCut)
    DatasetLower = Dataset[ NumpySliceWeightsBelowCut ]
    WeightsLower = Weights[ NumpySliceWeightsBelowCut ]
    WeightsIndexesNumpyArrayLower = numpy.hstack([DatasetLower, numpy.atleast_2d(WeightsLower).T  ])


    if PrintExtra:
        print ('DatasetUpper.shape', DatasetUpper.shape)
        print ('WeightsUpper.shape', WeightsUpper.shape)
        print ('WeightsIndexesNumpyArrayUpper.shape', WeightsIndexesNumpyArrayUpper.shape)    
        #print (DatasetUpper[:10])
        #print (numpy.atleast_2d(WeightsUpper[:10]).T)
        #print (WeightsIndexesNumpyArrayUpper[:10])

    if DoWeightsScatterPlot:
        Library_GraphScatterPlot.Main(
            NumpyTwoDimensionalDatasets = [ WeightsIndexesNumpyArrayUpper,  WeightsIndexesNumpyArrayLower ],
            DatasetLabels = ['Weights Upper', 'Weights Lower'],
            MarkerColors = [Config_NumpyMatplotlibColors.ColorBlue, Config_NumpyMatplotlibColors.ColorRed],
            PlotTitle = 'Coordinates&Weights Left To Train GMM',
            )
        matplotlib.pyplot.draw()    
        #matplotlib.pyplot.show()    



    #Model the data with a gaussian mixture model (upper and lower)
    TrainStart = time.time()
    GaussianMixtureModelObjectUpper = Library_GaussianMixtureModel.Main( 
        NumpyTwoDimensionalDataset = DatasetUpper,
        ResultFormat = 'Dictionary',
        DataPointWeights = WeightsUpper, 
        Method = 'pomegranate', 
        HideProgressBar = HideProgressBar,
        )   

    GaussianMixtureModelObjectLower = Library_GaussianMixtureModel.Main( 
        NumpyTwoDimensionalDataset = DatasetLower,
        ResultFormat = 'Dictionary',
        DataPointWeights = numpy.abs(WeightsLower), 
        Method = 'pomegranate', 
        HideProgressBar = HideProgressBar,
        )   
    TrainStop = time.time()
    TrainTimeTaken = TrainStop - TrainStart
    if not HideProgressBar:    print ('TrainTimeTaken', TrainTimeTaken)

    FitFunctionUpper = GaussianMixtureModelObjectUpper['GaussianMixtureModelFunction']
    FitFunctionLower = GaussianMixtureModelObjectLower['GaussianMixtureModelFunction']

    #Craft a full fit function 
    def FitFunctionFull(Point):
        UpperValMag = FitFunctionUpper(Point)
        LowerValMag = FitFunctionLower(Point)
        return UpperValMag - LowerValMag


    #Craft the result into the right format:
    if ResultFormat == 'Function':
        Result = FullFitFunction
    elif ResultFormat == 'Dictionary':
        Result = {
            'GaussianMixtureModelObjectUpper' : GaussianMixtureModelObjectUpper,
            'GaussianMixtureModelObjectLower' : GaussianMixtureModelObjectLower,
            'FitFunctionFull' : FitFunctionFull,
            'FitFunctionUpper' : FitFunctionUpper,
            'FitFunctionLower' : FitFunctionLower,
            'TrainTimeTaken' : TrainTimeTaken, 
            }


    return Result 

















