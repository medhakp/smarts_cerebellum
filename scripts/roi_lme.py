import pandas as pd
import nibabel as nib
import os
import statsmodels.formula.api as smf
import smarts_cerebellum.globals as gl
from smarts_cerebellum import predictors_df as pred_df


space = 'MNISymC'
segment = 'WM_mod' # modulated volumes
roi_tract = 'CST'
folder = f'{space}_WM'
label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')
region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']

regions = [f'left_{roi_tract}', f'right_{roi_tract}']

weeks = ['Week[T.4]', 'Week[T.12]', 'Week[T.24]', 'Week[T.52]']



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
def run_lme(y_df, region):

    y_df.rename(columns = {'mean': 'y'},inplace = True)
    y_df = y_df[['subj_id', 'Week', 'regionname', 'y']]
    y_df = y_df[y_df.regionname == region]
    y_df = y_df.reset_index(drop = True)

    model = smf.mixedlm('y~Week', data = y_df, groups = 'subj_id').fit(maxiter = 400)

    results = _results_df(model)
    results['regionname'] = region

    return results

def week_betas(df, regionnames = regions, weeks = weeks):
    for regionname in regionnames:
        intercept_beta = df[(df.week == 'Intercept') & (df.regionname == regionname)]['beta'].iloc[0]
        df.loc[(df.week == 'Intercept') & (df.regionname == regionname), 'week_beta'] = intercept_beta

        for week in weeks:
            week_beta = df[(df.week == f'{week}') & (df.regionname == regionname)]['beta'].iloc[0]

            summed_beta = intercept_beta + week_beta
            df.loc[(df.week == week) & (df.regionname == regionname), 'week_beta'] = summed_beta
    return df

def lme_results(group,
                p_df,
                folder = folder,
                segment = segment,
                label_image = label_image,
                region_names = region_names,
                regions = regions,
                roi_tract = roi_tract,
                space = space):
        
        dfs = []
        y_df = pred_df.response_df(p_df = p_df, folder = folder,segment = segment,
                            label_image = label_image, region_names = region_names)
        for region in regions:
            df = run_lme(y_df, region = region)
            dfs.append(df)

        result = pd.concat(dfs, ignore_index = True)
        result = week_betas(result) # calculate beta for each week (sum week beta value with intercept)
        result.to_csv(os.path.join(gl.baseDir, 'lme', f'{group}_{space}_{segment}_{roi_tract}_lme.tsv'), sep = '\t')



if __name__ == '__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]


    lme_results(group = 'patients', p_df = patients_df)
    lme_results(group = 'controls', p_df = controls_df)

