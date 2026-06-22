"""
ADD THIS TO HELPER FUNCTIONS FOLDER?
Use: move files
Input: string tuple of file suffixes to move; source folder; destination folder
"""

import os
import shutil
import pandas as pd

def move_files(source_dir, dest_dir, ends):

    # create destination dir
    os.makedirs(dest_dir, exist_ok = True)

    for filename in os.listdir(source_dir):
        if filename.endswith(ends):
            
            shutil.move(
                os.path.join(source_dir, filename),
                os.path.join(dest_dir, filename)
            )
            print(f'Moved {filename} from {source_dir} to {dest_dir}')


"""
Example usage
"""
"""
# list of files to move: from isolate and normalize functions
ends = (
    '_T1_cerebellum_dseg.nii.gz', # isolation mask

    '_T1_from-SUIT_mode-image_xfm.nii.gz', # norm
    '_T1_space-SUIT.nii.gz', # norm
    '_T1_to-SUIT_mode-image_detJ.nii.gz', # norm
    '_T1_to-SUIT_mode-image_xfm.nii.gz', # norm
    '_T1_xfm-SUIT_0GenericAffine.mat', # norm
    '_T1_xfm-SUIT_1InverseWarp.nii.gz', # norm
    '_T1_xfm-SUIT_1Warp.nii.gz' # norm
)

p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')

for i in range(0, p_df.shape[0]):

    p_id = p_df['ID'].iloc[i]
    week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
    p_centre = (str(p_df['Centre'].iloc[i])).strip()
    refT1 = p_df['RefT1'].iloc[i]

    subj_id = f'{p_centre.strip()}_{p_id}'

    source_dir = f'/cifs/diedrichsen/data/smarts_cerebellum/anatomicals/{subj_id}/{week}/'
    dest_dir = f'/cifs/diedrichsen/data/smarts_cerebellum/anatomicals/{subj_id}/{week}/iso_norm'

    if os.path.isdir(source_dir):
        move_files(source_dir, dest_dir, ends)
"""