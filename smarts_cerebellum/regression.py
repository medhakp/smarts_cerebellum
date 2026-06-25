import numpy as np
import nibabel as nib
import pandas as pd

import nitools as nt

from smarts_cerebellum.helper_fcns import week_path_search
# NEED TO ADD CREDITS FOR CODE DESIGN
# @Joern

def week_response_matrix(img0,
                    x, y, z, 
                    p_paths
                    ):
    
    """
    Builds the response matrix Y for week-regression.
    """
    
    # initialize empty array
    Y = np.zeros((len(p_paths), np.prod(img0.shape)))

    for row_idx, week_path in enumerate(p_paths): # enumerate through actual week and store the index of that week

        week_img = nib.load(week_path)

        #week_img.get_fdata()

        # populate response matrix
        Y[row_idx, :] = nt.sample_image(week_img, 
                                        xm=x, ym=y, zm=z,
                                        interpolation=1 # trilinear interpolation (since 3 dimensions in array)
                                        ).flatten() # store each (resampled) voxel array as a row vector for each week
    return Y

def week_design_matrix(p_weeks):
    """
    Function to build the design matrix for week-regression.
    """
    num_weeks = len(p_weeks)
    X = [np.ones(shape = (num_weeks)), p_weeks]
    X = np.array(X)
    X=X.T
    return X



# should pass to regression_week function the paths for each subject - this will be found using our function.

# so this is the general regression function, and then we will call this general function in another function that: finds the weeks available, runs the regression, spits out slope and intercept images.

# we can acquire p_weeks, p_paths from our week_path_searcher function.
def regression_week(reference_img, p_paths, p_weeks):
    """
    Voxel-wise MLR over multiple weeks.
    """

    # load reference image.
    img0 = nib.load(reference_img)

    # transform into world coordinates
    i, j, k = np.indices(img0.shape) # matrix indices for premult by affine
    x,y,z = nt.affine_transform(i, j, k, img0.affine)

    
    # build response matrix Y
    Y = week_response_matrix(img0, x,y,z, p_paths)

    # build design matrix X
    X = week_design_matrix(p_weeks)

    # calculate estimator B_hat (coefficients matrix), where B_hat = [B_0 B_1].T
    B_hat = np.linalg.pinv(X) @ Y


    # get slope and intercept matrices
    slope = np.zeros(img0.shape) # tensor with shape of reference img
    intercept = np.zeros(img0.shape)

    # indices from reference image's voxel coordinates
    iv = i.flatten()
    jv = j.flatten()
    kv = k.flatten()

    slope[iv, jv, kv] = B_hat[1,:] # write the slope into the vectors i, j, k for coordinates
    intercept[iv, jv, kv] = B_hat[0,:]


    # convert to Nifti image with reference image's affine
    intercept_img = nib.Nifti1Image(intercept, img0.affine)
    slope_img = nib.Nifti1Image(slope, img0.affine)


    return intercept_img, slope_img


# now, we have a function that just performs the regression. Now we need the function that will actually call it.
def perform_regression_week(reference_img, subj_id):
    """
    Function to perform regression.

    Inputs:
        reference_img (str)

    Outputs:
        intercept_img (Nifti)
        slope_img (Nifti)
    """

    # determine whether there are sufficient weeks to perform regression
    """
    This will use a sufficient_weeks function: this function will just use functions available in util
    """
    p_paths, p_weeks = week_path_search(reference_img, subj_id)

    if len(p_weeks)<2:
        return None, None # exit function if not enough measurement weeks
    
    # now that we've checked if there are enough measurement weeks, we can perform the regression

    return regression_week(reference_img, p_paths, p_weeks)



# @Marco
"""
# so the general regression function will work for 

def regression_week(paths):

    # take week from util.find_week and run the regression

    for w in week:
        pass
        # load vol and make it a vector and make Y

    # run the regression

    # spit slope and intercetp

    # this function will return slope and intercept

    pass

def regression_week(datatpye="WM, GM..."):



    pass
    
"""