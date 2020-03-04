"""

SOURCE:


    There is no time difference between Coordinated Universal Time and Greenwich Mean Time


DESCRIPTION:
    takes a native python datetime object, 
    and turns it into a 'Type_Datestring' object

    Result is always converted to ( GMT == UTC ) time zone

ARGS:
    Datetime -> python datetime object
    Timezone -> specifys the timezone associated with the datetime object provided 


RETURNS:
    Datestring
        Description: 
            looks like  'yyyy_mm_dd_hh_mm_ss_mmmmmm_tzn'
        Type:
            `Type_DateString`

TESTS:
    Test_DatetimeToDateString


"""


import Library_IntegerToStringPadWithZeros

def Main(
    Datetime = None, 
    Timezone = "NAN"
    ):
    
    if (Datetime is None):
        raise Exception('Datetime cannot be null')

    DateString = ""
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.year,           4) + "_"
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.month,          2) + "_"
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.day,            2) + "_"
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.hour,           2) + "_"
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.minute,         2) + "_"
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.second,         2) + "_"
    DateString += Library_IntegerToStringPadWithZeros.Main(Datetime.microsecond,    6) + "_" 
    DateString += Timezone

    return DateString
