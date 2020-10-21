
"""
SOURCE:

    pp
        http://www.parallelpython.com/

    **kwargs
        http://stackoverflow.com/questions/1769403/understanding-kwargs-in-python
        NOTE-> these are also used in the `Test_TestLooper`



DESCRIPTION:
    This is a library built to parallize a loop of code for which each iteration of the loop
    is independent of the other iterations of the loop


    for `ArgSet` in 'ListOfArgSets':
        ResultList.append( 'Function'(`ArgSet`) )


ARGS:
    Function
        -> this is the function to be run with each iteration of the loop
    
    ListOfArgSets
        -> this is a list of args, of which each element is a combination of args 
            to call the 'Function' one time
            Looks like:
                [
                ArgSet1,
                ArgSet2,
                .
                .
                ArgSetN,
                ]
            Each `ArgSet` is a dictionary which contains the argument:
                ArgSet1 might look like:
                    {
                    'Arg1' : 'HelloWorld'
                    'Arg2' : 2
                    }

                ArgSet2 might have slightly different arguments (Presumably)
                    {
                    'Arg1' : 'HelloWorld'
                    'Arg2' : 3
                    }

    Algorithm
        Descirption:
            The way in which the loop is parallelized
    
        Default:
            None
                -> if this is the case then the loop isn't parallel at all




RETURNS:
    ResultList:
        Description:
            List of results, each element matches each element of the `ListOfArgSets`:
        [
        ArgSet1Result,
        ArgSet2Result,
        .
        .
        ArgSetNResult,
        ]
       

"""
#import pp
#import mpi4py
import numpy
import time
import tqdm
import copy
import Const_Parallel
import pprint
import multiprocessing_on_dill #as multiprocessing
import itertools
#-------------------------------------------------------------------------------
import Library_CopyFunction
import Library_IsPrime
import Library_SumPrimesBelowInteger
import Library_IterableSplitIntoChunks
#-------------------------------------------------------------------------------
#TODO Memcached init before looping

def Main(
    Function = None,
    ListOfArgSets = None,
    Algorithm = None,
    Method = None,
    BatchSize = None,
    BatchCount = None,
    HideProgressBar = None,
    DefaultValue = None,
    CheckArguments = True,
    PrintExtra = True,
    ):

    StartTime = time.time()


    if BatchSize is None and BatchCount is None:
        BatchSize = 1
    #elif BatchSize is not None and BatchCount is None:
    #    pass
    #elif BatchSize is None and BatchCount is not None:
    #    pass
      
    #TODO: rename 'Algorithm' as 'Method'

    if HideProgressBar is None:
        HideProgressBar = False

    if DefaultValue is None:
        DefaultValue = None

    if Algorithm is None:
        Algorithm = 'loop'

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if BatchSize is not None and BatchCount is not None:
            ArgumentErrorMessage += ' BatchSize is not None and BatchCount is not None...\n'

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #Determine if the ArgSets are named, or not. 
    #   if not, we will assume the function is of a single variable
    ArgSetsNamed = isinstance( ListOfArgSets[0], dict )
    if PrintExtra: print ('ArgSetsNamed', ArgSetsNamed)

    #Build an object to collect the results
    ResultList = []

    #Make a function which uses the invoker, the functino, and handles errors gracefully
    def WrappedFunction( ArgSet ):
        WrappedResult = None
        try:
            if ArgSetsNamed:
                WrappedResult = Function( **ArgSet ) #Library_FunctionInvoker.Main( Function, ArgSet )
            else:
                WrappedResult = Function( ArgSet )
        except Exception as ExceptionObject:
            print ('FAIL: ArgSet ', ArgSet)
            print (ExceptionObject)
            WrappedResult = DefaultValue
        return WrappedResult


    #Make a function which is designed to iterate over the wrappped function 
    def BatchWrappedFunction( ArgSets ):
        BatchResults = []
        for ArgSet in ArgSets:
            BatchResults.append( WrappedFunction(ArgSet)  )
        return BatchResults


    if (Algorithm == 'loop'):
        for ArgSet in tqdm.tqdm(ListOfArgSets, disable=HideProgressBar ):
            ResultList.append( WrappedFunction(ArgSet ) )
    elif ( Algorithm == 'pp'):
        pass

    elif ( Algorithm in ['multiprocessing', 'multiprocessing_on_dill']):


        CPU_count = multiprocessing_on_dill.cpu_count()
        if PrintExtra:
            print ('CPU_count', CPU_count)

        #with multiprocessing_on_dill.Pool() as Pool:
        #PoolObject = multiprocessing_on_dill.Pool(CPU_count - 1) 
        #ResultList = PoolObject.map( WrappedFunction, ListOfArgSets  )

        if BatchCount is None and BatchSize == 1:
            with multiprocessing_on_dill.Pool(CPU_count, initializer=numpy.random.seed) as PoolObject:
                ResultList = list(tqdm.tqdm(
                    PoolObject.imap(WrappedFunction, ListOfArgSets), 
                    total   = len(ListOfArgSets), 
                    disable = HideProgressBar 
                    ) )
        else:
            ListOfListsOfArgSets = Library_IterableSplitIntoChunks.Main(
                Iterable= ListOfArgSets,
                ChunkCount= BatchCount,
                ChunkLength=  BatchSize,
                )
            with multiprocessing_on_dill.Pool(CPU_count, initializer=numpy.random.seed) as PoolObject:
                ListOfResultLists = list(tqdm.tqdm(
                    PoolObject.imap(BatchWrappedFunction, ListOfListsOfArgSets), 
                    total   = len(ListOfListsOfArgSets), 
                    disable = HideProgressBar 
                    ) )

                ResultList = list(itertools.chain.from_iterable( ListOfResultLists ))


    elif ( Algorithm == 'mpi4py'):
        ErrMsg = 'Not Implemented Yet...'
        raise Exception()

    elif ( Algorithm == 'dougserver'):
        #dougserver.submitJob
        ErrMsg = 'Not Implemented Yet...'
        raise Exception()
    else:
        ErrMsg = 'Unrecognized `Algorithm`... Library_ParallelLoop  FAILED to execute'
        raise Exception(ErrMsg)



    EndTime = time.time()
    TimeTaken = EndTime - StartTime
    if not HideProgressBar:
        print ('TimeTaken', TimeTaken)


    return ResultList














    




