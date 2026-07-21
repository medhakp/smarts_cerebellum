import pandas as pd
import nibabel as nib
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

def modulate_volume(df,
                    tissue,
                    space = 'MNISymC'
                    ):
    for subj, week in _subj_week_loop(df):
        # tissue probability image
        tissue_img = nib.load(f'{gl.baseDir}/{space}_{tissue}/{subj}/{subj}_{week}_{space}_{tissue}.nii.gz')
        tissue_arr = tissue_img.get_fdata()

        # Jacobian determinant
        detJ_img = nib.load(f'{gl.baseDir}/{space}_trans/{subj}/{week}/{subj}_{week}_T1_to-MNI152NLin2009cSymC_mode-image_detJ.nii.gz')
        detJ_arr = detJ_img.get_fdata()

        # multiply arrays - element-wise
        mod_vol_arr = tissue_arr * detJ_arr

        # save image
        mod_vol_img = nib.Nifti1Image(mod_vol_arr, tissue_img.affine, tissue_img.header)
        nib.save(mod_vol_img, f'{gl.baseDir}/{space}_{tissue}/{subj}/{subj}_{week}_{space}_{tissue}_mod.nii.gz')

if __name__ == '__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')

    tissues = ['WM', 'GM', 'CSF']
    for tissue in tissues:
        modulate_volume(df = p_df, tissue = tissue)
    