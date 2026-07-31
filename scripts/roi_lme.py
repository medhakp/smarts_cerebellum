import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import smarts_cerebellum.globals as gl
from smarts_cerebellum import predictors_df as pred_df


space = 'MNISymC'

weeks = ['Week[T.4]', 'Week[T.12]', 'Week[T.24]', 'Week[T.52]']

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
        'week': model.fe_params.index, # use re string search to get week num later
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

def week_betas(df, regionnames, weeks = weeks):
    for regionname in regionnames:
        intercept_beta = df[(df.week == 'Intercept') & (df.regionname == regionname)]['beta'].iloc[0]
        df.loc[(df.week == 'Intercept') & (df.regionname == regionname), 'week_beta'] = intercept_beta

        for week in weeks:
            week_beta = df[(df.week == f'{week}') & (df.regionname == regionname)]['beta'].iloc[0]

            summed_beta = intercept_beta + week_beta
            df.loc[(df.week == week) & (df.regionname == regionname), 'week_beta'] = summed_beta
    return df

# run lme in rois
def run_lme(y_df, region):

    y_df.rename(columns = {'mean': 'y'},inplace = True)
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]
    y_df = y_df[y_df.regionname == region]
    y_df = y_df.reset_index(drop = True)

    model = smf.mixedlm('y~Week', data = y_df, groups = 'subj_id').fit(maxiter = 400)

    results = _results_df(model)
    results['regionname'] = region

    return results



def lme_results(group,
                p_df,
                folder,
                segment,
                atlas_space = None,
                atlas = None,
                maps = None,
                label_image = None,
                region_names = None,
                rois = None,
                space = space):
        
        dfs = []
        y_df = pred_df.response_df(p_df = p_df, folder = folder,segment = segment,
                            label_image = label_image, region_names = region_names,
                            atlas_space = atlas_space, atlas = atlas, maps = maps)
        regions = y_df.regionname.unique()
        for region in regions:
            df = run_lme(y_df, region = region)
            dfs.append(df)

        result = pd.concat(dfs, ignore_index = True)
        result = week_betas(result, regions) # calculate beta for each week (sum week beta value with intercept)

        lme_x_dict = {
            'Intercept': 0,
            'Week[T.4]': 4,
            'Week[T.12]': 12,
            'Week[T.24]': 24,
            'Week[T.52]': 52
        }

        result['Week'] = result['week'].map(lme_x_dict)
        result.to_csv(os.path.join(gl.baseDir, 'lme', f'{group}_{space}_{segment}_{rois}_lme.tsv'), sep = '\t')

# run for cerebellar atlas (e.g. Diedrichsen_2009 anatomical map)
if __name__ == '__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]

    # cerebellar atlas
    atlas_space = 'MNISym'
    atlas = 'Diedrichsen_2009'
    maps = 'atl-Anatom'

    # custom ROI
    roi_tract = 'CST'
    label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')
    region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']


    cereb_segments = ['T1', 'GM_mod']
    cereb_folders = [f'{space}_T1', f'{space}_GM']

    for c_segment, c_folder in zip(cereb_segments, cereb_folders):
        lme_results(group = 'patients', p_df = patients_df, segment = c_segment, folder = c_folder, 
                    atlas_space = atlas_space, atlas = atlas, maps = maps, rois = atlas)
        lme_results(group = 'controls', p_df = controls_df, segment = c_segment, folder = c_folder,
                    atlas_space = atlas_space, atlas = atlas, maps = maps, rois = atlas)
        
    
    tract_segments = ['T1', 'WM_mod']
    tract_folders = [f'{space}_T1', f'{space}_WM']
    for t_segment, t_folder in zip(tract_segments, tract_folders):
        lme_results(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, 
            label_image = label_image, region_names = region_names, rois = roi_tract)
        lme_results(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder,
                    label_image = label_image, region_names = region_names, rois = roi_tract)