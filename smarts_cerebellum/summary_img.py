import numpy as np
import pandas as pd
import nibabel as nib
from pathlib import Path
import os
import smarts_cerebellum.globals as gl


def mean_image_right(group,
                     group_df, 
                     left_lesion_df,
                     template_img,
                     search_dir = 'regression',
                     segment = 'T1',
                     space = 'MNISymC',
                     metric = '_slope',
                     week = None
                     ):
    """
    @Authors: Marco,

    Calculates mean image (where all lesions are on RH).
    """
    subj_paths = []

    counter = 0

    mean_arr = np.zeros((template_img.get_fdata()).shape)

    for subj in group_df.subj_id.unique():
        subj_dir = os.path.join(gl.baseDir, search_dir, subj)

        if subj in left_lesion_df.subj_id.unique():
            if week is not None:
                subj_path = f'{subj_dir}/{subj}_{week}_{space}_{segment}{metric}_FlipLR.nii.gz'
            else:
                subj_path = f'{subj_dir}/{subj}_{space}_{segment}{metric}_FlipLR.nii.gz'
        else:
            if week is not None:
                subj_path = f'{subj_dir}/{subj}_{week}_{space}_{segment}{metric}.nii.gz'
            else:
                subj_path = f'{subj_dir}/{subj}_{space}_{segment}{metric}.nii.gz'
        if not Path(subj_path).exists():
            continue
        
        subj_paths.append(subj_path)

        subj_img = nib.load(subj_path)

        subj_arr = subj_img.get_fdata()

        # add each image to the overall slope image
        mean_arr +=subj_arr
        counter +=1 # number of slope matrices used

    mean_arr = mean_arr/counter
    mean_img = nib.Nifti1Image(mean_arr, template_img.affine)
    means_dir = os.path.join(gl.baseDir, search_dir, 'means')
    
    if week is not None:
        nib.save(mean_img, f'{means_dir}/{group}_{week}_{space}_{segment}{metric}_mean.nii')
    else:
        nib.save(mean_img, f'{means_dir}/{group}_{space}_{segment}{metric}_mean.nii')
    return subj_paths


def median_image_right( group,
                        group_df, 
                        left_lesion_df,
                        template_img,
                        search_dir = 'regression',
                        segment = 'T1',
                        space = 'MNISymC',
                        metric = '_slope',
                       ):
    """
    @Authors: Marco,

    Calculates median image where all lesions are on RH.
    """
    
    arrays = []

    median_arr = np.zeros((template_img.get_fdata()).shape)

    for subj in group_df.subj_id.unique():
        subj_dir = os.path.join(gl.baseDir, search_dir, subj)

        if subj in left_lesion_df.subj_id.unique():
            subj_path = f'{subj_dir}/{subj}_{space}_{segment}{metric}_FlipLR.nii.gz'
        else:
            subj_path = f'{subj_dir}/{subj}_{space}_{segment}{metric}.nii.gz'

        if not Path(subj_path).exists():
            continue

        subj_img = nib.load(subj_path)

        arrays.append(subj_img.get_fdata())
                
    # stack arrays to get median
    median_arr = np.median(np.stack(arrays, axis = 0), axis = 0)

    median_img = nib.Nifti1Image(median_arr, template_img.affine)
    medians_dir = os.path.join(gl.baseDir, search_dir, 'medians')
    nib.save(median_img, f'{medians_dir}/{group}_{space}_{segment}{metric}_median.nii')

