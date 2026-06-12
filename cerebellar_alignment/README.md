# Cerebellar alignment

**Add credits**

Some individuals with cortical strokes experience cerebral tissue swelling in week 0 (W0) which goes down in W4. As a result, 

### To-do

**Cerebellum-only image coregistration**

- [x] Using SUITPy isolation pipeline, get a cerebellar isolation mask for each subject at each time point
- [ ] Get a cerebellum-only image: multiply isolation mask (binary) by T1 anatomical - save with suffix `_T1_cerebellum_only.nii` in new folder "cerebellar_alignment" for each subj-week
      *Note*: SPM `coreg` does not read archived (.nii.gz) files; cerebellar image MUST be saved as uncompressed Nifti
- [ ] Update `sc_anat.m` function to read images with suffix `_T1_cerebellum_only.nii` (save as new function, `sc_anat_cerebel.m`); update directory (add "cerebellar_alignment" to path). Run coregistration on cerebellum-only images.

**Updating affine**
- [ ] Coming soon: function to update affines
- [ ] Use that function to update the **affine** of the T1 anatomical with the affine from cerebellum-only alignment (i.e. set its affine to that of the cerebellum-only coregistered image for the corresponding week); save in "cerebellum_alignment" with suffix
- [ ] Repeat for tissue probability maps (e.g. white matter probability map, c2-prefixed file), and save in "cerebellar_alignment" folder as well.
- [ ] Run linear regression on new cerebellum-aligned-affine, save slope and intercept images to each subject's folder under "cerebellar_alignment_regression" subfolder
