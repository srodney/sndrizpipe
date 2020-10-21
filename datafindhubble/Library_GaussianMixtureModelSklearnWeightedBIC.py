"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    does the sklearn BIC with WEIGHTS on the dataset
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
    GaussianMixtureObjectSklearn
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
#-------------------------------------------------------------------------------
def Main(
    ScoreSamplesFunction= None,
    NumpyTwoDimensionalDataset = None, 
    NumParameters = None, 
    Weights = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    #https://github.com/scikit-learn/scikit-learn/blob/fd237278e895b42abe8d8d09105cbb82dc2cbba7/sklearn/mixture/_base.py#L323
    #https://stackoverflow.com/questions/38241174/weighted-average-using-numpy-average

    NumPoints = NumpyTwoDimensionalDataset.shape[0]


    if Weights is None:
        Weights = numpy.ones(NumPoints)
    

    ScorePerPoint = ScoreSamplesFunction( NumpyTwoDimensionalDataset )
    ScoreMeanWeighted = numpy.average(ScorePerPoint, weights=Weights)

    Term1Full = -2 *NumPoints * ScoreMeanWeighted
    Term2Full = NumParameters * numpy.log(NumPoints)

    Result = Term1Full + Term2Full


    return Result 















