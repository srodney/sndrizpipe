"""
SOURCE:
    Mind of Douglas Adams
    https://stackoverflow.com/questions/42392887/gaussianmixture-initialization-using-component-parameters-sklearn
DESCRIPTION:
    Takes a mixture model object built with pomegranate
    Turns the object into an equivelant sklearn object6
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
    GaussianMixtureObjectPomegranate
        Type:
            <class 'NoneType'>
        Description:
            None
RETURNS:
    Result
        Type:
        Description:
"""
import pomegranate
import numpy
import sklearn
#-------------------------------------------------------------------------------
def Main(
    GaussianMixtureObjectPomegranate= None,
    CheckArguments = True,
    PrintExtra = False,
    ):

    Result = None

    if (CheckArguments):
        ArgumentErrorMessage = ""

        if (len(ArgumentErrorMessage) > 0 ):
            if(PrintExtra):
                print("ArgumentErrorMessage:\n", ArgumentErrorMessage)
            raise Exception(ArgumentErrorMessage)


    


    #https://github.com/jmschrei/pomegranate/issues/338
    #The returned weights are actually log-weights
    #   the developer claims they might be fixed.
    #   So I try to write the simple future-proof fix below, 
    #   which should stop triggering after pomegranate changes
    weights = GaussianMixtureObjectPomegranate.weights
    if weights[0] < 0:
        weights = numpy.exp(weights) 

    #Get means and covs out of the pomegranate object as well:
    means = []
    covs = []
    inv_covs = []
    precisions_choleskys = []
    for dist in GaussianMixtureObjectPomegranate.distributions:
        means.append(dist.mu)
        covs.append(dist.cov)


        #Yet another name mistake --> dist.inv_cov  !=   inv(dist.cov)
        #inv_covs.append(dist.inv_cov)
        inv_cov = None
        try:
            inv_cov = numpy.linalg.inv(dist.cov)
        except: #Sometimes the matrix ends up singular from rounding problems.
            inv_cov = numpy.linalg.pinv(dist.cov)

        inv_covs.append( inv_cov )

        precisions_choleskys.append( numpy.linalg.cholesky( inv_cov )  )

    means = numpy.array(means)
    covs = numpy.array(covs)
    inv_covs = numpy.array(inv_covs)
    precisions_choleskys = numpy.array(precisions_choleskys)


    if PrintExtra:
        print ('weights', weights)
        print ('means', means)
        print ('covs', covs)
        print ('inv_covs (precisions)', inv_covs)
        print ('precisions_choleskys', precisions_choleskys)


    #Build the sklearn object
    GaussianMixtureObjectSklearn = sklearn.mixture.GaussianMixture(
        n_components    = len(weights), 
        covariance_type = 'full',
        )

    #Now force all the values in the sklearn implementation:
    GaussianMixtureObjectSklearn.weights_       = weights
    GaussianMixtureObjectSklearn.means_         = means 
    GaussianMixtureObjectSklearn.covariances_   = covs
    #GaussianMixtureObjectSklearn.precisions_cholesky_ = numpy.linalg.cholesky(numpy.linalg.inv(  covs  )).transpose((0, 2, 1))
    GaussianMixtureObjectSklearn.precisions_ = inv_covs
    GaussianMixtureObjectSklearn.precisions_cholesky_ = precisions_choleskys


    GaussianMixtureObjectSklearn.converged_     = True
    GaussianMixtureObjectSklearn.n_iter_        = 1


    Result = GaussianMixtureObjectSklearn
    return Result 



















