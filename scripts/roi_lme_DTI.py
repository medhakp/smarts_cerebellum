import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main

if __name__ == '__main__':

    
    # FaMap - images in MNISymC (template space)

    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')

    # for predictors, use already-made df (for obs values)
    x_df = pd.read_csv(os.path.join(gl.baseDir, 'MNISymC_FaMap', 'summary_MNISymC_Nettekoven_2024_FaMap.tsv'), sep = '\t')
    x_df = x_df[x_df.regionname.str.endswith("R")].copy()
 

    space = 'MNISymC'
    # cerebellar atlas
    atlas_space = 'MNISym'
    atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'

    # CEREBELLUM
    cereb_segments = ['FaMap']
    cereb_folders = [f'{space}_FaMap']

    for c_segment, c_folder in zip(cereb_segments, cereb_folders):
        lme_main(group = 'patients', p_df = p_df, segment = c_segment, folder = c_folder, space = 'MNISymC',
                atlas_space = atlas_space, atlas = atlas, maps = maps, roi = atlas, stat = 'asymmetry_index', predictors_df = x_df)
    
    

    # # custom ROI
    # roi_tract = 'CST'
    # label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')
    # region_names = [''] * 13 + [f'left_{roi_tract}', f'{roi_tract}_R']

    # segment = 'FaMap'
    # folder = f'{space}_{segment}'

    #x_df = pd.read_csv(os.path.join(gl.baseDir, 'MNISymC_FaMap', 'summary_MNISymC_CST_FaMap.tsv'), sep = '\t')

   
   
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
    tracts = ['CST_L', 'CST_R']
    y_df = y_df[y_df.regionname.isin(tracts)]

    lme_main(group = 'patients', predictors_df = y_df,roi = 'CST', space = 'WMPMII', segment = metric)
    """

