"""
SOURCE:
    Mind of Douglas Adams
    https://realpython.com/python-rounding/
    https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
DESCRIPTION:
    Rounds a number.
    This library is the home for the many 
    options which are available depending on the circumstance. 

    Ways to round a number:
        Significant figures
        Decimal Count
        Truncate

    Can round up, down, or standard  x>=5 ==> Up else Down


    Why do this carefully at all?

    See the source above, but for the lazy reader a short explanation is that
    when you round, you are using the wrong number. 
    If you use the wrong number many many times in a calculation,
    how you choose it to be wrong can have serious consequences.

    For the probabilistic mathematician reader, the technical sentence is below:
    Rounding is an approximate technique for estimation of the algebra 
    of random variables of which each number in a calculation needs 
    to be treated as a random variable in the case that the numbers
    are not mathematically absolutely correct. 

    For the physicist reader: Obviously one should do the correct 
    likelihood analysis given knowledge of randomness of numbers,
    and for small parts of certain monte carlo methods, rounding correctly
    is also required. 

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
    Number
        Type:
            <class 'float'>
        Description:
            The number to round
    Method
        Type:
            <class 'str'>
        Description:
            ['DecimalCount', 'SignificantFigures', 'Truncate']
    DigitCount
        Type:
            <class 'int'>
        Description:
            Based on the method, the ammountyness to round the number
    Direction
        Type:
            <class 'str'>
        Description:
            ['Up', 'Down', 'AwayFromZero', 'TowardsZero' , None]
RETURNS:
    Result
        Type:
        Description:
"""
import math

#-------------------------------------------------------------------------------
def Main(
    Number= None,

    Method= None,
    DigitCount= None,
    Direction= None,

    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None


    if Direction is None:
        Direction = 'AwayFromZero'

    if Method is None:
        Method = 'DecimalCount'

    if DigitCount is None:
        DigitCount = 0


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)

    



    def truncate(n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    def round_up(n, decimals=0):
        multiplier = 10 ** decimals
        return math.ceil(n * multiplier) / multiplier

    def round_down(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier

    def round_half_up(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n*multiplier + 0.5) / multiplier

    def round_half_down(n, decimals=0):
        multiplier = 10 ** decimals
        return math.ceil(n*multiplier - 0.5) / multiplier

    def round_half_away_from_zero(n, decimals=0):
        rounded_abs = round_half_up(abs(n), decimals)
        return math.copysign(rounded_abs, n)

    def round_half_towards_zero(n, decimals=0):
        rounded_abs = round_half_down(abs(n), decimals)
        return math.copysign(rounded_abs, n)


    round_to_n = lambda x, n: x if x == 0 else round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


    if Method is 'DecimalCount':

        if Direction is 'AwayFromZero':
            Result = round_half_away_from_zero(Number, decimals = DigitCount)

        elif Direction is 'TowardsZero':
            Result = round_half_towards_zero(Number, decimals = DigitCount)

        elif Direction is 'Up':
            Result = round_up(Number, decimals = DigitCount)

        elif Direction is 'Down':
            Result = round_down(Number, decimals = DigitCount)

    elif Method is 'SignificantFigures':
        Result =  round_to_n(Number, DigitCount)

    elif Method is 'Truncate':
        Result = truncate(Number, decimals = DigitCount)


    if PrintExtra: 
        print( 
            'Round(Number =', Number, 
            ', Method =', Method, 
            ', Direction =', Direction, 
            ', DigitCount =', DigitCount,
            '==', Result)

    return Result 





































