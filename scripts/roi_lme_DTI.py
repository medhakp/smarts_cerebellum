import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main

if __name__ == '__main__':

    """
    # FaMap - images in MNISymC (template space)


    p_df = pd.read_excel(os.path.join(gl.baseDir, 'DTI', 'patient_list.xlsx'), usecols = range(10))
    p_df['subj_id'] = p_df['Centre'].str.strip() + '_' + p_df['ID'].astype(str)

    space = 'MNISymC'

    # custom ROI
    roi_tract = 'CST'
    label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')
    region_names = [''] * 13 + [f'{roi_tract}', f'right_{roi_tract}']

    segment = 'FaMap'
    folder = f'{space}_{segment}'
    lme_main(group = 'patients', p_df = p_df, segment = segment, folder = folder, space = 'MNISymC',
            label_image = label_image, region_names = region_names, rois = roi_tract)
    """

    # FaMap - from .tsv file (dataframe) in JHU-MNI

    # provide predictors dataframe - exclude controls
    y_df = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'JHU_MNI_DTI_flip.tsv'), sep = '\t', low_memory = False) # warning: 2 diff dtypes
    controls = ['CUP_1001', 'CUP_1002', 'JHP_1001', 'JHP_1002', 'JHP_1004']
    y_df = y_df[~y_df.subj_id.isin(controls)]

    # choose metric
        # options: FaMap, trace, lambda_1, lambda_2, lambda_3, mean_diffusivity, radial_diffusivity
    metric = 'lambda_1'
    y_df = y_df[y_df.metric == metric]
    y_df = y_df.copy() # warning

    # choose tracts
    tracts = ['CST_L', 'CST_R']
    y_df = y_df[y_df.regionname.isin(tracts)]

    lme_main(group = 'patients', predictors_df = y_df,roi = 'CST', space = 'JHU_MNI', segment = metric)

