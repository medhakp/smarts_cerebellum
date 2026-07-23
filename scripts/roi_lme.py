import pandas as pd
import nibabel as nib
import os
import statsmodels.formula.api as smf
import smarts_cerebellum.globals as gl


def _results_df(model):

    fe = model.fe_params
    ci = model.conf_int().loc[fe.index]

    results = pd.DataFrame({
        'week': model.fe_params.index, # use re string search to get week num later
        'beta': model.fe_params.to_numpy(),
        'se': model.bse_fe.to_numpy(),
        'converged': model.converged,
        't-val': model.tvalues.loc[fe.index].to_numpy(),
        'p-val': model.pvalues.loc[fe.index].to_numpy(),
        'ci_lower': ci[0].to_numpy(),
        'ci_upper': ci[1].to_numpy(),
        'log_likelihood': model.llf
    })

    return results


# run lme in rois
def run_lme(y_df, region_name):

    y_df.rename(columns = {'mean': 'y'},inplace = True)
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]
    y_df = y_df[y_df.regionname == region_name]
    y_df = y_df.reset_index(drop = True)

    model = smf.mixedlm('y~Week', data = y_df, groups = 'subj_id').fit(maxiter = 400)

    results = _results_df(model)
    results['regionname'] = region_name
    return results
