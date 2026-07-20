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
                     metric = 'slope',
                     ):
    """
    @Authors: Marco,

    Calculates mean image (where all lesions are on RH).
    """
    
    counter = 0

    mean_arr = np.zeros((template_img.get_fdata()).shape)

    for subj in group_df.subj_id.unique():
        subj_dir = os.path.join(gl.baseDir, search_dir, subj)

        if subj in left_lesion_df.subj_id.unique():
            subj_path = f'{subj_dir}/{subj}_{space}_{segment}_{metric}_FlipLR.nii.gz'
        else:
            subj_path = f'{subj_dir}/{subj}_{space}_{segment}_{metric}.nii.gz'

        if not Path(subj_path).exists():
            continue

        subj_img = nib.load(subj_path)

        subj_arr = subj_img.get_fdata()

        # add each image to the overall slope image
        mean_arr +=subj_arr
        counter +=1 # number of slope matrices used

    mean_arr = mean_arr/counter
    mean_img = nib.Nifti1Image(mean_arr, template_img.affine)
    means_dir = os.path.join(gl.baseDir, search_dir, 'means')
    nib.save(mean_img, f'{means_dir}/{group}_{space}_{segment}_{metric}_mean.nii')


def median_image_right( group,
                        group_df, 
                        left_lesion_df,
                        template_img,
                        search_dir = 'regression',
                        segment = 'T1',
                        space = 'MNISymC',
                        metric = 'slope',
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
            subj_path = f'{subj_dir}/{subj}_{space}_{segment}_{metric}_FlipLR.nii.gz'
        else:
            subj_path = f'{subj_dir}/{subj}_{space}_{segment}_{metric}.nii.gz'

        if not Path(subj_path).exists():
            continue

        subj_img = nib.load(subj_path)

        arrays.append(subj_img.get_fdata())
                
    # stack arrays to get median
    median_arr = np.median(np.stack(arrays, axis = 0), axis = 0)

    median_img = nib.Nifti1Image(median_arr, template_img.affine)
    medians_dir = os.path.join(gl.baseDir, search_dir, 'medians')
    nib.save(median_img, f'{medians_dir}/{group}_{space}_{segment}_{metric}_median.nii')





if __name__=='__main__':
    # MACROS
    template_path = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii')
    template_img = nib.load(template_path)

    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    left_lesion_df = p_df[p_df.LesionSide == 'left ']
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]

    segments = ['T1', 'WM', 'GM', 'CSF']
    for segment in segments:
        # patients: mean, median
        mean_image_right(group = 'patients', group_df = patients_df, left_lesion_df = left_lesion_df, template_img = template_img,
                         search_dir = 'regression', segment = segment, space = 'MNISymC', metric = 'slope')
        median_image_right(group = 'patients', group_df = patients_df, left_lesion_df = left_lesion_df, template_img = template_img,
                         search_dir = 'regression', segment = segment, space = 'MNISymC', metric = 'slope')
        
        # control: mean, median
        mean_image_right(group = 'controls', group_df = controls_df, left_lesion_df = left_lesion_df, template_img = template_img,
                         search_dir = 'regression', segment = segment, space = 'MNISymC', metric = 'slope')
        median_image_right(group = 'controls', group_df = controls_df, left_lesion_df = left_lesion_df, template_img = template_img,
                         search_dir = 'regression', segment = segment, space = 'MNISymC', metric = 'slope')