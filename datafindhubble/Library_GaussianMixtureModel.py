"""
SOURCE:
    Mind of Douglas Adams
    https://stackoverflow.com/questions/42392887/gaussianmixture-initialization-using-component-parameters-sklearn
    https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html
    https://pomegranate.readthedocs.io/en/latest/GeneralMixtureModel.html
    https://stackoverflow.com/questions/42392887/gaussianmixture-initialization-using-component-parameters-sklearn
    #https://github.com/jmschrei/pomegranate/blob/master/tutorials/B_Model_Tutorial_2_General_Mixture_Models.ipynb
DESCRIPTION:
    Takes a numpy 2d dataset
    fits a gaussian mixture model to the dataset
    If number of components is unknown - 
    it will try to infer from the data


    Sklearn     CANNOT handle weighted datapoints.
    Pomegranate CAN

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
    NumberComponents
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import time
import numpy
import sklearn
import sklearn.mixture
import pomegranate
import Library_GaussianMixtureModelPomegranateToSklearn
import Library_GaussianMixtureModelSklearnWeightedBIC
import Library_GaussianMixtureModelSklearnWeightedAIC
import Library_DateStringNowGMT
#-------------------------------------------------------------------------------
def Main(
    NumpyTwoDimensionalDataset = None,
    DataPointWeights = None,
    NumberComponents= None,
    ResultFormat = None,
    Method = None,
    HideProgressBar = None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if ResultFormat is None:
        ResultFormat = 'Dictionary'

    if HideProgressBar is None:
        HideProgressBar = True

    if Method is None and DataPointWeights is None:
        Method = 'sklearn'
    else:
        Method = 'pomegranate'


    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    #What are all the properties we need to investigate in order to get a good fit?
    GaussianMixtureModelFunction = None
    GaussianMixtureObjectSklearn = None
    GaussianMixtureObjectPomegranate = None
    AICs = []
    BICs = []
    BICs_adjusted = []
    ComponentCounts = []
    MixtureMeans= None
    MixtureCovariances= None
    BestAICcomponentCount= None
    BestBICcomponentCount= None

    AllGaussianMixtureObjectsPomegranate = []
    AllGaussianMixtureObjectsSklearn = []

    #Determine the best number of components to have in the model using the information criterion
    if NumberComponents is None:
        NumberComponents = 2
        Descending = True
        DescendingAICs = True
        DescendingBICs = True

        while Descending:

            if not HideProgressBar:
                print (Library_DateStringNowGMT.Main()  , 'GMM Training N_comp', NumberComponents )

            #Get the model and information criteron
            if Method == 'sklearn':

                #Make the GMM model using sklearn
                GaussianMixtureObjectSklearn = sklearn.mixture.GaussianMixture(
                    n_components    = NumberComponents, 
                    covariance_type = 'full',
                    )
                GaussianMixtureObjectSklearn.fit(NumpyTwoDimensionalDataset)

                #keep the fits we made
                AllGaussianMixtureObjectsSklearn.append(GaussianMixtureObjectSklearn)

            elif Method == 'pomegranate':
                #Make the GMM model using pomegranate (using weights)
                GaussianMixtureObjectPomegranate  = pomegranate.gmm.GeneralMixtureModel.from_samples(
                    pomegranate.MultivariateGaussianDistribution,   
                    n_components=NumberComponents,                 
                    X=NumpyTwoDimensionalDataset,     
                    weights = DataPointWeights,  
                    stop_threshold = .01,  
                    max_kmeans_iterations = 2,
                    )

                #Now... cast the pomegranate fit into an sklearn fit:                
                GaussianMixtureObjectSklearn = Library_GaussianMixtureModelPomegranateToSklearn.Main(
                    GaussianMixtureObjectPomegranate= GaussianMixtureObjectPomegranate
                    )

                #keep the fits we made
                AllGaussianMixtureObjectsPomegranate.append(GaussianMixtureObjectPomegranate)
                AllGaussianMixtureObjectsSklearn.append(GaussianMixtureObjectSklearn)


            #Get the information criterion (with weights)
            #FIXME:     Submit a git pull request for sklearn to actually use this...
            #AIC = GaussianMixtureObjectSklearn.aic(NumpyTwoDimensionalDataset)
            #BIC = GaussianMixtureObjectSklearn.bic(NumpyTwoDimensionalDataset)
            AIC = Library_GaussianMixtureModelSklearnWeightedAIC.Main(
                ScoreSamplesFunction = GaussianMixtureObjectSklearn.score_samples, 
                NumpyTwoDimensionalDataset = NumpyTwoDimensionalDataset,
                NumParameters = GaussianMixtureObjectSklearn._n_parameters(), 
                Weights = DataPointWeights, 
                )
            BIC = Library_GaussianMixtureModelSklearnWeightedBIC.Main(
                ScoreSamplesFunction = GaussianMixtureObjectSklearn.score_samples, 
                NumpyTwoDimensionalDataset = NumpyTwoDimensionalDataset,
                NumParameters = GaussianMixtureObjectSklearn._n_parameters(), 
                Weights = DataPointWeights, 
                )

            AICs.append(AIC)
            BICs.append(BIC)
            ComponentCounts.append(NumberComponents)


            #Figure out if we are improving the model, or making it worse
            #   Once we have made it worse twice in a row, we will break the loop
            if NumberComponents > 4:
                DescendingAICs = not(    (AICs[-1] > AICs[-2]) and (AICs[-2] > AICs[-3]) and (AICs[-3] > AICs[-4])    )
                DescendingBICs = not(    (BICs[-1] > BICs[-2]) and (BICs[-2] > BICs[-3]) and (BICs[-3] > BICs[-4])    )
                Descending = DescendingAICs and DescendingBICs

            #Break if the BIC or AIC is LARGE then a single gaussian fit.
            #SEE IMAGE: https://drive.google.com/file/d/13jw7lT_M2POJ305MURV1GmllLRc8_tbM
            if NumberComponents > 4 and BICs[-1] > BICs[0]:
                break


            NumberComponents += 1


        BestIndexBIC = BICs.index(min(BICs))
        BestIndexAIC = AICs.index(min(AICs))
    
        BestBICcomponentCount   = ComponentCounts[  BestIndexBIC  ]
        BestAICcomponentCount   = ComponentCounts[  BestIndexAIC   ]




        BestComponentCount      = BestBICcomponentCount

    elif NumberComponents is not None:
        BestComponentCount = NumberComponents


    #Refit after training using the best number of components:
    #   Also: Turn the model object into a single function
    if Method == 'sklearn':
        """
        GaussianMixtureObjectSklearn = sklearn.mixture.GaussianMixture(
            n_components=BestComponentCount, 
            covariance_type='full'
            )
        GaussianMixtureObjectSklearn.fit(NumpyTwoDimensionalDataset)
        """

        GaussianMixtureObjectSklearn = AllGaussianMixtureObjectsSklearn[BestIndexBIC]

        #Get the some data back out of the fit...
        MixtureMeans        = GaussianMixtureObjectSklearn.means_
        MixtureCovariances  = GaussianMixtureObjectSklearn.covariances_

        def GaussianMixtureModelFunction( Point ):
            return numpy.exp( GaussianMixtureObjectSklearn.score_samples( numpy.atleast_2d( Point ) ) )


    if Method == 'pomegranate':

        """
        GaussianMixtureObjectPomegranate  = pomegranate.gmm.GeneralMixtureModel.from_samples(
            pomegranate.MultivariateGaussianDistribution,   
            n_components=BestComponentCount,                 
            X=NumpyTwoDimensionalDataset,     
            weights = DataPointWeights,  
            #stop_threshold = .0001,  #Train extra hard
            max_kmeans_iterations = 10,
            )
        
        #Get the some data back out of the fit... easiest thing is to cast to sklearn and extract
        GaussianMixtureObjectSklearn = Library_GaussianMixtureModelPomegranateToSklearn.Main(
            GaussianMixtureObjectPomegranate= GaussianMixtureObjectPomegranate
            )
        """
        GaussianMixtureObjectPomegranate    = AllGaussianMixtureObjectsPomegranate[BestIndexBIC]
        GaussianMixtureObjectSklearn        = AllGaussianMixtureObjectsSklearn[BestIndexBIC]

        MixtureMeans        = GaussianMixtureObjectSklearn.means_
        MixtureCovariances  = GaussianMixtureObjectSklearn.covariances_

        def GaussianMixtureModelFunction(Point):
            return GaussianMixtureObjectPomegranate.probability(numpy.atleast_2d( numpy.array(Point) ))





    if ResultFormat == 'Function':
        Result = GaussianMixtureModelFunction
    elif ResultFormat == 'Dictionary':
        Result = {
        'GaussianMixtureModelFunction': GaussianMixtureModelFunction,
        'GaussianMixtureObjectSklearn': GaussianMixtureObjectSklearn,
        'GaussianMixtureObjectPomegranate': GaussianMixtureObjectPomegranate,
        'AICs' : AICs, 
        'BICs' : BICs, 
        'ComponentCounts':ComponentCounts,
        'Means' : MixtureMeans,
        'Covariances' : MixtureCovariances,
        'BestAICcomponentCount':BestAICcomponentCount,
        'BestBICcomponentCount':BestBICcomponentCount,
        }

    return Result 





















