"""
SOURCES:

DEFINITION:
    Creates an outer product possibility space 
    given a number of differnt independent events 
    accross differnt dimensions

    Though this really is an outer product, it was written in my sophmore year of college
    within the context of counting in different bases for each digit of a clock. 
    
    For example:
        if you wanted to count in binary, up to the number   11111
        then you would pass in :
            [1,1,1,1,1]

        if you wanted to count in base 10 up to 100
        then you would pass in :
            [9,9]

    the thought was that you would allow up to some maximum number for each digit.
    
    It was later that I realized this was the same thing as an outer product.

ARGS:
    DigitMaximums
        Type: Python List of Python Ints
        Description:
            Contains a list of the number of possibilities within each dimension - 1.
            i.e
                1,2,3
            has possiblities for each index:
                [0,1]  [0,1,2]  [0,1,2,3]


RETURNS:
    A list of every possibile combination of possibliities
        i.e the arg:
            1,2,3
        would return:
        [
        [0, 0, 0]
        [1, 0, 0]
        [0, 1, 0]
        [1, 1, 0]
        [0, 2, 0]
        [1, 2, 0]
        [0, 0, 1]
        [1, 0, 1]
        [0, 1, 1]
        [1, 1, 1]
        [0, 2, 1]
        [1, 2, 1]
        [0, 0, 2]
        [1, 0, 2]
        [0, 1, 2]
        [1, 1, 2]
        [0, 2, 2]
        [1, 2, 2]
        [0, 0, 3]
        [1, 0, 3]
        [0, 1, 3]
        [1, 1, 3]
        [0, 2, 3]
        [1, 2, 3]
        ]

"""


import numpy
def Main(DigitMaximums = None):

    possibility_space = []
    #set the counter to start at 0
    current_number = [0]*len(DigitMaximums)
    k = 0 
    while (current_number != DigitMaximums):
        current_through_k = [0]*(k + 1)
        max_through_k = [0]*(k + 1)
        n = 0
        while (n <= k):
            current_through_k[n] = current_number[n]
            max_through_k[n] = DigitMaximums[n]
            n = n + 1
        if (current_through_k == max_through_k):
            k = k + 1
        else:
            #print current_number
            possibility_space.append(current_number[:]) #need to make sure and copy the array, instead of referencing it
            current_number[k] = current_number[k] + 1
            n = 0
            while (n < k):
                current_number[n] = 0
                n = n + 1
            current_through_k = [0]*(k + 1)
            max_through_k = [0]*(k + 1)
            k = 0

    possibility_space.append(DigitMaximums  )
#    possibility_space.append(list( numpy.array(DigitMaximums) - 1) )            

    return possibility_space




