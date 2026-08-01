import pandas as pd
import numpy as np
import os
import statsmodels.formula.api as smf
import smarts_cerebellum.globals as gl
from smarts_cerebellum import predictors_df as pred_df


space = 'MNISymC'

weeks = ['Week[T.4]', 'Week[T.12]', 'Week[T.24]', 'Week[T.52]']


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
    return results_df, fe_df # temp return fe_df for the notebooks that we already have


# run lme in rois
def run_lme(y_df, region):

    y_df.rename(columns = {'mean': 'y'},inplace = True)
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]
    y_df = y_df[y_df.regionname == region]
    y_df = y_df.reset_index(drop = True)

    model = smf.mixedlm('y~0 + Week', data = y_df, groups = 'subj_id').fit(maxiter = 400)

    results, fe_df = _results_df(model)
    results['regionname'] = region
    fe_df['regionname'] = region

    return results, fe_df



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
        
        results = []
        fe_dfs = []
        y_df = pred_df.response_df(p_df = p_df, folder = folder,segment = segment,
                            label_image = label_image, region_names = region_names,
                            atlas_space = atlas_space, atlas = atlas, maps = maps)
        regions = y_df.regionname.unique()

        for region in regions:
            result_df, fe_df = run_lme(y_df, region = region)
            results.append(result_df)
            fe_dfs.append(fe_df)

        result = pd.concat(results, ignore_index = True)
        fe_result = pd.concat(fe_dfs, ignore_index = True)

        lme_x_dict = {
            'Week[0]': 0,
            'Week[4]': 4,
            'Week[12]': 12,
            'Week[24]': 24,
            'Week[52]': 52
        }

        result['Week'] = result['week'].map(lme_x_dict)
        result.to_csv(os.path.join(gl.baseDir, 'lme/results', f'{group}_{space}_{segment}_{rois}_lme.tsv'), sep = '\t')

        # TEMP SAVE FE DF SEPARATELY
        fe_result['Week'] = fe_result['week'].map(lme_x_dict)
        fe_result.to_csv(os.path.join(gl.baseDir, 'lme', f'{group}_{space}_{segment}_{rois}_lme.tsv'), sep = '\t') # temp; for what we alr have

# run for cerebellar atlas (e.g. Diedrichsen_2009 anatomical map)
if __name__ == '__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]

    # cerebellar atlas
    atlas_space = 'MNISym'
    atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'
    # atlas = 'Diedrichsen_2009'
    # maps = 'atl-Anatom'

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
        
    
    # tract_segments = ['T1', 'WM_mod']
    # tract_folders = [f'{space}_T1', f'{space}_WM']
    # for t_segment, t_folder in zip(tract_segments, tract_folders):
    #     lme_results(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, 
    #         label_image = label_image, region_names = region_names, rois = roi_tract)
    #     lme_results(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder,
    #                 label_image = label_image, region_names = region_names, rois = roi_tract)