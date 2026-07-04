"""
Function to run voxel-wise lme; for now, just random intercept model

If image normalized to cerebellum-only template, then outside voxels are 0
So instead of binary mask, maybe take the sum of each voxel column and if sum is zero, remove that column (outside-brain voxels are zero)
fslstats mask.nii.gz -V (voxel count)

"""

import numpy as np
import pandas as pd
import nibabel as nib
import nitools as nt
import os
import statsmodels.formula.api as smf

import smarts_cerebellum.globals as gl
from smarts_cerebellum.util import subj_path_search




template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)

time_points = [0, 4, 12, 24, 52]

# for file searching: file in a given week across different subjects
ref_subj = 'CU_2310'
subdir = 'MNISym_T1'
file_suffix = 'MNISym_T1_coreg_reslice.nii.gz'

thres = 1e-6


def world_indices(img):
    """
    Function to get indices (x,y,z) for world coordinates for an image
    """
    i, j, k = np.indices(img.shape)
    x,y,z = nt.affine_transform(i, j, k, img.affine)
    return x,y,z


def response_matrix_week(subj_path_dict,
                         x,y,z, # indices from world image
                         week, # which week this matrix is for
                         ):
    # initialize empty array
    week_subj_rows = []
    week_subj_ids = [] # extra check: store subj_id AFTER they are added to matrix
    
    for s_id, s_path in subj_path_dict.items():
        # let's do a try-except loop
        try:
            subj_img = nib.load(s_path)

            row = nt.sample_image(subj_img, 
                                  xm = x, ym = y, zm = z, # resample to template world indices
                                  interpolation = 1
                                  ).flatten() # store as row vector
        except Exception: # file path not exist; subj not added to s_id for that week
            print(f'path {s_path} not exist; skip')
            continue

        week_subj_rows.append(row) # voxels
        week_subj_ids.append(s_id) # subj_id in order of their voxels put in rows
    
    Y_w = np.array(week_subj_rows)
    week_subj_ids = np.array(week_subj_ids)
    

    return Y_w, week_subj_ids, week # returns week used



def Y_tensor(df, subj_path_dict, time_points = time_points, template_img=template_img):
    """
    Function to make tensor out of subj-voxel matrices, where each matrix is for a given week

    Inputs:
        matrices = list of matrices
        N_p: number of subjects
        N_t: number of time points
        P: number of voxels (use from response_matrix_week)
        In this tensor, only brain voxels, so number of voxels = total_voxels - voxels_removed
        df: dataframe containing all subjects being used in this tensor (e.g. all patients)
    """
    # initialize tensor with NaN

    num_voxels = np.prod(template_img.get_fdata().shape) # all images in same template space
    # number of zero voxels should be same for all weeks; get number of zero voxels from template image
    

    N_p = len(df.subj_id.unique()) # need to have a row for each subject (x-axis); if missing data, they will have NaN
    N_t = len(time_points)


    Y_tensor = np.full((N_p, N_t, num_voxels), np.nan)
    #Y_tensor = np.zeros((N_p, N_t, num_voxels))

    x,y,z = world_indices(template_img) # for making response matrices for each week

    subj_pos = {s: i for i, s in enumerate(df.subj_id.unique())}

    for idx, w in enumerate(time_points):
        Y_w, week_subjs, week = response_matrix_week(subj_path_dict[idx],
                                                                 x,y,z,
                                                                 w, # returned as-is
                                                                 )
        subj_idx = [subj_pos[s] for s in week_subjs] # position to place each subject's voxels in
        Y_tensor[subj_idx, idx, :] = Y_w # each subject-week row placed in subj-week row in tensor

    return Y_tensor, num_voxels


def clean_tensor(Y, thres = 1e-6):
    """
    removes voxels from array that are below a certain threshold

    for all voxels, takes the sum of each col (voxel has own col); is sum <= thres, remove col
    """

    thres = 1e-6
    sums = np.nansum(Y, axis=(0, 1))
    zero_mask = (sums <= thres) 
    Y = Y[:, :, ~zero_mask]

    # just need indices (col values) - get first array from np.where
    zero_idx = np.where(zero_mask)[0] # zero voxels
    brain_idx = np.where(~zero_mask)[0] # voxels not removed (in-brain voxels)
    
    
    return Y, zero_idx, brain_idx # return cols with removed voxels and in-brain voxels


# will need to use clean_tensor before putting in dataframe


# SHOULD USE THE SAME N_t EVERYWHERE - just have it in the mian fcn

# make a dataframe for each voxel
def voxel_dataframe(Y, subjs, time_points):
    """
    Makes a dataframe for each voxel, where cols are:
    subj, week, y = voxel
    
    Y is matrix (subj, week) for a given voxel
    """
    # for this function, pretend we have all the information we need

    df = pd.DataFrame(data = Y, index = subjs,  columns = time_points)
    df.index.name = 'subj'

    df = df.reset_index()

    df = df.melt(id_vars = 'subj', value_vars = time_points, var_name = 'Week', value_name = 'y')

    return df

# even better:
# make a tensor filled with NaN for (subjects, voxels, weeks)
# need to check how this tensor is being built - is it correct?


# call to make the dataframe + run lme
def main(subj_path_dict, df, time_points = time_points):
    """
    function to perform lme; calls above (prerequisite) functions
    """
    # get the tensor - that contains all the data
    Y, num_voxels = Y_tensor(df, subj_path_dict)

    # clean tensor
    Y, _, brain_idx = clean_tensor(Y)

    # initialize B to store coefficients. shape = (week, voxels)
    N_t = len(time_points)
    B = np.zeros((N_t, num_voxels))

    # get dataframe for each voxel
    subjs = df.subj_id.unique() # for df; make sure not array

    betas = []

    for v in range(Y.shape[-1]): # iterate over voxels, so last dim
        V = Y[:,:,v] # (subj, week) matrix for that voxel
        # this gets: for each voxel, the matrix (subj, week)
        voxel_df = voxel_dataframe(V, subjs, time_points)

        # drop NaN rows in dataframe
        voxel_df.dropna(axis = 0, subset = ['y'], inplace = True, ignore_index = True)

        model = smf.mixedlm('y~Week', data = voxel_df, groups = 'subj').fit()

        # store betas in a list
        betas.append(model.fe_params.to_numpy()) # add each voxel's betas to a list
    
    # make a numpy array of betas
    betas = np.array(betas) # shape = (brain_voxels, weeks)
    betas = betas.T # shape = (weeks, brain_voxels)

    # now, populate B with betas (only with in-brain voxel indices)
    for i, idx in enumerate(brain_idx):
        # indexing is like:
        # brain_idx is the index in B matrix (which has col for ALL voxels)
        # i has index for betas
        # want to populate in-brain voxel cols in B with betas (coefs)
        # so first col in betas corresponds to the first in-brain voxel (so that brain_idx in B)
        
        # out-of-brain voxels do not appear in betas; left out (as zero)

        B[:,idx] = betas[:,i]
    
    return betas, B


# this is another function - to save each week image

    # save betas to array: each voxel gets its own column for k = 5 weeks
        # also need to populate with zeroes - use zero_mask to get these

        # populate B for that voxel's column:
        # for each voxel, do this

    

    # run lme for each dataframe

    # save betas

    # now we have our tensor. So each voxel is stored along the z-axis, so for each index on z-axis, get x-y matrix, make df, run lme, save results

    # each image put back in voxel coordiantes
