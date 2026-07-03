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
                                  xm = x, ym = y, zm = z, # resample to template world indices - pass to fcn template world indices
                                  interpolation = 1
                                  ).flatten() # store as row vector
        except Exception: # file path not exist; subj not added to s_id for that week
            print(f'path {s_path} not exist; skip')
            continue

        week_subj_rows.append(row)
        week_subj_ids.append(s_id)
    
    Y_w = np.array(week_subj_rows)
    week_subj_ids = np.array(week_subj_ids)

    return Y_w,week_subj_ids, week # returns week used



def make_week_dataframe(
                   subj_path_dict, 
                   week, # which week this df is for
                   template_img):
    """
    makes dataframe out of each week's response matrix
    """
    x,y,z, = world_indices(template_img)

    Y_w, week_subjs, week = response_matrix_week(subj_path_dict,
                                           x,y,z,
                                           week # returns same week
                                           )
    
    template_arr = template_img.get_fdata()
    P = np.prod(template_arr.shape)


    df = pd.DataFrame(data = Y_w, 
                      columns = [f'v{i}' for i in range(P)]
                      )
    df.insert(0, 'Week', week) # add week as beginning col
    df.insert(0, 'Subj', week_subjs)

    return df


def make_week_dicts(df,
                    ref_subj = ref_subj,
                    subdir = subdir,
                    file_suffix = file_suffix,
                    ):
    """
    Make dictionaries for all weeks (time points)
    """
    dictionaries = []
    for week in time_points:
        ref_search_path = os.path.join(gl.baseDir, subdir, ref_subj, f'{ref_subj}_W{week}_{file_suffix}')
        paths, subjs = subj_path_search(ref_search_path, ref_subj, week, df)
        dictionaries.append(dict(zip(subjs, paths)))
    return dictionaries


def lme_dataframe(df,
                  template_img=template_img,
                  ):
    """
    Make full response dataframe (concatenate week dataframes)
    
    Inputs:
        df: subj_info df
    """
    # make subj-path dictionaries for all weeks
    subj_path_dictionaries = make_week_dicts(df)
    
    dfs = []
    for idx, t in enumerate(time_points):
        
        week_df = make_week_dataframe(subj_path_dict = subj_path_dictionaries[idx], # get i^th week's dictionary
                                      week = t,
                                      template_img = template_img,
                                      )
        dfs.append(week_df)

    Y_df = pd.concat(dfs, axis = 0, ignore_index = True)
    return Y_df

# save this dataframe

"""
Example for just getting the response dataframe:

import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum import lme

p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants_anat.tsv'), sep = '\t')
small_df = p_df.iloc[:11] # just try on a few subjects

lme_df = lme.lme_dataframe(small_df) # runs in ~11.3s
lme_df
"""

def brain_voxels_df(lme_df):
    """
    cleans dataframe: removes voxel columns where all voxels in that column are zero (removes out-of-brain voxels)
    """
    # get voxel columns
    voxel_cols = [v for v in lme_df.columns if v.startswith('v')]

    # convert to numpy - faster as pd
    lme_voxel_arr = lme_df[voxel_cols].values

    # get sums of each col and save those whose sum if zero
    sums = lme_voxel_arr.sum(axis = 0)
    zero_voxels = sums == 0
    zero_cols = np.array(voxel_cols)[zero_voxels]

    # return cleaned-up df
    lme_df = lme_df.drop(columns = zero_cols)
    return lme_df

def run_lme(lme_df):
    """
    Function to actually run the lme (voxel-wise); uses statsmodels mixedlm random intercept model
    """
    
    results = []
    results_df = []

    # get voxel columns from df
    voxel_cols = [v for v in lme_df.columns if v.startswith('v')]

    # run lme on each voxel individually
    for voxel in voxel_cols:
        voxel_df = lme_df[['Subj', 'Week', f'{voxel}']]

        # try running model and adding its results to a row;
        # except convergence fails, runtime error, etc.
        try:
            model = smf.mixedlm(f'{voxel}~Week', data = voxel_df, groups = 'Subj').fit()
            row={
                'voxel': voxel,

                'intercept': model.fe_params['Intercept'],
                'intercept_bse': model.bse_fe['Intercept'],
                'intercept_z': model.tvalues['Intercept'],
                'intercept_p': model.pvalues['Intercept'],

                'Week': model.fe_params['Week'],
                'Week_bse': model.bse_fe['Week'],
                'Week_z': model.tvalues['Week'],
                'Week_p': model.pvalues['Week'],

                'subj_var': model.params['Subj Var'],
                'subj_var_bse': model.bse['Subj Var'],
                'subj_var_z': model.tvalues['Subj Var'],
                'subj_var_p': model.pvalues['Subj Var'],

                'cov_re': model.cov_re.iloc[0,0], # only gets the intercept cov - intercept model
                'log_likelihood': model.llf,

                'intercept_ci_low': model.conf_int().loc['Intercept', 0],
                'intercept_ci_high': model.conf_int().loc['Intercept', 1],
                'Week_ci_low': model.conf_int().loc['Week', 0],
                'Week_ci_high': model.conf_int().loc['Week', 1],
                'subj_var_ci_low': model.conf_int().loc['Subj Var', 0],
                'subj_var_ci_high': model.conf_int().loc['Subj Var', 1],

                'converged': model.converged, # bool

                # successful run
                'exception_type': np.nan,
                'exception_message': np.nan
            }

        except Exception as e: # model fails: not converge or runtime error, etc
            row={
                'voxel': voxel,

                'intercept': np.nan,
                'intercept_bse': np.nan,
                'intercept_z': np.nan,
                'intercept_p': np.nan,

                'Week': np.nan,
                'Week_bse': np.nan,
                'Week_z': np.nan,
                'Week_p': np.nan,

                'subj_var': np.nan,
                'subj_var_bse': np.nan,
                'subj_var_z': np.nan,
                'subj_var_p': np.nan,

                'cov_re': np.nan,
                'log_likelihood': np.nan,

                'intercept_ci_low': np.nan,
                'intercept_ci_high': np.nan,
                'Week_ci_low': np.nan,
                'Week_ci_high': np.nan,
                'subj_var_ci_low': np.nan,
                'subj_var_ci_high': np.nan,

                'converged': model.converged, # bool

                # save type of exception: name, message
                'exception_type': type(e).__name__,
                'exception_message': str(e)

            }
        
        # add each row to list
        results.append(row)

    # make dataframe
    results_df = pd.DataFrame(results)
    return results_df
      
