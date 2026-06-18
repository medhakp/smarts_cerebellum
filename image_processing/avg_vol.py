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

#______________________________
# helper functions

def sufficient_weeks(subj_id, subpath, tissue):

    tissue_dict = {
        'gm': 'c1',
        'wm': 'c2',
        'csf': 'c3'
    }

    weeks = np.array([0,4,12,24,52])

    p_weeks = []
    for week in weeks:
        #week_path = f'{anat_dir}/{subj_id}/W{week}/wm_results/{subj_id}_W{week}_T1_wm_vol.nii'
        #week_path = week_path
        #week_path = f'{anat_dir}/{subj_id}/W{week}/c2{subj_id}_W{week}_T1.nii' # fix

        # e.g. if in cerebellar_alignment dir
        if not subpath == None:
            base_path =  f'{anat_dir}/{subj_id}/{subpath}/W{week}'
        else:
            base_path =  f'{anat_dir}/{subj_id}/W{week}'

        if not tissue==None:
            week_path = f'{base_path}/{tissue_dict[tissue]}{subj_id}_W{week}_T1.nii'
        else:
            week_path = f'{base_path}/{subj_id}_W{week}_T1.nii'


        # skip over missed measurement weeks.
        if not os.path.exists(week_path):
            continue

        p_weeks.append(week)
    
    if len(p_weeks) == 1: # only one measurement week available
        return None # exit function (skip subject)    
    
    return p_weeks


# this entire loop could probably be its own fucntion.
def response_matrix(Y, 
                    x, y, z, 
                    tissue,
                    weeks, subj_id, subpath):
    
    tissue_dict = {
        'gm': 'c1',
        'wm': 'c2',
        'csf': 'c3'
    }

    for week in weeks: # resample ALL weeks, including the reference week
        #week_path = f'{anat_dir}/{subj_id}/W{week}/wm_results/{subj_id}_W{week}_T1_wm_vol.nii'
        #week_path = week_path
        
        #__________________________________________
        # find week image if exists
        if not subpath == None:
            base_path =  f'{anat_dir}/{subj_id}/{subpath}/W{week}'
        else:
            base_path =  f'{anat_dir}/{subj_id}/W{week}'

        if not tissue==None:
            week_path = f'{base_path}/{tissue_dict[tissue]}{subj_id}_W{week}_T1.nii'
        else:
            week_path = f'{base_path}/{subj_id}_W{week}_T1.nii'

        # skip over missed measurement weeks.
        if not os.path.exists(week_path):
            continue

        week_img = nib.load(week_path)
        print(f'on week {week} for {subj_id}')
        #__________________________________________

        

        # dummy variable for weeks (code as 0, ..., 4)
        week_dict = {
            '0': 0,
            '4': 1,
            '12': 2,
            '24': 3,
            '52': 4
        }

    
        # resample each week's image so that voxels are exactly on top of reference week voxels; add to response matrix as row vector
        Y[week_dict[str(week)],:] = nt.sample_image(week_img, # response matrix
                                xm=x, ym = y, zm = z, # world coordinates
                                interpolation = 1 # using trilinear resampling
                                ).flatten() # need to put each week as a row
        
        # now we have Y as a k by p matrix, where k is the number of weeks. 
        # 
    return Y 

#_____________________

# add input: type of file (e.g. native, tissue_resliced, etc.)
def avg_vol(subj_id, 
            reference_img, # reference anatomical
            #week_path, # path to week image
            results_path,
            image_suffix,
            subpath = None, # specify subfolder
            input_suffix = None, # suffix for input image; MUST begin with '_'
            tissue=None):
    """
    Inputs:
    updated again
    anat dir: participants file OR [(subj, week) and call it inside a loop].
    Reference img (inside the Jupyter notebook loop for reading off the info file)
    #week_path (path for each week's image), results_path (store results)
    results path: directory to store results
    subpath: path with the images, usually same as the reference image's parent folder
    image suffix: suffix with which to save the slope and intercept images
        suggested: <image_type>_<space> where 'image_type' is "anat", "wm", "gm", etc; 'space' is native or template (<template_name>)
    input_suffix: suffix for input image, if applicable (default = None) - if supplying, must being with "_"

    Everything is done in the reference image. So this function will (...) (resample voxels in other weeks so that they are aligned with the reference, and perform multiple linear regression)

    Returns B_hat coefficient matrix (for more flexibility in other possible operations)
    
    """

    # file prefix encoding (based on SPM segmentation notation)
    tissue_dict = {
        'gm': 'c1',
        'wm': 'c2',
        'csf': 'c3'
    }

    img0 = nib.load(reference_img)

    # later fix: option to reduce to only wtihin-brain voxels
    
    # transform into world coordinates
    i, j, k = np.indices(img0.shape) # matrix indices for premult by affine
    x,y,z = nt.affine_transform(i, j, k, img0.affine)

    # all possible weeks.
    weeks = np.array([0,4,12,24,52]) # read from file, use file reading function maybe
    
    p_weeks = sufficient_weeks(subj_id, subpath, tissue)


    Y_empty = np.zeros((len(p_weeks), np.prod(img0.shape))) # initialize Y (shape = (k by p)) array, where k = number of weeks available

    Y = response_matrix(Y_empty,
                        x,y,z,
                        tissue,
                        weeks, subj_id, subpath)
    
    # design matrix
    num_weeks = len(p_weeks)
    X = [np.ones(shape = (num_weeks)), p_weeks]
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

    nib.save(intercept_img, f'{results_path}/{subj_id}_intercept_{image_suffix}.nii.gz') # specify file name
    nib.save(slope_img, f'{results_path}/{subj_id}_slope_{image_suffix}.nii.gz')

    return B_hat