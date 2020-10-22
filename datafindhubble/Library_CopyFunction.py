"""
SOURCE:
    http://stackoverflow.com/questions/6527633/how-can-i-make-a-deepcopy-of-a-function-in-python

        **Cannot find the official documentation for `types.FunctionType` 
            Must have named arguments somehwere, and cannot find with google


    http://nullege.com/codes/search/types.FunctionType
    
        types.FunctionType
            function(code, globals[, name[, argdefs[, closure]]])


    http://snipplr.com/view/17819/

        import types
         
        def create_function(name, args):
         
            def y(): pass
         
            y_code = types.CodeType(args, \
                        y.func_code.co_nlocals, \
                        y.func_code.co_stacksize, \
                        y.func_code.co_flags, \
                        y.func_code.co_code, \
                        y.func_code.co_consts, \
                        y.func_code.co_names, \
                        y.func_code.co_varnames, \
                        y.func_code.co_filename, \
                        name, \
                        y.func_code.co_firstlineno, \
                        y.func_code.co_lnotab)
         
            return types.FunctionType(y_code, y.func_globals, name)
         
        myfunc = create_function('myfunc', 3)
         
        print repr(myfunc)
        print myfunc.func_name
        print myfunc.func_code.co_argcount
         
        myfunc(1,2,3,4)
        # TypeError: myfunc() takes exactly 3 arguments (4 given)

    http://late.am/post/2012/03/26/exploring-python-code-objects.html

    http://stackoverflow.com/questions/427453/how-can-i-get-the-source-code-of-a-python-function


    http://sweetme.at/2013/10/21/how-to-detect-python-2-vs-3-in-your-python-script/
    

    https://www.programcreek.com/python/example/2068/types.CodeType
        #Python 3 implementation of passing arg names:


        def make_code(self, assembly, name, argcount, has_varargs, has_varkws):
                kwonlyargcount = 0
                nlocals = len(self.varnames)
                stacksize = plumb_depths(assembly)
                flags = (  (0x02 if nlocals                  else 0)
                         | (0x04 if has_varargs              else 0)
                         | (0x08 if has_varkws               else 0)
                         | (0x10 if self.scope.freevars      else 0)
                         | (0x40 if not self.scope.derefvars else 0))
                firstlineno, lnotab = make_lnotab(assembly)
                return types.CodeType(argcount, kwonlyargcount,
                                      nlocals, stacksize, flags, assemble(assembly),
                                      self.collect_constants(),
                                      collect(self.names), collect(self.varnames),
                                      self.filename, name, firstlineno, lnotab,
                                      self.scope.freevars, self.scope.cellvars) 

    https://github.com/darius/tailbiter/blob/master/compiler.py

DESCRIPTION:
    Makes a deep copy of a function in python


    return a function with same code, globals, defaults, closure, and 
    name (or provide a new name)


    #STILL DOES NOT TRUELY DEEP COPY A FUNCTION 
    #   -> THE DEFAULT ARGS DON'T GET COPIED OVER
    #   -> THEY REMAIN REFERENCES/POINTERS

    Behavior changes between version 2 and three for getting the types.CodeType
    There is an additional arguement which comes right after arg count. 
    "kwonlyargcount" is new in python 3


ARGS:
    Function
        The function to copy
    NewName
        The new name for the function's copy
    NewDefaults
        Description:
            New default values for the function arguments
            This enables copying some data to private scope for the new function copy
                Especially useful in parallel processing
        type  
            python `None`
            OR 
            python `tuple`
            OR 
            `Type_HashTable` allowed if `CheckArguments==True` 



RETURNS:
    FunctionCopy


"""
import pprint
import types
import copy
import pprint
import inspect
import Type_HashTable
import sys

