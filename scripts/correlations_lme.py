# lme to predict the amount of cerbeellar degeneartion at time X based on CST degeneration at week Y; this is in-place of a correlation matrix (since we have missing data)

"""
Think about this: can we do a correlation matrix between lme betas?
Well the first thing to look at for this would be if our lme is even "good"

If we do another lme here, our model would be:
"""

# we can probably use predictors_df to build our predictors dataframe; we will have dataframes for each cerebellar ROI and tract ROI; then, we can concat them here
"""
Our dataframe should look like:
cols = subj, week, roi, value
And we want to use CST ROIs to predict cerebellar ROI, so when we call for the model, we should have a dataframe that's one particular cerebellar_ROI-week and for one particular CST ROI, all weeks

So if we have 32 cerebellar ROIs, each will have 5 weeks, times 2 CST ROIs for each ROI-week --> in total, 320 LME models (outputs)
"""

import pandas as pd
import os
import statsmodels.formula.api as smf
from smarts_cerebellum import predictors_df as pred_df
import smarts_cerebellum.globals as gl

#   1. get dataframes: cerebellar ROIs, CST
# --> for this, it would be better if we just summmarized all subjs into one dataframe; we can use this in our roi_lme and in this lme

# 2. model's response df: for each cerebellar ROI, for each week, make dataframe that has that ROI and (for one particular CST ROI) all weeks for CST ROI

# 3. run model with this df

# 4. get results of model - functions from roi_lme should work


def _se_vals(model):
    weeks = model.fe_params.index
    cov = model.cov_params()
    var_int = cov.loc['Intercept', 'Intercept']

    se_weeks = []
    for week in weeks:
        var_week = cov.loc[week, week]
        cov_int_week = cov.loc['Intercept', week]
        se_week = np.sqrt(var_int + var_week + (2*cov_int_week))
        se_weeks.append(se_week)

    se_vals = np.zeros(5,)
    se_vals[0] = np.sqrt(var_int)
    se_vals[1:] = se_weeks[1:]

    return se_vals


def _results_df(model):

    fe = model.fe_params
    ci = model.conf_int().loc[fe.index]
    se_vals = _se_vals(model)

    results = pd.DataFrame({
        'week': model.fe_params.index,
        'beta': model.fe_params.to_numpy(),
        'bse': model.bse_fe.to_numpy(),
        'converged': model.converged,
        't-val': model.tvalues.loc[fe.index].to_numpy(),
        'p-val': model.pvalues.loc[fe.index].to_numpy(),
        'ci_lower': ci[0].to_numpy(),
        'ci_upper': ci[1].to_numpy(),
        'log_likelihood': model.llf,
        'se': se_vals
    })

    return results

def _week_betas(df, regionnames, weeks = weeks):
    for regionname in regionnames:
        intercept_beta = df[(df.week == 'Intercept') & (df.regionname == regionname)]['beta'].iloc[0]
        df.loc[(df.week == 'Intercept') & (df.regionname == regionname), 'week_beta'] = intercept_beta

        for week in weeks:
            week_beta = df[(df.week == f'{week}') & (df.regionname == regionname)]['beta'].iloc[0]

            summed_beta = intercept_beta + week_beta
            df.loc[(df.week == week) & (df.regionname == regionname), 'week_beta'] = summed_beta
    return df

def _predict_roi_df(response_df, predict_df):
    # this will give a dataframe for each response_roi-week, you have vlaues of all weeks for each pred_roi
    predictors_df = predict_df.rename(columns = {'regionname': 'pred_region', 'mean': 'pred_mean', 'Week': 'pred_week'})
    roi_df = response_df.merge(predictors_df, how = 'cross') # Cartesian product of response_df with predictoes_df, so each value of response_df has all values in predictors_df

    return roi_df


def run_lme(y_df, response_region, response_week, pred_region):
    y_df = y_df.rename(columns = {'mean': 'y'})
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y', 'pred_region', 'pred_week', 'pred_mean']]
    y_df = y_df[(y_df.regionname == response_region) & (y_df.Week  == response_week) & (y_df.pred_region == pred_region)]
    y_df = y_df.reset_index(drop = True)

    model = smf.mixedlm('y ~ C(pred_week) * pred_mean', data = y_df, groups = 'subj_id').fit(maxiter = 400)
    return model
    # model: y = roi-week --> y, predictors: amount of degeneration in roi at time - so week, roi --> C(pred_week)*pred_mean

def lme_results(group,
                p_df,
                folder,
                segment,
                atlas_space = None,
                atlas = None,
                maps = None,
                label_image = None,
                region_names = None,
                regions = None,
                rois = None,
                space = None):
        
        dfs = []

        # UPDATE NEEDED
        # THIS PART: NEED SEPARATE INPUTS FOR RESPONSE AND PREDICTORS DATAFRAMES - AVOID SUPER LONG INPUT LIST
        resp_df = pred_df.response_df(p_df = p_df, folder = folder,segment = segment,
                            label_image = label_image, region_names = region_names,
                            atlas_space = atlas_space, atlas = atlas, maps = maps)
        
        preds_df = pred_df.response_df(p_df = p_df, folder = folder,segment = segment,
                            label_image = label_image, region_names = region_names,
                            atlas_space = atlas_space, atlas = atlas, maps = maps)
        y_df = _predict_roi_df(response_df=resp_df, predict_df=preds_df)
        
        # UPDATE THIS PART
        regions = y_df.regionname.unique()
        for region in regions:
            df = run_lme(y_df, region = region)
            dfs.append(df)

        result = pd.concat(dfs, ignore_index = True)
        result = _week_betas(result, regions) # calculate beta for each week (sum week beta value with intercept)

        lme_x_dict = {
            'Intercept': 0,
            'Week[T.4]': 4,
            'Week[T.12]': 12,
            'Week[T.24]': 24,
            'Week[T.52]': 52
        }

        result['Week'] = result['week'].map(lme_x_dict)
        result.to_csv(os.path.join(gl.baseDir, 'lme', f'{group}_{space}_{segment}_{rois}_lme.tsv'), sep = '\t')

"""
So if we want to run this for each roi-week (response), we will have a model for each of these. We can collect all these models and concat them into a common df at the end
"""

