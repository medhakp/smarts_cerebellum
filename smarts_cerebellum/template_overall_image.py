"""
Get the overall image for images normalized to a specific template.

This is ONLY for use in a group or template space.

for now, only for use in regression slopes
"""

import numpy as np
import nibabel as nib
from pathlib import Path
import smarts_cerebellum.globals as gl
from smarts_cerebellum import mirror_lesion

base_dir = gl.baseDir

def mean_image_right(df, suffix, template_img):
    """
    @Authors: Marco,

    only for use in regression slopes for now

    slope image searched for as {subj_dir}/{subj}_{suffix}_slope.nii.gz
        where subdir is smarts_cerebellum/Regression/subj
    """
    counter = 0
    
    # empty array in the shape of the slope image
    slope = np.zeros((template_img.get_fdata()).shape)

    for subj in df.subj_id.unique():
        
        subj_dir = f'{base_dir}/Regression/{subj}'
        subj_slope = f'{subj_dir}/{subj}_{suffix}_slope.nii.gz'

        if not Path(subj_slope).exists():
            print(f'skipped {subj}')
            continue

        subj_slope_img = nib.load(subj_slope)

        subj_df = df[df.subj_id == subj]

        if (subj_df.iloc[0]['LesionSide']).strip() == 'left':
            # flip slope
            subj_slope_img = mirror_lesion.FlipLR(subj_slope_img)

        
        subj_slope_arr = subj_slope_img.get_fdata()


        # add each image to the overall slope image
        slope +=subj_slope_arr
        counter +=1 # number of slope matrices used
        
    # average
    slope = slope/counter

    return slope


def median_image_right(df, suffix, template_img):
    """
    @Authors: Marco,

    only for use in regression slopes for now
    """

    arrays = [] # tuple of (slope) tensors
    
    # empty array in the shape of the slope image
    slope = np.zeros((template_img.get_fdata()).shape)

    for subj in df.subj_id.unique():
        
        subj_dir = f'{base_dir}/Regression/{subj}'
        subj_slope = f'{subj_dir}/{subj}_{suffix}_slope.nii.gz'

        if not Path(subj_slope).exists():
            print(f'skipped {subj}')
            continue

        subj_slope_img = nib.load(subj_slope)

        subj_df = df[df.subj_id == subj]

        if (subj_df.iloc[0]['LesionSide']).strip() == 'left':
            # flip slope
            subj_slope_img = mirror_lesion.FlipLR(subj_slope_img)
            
        arrays.append(subj_slope_img.get_fdata())
    
    # stack arrays to get median
    slope = np.median(np.stack(arrays, axis = 0), axis = 0)
    return slope