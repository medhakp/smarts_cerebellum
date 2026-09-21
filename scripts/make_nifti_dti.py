import pandas as pd
import os
import numpy as np
from pathlib import Path
import nibabel as nib
import smarts_cerebellum.globals as gl

# AUTHOR: Marco Emanuele


def img_2_nii(
    input_dir,
    output_dir=None,
    recursive=True,
    compress=False,
    overwrite=False,
    ):
    """Convert every .img file in a folder to a single-file .nii.

    Parameters
    ----------
    input_dir : str or Path
        Folder containing the .img/.hdr pairs.
    output_dir : str or Path, optional
        Where to write the .nii files. Defaults to input_dir.
    recursive : bool
        If True, also search subfolders.
    compress : bool
        If True, write .nii.gz instead of .nii.
    overwrite : bool
        If True, overwrite existing output files instead of skipping them.

    Returns
    -------
    list of tuple
        (source_path, status) where status is "converted", "skipped",
        or an error message string.
    """

    try:
        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Not a folder: {input_dir}")
    except NotADirectoryError as error:
        print(f"Skipping {input_dir}: not a folder")
        return # exit function

    out_base = Path(output_dir) if output_dir else input_dir
    out_base.mkdir(parents=True, exist_ok=True)

    ext = ".nii.gz" if compress else ".nii"
    pattern = "**/*.img" if recursive else "*.img"

    results = []
    for img_path in sorted(input_dir.glob(pattern)):
        # Preserve subfolder structure when recursing
        rel_parent = img_path.parent.relative_to(input_dir)
        target_dir = out_base / rel_parent
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / (img_path.stem + ext)

        if out_path.exists() and not overwrite:
            results.append((img_path, "skipped (already exists)"))
            print(f"SKIP  {img_path.name} -> {out_path.name} (exists)")
            continue

        try:
            image = nib.load(str(img_path))  # auto-locates the .hdr
            nib.save(image, str(out_path))
            results.append((img_path, "converted"))
            print(f"OK    {img_path.name} -> {out_path.name}")
        except Exception as e:  # noqa: BLE001 - report and keep going
            results.append((img_path, f"error: {e}"))
            print(f"FAIL  {img_path.name}: {e}")

    n_ok = sum(1 for _, s in results if s == "converted")
    print(f"\nDone: {n_ok}/{len(results)} converted.")
    return results


def _subj_week_loop(df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week

# images saved as 4D array; need them as 3D
def _array_4d_to_3d(img_name):
    img = nib.load(img_name)
    arr = img.get_fdata()
    arr_3d = np.squeeze(arr) # remove axis of dimension 1
    img_3d = nib.Nifti1Image(arr_3d, img.affine)
    return img_3d


if __name__ == '__main__':
    p_dti = pd.read_excel(os.path.join(gl.baseDir, 'DTI', 'patient_list.xlsx'), usecols = range(10)) # only need the first 5 cols
    p_dti['subj_id'] = p_dti['Centre'].str.strip() + '_' + p_dti['ID'].astype(str)

    for subj, week in _subj_week_loop(p_dti):
        try:
            input_dir = os.path.join(gl.baseDir, 'DTI', subj, week, 'coreg_T1MNI_TP1')
            img_2_nii(input_dir = input_dir, recursive = False, overwrite = True)

        except NotADirectoryError:
            print(f"{input_dir} does not exist; skipping")
            continue

    # #remove extra dimension (of size 1) (so that we can normalise later for just cerebellum - need to multiple by cerebellar mask with 3d array)
    for subj, week in _subj_week_loop(p_dti):
        image_dir = os.path.join(gl.baseDir, 'DTI', subj, week, 'coreg_T1MNI_TP1')
        image = os.path.join(image_dir, 'FaMap_dc_ss.nii')
        if not Path(image).exists():
            continue
        img_3d = _array_4d_to_3d(image)
        nib.save(img_3d, image)

    
