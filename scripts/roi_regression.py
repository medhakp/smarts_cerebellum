import numpy as np
import pandas as pd
import os
import smarts_cerebellum.globals as gl
import statsmodels.api as sm

def roi_regression(pred_df, subj_id, tract='CST_R', metric = 'FaMap'):
    pred_df = pred_df[pred_df.Object == tract]
    pred_df = pred_df[pred_df.subj_id == subj_id]
    pred_df = pred_df[pred_df.metric == metric]

    X = sm.add_constant(pred_df.week_num) # design matrix
    Y = pred_df['Mean'] # response matrix

    # at least 2 weeks for regression
    if len(Y)<2:
        return None

    model = sm.OLS(Y, X).fit()


    # save to dataframe
    results = pd.DataFrame({
        'subj_id': subj_id,
        'metric': metric,
        'tract': tract,
        'beta_0': [model.params.iloc[0]],
        'beta_1': [model.params.iloc[1]]
    })

    return results


if __name__ == '__main__':
    pred_df = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'JHU_MNI_DTI.tsv'), sep = '\t', low_memory = False) # warning: 2 diff dtypes

    tracts = ['CST_L', 'CST_R', 'SCP_L', 'SCP_R','MCP_L', 'MCP_R', 'ICP_L', 'ICP_R']
    metric = 'FaMap'

    results = []
    for tract in tracts:
        for subj in pred_df.subj_id.unique():
            result = roi_regression(pred_df, subj_id = subj, tract = tract, metric = metric)
            if result is not None:
                results.append(result)
    all_results = pd.concat(results, ignore_index = True)
    all_results.to_csv(os.path.join(gl.baseDir, 'DTI', 'regression_DTI.tsv'), sep = '\t')