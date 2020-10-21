"""
SOURCE:
    Mind of Douglas Adams
DESCRIPTION:
    Find the global minimum of an arbitrary scalar function

    #   (default scipy will likely be good enough minimazation algorithm
    #   for nice shaped density functions)

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
    ScalarFunctionPython
        Type:
            <type 'NoneType'>
        Description:
            Some python function which is a scalar function
            (has points, and point as args) ---> like a density function which is allowed to go negative and not integrate to 1
    StartDataPoint
        Type:
            <type 'NoneType'>
        Description:
            An initial guess for where to start MC algorithms. 
    DimensionCountDataPoint
        Type:
            <type 'NoneType'>
        Description:
            The number of axes on the coordinate system
    Constraints
        Type:
            <type 'NoneType'>
        Description:
            Any areas of point space which are off limits
    Technique
        Type:
            <type 'NoneType'>
        Description:
            Which algorithm should we be using to perform the optimization?

    ReturnFormat
        Type:
            <type 'NoneType'>
        Description:
            Do we want to see a dictionary returned, or just the value, or just he datapoint:?
RETURNS:
    Result
        Type:
        Description:
"""

import time
import numpy
import scipy
import scipy.optimize
import tqdm
#TODO: Type_PythonScalarFunction

#-------------------------------------------------------------------------------
def Main(
    ScalarFunctionPython= None,
    StartDataPoint= None,
    DimensionCountDataPoint= None,

    DomainMinimumPoint = None,
    DomainMaximumPoint = None,

    BatchSize = None,
    MaximumTrialCount = None,

    Constraints= None, #not sure if we should go with this argument 
    Technique = None,
    Method = None,
    ReturnFormat= None,

    HideProgressBar = None,

    CheckArguments = True,
    PrintExtra = False,
    PrintCurrentBatch = False,
    ):

    Result = None


    #SET SOME DEFAULT ARGS:
    if ReturnFormat is None:
        ReturnFormat = 'Dictionary'

    if BatchSize is None:
        BatchSize = 10

    if MaximumTrialCount is None:
        MaximumTrialCount=  1000

    if HideProgressBar is None:
        HideProgressBar = True

    #Technique and method are different names for the same arg
    if Technique is None and Method is not None:
        Technique = Method
    elif Method is None and Technique is not None:
        Method = Technique
    elif Method is None and Technique is None:
        Method = 'LazyGuess'


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (DimensionCountDataPoint is None and StartDataPoint is None):
            ArgumentErrorMessage += "`DimensionCountDataPoint` and `StartDataPoint` both None)"

        if Method is not None and Technique is not None and Method != Technique:
            ArgumentErrorMessage += '`Library_MinimizeScalarFunction` canot have both a technique and a method with different values\n'
            ArgumentErrorMessage += 'Technique == '+str(Technique)+'\n'
            ArgumentErrorMessage += 'Method == '+str(Method)+'\n'

        if Method is 'LazyGuess' and (DomainMinimumPoint is None or DomainMaximumPoint is None) :
            ArgumentErrorMessage += 'LazyGuess method needs a domain box\n'
            ArgumentErrorMessage += 'DomainMinimumPoint == '+str(DomainMinimumPoint)+'\n'
            ArgumentErrorMessage += 'DomainMaximumPoint == '+str(DomainMaximumPoint)+'\n'


        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    if not HideProgressBar: print ('Starting Minimization...')
    StartTime = time.time()

    if PrintExtra: print('Method', Method)


    if Method is 'LazyGuess': #OMG this works so well for how stupid it is
        DimensionCount = len(DomainMinimumPoint) #How many dimensions in the coordinates?

        BestDomainPoint = None
        BestRangeValue = None
        AttemptedDomainPoints = []
        AttemptedRangeValues = []

        for Trial in tqdm.tqdm(range(MaximumTrialCount), disable=HideProgressBar ):
            if PrintCurrentBatch or PrintExtra:
                if Trial % BatchSize == 0:
                    print('Current Trial Batch', Trial, '-', Trial + BatchSize)

            #Throw the domain dart:
            AttemptedDomainPoint = []
            for Dimension in range(DimensionCount):
                DimensionDomainMinimum = DomainMinimumPoint[Dimension]
                DimensionDomainMaximum = DomainMaximumPoint[Dimension]
                AttemptedDomainPoint.append( numpy.random.uniform(
                    low = DimensionDomainMinimum, 
                    high = DimensionDomainMaximum) )

            Value = ScalarFunctionPython( Point = numpy.array(AttemptedDomainPoint) ) #Point = AttemptedDomainPoint )
            AttemptedDomainPoints.append(AttemptedDomainPoint)
            AttemptedRangeValues.append(Value)
            if BestRangeValue is None or Value < BestRangeValue:
                BestRangeValue = Value
                BestDomainPoint = AttemptedDomainPoint

        if PrintExtra:
            print('BestRangeValue', BestRangeValue)
            print('BestDomainPoint', BestDomainPoint)

    elif Method is 'Scipy':
        #Create a version of the function which is scipy ready
        #   Note while it is tempting to just pass the given function
        #   Into the minimizer of scipy --->
        #       That could cause problems, because our scalar function tyope check
        #       May not have the arg `Point` as the FIRST arg
        #       The function sent to scipy needs to be callable WITHOUT NAME
        #       i.e:L
        #           def f(Points= None, Point= None): ...
        #           scipy.min( f )   ---> fail
        #
        #           g(Point)
        #           scipy.min( g )   ---> win
        global EvalCount 
        EvalCount = 0
        def ScipyReadyPythonFunction( Point ): #<---- DONT ERASE (read note)
            Value = ScalarFunctionPython(Point = Point)

            if not HideProgressBar: 
                global EvalCount
                EvalCount += 1
                if EvalCount % 10 == 0: 
                    print ('Iter:', EvalCount, ' | f(',Point,')=', float(Value))
            return Value

        
        #Perform the minimization: #TODO:  add other techniques
        options = {
            "xtol" : 0.01,
            "ftol" : 0.001,
            "maxfev": 1000,
            "disp": PrintExtra or (not HideProgressBar),
            }

        MinimumResultObject = scipy.optimize.minimize(
            ScipyReadyPythonFunction, 
            StartDataPoint,
            #method = 'SLSQP',
            #method = 'BFGS',
            method = 'Nelder-Mead', #Seems to work well for my dark matter paper
            #method = 'Powell',	        
            #constraints = Constraints,
            #bounds = [(None, None),(-3, None)]
            #options = options,
            #callback = CallbackShowProgress,
            )
        if (PrintExtra):
            print('MinimumResultObject', MinimumResultObject)
            

        BestRangeValue = MinimumResultObject.fun
        BestDomainPoint = MinimumResultObject.x


    #Report progress to the terminal:
    EndTime = time.time()
    TimeTaken = EndTime - StartTime
    if not HideProgressBar:    print ('Minimization TimeTaken:', TimeTaken)


    if ReturnFormat is 'Parameters':
        return MinimumParameters

    elif ReturnFormat is 'Value':
        return MinimumValue

    elif ReturnFormat is 'Dictionary':
        ResultDictionary = {}
        ResultDictionary['DataPoint'] = BestDomainPoint
        ResultDictionary['MinimumValue'] = BestRangeValue
        #ResultDictionary['NumberIterationsRequired'] = MinimumResultObject.nit
        #ResultDictionary['Success'] = MinimumResultObject.success
        return ResultDictionary
    else:
        raise Exception('unrecognized return format')


    return Result 
