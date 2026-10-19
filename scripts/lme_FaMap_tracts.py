import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main


if __name__ == '__main__':

    # CHANGE THIS
    roi_tract = 'MCP'
    
    # FaMap - images in MNISymC (template space)

    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    p_df = p_df[p_df.isPatient == 1]

    space = 'MNISymC'

    if roi_tract == 'MCP':
        region_names = [''] * 2 + [f'{roi_tract}_L', f'{roi_tract}_R']
    elif roi_tract == 'CST':
        region_names = [''] * 13 + [f'{roi_tract}_L', f'{roi_tract}_R']
    else:
        raise ValueError(f'invalid tract {roi_tract}')
    
    label_image = os.path.join(gl.baseDir, 'ROI', f'MNISymC.{roi_tract}.nii') # MCP_no_ventral_pons renamed MCP; with_ventral_pons is the original

    segment = 'FaMap'
    folder = f'{space}_{segment}'

    # predictors df (x_df) - use obs values.
    x_df = pd.read_csv(os.path.join(gl.baseDir, 'MNISymC_FaMap', f'summary_MNISymC_{roi_tract}_FaMap.tsv'), sep = '\t')
    x_df = x_df[x_df.regionname == f'{roi_tract}_R'].copy() # if using ratio, log ratio, or asymmetry index
    x_df['regionname'] = f'{roi_tract}_ai'

    lme_main(group = 'patients', p_df = p_df, segment = segment, folder = folder, space = 'MNISymC',
                label_image = label_image, region_names = region_names, roi = roi_tract, 
                predictors_df= x_df, stat = 'asymmetry_index')
   
    """
    # FaMap - from .tsv file (dataframe) in JHU-MNI (Eve) (WMPMII atlas)

    # provide predictors dataframe - exclude controls
    y_df = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'WMPMII_DTI_flip.tsv'), sep = '\t', low_memory = False) # warning: 2 diff dtypes
    controls = ['CUP_1001', 'CUP_1002', 'JHP_1001', 'JHP_1002', 'JHP_1004']
    y_df = y_df[~y_df.subj_id.isin(controls)]

    # choose metric
        # options: FaMap, (trace), lambda_1,(lambda_2, lambda_3), mean_diffusivity, radial_diffusivity
    metric = 'radial_diffusivity'
    y_df = y_df[y_df.metric == metric]
    y_df = y_df.copy() # warning

    # choose tracts
    tracts = ['MCP_L', 'MCP_R']
    y_df = y_df[y_df.regionname.isin(tracts)]

    lme_main(group = 'patients', predictors_df = y_df,roi = 'MCP', space = 'WMPMII', segment = metric)
    """

