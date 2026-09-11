import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import smarts_cerebellum.globals as gl
from smarts_cerebellum import predictors_df as pred_df


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

# run lme in rois
def run_lme(y_df, region):

    y_df.rename(columns = {'mean': 'y'},inplace = True)
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]
    y_df = y_df[y_df.regionname == region]
    y_df = y_df.reset_index(drop = True)

    model = smf.mixedlm('y~0 + Week', data = y_df, groups = 'subj_id').fit(maxiter = 400)

    results = _results_df(model)
    results['regionname'] = region

    return results



def lme_anat(group,
                p_df,
                folder,
                segment,
                atlas_space = None,
                atlas = None,
                maps = None,
                label_image = None,
                region_names = None,
                rois = None,
                space = None):
        
        # makes predictors dataframe
        
        results = []
        y_df = pred_df.response_df(p_df = p_df, folder = folder,segment = segment,
                            label_image = label_image, region_names = region_names,
                            atlas_space = atlas_space, atlas = atlas, maps = maps)
        regions = y_df.regionname.unique()

        for region in regions:
            result_df = run_lme(y_df, region = region)
            results.append(result_df)

        result = pd.concat(results, ignore_index = True)

        lme_x_dict = {
            'Week[0]': 0,
            'Week[4]': 4,
            'Week[12]': 12,
            'Week[24]': 24,
            'Week[52]': 52
        }

        result['Week'] = result['week'].map(lme_x_dict)
        result.to_csv(os.path.join(gl.baseDir, 'lme', f'{group}_{space}_{segment}_{rois}_lme.tsv'), sep = '\t')

def lme_roi(group, y_df, rois, imaging = 'DTI', metric = 'FaMap'):
    results = []
    y_df = y_df[y_df.regionname.isin(rois)]
    y_df = y_df[y_df.metric == metric]
    for roi in rois:
        result_df = run_lme(y_df, region = roi)
        results.append(result_df)
    result = pd.concat(results, ignore_index = True)
    lme_x_dict = {
            'Week[0]': 0,
            'Week[4]': 4,
            'Week[12]': 12,
            'Week[24]': 24,
            'Week[52]': 52
        }
    result['Week'] = result['week'].map(lme_x_dict)
    result.to_csv(os.path.join(gl.baseDir, imaging, f'{group}_lme_{imaging}.tsv'), sep = '\t')