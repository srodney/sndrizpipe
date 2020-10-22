"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Take a fits file / image data which is already a subtraction image
    of two other images.
    Search the surface of the image for the x,y pixel 
    which is the center of a transient object.
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
import numpy
import Library_FitsSubtractionImageGaussianMixtureModel
import Library_MinimizeScalarFunction
#-------------------------------------------------------------------------------
def Main(
    ImageData= None,
    ResultFormat= None,
    Method= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if ResultFormat is None:
        ResultFormat = 'Dictionary'

    if Method is None:
        Method = 'GaussianMixtureModel' 
        #TODO: generalize the result dictionary so new methods can be added

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #-------------------------------------------------------------------------------
    #GMM FITTING:
    #Fit the image to a gaussian mixture mode:
    GMMFitsFitObject = Library_FitsSubtractionImageGaussianMixtureModel.Main(
        ImageData= ImageData,
        ResultFormat = 'Dictionary',
        Method= None,
        DoWeightsScatterPlot = False,
        HideProgressBar = True,
        )
    FitFunctionFull = GMMFitsFitObject['FitFunctionFull']
    FitFunctionUpper = GMMFitsFitObject['FitFunctionUpper']
    FitFunctionLower = GMMFitsFitObject['FitFunctionLower']

    GMMObjectUpperMeans = GMMFitsFitObject['GaussianMixtureModelObjectUpper']['Means']
    print ('GMMObjectUpperMeans', GMMObjectUpperMeans)

    GMMObjectLowerMeans = GMMFitsFitObject['GaussianMixtureModelObjectLower']['Means']
    print ('GMMObjectLowerMeans', GMMObjectLowerMeans)

    TrainTimeTaken = GMMFitsFitObject['TrainTimeTaken']
    print ('TrainTimeTaken (2 GGMs on fits)', TrainTimeTaken)

    ExampleProbability = FitFunctionFull( numpy.array([ 0,0 ]) )
    print ('ExampleProbability', ExampleProbability)

    GMMObjectAllMeans = numpy.concatenate([GMMObjectUpperMeans, GMMObjectLowerMeans], axis=0)

    #-------------------------------------------------------------------------------
    #TRANSLATION FITTING:
    #Translate the lower gmm and sum[ abs( upperpeaks - lowerpeaks) ]@( all upper peak loc)

    def DiffPlain( v1, v2 ):
        return numpy.abs(v1 - v2)

    def DiffLogs( v1, v2 ):
        return numpy.abs(numpy.log(v1) - numpy.log(v2))

    def DiffSquared(v1, v2):
        return (v1 - v2)**2

    def DiffLogsSquared(v1, v2):
        return (numpy.log(v1) - numpy.log(v2))**2

    def DiffEntropy(v1, v2):
        Diff = numpy.abs(v1 - v2)
        return Diff * numpy.log(Diff)

    def DiffLogPlain(v1, v2):
        return numpy.log( numpy.abs(v1 - v2) )


    #Pick a diff function:
    DiffFunction = DiffLogsSquared


    #Build the goodness of fit function using the picked diff function:
    def TranslationGoodness( Point ):
        Translation = Point
        SumDiffs = 0.0
        for Mean in GMMObjectAllMeans:
            v1 = FitFunctionUpper( Mean  ) 
            v2 = FitFunctionLower( Mean - Translation ) 
            Diff = DiffFunction(v1, v2)
            SumDiffs += Diff
        return SumDiffs



    #Find the best translation (minimize twice with 2 different methods)
    MinimizerResult = Library_MinimizeScalarFunction.Main(
        Method = 'LazyGuess',
        ScalarFunctionPython= TranslationGoodness,
        StartDataPoint= [0.0, 0.0],
        DomainMinimumPoint = [-20, -20],
        DomainMaximumPoint = [20, 20],
        #HideProgressBar = False,
        )
    BestTranslation = MinimizerResult['DataPoint']

    MinimizerResult = Library_MinimizeScalarFunction.Main(
        Method = 'Scipy',
        ScalarFunctionPython= TranslationGoodness,
        StartDataPoint= BestTranslation,
        #HideProgressBar = False,
        )
    BestTranslation = MinimizerResult['DataPoint']
    print ('BestTranslation', BestTranslation)
    def FitFunctionFullBestLowerTranslation(Point):
        return FitFunctionUpper(Point) - FitFunctionLower( Point - BestTranslation )

    #-------------------------------------------------------------------------------
    #PEAK FINDING:
    #Find the best peak in the translated result:
    MaxValue = 0.0
    TruePeak = [0,0]
    for UpperMean in GMMObjectUpperMeans:
        UpperMeanValue = FitFunctionFullBestLowerTranslation(UpperMean)
        if UpperMeanValue > MaxValue:
            MaxValue = UpperMeanValue
            TruePeak = UpperMean
    print ('TruePeak', TruePeak)


    #Cast the result to integers
    TruePeak_x = int(TruePeak[0])
    TruePeak_y = int(TruePeak[1])
    TruePeak = [TruePeak_x, TruePeak_y]


    if ResultFormat == 'Dictionary':
        Result = {
            'BestTranslation': BestTranslation,
            'FitFunctionFullBestLowerTranslation' : FitFunctionFullBestLowerTranslation,
            'TruePeak': TruePeak,
            'FitsSubtractionFitObject' : GMMFitsFitObject, 
            'TranslationGoodness' : TranslationGoodness,
            }



    return Result 
