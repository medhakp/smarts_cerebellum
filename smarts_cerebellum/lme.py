import numpy as np
import pandas as pd
import nibabel as nib
import nitools as nt
import os

import smarts_cerebellum.globals as gl
from smarts_cerebellum.util import subj_path_search


template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)

time_points = [0, 4, 12, 24, 52]




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
                    ref_subj = 'CU_2310',
                    #time_points = [0, 4, 12, 24, 52],
                    subdir = 'MNISym_T1',
                    file_suffix = 'MNISym_T1_coreg_reslice.nii.gz',
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

"""
Example for just getting the response dataframe:

import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum import lme

p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants_anat.tsv'), sep = '\t')
small_df = p_df.iloc[:11] # just try on a few subjects

response_df = lme.lme_dataframe(small_df) # runs in ~11.3s
response_df
"""