import numpy as np
import nibabel as nib
import pandas as pd
import nitools as nt
import os
import re
import smarts_cerebellum.globals as gl
from pathlib import Path

def find_weeks(SID):

    # @Marco
    
    ### look into particpants.tsv and return weeks as numpy array of int e.g., (2, 4, )
    
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')

    # access only that subject's rows
    df_subj = p_df[p_df.subj_id == SID]
    weeks = []

    for week in df_subj['week']:
        weeks.append(week)

    return weeks


def week_path_search(reference_file, subj_id):
    """
    Finds files from other weeks that match the structure of reference file.

    Inputs:
        reference_file (str): path to a file whose path will be used as reference.
            That is, this file's path should have the structure that all other files from that week should have.
        weeks: weeks in filepath
    
    Outputs:
        week_paths (list[str]): paths to all files (including reference) that exist for weeks
        week_available (list[str]): weeks whose files exist
    """

    ref_path = str(reference_file)

    # find all places in path str with the week
    match = re.search(r'W(\d+)', ref_path)
    if not match:
        print(f'could not find week token in reference path for {ref_path}')
        return None
    
    ref_week_token = match.group(1) # return entire text that ws matched.

    weeks_paths = []
    weeks_available = []

    weeks = find_weeks(subj_id)

    for week in weeks:
        # search for every week's file

        # replace the week token(s) in reference image path with other tokens for new week path
        #week_path = ref_path.replace(ref_week_token, f'W{week}')

        week_path = re.sub(rf'W{ref_week_token}(?!\d)', f'W{week}', ref_path)

        # this should be dead code
        if not Path(week_path).exists():
            print(f'skipping W{week}')
            continue

        weeks_paths.append(week_path)
        weeks_available.append(week) # add weeks as integers

    return weeks_paths, weeks_available


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


def run_regression(p_df,
                   space   = 'MNISym',
                   segment = None,
                   ):
    
    p_df = p_df.sort_values("week").groupby("subj_id", as_index=False).first()
    
    subj_ids = p_df.subj_id

    for subj in subj_ids:

        refT1   = (p_df.loc[(p_df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        ref_img = f'{gl.baseDir}/{space}_{segment}/{subj}/{subj}_{refT1}_{space}_{segment}_coreg_reslice.nii.gz'

        p_paths, p_weeks = week_path_search(refT1, subj)

        if len(p_weeks)<2:
            continue

        intercept_img, slope_img = regression_week(ref_img, p_paths, p_weeks)

        nib.save(intercept_img, f'{gl.baseDir}/regression/{subj}_{space}_{segment}_intercept.nii.gz')
        nib.save(slope_img, f'{gl.baseDir}/regression/{subj}_{space}_{segment}_slope.nii.gz')



if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'))
    segments = ['T1', 'WM', 'GM', 'CSF']
    for segment in segments:
        run_regression(p_df, segment=segment)