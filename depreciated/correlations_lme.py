import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import smarts_cerebellum.globals as gl
from smarts_cerebellum import predictors_df as pred_df

def _results_df(model):

    fe = model.fe_params
    ci = model.conf_int().loc[fe.index]
    #se_vals = _se_vals(model)

    results = pd.DataFrame({
        'week': model.fe_params.index, # use re string search to get week num later
        'beta': model.fe_params.to_numpy(),
        'bse': model.bse_fe.to_numpy(),
        'converged': model.converged,
        't-val': model.tvalues.loc[fe.index].to_numpy(),
        'p-val': model.pvalues.loc[fe.index].to_numpy(),
        'ci_lower': ci[0].to_numpy(),
        'ci_upper': ci[1].to_numpy(),
        'log_likelihood': model.llf,
        #'se': se_vals
    })

    return results

def _predict_roi_df(response_df, predict_df):
   predictors_df = predict_df.rename(columns = {'regionname': 'pred_region', 'mean': 'pred_mean', 'Week': 'pred_week'})
   roi_df = response_df.merge(predictors_df, on = 'subj_id', how = 'inner')
   roi_df = roi_df.rename(columns = {'mean': 'resp_mean', 'Week': 'resp_week', 'regionname': 'resp_region'})
   return roi_df


def run_lme(y_df):
    #models = {}
    results = []
    for pred_region in y_df.pred_region.unique():
        for resp_region in y_df.resp_region.unique():
            region_df = y_df[(y_df.pred_region == pred_region) & (y_df.resp_region == resp_region)]
            model = smf.mixedlm("mean~0 + C(Week)*C(pred_week)*pred_mean", data = region_df, groups = region_df.subj_id).fit(maxiter = 400)
            #models[(pred_region, resp_region)] = model

            # make dataframe for summarizing results
            result = _results_df(model)
            result['response_region'] = resp_region
            result['predictor_region'] = pred_region

            # get predictor, response weeks from model



            results.append(result)
    df = pd.concat(results, ignore_index = True)
    return df


def lme_main(group,
                p_df,
                atlas_space = None,

                response_folder = None,
                response_segment = None,
                response_label_image = None,
                response_region_names = None,
                response_atlas = None,
                response_maps = None,

                predict_folder = None,
                predict_segment = None,
                predict_label_image = None,
                predict_region_names = None,
                predict_atlas = None,
                predict_maps = None,
                ):
    response_df = pred_df.response_df(p_df = p_df,
                                      folder = response_folder,
                                      segment = response_segment,
                                      label_image = response_label_image,
                                      region_names = response_region_names,
                                      atlas_space = atlas_space,
                                      atlas = response_atlas,
                                      maps = response_maps)
    
    predict_df = pred_df.response_df(p_df = p_df,
                                    folder = predict_folder,
                                    segment = predict_segment,
                                    label_image = predict_label_image,
                                    region_names = predict_region_names,
                                    atlas_space = atlas_space,
                                    atlas = predict_atlas,
                                    maps = predict_maps)
    
    y_df = _predict_roi_df(response_df = response_df, predict_df = predict_df)

    # number of models = num_response_regions * num_predictor_regions
    results = run_lme(y_df)


    # store results in a dataframe; we can store all of the betas, or just the ones that we are interested in?
    # also, all the models will be in a common dataframe with a column that specifies the response and predictor tracts