def Main(
    Function = None, 
    NewName = None,
    NewDefaults = None, 
    CheckArguments = True,
    PrintExtra = False
    ):

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (type(NewDefaults) == type(None)):
            pass

        elif ( type(NewDefaults) is tuple):
            pass

        elif( Type_HashTable.Main(NewDefaults) ):

            #TODO: We will ignore **kwards, and *args for now
            #FunctionSpecialArgsName = FunctionArgumentNamesInOrder[1] 
            #print 'FunctionSpecialArgsName', FunctionSpecialArgsName
            #FunctionSpecialKwarsName = FunctionArgumentNamesInOrder[2]
            #print 'FunctionSpecialKwarsName', FunctionSpecialKwarsName
            pass

        else:
            ArgumentErrorMessage += 'NewDefaults == ' + str(NewDefaults) + '\n'
            ArgumentErrorMessage += 'NewDefaults must be of type `None`, `tuple`, or `Type_HashTable`'

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)

            raise Exception(ArgumentErrorMessage)

    if (PrintExtra):
        FunctionProperties = dir(Function)
        print('FunctionProperties')
        pprint.pprint(FunctionProperties)


    #DEFINE THE NEW FUNCTION NAME:
    FinalNewFunctionName = copy.deepcopy(NewName) or Function.__name__

    if (PrintExtra):
        print('FinalNewFunctionName')
        print(FinalNewFunctionName)


    #DEFINE THE NEW FUNCTION DEFAULTS:

    FinalNewDefaultArgumentValues = tuple()
    FinalNewDefaultArgumentNames = tuple()

    #Get original Function Defaults:
    FunctionArgumentInformation = inspect.getargspec(Function)       
    OriginalFunctionDefaults = Function.__defaults__
    OriginalArgumentDefaultCount = 0
    if (OriginalFunctionDefaults is not None): 
        OriginalArgumentDefaultCount = len(OriginalFunctionDefaults)
    OriginalFunctionArgumentNamesInOrder = FunctionArgumentInformation.args
    OriginalFunctionArgumentsCount = len(OriginalFunctionArgumentNamesInOrder)

    if (PrintExtra):
        print('OriginalFunctionDefaults', OriginalFunctionDefaults)
        print('OriginalFunctionArgumentNamesInOrder', OriginalFunctionArgumentNamesInOrder)

    NewFunctionArgumentsCount = 0

    if (type(NewDefaults) == type(None)):
        FinalNewDefaultArgumentValues = OriginalFunctionDefaults
        FinalNewDefaultArgumentNames = tuple(OriginalFunctionArgumentNamesInOrder)

    elif (type(NewDefaults) is tuple):
        NewFunctionArgumentsCount = len(NewDefaults)
        FinalNewDefaultArgumentValues = tuple(NewDefaults)
        FinalNewDefaultArgumentNames = tuple(OriginalFunctionArgumentNamesInOrder)
        
    elif (Type_HashTable.Main(NewDefaults)):
        NewFunctionArgumentsCount = len(list(NewDefaults.keys()))

        #Figure out the new function defaults
        NewDefaultValuesList = []
        NewDefaultNamesList = []
        for OriginalFunctionArgumentNumber in range(OriginalFunctionArgumentsCount):
            OriginalArgumentName = OriginalFunctionArgumentNamesInOrder[OriginalFunctionArgumentNumber]
            NewArgumentDefaultValue = None
            if OriginalArgumentName in NewDefaults:
                NewArgumentDefaultValue = NewDefaults[OriginalArgumentName]
            NewDefaultValuesList.append(NewArgumentDefaultValue)
            NewDefaultNamesList.append(OriginalArgumentName)

        #Fill in any missing new default values with the old default ones
        k = 0
        while (k < OriginalArgumentDefaultCount):
            if (NewDefaultValuesList[ OriginalFunctionArgumentsCount - 1 - k] is None):
                if (OriginalFunctionDefaults[OriginalArgumentDefaultCount -1 -k] is not None):
                    NewDefaultValuesList[ OriginalFunctionArgumentsCount - 1 - k] = OriginalFunctionDefaults[OriginalArgumentDefaultCount -1 -k] 
            k = k + 1
        if (PrintExtra):
            print('NewDefaultValuesList', NewDefaultValuesList)

        #Find NewDefaultKeys which are not listed as original Function arguements
        NewDefaultArgumentNames = set(NewDefaults.keys())

        OriginalDefaultArgumentNames = set(OriginalFunctionArgumentNamesInOrder)

        NewDefaultArgumentNamesToAdd = NewDefaultArgumentNames - OriginalDefaultArgumentNames

        if (PrintExtra):
            print('NewDefaultArgumentNames', NewDefaultArgumentNames)
            print('OriginalDefaultArgumentNames', OriginalDefaultArgumentNames)
            print('NewDefaultArgumentNamesToAdd', NewDefaultArgumentNamesToAdd)

        for NewDefaultArgumentName in NewDefaultArgumentNamesToAdd:
            NewDefaultArgumentValue = NewDefaults[NewDefaultArgumentName]
            NewDefaultValuesList.append(NewDefaultArgumentValue)
            NewDefaultNamesList.append(NewDefaultArgumentName)
            if (PrintExtra):
                print('  NewDefaultArgumentName', NewDefaultArgumentName)
                print('  NewDefaultArgumentValue', NewDefaultArgumentValue)

        FinalNewDefaultArgumentValues = tuple(NewDefaultValuesList) #<- Ignore the new arguments
        FinalNewDefaultArgumentNames = tuple(NewDefaultNamesList)

    if (PrintExtra):
        print('FinalNewDefaultArgumentValues')
        print(FinalNewDefaultArgumentValues)

        print('FinalNewDefaultArgumentNames')
        print(FinalNewDefaultArgumentNames)

    FinalNewFunctionArgumentsCount = len(FinalNewDefaultArgumentNames)


    #Create a copy of the old function code into the new function
    if (PrintExtra): 
        pprint.pprint( dir( Function.__code__ ))
    
    #NewFunctionCode = Function.__code__
    NewFunctionCode = None
    if (sys.version_info < (3, 0)):
        print ("-----------------")
        print ("Detected python 2")
        print ("-----------------")
        pprint.pprint(inspect.getargspec(types.CodeType.__init__))
        NewFunctionCode = types.CodeType(
            FinalNewFunctionArgumentsCount,  #co_argcount
            Function.__code__.co_nlocals, 
            Function.__code__.co_stacksize, 
            Function.__code__.co_flags, 
            Function.__code__.co_code, 
            Function.__code__.co_consts, 
            Function.__code__.co_names, 
            FinalNewDefaultArgumentNames, #Function.func_code.co_varnames, 
            Function.__code__.co_filename, 
            FinalNewFunctionName,  #co_name
            Function.__code__.co_firstlineno, 
            Function.__code__.co_lnotab,
            )
    else:
        print ("-----------------")
        print ("Detected python 3")
        print ("-----------------")
        #'co_kwonlyargcount',  IS NEW
        NewFunctionCode = types.CodeType(
            FinalNewFunctionArgumentsCount,  #co_argcount
            Function.__code__.co_kwonlyargcount,  #<-------------NEW NEW NEW NEW
            Function.__code__.co_nlocals, 
            Function.__code__.co_stacksize, 
            Function.__code__.co_flags, 
            Function.__code__.co_code, 
            Function.__code__.co_consts, 
            Function.__code__.co_names, 
            FinalNewDefaultArgumentNames, #Function.func_code.co_varnames, 
            Function.__code__.co_filename, 
            FinalNewFunctionName,  #co_name
            Function.__code__.co_firstlineno, 
            Function.__code__.co_lnotab,
            )

    #Create a new function by invoking the python function `types.FunctionType`
    FunctionCopy = types.FunctionType(
        NewFunctionCode, 
        Function.__globals__, 
        FinalNewFunctionName,
        FinalNewDefaultArgumentValues , 
        Function.__closure__ #Does not work with scipy spline object
        )

    if (PrintExtra):
        print('FunctionCopy.__defaults__ ')
        print(FunctionCopy.__defaults__) 
        FunctionCopyArgumentInformation = inspect.getargspec(FunctionCopy)       
        print('FunctionCopyArgumentInformation')
        print(FunctionCopyArgumentInformation)

    # in case Function was given attrs 
    #   Note: 
    #       * The original version of this dict copy was a shallow copy):
    #       * It is unknown if using the copy.deepcopy method fixes this to be a true deep copy
    FunctionCopy.__dict__.update(copy.deepcopy( Function.__dict__) ) 

    return FunctionCopy
















