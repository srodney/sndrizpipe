import matplotlib.pyplot
import pandas
import pprint
import numpy
import Library_DataFindOpenSuperNovaCatalogSingleObject

TryFullDataObject = False
TryPhotDataObject = True

if TryFullDataObject:

    Result = Library_DataFindOpenSuperNovaCatalogSingleObject.Main(

        SuperNovaId = "03D1ax",
        )
    for Key in Result["SNLS-03D1ax"].keys():
        print ( Key)

    PhotItems = Result["SNLS-03D1ax"]['photometry']

    #phot item keys:
    #['time', 'band', 'bandset', 'countrate', 'e_countrate', 'e_upper_magnitude', 
    #'instrument', 'magnitude', 'system', 'telescope', 'u_countrate', 'u_time', 
    #'upperlimit', 'upperlimitsigma', 'zeropoint', 'source']

    print ('PhotItems[0]', PhotItems[0])

    Times = []
    Mags  = []
    for Item in PhotItems:
        if Item['band'] == 'g':
            #print (Item['band'])
            print (Item['time'])
            print (Item['magnitude'])

            Times.append(Item['time'])
            Mags.append(Item['magnitude'])
        #print (Item.keys())




    matplotlib.pyplot.scatter(Times, Mags)
    matplotlib.pyplot.ylabel('mags')
    matplotlib.pyplot.xlabel('times')
    matplotlib.pyplot.draw()


if TryPhotDataObject:

    Result = Library_DataFindOpenSuperNovaCatalogSingleObject.Main(
        SuperNovaId = "03D1ax",
        ResultFormat = "PhotometryOnly",
        )

    print ('Result', Result['SNLS-03D1ax'].keys())
    #print (Result.keys)


    PhotItems = Result["SNLS-03D1ax"]['photometry']
    print ('PhotItems')
    print (PhotItems)


    PhotColumnNames = ['magnitude', 'e_magnitude','band', 'time',]
    print ('PhotColumnNames', PhotColumnNames)


    PhotDataFrame = pandas.DataFrame(data = PhotItems, columns = PhotColumnNames)
    print ('PhotDataFrame', PhotDataFrame)


    #sncosmo.plot_lc(astropydatatable, model=fitted_model, errors=result.errors)


    Bands =  list( set( PhotDataFrame['band'] ) )
    print ('Bands', Bands)


    matplotlib.pyplot.figure()
    for Band in Bands:
        print ('Band', Band)
        Rows = PhotDataFrame.loc[PhotDataFrame['band'] == Band]    

        Times = Rows['time']

        Mags = Rows['magnitude']

        print ('Times', Times)
        print ('Mags', Mags)

        Times = numpy.array(Times).astype(numpy.float64)
        Mags = numpy.array(Mags).astype(numpy.float64)

        matplotlib.pyplot.scatter( Times, Mags, label = Band)



    matplotlib.pyplot.legend(loc = 'best', numpoints=1)
    matplotlib.pyplot.xlabel('times')
    matplotlib.pyplot.ylabel('mags')
    #matplotlib.pyplot.draw()




matplotlib.pyplot.show()













