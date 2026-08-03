import pandas as pd
import nibabel as nib
import SUITPy as suit
from pathlib import Path
import os
import smarts_cerebellum.globals as gl

def _subj_week_loop(df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week

def reslice_atlas(
            df = None,
            atlas_name = None,
            atlas = None,
            trans_path = None,
            inverse_deformation = 'T1_from-MNI152NLin2009cSymC_mode-image_xfm.nii.gz',
            save_atlas_path = None, # save to same place as native anatomicals? so gl.baseDir/anatomicals (= save_atlas_path)
            interp = 0 # atlas is label file => nearest-neighbour interpolation
            ):
    """
    inverse deformation
    """

    atlas_path = f'{gl.baseDir}/ROI/cerebellar_atlases/{atlas}/{atlas_name}.nii'
    if not Path(atlas_path).is_file():
        print(f'{atlas_path} not found')
        return None


    for subj, week in _subj_week_loop(df):
        # files required for normalization: atlas (atlas, map; or just atlas-map name), inverse deformation
        deformation_path = f'{trans_path}/{subj}/{week}/{subj}_{week}_{inverse_deformation}'

        if not Path(deformation_path).is_file():
            print(f'inv def path does not exist for {subj} in week {week}')
            continue
     
        resliced_atlas = suit.reslice_image(source_image = atlas_path,
                                          deformation = deformation_path,
                                          interp = interp
                                          )
        
        subj_save_path = os.path.join(save_atlas_path, subj, week)
        subj_save_path = Path(subj_save_path)
        subj_save_path.mkdir(parents = True, exist_ok = True)

        nib.save(resliced_atlas, os.path.join(subj_save_path, f'{subj}_{week}_{atlas_name}.nii.gz'))


if __name__ == '__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')

    atlas_names = ['atl-NettekovenSym32_space-MNISym_dseg', 'atl-Anatom_space-MNISym_dseg'] # Nettekoven_2024 (sym, 32 region), Diedrichsen_2009 (anatomical)
    atlases = ['Nettekoven_2024', 'Diedrichsen_2009']

    trans_folder = os.path.join(gl.baseDir, 'MNISymC_trans')
    save_atlas_path = os.path.join(gl.baseDir, 'anatomicals') # save subj-week atlas to same place as subj-week anatomicals

    for atlas_name, atlas in zip(atlas_names, atlases):
        reslice_atlas(
                df = p_df,
                atlas_name = atlas_name,
                atlas = atlas,
                trans_path = trans_folder,
                save_atlas_path = save_atlas_path
                )
