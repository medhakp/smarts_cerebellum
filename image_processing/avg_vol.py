# need to rename this and fix comment documentation.

"""
Calculates average image for a subject over all time points. For example, get the average white matter image for a subject.

Uses a multiple linear regression model.
"""

# Imports

# model libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# image reading libraries
import nibabel as nib
from nilearn import plotting as npl
from nilearn import masking # for masking within-brain voxels

import nitools as nt

from helper_functions import week_path_search

import os

# helper functions

def sufficient_weeks(reference_img):

    # need at least 2 measurement weeks to run our regression
    # this function will search for all week files, such that week files are the same path structure as the reference file, but exist for other weeks
    p_paths, p_weeks = week_path_search.week_path_search(reference_img)
    
    if len(p_weeks) == 1: # only one measurement week available
        return None # exit function (skip subject)    
    
    return p_weeks, p_paths


# this entire loop could probably be its own fucntion.
def response_matrix(Y, 
                    x, y, z, 
                    p_paths
                    ):
    
  

    for row_idx, week_path in enumerate(p_paths): # enumerate through actual week and store the index of that week
        # so (e.g.) if W0, W24, then store their flattened arrays in rows 1 and 2 respectively in Y matrix
        
        # we've already returned all the week paths (images) that are available for a given subject, so just use those

        #print(f'{week_path} is in Y index {row_idx}')

        week_img = nib.load(week_path)

        
        Y[row_idx, :] = nt.sample_image(week_img, 
                                        xm=x, ym=y, zm=z,
                                        interpolation=1 # trilinear interpolation (since 3 dimensions in array)
                                        ).flatten() # store each (resampled) voxel array as a row vector for each week
    return Y 

# add input: type of file (e.g. native, tissue_resliced, etc.)
def avg_vol(
            subj_id, 
            reference_img, # reference anatomical
            #week_path, # path to week image
            results_path,
            image_suffix,
            #subpath = None, # specify subfolder
            #input_suffix = None, # suffix for input image; MUST begin with '_'
            #tissue=None
            ):
    """
    Inputs:
        subj_id (str): subject ID used for output image naming.
        reference_img (str): path to reference image
        results_path (str): path to directory to save file to
        image_suffix (str): suffix for output image (follow naming convention)
            suggested: <level>_<if coreg, which>_<tissue = wm, gm, T1, ...>

    Everything is done in the reference image. So this function will (...) (resample voxels in other weeks so that they are aligned with the reference, and perform multiple linear regression)

    Outputs:
        B_hat correlation matrix
        X, Y design and response matrices
        intercept_img, slope_img as Nifti images

        Also saves intercept and slope images to specified directory with specified suffix, following convention <subj_id>_<suffix = level(=native or template (which))_<coreg, if relevant>_tissue>_<algorithm = intercept/slope>
    
    """

    print(f'currently on {reference_img}')

    img0 = nib.load(reference_img)

    # later fix: option to reduce to only wtihin-brain voxels
    
    # transform into world coordinates
    i, j, k = np.indices(img0.shape) # matrix indices for premult by affine
    x,y,z = nt.affine_transform(i, j, k, img0.affine)

    # get the available weeks for this subject's files
    p_results = sufficient_weeks(reference_img)
    if p_results is None:
        print(f'skipping {subj_id}: insufficient measurement weeks')
        return None, None, None, None, None # if invalid, returns 5 None's; otherwise, returns two lists
    p_weeks, p_paths = p_results


    # initialize Y (shape = (k by p)) array, where k = number of weeks available
    Y_empty = np.zeros((len(p_weeks), np.prod(img0.shape)))

    Y = response_matrix(Y=Y_empty,
                        x=x,y=y,z=z,
                        p_paths=p_paths)
    
    # design matrix
    num_weeks = len(p_weeks)
    X = [np.ones(shape = (num_weeks)), p_weeks] # p_weeks must be INTEGER (or some type of number, like float) for matrix
    X = np.array(X)
    X = X.T

    # estimator (coefficients matrix)
    B_hat = np.linalg.pinv(X) @ Y
    # where B_hat = [B_0 B_1].T

    #_________________
    # save image with voxel coordinates
    slope = np.zeros(img0.shape) # tensor with shape of reference img
    intercept = np.zeros(img0.shape)
    # need i, j, k as vectors (they're tensors right now)

    iv = i.flatten()
    jv = j.flatten()
    kv = k.flatten()

    slope[iv, jv, kv] = B_hat[1,:] # write the slope into the vectors i, j, k for coordinates
    intercept[iv, jv, kv] = B_hat[0,:]
    #________________

    """
    Joern's pseudocode

    results = np.zeros(img0.shape)
    results(i,j,k)=B(:,1) # Slopw
    nifti = np.Nifti1image(results,img0.affine)
    niftt.to_filename()

    """

    # intercept and slope reshaped into Nifti-compatible array
    #intercept = B_hat[0,:].reshape(img0.shape)
    #slope = B_hat[1,:].reshape(img0.shape)

    """
    So this image is in world coordinates now, and saved with the affine of the original image.
    Should it be converted back to voxel coordinates (bc otherwise, the affine is kinda meaningless)?

    # intercept and slope are already world-coordinates array, so multiply by inverse affine
    
    """
    
    # save as Nifti
    intercept_img = nib.Nifti1Image(intercept, img0.affine)
    slope_img = nib.Nifti1Image(slope, img0.affine)

    # save image: choose path to save image to (as function input) and specify suffix of file.
        # image name follows convention: <subj_id>_<level = native or template (specify)>_<algorithm = intercept or slope>

    nib.save(intercept_img, f'{results_path}/{subj_id}_{image_suffix}_intercept.nii.gz') # specify file name
    nib.save(slope_img, f'{results_path}/{subj_id}_{image_suffix}_slope.nii.gz')

    return B_hat, X, Y, intercept_img, slope_img