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

# parallel jobs (for model fit over many voxels)
from joblib import Parallel, delayed

# catch exceptions/warnings from statsmodels
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning # convergence failure

import smarts_cerebellum.globals as gl
from smarts_cerebellum.util import subj_path_search



# function macros
template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)

time_points = [0, 4, 12, 24, 52]

thres = 1e-6


def make_week_dicts(df,
                    ref_subj,
                    subdir,
                    file_suffix,
                    ):
    """
    Make dictionaries for all weeks (time points)

    Returns LIST of dictionaries
    """
    dictionaries = []
    for week in time_points:
        ref_search_path = os.path.join(gl.baseDir, subdir, ref_subj, f'{ref_subj}_W{week}_{file_suffix}')
        paths, subjs = subj_path_search(ref_search_path, ref_subj, week, df)
        dictionaries.append(dict(zip(subjs, paths)))
    return dictionaries


def world_indices(img):
    """
    Function to get indices (x,y,z) for world coordinates for an image
    """
    i, j, k = np.indices(img.shape)
    x,y,z = nt.affine_transform(i, j, k, img.affine)
    return x,y,z, i, j, k


def response_matrix_week(subj_path_dict_idx,
                         x,y,z, # indices from world image
                         week, # which week this matrix is for
                         ):
    # initialize empty array
    week_subj_rows = []
    week_subj_ids = [] # extra check: store subj_id AFTER they are added to matrix
    
    for s_id, s_path in subj_path_dict_idx.items():
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

    x,y,z, i, j, k = world_indices(template_img) # for making response matrices for each week

    subj_pos = {s: i for i, s in enumerate(df.subj_id.unique())}

    for idx, w in enumerate(time_points):
        Y_w, week_subjs, week = response_matrix_week(subj_path_dict[idx],
                                                                 x,y,z,
                                                                 w, # returned as-is
                                                                 )
        subj_idx = [subj_pos[s] for s in week_subjs] # position to place each subject's voxels in
        Y_tensor[subj_idx, idx, :] = Y_w # each subject-week row placed in subj-week row in tensor

    return Y_tensor, num_voxels, i, j, k

# make a tensor filled with NaN for (subjects, voxels, weeks)
# need to check how this tensor is being built - is it correct?

def clean_tensor(Y, thres = thres):
    """
    removes voxels from array that are below a certain threshold

    for all voxels, takes the sum of each col (voxel has own col); is sum <= thres, remove col
    """
    
    # voxels (axis = 2) whose sum is <=thres
    sums = np.nansum(Y, axis=(0, 1))

    zero_mask = (sums <= thres) #| nan_cols
    #nan_mask = nan_cols

    # clean axis 2 (out-of-brain voxels)
    Y = Y[:, :, ~zero_mask]

    # just need indices (col values) - get first array from np.where
    zero_idx2 = np.where(zero_mask)[0] # zero voxels
    brain_idx2 = np.where(~zero_mask)[0] # voxels not removed (in-brain voxels)
    
    # returning only removed columns (voxels), since need these to populate B later
    return Y, zero_idx2, brain_idx2 # return cols with removed voxels and in-brain voxels


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



##%%
def nifti_image(A, i, j, k, week_num, template_img = template_img):
    """
    Function to make image (one per week) from matrix A
    NOTE: week_num is relative position of week (e.g. 0, 1, 2, ...) NOT week point (not 0, 4, 12, ...) - use enumerate indices
    """

    # initialize empty array
    img_arr = np.zeros(template_img.shape)
    iv = i.flatten()
    jv = j.flatten()
    kv = k.flatten()

    # get col of B from that week and populate along voxel coord indices
    img_arr[iv, jv, kv] = A[week_num,:] # populate indices with each row - each week has a flattened vector stored in rows.

    nifti_img = nib.Nifti1Image(img_arr, template_img.affine)
    return nifti_img


# make binary mask for convergence

# putting this in its own function to run in parallel
def voxel_fit(v, Y, subjs):

    V = Y[:,:,v] # (subj, week) matrix for that voxel

    voxel_df = voxel_dataframe(V, subjs, time_points)
    voxel_df.dropna(axis = 0, subset = ['y'], inplace = True, ignore_index = True)


    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('error', category = ConvergenceWarning)
            model = smf.mixedlm('y~Week', data = voxel_df, groups = 'subj').fit(maxiter = 400)

        return model.fe_params.to_numpy(), {'voxel': v, 'converged': True} # converged
    
    except Exception as e:
        return model.fe_params.to_numpy(), {'voxel': v, 'converged': False, 'error': str(e)}



##%%
# call to make the dataframe + run lme
def main(subj_path_dict, df,
          results_path, prefix, # for image name when saving
          time_points = time_points):
    """
    function to perform lme; calls above (prerequisite) functions

    prefix: e.g. MNISymC_T1 (space_segment)
    """
    # get the tensor - that contains all the data
    Y, num_voxels, i, j, k = Y_tensor(df, subj_path_dict)

    # clean tensor
    Y, _, brain_idx = clean_tensor(Y)

    # initialize B to store coefficients. shape = (week, voxels)
    N_t = len(time_points)
    B = np.zeros((N_t, num_voxels)) # image of fe
    binary_mask = np.zeros((N_t, num_voxels)) # binary mask

    # get dataframe for each voxel
    subjs = df.subj_id.unique()

    # run voxel-wise lme fit in parallel
    results = Parallel(n_jobs = 8)(
        delayed(voxel_fit)(v, Y, subjs) for v in range(Y.shape[-1])
    ) # returns betas for k = 5 weeks for each voxel


    betas_list, status_list = zip(*results)

    betas = np.column_stack(betas_list) # (5, p = num_in_brain_voxels))
    
    # make a numpy array of betas
    betas = np.array(betas) # shape = (brain_voxels, weeks)
    #betas = betas.T # shape = (weeks, brain_voxels)

    # now, populate B with betas (only with in-brain voxel indices)
    for a, idx in enumerate(brain_idx):
        # only populate indices with those voxel cols in brain - otherwise, leave zero
        B[:,idx] = betas[:,a]
        # each week is stored in a row in B, where B.shape = (5 weeks, P voxels) (P = ALL voxels, incl. out-of-brain)

        # make binary mask: if voxel in status_list[v] (dict, v^th in list) has converge = False, put 0 in that binary mask's column
        voxel_dict = status_list[a] # (convergence status) dictionary for that voxel
        if voxel_dict['converged'] == True:
            binary_mask[:,idx] = 1 # if converged, fill that voxel's col with ones
        else: # this part not necessary; matrix already initialized wtih zeroes
            binary_mask[:,idx] = 0

    beta_images = []
    mask_images = []

    for b, beta_week in enumerate(time_points): # b^th time point (week)

        # make Nifti1Image from each of B, binary_mask (for each week - fcn handles this)
        beta_img = nifti_image(B, i, j, k, week_num = b) # nifti_image returns one function per week
        mask_img = nifti_image(binary_mask, i, j, k, week_num = b)

        beta_images.append(beta_img) # list of Nifti1Images
        mask_images.append(mask_img)

        nib.save(beta_img, f'{results_path}/{prefix}_W{beta_week}_lme_beta.nii.gz')
        nib.save(mask_img, f'{results_path}/{prefix}_W{beta_week}_lme_conv_mask.nii.gz')
    
    return betas, B, beta_images, binary_mask, mask_images, status_list
