# Import packages
import nibabel as nib
import pandas as pd
import os
import numpy as np


# directories
anat_dir = "/cifs/diedrichsen/data/smarts_cerebellum/anatomicals"
p_df = pd.read_csv("/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv", sep = '\t')

for i in range(0, p_df.shape[0]):

    p_id = p_df['ID'].iloc[i]
    week = (p_df['Week'].iloc[i]).strip()
    p_centre = str(p_df['Centre'].iloc[i])
    refT1 = (p_df['RefT1'].iloc[i]).strip()

    subj_id = f'{p_centre.strip()}_{p_id}'
    
    if week!=refT1: # do not change reference images!
        
        t1_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1.nii'

        # skip if file does not exist
        if not os.path.exists(t1_path):
            print(f'{t1_path} does not exist; skip')
            continue

        t1_read = nib.load(t1_path)

        data = np.array(t1_read.dataobj) # lazy loading; point to file

        updated_t1 = nib.Nifti1Image(data, affine = t1_read.affine, header = t1_read.header)
        updated_t1.set_sform(t1_read.get_sform())
        updated_t1.set_qform(t1_read.get_sform())

        # save image with updated affine
        nib.save(updated_t1, t1_path)

        # progress check
        print(f'qform changed to sform for {subj_id} {week}')
