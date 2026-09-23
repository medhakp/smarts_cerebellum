import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import SUITPy as suit
import re
import smarts_cerebellum.globals as gl


# make predictors dataframe
#_______________________________
def _week_token(image_name):
    match = re.search(r'W(\d+)', image_name)
    week_val = match.group(1)
    return week_val

def _load_img_list(p_df, folder, subj, space, segment):

    p_df_s = p_df[p_df.subj_id==subj]

    LesionSide = p_df_s.LesionSide.iloc[0] #LesionSide = p_df_s.LesionSide.unique()
        
    imgs = []
    weeks = p_df_s.Week.unique()
    for _week in weeks:
        week = _week.strip()
        if LesionSide == 'left ':
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}_FlipLR.nii.gz')

        else:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}.nii.gz')
        
        if os.path.isfile(fname):
            imgs.append(fname)

    return imgs

def response_df(p_df,
                     folder = None,
                     space = 'MNISymC',
                     atlas_space = 'MNISymC', # if using atlas and maps, set MNISym, etc. Otherwise, default is same as space (MNISymC)
                     segment = 'T1',
                     stats = ['mean'],
                     label_image = None,
                     region_names = None,
                     atlas = None,
                     maps = None,
                     ):
    dfs = []

    subj_ids = p_df.subj_id.unique()
    # find subj-week images - _load_img_list does this
    for subj in subj_ids:
        imgs = _load_img_list(p_df, folder, subj, space, segment)
        if len(imgs) == 0:
            continue
        if not atlas == None:
            suit.fetch_atlas(atlas)
        df_subj = suit.summarize_data(images = imgs,
                                      space = atlas_space,
                                      stats = stats,
                                      atlas = atlas,
                                      maps = maps,
                                      label_image = label_image,
                                      region_names = region_names)
        df_subj['subj_id'] = subj
        dfs.append(df_subj)
    
    df = pd.concat(dfs, ignore_index = True)
    df = df[~df.subj_id.isin(gl.bad)]
    df['Week'] = df['image_name'].apply(_week_token) # weeks in image name
    
    return df
#_________________________________


# add fixed effects to dataframe
def _fe_results_df(model):

    fe = model.fe_params
    ci = model.conf_int().loc[fe.index]

    results = pd.DataFrame({
        'week': model.fe_params.index, # use re string search to get week num later
        'beta': model.fe_params.to_numpy(),
        'se': model.bse_fe.to_numpy(), # with y~0 + Week, bse is the se (beta value is the beta mean)
        'converged': model.converged,
        't-val': model.tvalues.loc[fe.index].to_numpy(),
        'p-val': model.pvalues.loc[fe.index].to_numpy(),
        'ci_lower': ci[0].to_numpy(),
        'ci_upper': ci[1].to_numpy(),
        'log_likelihood': model.llf,
    })

    return results

def _re_results_df(model):
    re_results = pd.DataFrame(model.random_effects).T
    #re_results.index.name = 'subj_id'
    re_results = re_results.reset_index()
    re_results = re_results.rename(columns = {"index": "subj_id", "subj_id": "random_intercept"})
    return re_results

# fixed and random effects - subj-week
def _results_df(model):
    fe_df = _fe_results_df(model) # fixed effects
    re_df = _re_results_df(model) # random effects

    fe_df = fe_df.copy()
    re_df = re_df.copy()

    # temp key to join the dataframes
    fe_df['_key'] = 1
    re_df['_key'] = 1
    
    results_df = fe_df.merge(re_df, on = '_key').drop(columns = '_key')
    return results_df

# fit lme model
def fit_lme(y_df, region):

    # predictors dataframe for relevant region
    y_df.rename(columns = {'mean': 'y'},inplace = True)
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]
    y_df = y_df[y_df.regionname == region]
    y_df = y_df.reset_index(drop = True)

    # fit model
    model = smf.mixedlm('y~0 + Week', data = y_df, groups = 'subj_id').fit(maxiter = 400)

    # add fitted model results in dataframe
    results = _results_df(model)
    results['regionname'] = region

    return results


# run the lme and save results in a dataframe
def lme_main(group,
                p_df = None,
                folder = None,
                segment = None,
                atlas_space = None,
                atlas = None,
                maps = None,
                label_image = None,
                region_names = None,
                roi = None,
                space = None,
                predictors_df = None):
        
        """
        predictors_df (Pandas dataframe): default is None
            If not provided, assumes images are being used. Will make the response df.
            If provided, will use that dataframe as the predictors dataframe.
        """
        if predictors_df is not None:
            # predictors dataframe provided - same treatment given to this that is given when making the predictors dataframe
            y_df = predictors_df
            y_df = y_df[~y_df.subj_id.isin(gl.bad)]
            y_df['Week'] = y_df['image_name'].apply(_week_token)
        else:
            # makes predictors dataframe
            y_df = response_df(p_df = p_df, folder = folder,segment = segment,
                                label_image = label_image, region_names = region_names,
                                atlas_space = atlas_space, atlas = atlas, maps = maps)
        
        # fit lme for each region
        results = []
        regions = y_df.regionname.unique()
        for region in regions:
            result_df = fit_lme(y_df, region = region)
            results.append(result_df)

        # save results in dataframe
        result = pd.concat(results, ignore_index = True)
        lme_x_dict = {
            'Week[0]': 0,
            'Week[4]': 4,
            'Week[12]': 12,
            'Week[24]': 24,
            'Week[52]': 52
        }
        result['Week'] = result['week'].map(lme_x_dict)
        result.to_csv(os.path.join(gl.baseDir, 'lme', f'{group}_{space}_{segment}_{roi}_lme.tsv'), sep = '\t')
