from pathlib import Path

base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'

def parent_lookup(file_path, subj_id):
    """
    Looks for subject parent directory of a reference file. Also tracks how many *n* parents there are.

    e.g. If you have a reference file and want to access all other files in its parent (or grandparent, n^th-level parent) directory.

    Inputs:
        file_path (str or Posix path)
        subj_id: str

    Outputs:
        parent (PosixPath): subj_id parent folder
        level (int): levels from reference image to parent folder
    """

    path = Path(file_path)

    for level, parent in enumerate(path.parents, start = 1):
        if parent.name == subj_id:
            return parent, level
    
    print(f'{subj_id} not found in {path}. byeeee')
    return None


def find_week_files(file_path, subj_id, file_naming, subdir = None):
    """
    Finds files in a directory

    If subdir is not None, then looks for structure subj_id/subdir, and searches for week files within subdir

    Inputs:
        file_path (str): reference file
        subj_id (str)
        file_naming (str): naming convention of files being searched for
            e.g. if looking for all .nii files, do *.nii; if looking for wm seg files, do c2*.nii
        subdir (str): default is None; subdirectory (within subject's folder) to look inside for week folder/file
    """
    parent, level = parent_lookup(file_path, subj_id)

    # folder to search inside: subj_id/subdir/ or subj_id/
    folder_root = parent/subdir if subdir else parent

    # depth of file
    rel_parts = Path(file_path).relative_to(folder_root).parts # get all components of file path
    depth = len(rel_parts)

    # then goes down *n* folders to find the file
    glob_pattern = "/".join(["*"] * (depth - 1) + [file_naming])

    # return file (if found) as PosixPath
    return [p for p in folder_root.glob(glob_pattern) if p.is_file()]


"""
# Example usage



subj_id = 'CU_2538'
refT1 = 'W0'
#ref_img = f'{base_dir}/MNISym_GM/{subj_id}/{subj_id}_{refT1}_reslice.nii.gz'
ref_img = f'{base_dir}/anatomicals/{subj_id}/{refT1}/c2{subj_id}_{refT1}_T1.nii'




find_week_files(ref_img, subj_id, file_naming = "c2*.nii")

# e.g. c2*.nii to find all files that start with c2 and end in .nii

# using * for file naming to find all files in that subject's folder

# if using subdir: returns only files in that directory (subdirectory to subj_id directory)
# if not using subdir: returns all files in that subject's directory
"""