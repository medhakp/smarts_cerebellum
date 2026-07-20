"""
Using SUITPy: https://github.com/DiedrichsenLab/SUITPy
"""

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


def isolate(df, anat_dir):
    """
    Isolate cerebellum from T1 anatomical
    """
    for subj, week in _subj_week_loop(df):


        t1_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1.nii'

        if not Path(t1_path).is_file():
            continue

        save_folder = os.path.join(anat_dir, subj, week)
        suit.isolate(t1_path, result_folder = save_folder, verbose = 1)
        
        print(f'Cerebellar isolation mask for {subj} at {week} done!')    


def transformation_files(df,
                         anat_dir,
                         results_folder,
                         template_space,
                         write_ants_transform=False,
                         write_normalized=True,
                         write_deformation=True,
                         write_inv_deformation=True,
                         write_jacobian_determinant=True,
                         write_log_jacobian_determinant=True,
                         verbose = 1
                         ):
    """
    make transformation files for normalization into specified space
    """

    for subj, week in _subj_week_loop(df):
        # files required for transformation: t1_anat, cerebellar isolation mask (binary)
        t1_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1.nii'
        mask_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1_cerebellum_dseg.nii.gz'

        if not Path(t1_path).is_file():
            print(f'T1 path does not exist for {subj} in week {week}')
            continue

        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj} in week {week}')
            continue

        save_folder = os.path.join(results_folder, subj, week)
        save_folder = Path(save_folder)
        save_folder.mkdir(parents = True, exist_ok = True) # makes folder if it doesn't exist

        suit.normalize(
            source_file = t1_path,
            mask_file = str(mask_path),
            space = template_space,

            # optional files
            write_normalized= write_normalized,
            write_ants_transform=write_ants_transform,
            write_deformation=write_deformation,
            write_inv_deformation=write_inv_deformation,
            write_jacobian_determinant=write_jacobian_determinant,
            write_log_jacobian_determinant=write_log_jacobian_determinant,

            result_folder = save_folder,
            verbose = verbose
            )
        
        print(f'{subj} {week} transformation files done! \n')

def reslice(
            df,
            segment,
            trans_path,
            deformation,
            norm_save_path,
            space,
            anat_dir
            ):
    """
    forward deformation: normalize images to space from transformation file
    """

    tissue_dict = {
        'GM': 'c1',
        'WM': 'c2',
        'CSF': 'c3',
        'T1': ''
    }
    
    for subj, week in _subj_week_loop(df):
        # files required for normalization: img in native space, deformation file, isolation mask
        native_path = f'{anat_dir}/{subj}/{week}/{tissue_dict[segment]}{subj}_{week}_T1.nii'
        deformation_path = f'{trans_path}/{subj}/{week}/{subj}_{week}_{deformation}'
        mask_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1_cerebellum_dseg.nii.gz'

        if not Path(native_path).is_file():
            print(f'{segment} path does not exist for {subj} in week {week}')
            continue

        if not Path(deformation_path).is_file():
            print(f'fwd def path does not exist for {subj} in week {week}')
            continue
            
        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj} in week {week}')
            continue

        resliced_img = suit.reslice_image(source_image = native_path,
                                          deformation = deformation_path,
                                          mask = mask_path
                                          )
        
        subj_save_path = os.path.join(norm_save_path, subj)
        subj_save_path = Path(subj_save_path)
        subj_save_path.mkdir(parents = True, exist_ok = True)
        nib.save(resliced_img, os.path.join(subj_save_path, f'{subj}_{week}_{space}_{segment}.nii.gz'))



if __name__ == '__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    anat_dir = os.path.join(gl.baseDir, 'anatomicals')

    template_space = 'MNI152NLin2009cSymC'
    trans_folder = os.path.join(gl.baseDir, 'MNISymC_trans') # folder to which transformation files are saved

    fwd_deformation = 'T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz'
    segments = ['T1', 'GM', 'WM', 'CSF']
    space_folder = 'MNISymC'
    
    #isolate(p_df, anat_dir) # binary cerebellar isolation masks
    #transformation_files(p_df, anat_dir, trans_folder, template_space) # subj-week transformation files
    
    for segment in segments:
        segment_save_path = os.path.join(gl.baseDir, f'{space_folder}_{segment}')
        reslice(p_df,
                segment,
                trans_path = trans_folder,
                deformation = fwd_deformation,
                norm_save_path = segment_save_path,
                space = space_folder,
                anat_dir = anat_dir
                )
   