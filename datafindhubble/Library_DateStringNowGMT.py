"""
DESCRIPTION:

    Gets current time in format :
        `Type_Datestring` 
        == 
        'yyyy_mm_dd_hh_mm_ss_mmmmmm_GMT'
ARGS:
    NONE

RETURNS:
    Datetime == `Type_Datestring` == '<yyyy_mm_dd_hh_mm_ss_mmmmmm>_GMT'

"""


import Library_DatetimeToDateString
import datetime

def Main():
    CurrentDateTime = datetime.datetime.utcnow()
    DateString =  Library_DatetimeToDateString.Main(CurrentDateTime, "GMT")
    return DateString
