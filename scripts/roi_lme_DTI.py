import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_roi

def make_y_df():
    y_df = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'JHU_MNI_DTI_flip.tsv'), sep = '\t', low_memory = False) # warning: 2 diff dtypes
    controls = ['CUP_1001', 'CUP_1002', 'JHP_1001', 'JHP_1002', 'JHP_1004']
    y_df = y_df[~y_df.subj_id.isin(controls)]

    # some minor changes to make it match column names of anat
    y_df.rename(columns = {'Object': 'regionname', 'week': 'Week', 'Mean': 'mean'}, inplace = True) 

    return y_df

def assign_sides(lme_df):
    # assign LesionSide (note that lesion is flipped), ipsi/contra
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')

    lme_df['Week'] = lme_df['week'].str.extract(r'(\d+)') # get numeric values
    lme_df['region_bilat'] = lme_df['regionname'].str[:3]


    lme_df_patients = p_df[p_df.LesionSide == 'left ']['subj_id'].unique()
    right_patients = p_df[p_df.LesionSide == 'right']['subj_id'].unique()
    controls = p_df[p_df.LesionSide == 'none']['subj_id'].unique()

    lme_df.loc[lme_df.subj_id.isin(lme_df_patients), 'LesionSide'] = 'left '
    lme_df.loc[lme_df.subj_id.isin(right_patients), 'LesionSide'] = 'right'
    lme_df.loc[lme_df.subj_id.isin(controls), 'LesionSide'] = 'none'

    lme_df.loc[(lme_df.regionname.str[-1] == 'L'), 'side'] = 'contralesional'
    lme_df.loc[(lme_df.regionname.str[-1] == 'R'), 'side'] = 'ipsilesional'

    return lme_df


# DTI

y_df = make_y_df() # controls are excluded
y_df = y_df[y_df.metric == 'FaMap']
y_df = y_df.copy()

tracts = ['CST_L', 'CST_R', 'SCP_L', 'SCP_R','MCP_L', 'MCP_R', 'ICP_L', 'ICP_R']
metric = 'FaMap'

lme_roi(group = 'patients', y_df = y_df, rois = tracts)
lme_df = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'patients_lme_DTI.tsv'), sep = '\t')
lme_df = assign_sides(lme_df)

lme_df.to_csv(os.path.join(gl.baseDir, 'DTI', 'patients_lme_DTI.tsv'), sep = '\t', index = False)