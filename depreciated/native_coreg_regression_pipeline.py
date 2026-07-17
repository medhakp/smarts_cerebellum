
"""
Pipeline for regression on images in native space, where images have been full-image coregistered to that subject's reference week image
"""

import pandas as pd

import nibabel as nib

import smarts_cerebellum.globals as gl
from scripts import regression

from pathlib import Path


# add this to globals
p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')


def regression_native_coreg(segment):

    tissue_dict = {
        'GM': 'c1',
        'WM': 'c2',
        'CSF': 'c3',
        'T1': '' # no file prefix for T1
    }

    for subj in p_df['subj_id'].unique():

        # find each subject's reference image, and run it through the regression
        refT1 = (p_df.loc[(p_df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        ref_img = f'{gl.baseDir}/anatomicals/{subj}/{refT1}/{tissue_dict[segment]}{subj}_{refT1}_T1.nii'

        print(f"Regression (native coreg) on {subj} with {segment} \n")

        intercept_img, slope_img = regression.perform_regression_week(subj_id = subj,
                            reference_img = ref_img
                            )
        

        # if images exist, save them
        if intercept_img is not None and slope_img is not None:
            results_path = f'{gl.baseDir}/Regression/{subj}'
            results_path = Path(results_path)

            # if directory does not exist, make it.
            # results_path.mkdir(parents = True) # exist_ok = True

            nib.save(intercept_img, f'{results_path}/{subj}_native_{segment}_coreg_intercept.nii.gz')
            nib.save(slope_img, f'{results_path}/{subj}_native_{segment}_coreg_slope.nii.gz')



regression_native_coreg('GM')

"""
# REGRESSION
regression_native_coreg('GM')
regression_native_coreg('WM')
regression_native_coreg('CSF')
regression_native_coreg('T1')
"""