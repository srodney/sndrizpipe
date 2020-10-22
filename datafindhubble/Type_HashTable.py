
"""
SOURCE:

    http://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python


DESCRIPTION:

    This implements a combination of 
        `Duck typing`
            Does it quack?
            Does it look like a duck?
        `KnownTypeListing`
            Is it within a list of documented types?
            
    If its not a known hashy type, and it doesn't act like a hashy type:
        Then it is not a hashy type
    

            
ARGS:
    HashTableCandidate
        Description:
            The object of which to check if it is an HashTable python object
            Examples of hashtable python objects are:
                Dictionary
                Collections.<sooooooo many things>
                JSON object
                etc..

RETURNS:
    True if HashTable
    False if NOT HashTable


"""

import collections

def Main(
    HashTableCandidate = None,
    PrintExtra = False,
    CheckArguments = True,
    ):
    
    KnownHashTypes = [dict , collections.OrderedDict ]
    Result = False

    if (type(HashTableCandidate) in KnownHashTypes ):
        Result = True
    else:
        try:
            keys = list(HashTableCandidate.keys())
            #print 'keys', keys
            firstKey = keys[0]
            #print 'firstKey', firstKey
            firstValue = HashTableCandidate[firstKey]
            #print 'firstValue', firstValue
            Result = True
        except:
            Result = False


    return Result






























