import numpy as np
import pandas as pd
from scripts.roi_lme import run_lme, week_betas

regions = ['region1']
weeks = ['Week[T.4]', 'Week[T.12]', 'Week[T.24]', 'Week[T.52]']

# make a predictions dataframe of simulated data: full data, then we can remove some data, etc; it should fit into our present lme function in the place of the actual predictor's dataframe

"""
y = mean (renamed, so put mean in df)
y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]

"""

# 1. make a predictions dataframe of simulated data

# make df
def y_sim(N_p = 20,
             sim_weeks = [0,4,12,24,52],
             sc = 12,
             seed = 13):

    N_t = len(sim_weeks)
    y0 = np.zeros((N_p, N_t)) + np.array(sim_weeks)
    np.random.seed(seed)
    y_add = y0 + np.random.rand(N_p)[:, None] * sc

    df_add = pd.DataFrame(data=y_add, columns=sim_weeks)
    df_add['subj_id'] = np.arange(N_p) + 100
    df_add = pd.melt(df_add, id_vars='subj_id', value_vars=sim_weeks, var_name='Week', value_name='mean')
    df_add['regionname'] = 'region1'
    return df_add

# option to remove some data at random
def y_kill(y_df, size = 20):
     kill = np.random.randint(low = 0, high = 65, size = size)
     df_kill = y_df.drop(index = kill)
     return df_kill


# 2. run in lme_results with simulated df (just remove some args for pred_df fcn, don't save to csv)

def lme_results(y_df,
                regions = regions):
        
        dfs = []
        # put in your own y_df
        #y_df = y_df_sim()
        for region in regions:
            df = run_lme(y_df, region = region)
            dfs.append(df)

        result = pd.concat(dfs, ignore_index = True)
        result = week_betas(result, weeks = weeks, regionnames = regions)
        lme_x_dict = {
            'Intercept': 0,
            'Week[T.4]': 4,
            'Week[T.12]': 12,
            'Week[T.24]': 24,
            'Week[T.52]': 52
        }

        result['Week'] = result['week'].map(lme_x_dict)
        return result