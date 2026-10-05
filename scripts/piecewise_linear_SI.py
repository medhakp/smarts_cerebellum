import numpy as np
import pandas as pd
from scipy.optimize import minimize
import pandas as pd
import os
import smarts_cerebellum.globals as gl

"""
Following Jing's code to recreate the curvilinear relationship between x = strength (mvc_norm) and y = individuation (indiv_norm) (SI = strength-individuation)
"""

# following Jing's code

# parameters to be fit
def piecewise_lin_pred(x, params):
    x_star, b0, b1, b2 = params

    # this part is from piecewise_linfun(x,y,params) in Jing's code
    piecewise_fun = np.where(x<x_star, b0 + b1*x, b0 + (b1-b2)*x_star + b2*x) # x1: x<x_star (first eqn); x2: x>=x_star (second eqn)
    return piecewise_fun # vector: y values, [y_1, ..., y_n]

def piecewise_SSE(params, x, y):
    SSE = np.nansum((y - piecewise_lin_pred(x, params))**2)
    return SSE

# optimize parameters (b0 (intercept), b1, b2 (slope 1, slope 2, resp))
def piecewise_lin_fit(x,y):
    x = np.array(x)
    y = np.array(y)

    # use initial values given from Jing's code
    x_star = 0.5
    b0 = 0; b1 = 1; b2 = 0.1
    params = [x_star, b0, b1, b2]

    # optimize parameters: use minimization (Jing used fminsearch)
    result = minimize(fun = piecewise_SSE, # function to be minimized (minimize SSE)
             x0 = params, # initial guess
             args = (x, y), # args to fun
             method = 'Nelder-Mead', # MATLAB fminsearch(); minimization algorithm is Nelder-Mead

             # other params in Jing's code: max num iterations = 2000
             options = {'maxfev': 2000}
             )
    
    # piecewise function with optimized params (result.x)
    y_hat = piecewise_lin_pred(x, result.x)
    SS = np.nansum((y-y_hat)**2)
    TSS = np.nansum((y-np.nanmean(y))**2)

    results_df = pd.DataFrame([{
        'x_star': result.x[0], # inflection point
        'beta_0': result.x[1],
        'beta_1': result.x[2],
        'beta_2': result.x[3],
        'SS': SS,
        'TSS': TSS,
        'R2': 1-SS/TSS
    }])

    return results_df



def calculate_residuals(params_df, behav_df, x, y_obs):
    params = [params_df.iloc[0].x_star, params_df.iloc[0].beta_0, params_df.iloc[0].beta_1, params_df.iloc[0].beta_2]

    # calculate residuals
    res_df = pd.DataFrame({'subj_id': behav_df['subj_id'].values, 'Week': behav_df['Week'].values, 'x': np.array(x), 'y_obs': np.array(y_obs)}).dropna().copy()
    res_df['y_hat'] = piecewise_lin_pred(res_df['x'].values, params) # using optimized (minimized sum of squared error) parameters
    res_df['residuals'] = res_df['y_obs'] - res_df['y_hat']

    # fitted params
    res_df['x_star'] = params_df.iloc[0].x_star # inflection point
    res_df['beta_0'] = params_df.iloc[0].beta_0 # intercept
    res_df['beta_1'] = params_df.iloc[0].beta_1 # slope 1
    res_df['beta_2'] = params_df.iloc[0].beta_2 # slope 2

    return res_df

if __name__ == '__main__':

    # behavioural metrics
    behav = pd.read_csv(os.path.join(gl.baseDir, 'behavioural', 'summary_paretic.dat'), sep = '\t')
    behav.rename(columns = {'subj_name': 'subj_id', 'week': 'Week'}, inplace = True)
    behav['subj_id'] = behav['subj_id'].str.strip()
    behav.loc[behav['Week']==1, 'Week'] = 0

    # residuals per week
    dfs = []
    for week in gl.weeks:
        behav_week = behav[behav.Week == week]
        x = (behav_week['mvc_norm'])
        y = (behav_week['indiv_norm'])
        params_df = piecewise_lin_fit(x, y) # get fitted params, SSE, TSS, R^2
        residual_week = calculate_residuals(params_df = params_df, behav_df = behav_week, x = x, y_obs = y) # for a given week
        residual_week['Week'] = week
        dfs.append(residual_week)

    residuals_per_week = pd.concat(dfs)
    residuals_per_week.to_csv(os.path.join(gl.baseDir, 'behavioural', 'piecewise_SI_residuals_week.tsv'), sep = '\t', index = False)

    # residuals for all weeks (time-invariant)
    x = (behav['mvc_norm'])
    y = (behav['indiv_norm'])
    params_df = piecewise_lin_fit(x, y) # get fitted params, SSE, TSS, R^2
    residuals_time_invar = calculate_residuals(params_df = params_df, behav_df = behav, x = x, y_obs = y) # for a given week
    residuals_time_invar.to_csv(os.path.join(gl.baseDir, 'behavioural', 'piecewise_SI_residuals_time_invariant.tsv'), sep = '\t', index = False)