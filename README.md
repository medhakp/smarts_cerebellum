# Structural changes to the cerebellum following cortical stroke

Investigating anatomical changes to the cerebellum following cortical stroke over a year followign stroke.

This repository provides replicable functions to perform this analysis primarily using SPM12 and SUITPy.

**Pre-requisites**

* [SUITPy](https://github.com/DiedrichsenLab/SUITPy) (Python release of SUIT)
	* Plus pre-requisites required for SUITPy; see [tutorial](https://suitpy.readthedocs.io/en/latest/)
* [SPM12](https://github.com/spm/spm12)
* [spmj_tools](https://github.com/DiedrichsenLab/spmj_tools) (toolbox for SPM)
* [Dataframe](https://github.com/DiedrichsenLab/dataframe) (for reading .tsv as MAT file)


**1. Coregistration**

  To take full advantage of longitudinal data, images must be properly aligned with respect to the first available image - the reference image.
  
  First, manually align anatomicals: in FSLeyes, open the reference image and the image to be aligned on top. Manually translate and rotate the latter until they are aligned.
  
  Then, inside `sc_anat.m`, run the coregistration as `ANAT:coreg` (script made available in [spmj_tools](https://github.com/DiedrichsenLab/spmj_tools/blob/main/template_functional_singlesess.m)).

**2. Set q-form matrix equal to s-form matrix**

  Manual alignment and coregistration results in a mismatch between an image’s qform and sform matrices, where the former is how an individual was scanned in the coil and the latter is the matrix to align the image with its reference. Hence, we prefer to use the sform matrix.
  
  The function `set_qform_to_sform.py` will change the qform matrix to equal the sform matrix in all anatomical images, avoiding later physical space mismatches.
  
  This issue tends to arise because some packages use the qform matrix, while others use the sform matrix - so they read or (if in a function) output an image premultiplied with different affines, resulting in images in different world (physical) orientation.

**3. Segmentation**

  Segment T1-weighted anatomicals into tissues including grey and white matter, and CSF. This code is made available through [spmj_tools](https://github.com/DiedrichsenLab/spmj_tools/blob/main/template_anat.m). The output will be five segmentation files for grey matter, white matter, CSF, etc. (with prefixes c1, c2, c3, …).

**4. SUITPy Extractor Pipeline**
  
  This pipeline takes as input the T1-weighted anatomical image and specified segmentation file. You may choose which segmentation is being used.
  
  The pipeline isolates the cerebellum in a cerebellar isolation mask, which is then normalized to a template (SUIT by default) from aligned space, producing a forward transformation file. This transformation file is used to reslice the cerebellar isolation mask into template space. Then, calculate the volume of this tissue in the template space.
  
  Choose an appropriate cerebellar [atlas and map](https://suitpy.readthedocs.io/en/latest/atlases.html). Finally, the pipeline outputs the volume of the selected tissue or matter in each region defined on the atlas’s map. 
