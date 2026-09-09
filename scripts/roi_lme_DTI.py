import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_roi

# DTI
y_df = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'JHU_MNI_DTI.tsv'), sep = '\t', low_memory = False) # warning: 2 diff dtypes
controls = ['CUP_1001', 'CUP_1002', 'JHP_1001', 'JHP_1002', 'JHP_1004']
y_df = y_df[~y_df.subj_id.isin(controls)]

# some minor changes to make it match column names of anat
y_df.rename(columns = {'Object': 'regionname', 'week': 'Week', 'Mean': 'mean'}, inplace = True)

y_df = y_df[y_df.metric == 'FaMap']
y_df = y_df.copy()

tracts = ['CST_L', 'CST_R', 'SCP_L', 'SCP_R','MCP_L', 'MCP_R', 'ICP_L', 'ICP_R']
metric = 'FaMap'
lme_roi(group = 'patients', y_df = y_df, rois = tracts)