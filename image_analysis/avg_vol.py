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

import os

#_______________________________

# directories
# make as fcn args?
base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'
anat_dir = '/cifs/diedrichsen/data/smarts_cerebellum/anatomicals'
p_df = pd.read_csv(f'{base_dir}/participants_anat.tsv', sep = '\t') # not needed


def avg_vol(subj_id, 
            reference_img, # reference anatomical
            week_path, # path to week image
            #week_file,
            results_path,
            tissue=None):
    
    """
    Inputs: UPDATE
    anat dir; participants file OR [(subj, week) and call it inside a loop].
    Reference img (inside the Jupyter notebook loop for reading off the info file)
    week_path (path for each week's image), results_path (store results)

    Everything is done in the reference image. So this function will (...) (resample voxels in other weeks so that they are aligned with the reference, and perform multiple linear regression)

    Returns B_hat coefficient matrix (for more flexibility in other possible operations)
    
    """

    img0 = nib.load(reference_img)

    # later fix: option to reduce to only wtihin-brain voxels
    
    # transform into world coordinates
    i, j, k = np.indices(img0.shape) # matrix indices for premult by affine
    x,y,z = nt.affine_transform(i, j, k, img0.affine)

    # all possible weeks.
    weeks = np.array([0,4,12,24,52]) # read from file, use file reading function maybe


    #____________________________________
    # find the number of measurement weeks that exist
    p_weeks = []
    for week in weeks:
        #week_path = f'{anat_dir}/{subj_id}/W{week}/wm_results/{subj_id}_W{week}_T1_wm_vol.nii'
        week_path = week_path
        #week_path = f'{anat_dir}/{subj_id}/W{week}/{subj_id}_W{week}_T1.nii'

        # skip over missed measurement weeks.
        if not os.path.exists(week_path):
            continue

        p_weeks.append(week)
    
    if len(p_weeks) == 1: # only one measurement week available
        return None # exit function (skip subject)    
    #__________________________


    Y = np.zeros((len(p_weeks), np.prod(img0.shape))) # initialize Y (shape = (k by p)) array, where k = number of weeks available

    for week in weeks: # resample ALL weeks, including the reference week
        #week_path = f'{anat_dir}/{subj_id}/W{week}/wm_results/{subj_id}_W{week}_T1_wm_vol.nii'
        week_path = week_path
        #week_path = f'{anat_dir}/{subj_id}/W{week}/{subj_id}_W{week}_T1.nii'

        # skip over missed measurement weeks.
        if not os.path.exists(week_path):
            continue

        week_img = nib.load(week_path)

        week_dict = {
            '0': 0,
            '4': 1,
            '12': 2,
            '24': 3,
            '52': 4
        }

    
        # resample each week's image so that voxels are exactly on top of reference week voxels; add to response matrix as row vector
        Y[week_dict[str(week)]:,] = nt.sample_image(week_img, # response matrix
                                xm=x, ym = y, zm = z, # world coordinates
                                interpolation = 1 # using trilinear resampling
                                ).flatten() # need to put each week as a row
        
        # now we have Y as a k by p matrix, where k is the number of weeks.  

    # design matrix
    num_weeks = len(p_weeks)
    X = [np.ones(shape = (num_weeks)), p_weeks]
    X = np.array(X)
    X = X.T

    # estimator (coefficients matrix)
    B_hat = np.linalg.pinv(X) @ Y
    # where B_hat = [B_0 B_1].T

    # intercept and slope reshaped into Nifti-compatible array
    intercept = B_hat[0,:].reshape(img0.shape)
    slope = B_hat[1,:].reshape(img0.shape)

    """
    So this image is in world coordinates now, and saved with the affine of the original image.
    Should it be converted back to voxel coordinates (bc otherwise, the affine is kinda meaningless)?
    """
    

    # save as Nifti
    intercept_img = nib.Nifti1Image(intercept, img0.affine)
    slope_img = nib.Nifti1Image(slope, img0.affine)

    # fix: name of file should be insertable, too (e.g. which_type = 'native' or smth in fcn input)
    nib.save(intercept_img, f'{results_path}/{subj_id}_T1_intercept_native.nii.gz') # specify file name
    nib.save(slope_img, f'{results_path}/{subj_id}_T1_slope_native.nii.gz')

    return B_hat
