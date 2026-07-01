# code from Claude

import os

def rename_file(old_path: str, new_path: str) -> bool:
    """
    Rename a file from old_path to new_path.
    """
    try:
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} to {new_path}")
        return True
    except FileNotFoundError:
        print(f"Error: File not found: {old_path}")
    except FileExistsError:
        print(f"Error: Destination already exists: {new_path}")
    except PermissionError:
        print(f"Error: Permission denied")
    return False

"""
Example usage

# move old iso_norm_mniSymm folders into a common folder (for each subject-week) (to be deleted).
    # this is to help keep our trash organized.
for i in range(0, p_df.shape[0]):

    p_id = p_df['ID'].iloc[i]
    week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
    p_centre = (str(p_df['Centre'].iloc[i])).strip()

    subj_id = f'{p_centre.strip()}_{p_id}'

    # directory for each subject's files (each subject gets their own base_dir here)
    mni_base_dir = f'/cifs/diedrichsen/data/smarts_cerebellum/MNISym_GM/{subj_id}'

    old_path = f'{mni_base_dir}/{subj_id}_{week}_MNISym_GM_reslice.nii.gz'
    new_path = f'{mni_base_dir}/{subj_id}_{week}_MNISym_GM_coreg_reslice.nii.gz'

    rename_file(old_path = old_path, new_path = new_path)
"""