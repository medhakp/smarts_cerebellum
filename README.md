# Structural changes in the cerebellum following cortical stroke

This project investigates structural changes to the cerebellum and brain stem following (sub)cortical stroke in N = 40 patients and N = 12 healthy controls. T1-weighted structural MRIs are taken of individuals over the course of 1 year, from within 2 weeks post-stroke to 52 weeks post-stroke (in patients) - healthy controls are also imaged at the same time points. DTI-MRI was also taken at these time points, obtaining a grey-scale FA map.

## Image processing pipeline for T1w anatomicals

A pipeline for processing anatomicals, using mainly SUITPy and SPM12, has been written.

**Prerequisites**

* [SUITPy](https://github.com/DiedrichsenLab/SUITPy) (Python release of SUIT)
	* Plus pre-requisites required for SUITPy; see [tutorial](https://suitpy.readthedocs.io/en/latest/)
* [SPM12](https://github.com/spm/spm12)
* [spmj_tools](https://github.com/DiedrichsenLab/spmj_tools) (toolbox for SPM)
* [Dataframe](https://github.com/DiedrichsenLab/dataframe) (for reading .tsv as MAT file)

**Processing steps**

**1. Coregistration**

  To take full advantage of longitudinal data, images must be properly aligned with respect to the first available image - the reference image.
  
  First, manually align anatomicals: in FSLeyes, open the reference image and the image to be aligned on top. Manually align the latter to the reference so that anatomical structures are roughly aligned.
  
  Then, inside `sc_anat.m`, run the coregistration as `ANAT:coreg`. 
  
  Using algorithm SPM12; code made available through [spmj_tools](https://github.com/DiedrichsenLab/spmj_tools) by the Diedrichsen Lab.

  **2. Segmentation**

  Extract different segments from the image (e.g. soft tissue, CSF): inside `sc_anat.m`, run coregistration function, `ANAT:segment`. Output will be 5 files with prefix "c1" (grey matter segment), "c2" (white matter segment), "c3" (CSF segment), and "c4", "c5". Each voxel value is the volume of a given tissue in that voxel.

  Again, using algorithm SPM12; code made available through [spmj_tools](https://github.com/DiedrichsenLab/spmj_tools) by the Diedrichsen Lab.

  **3. Tissue extraction**

  (a) Extract cerebellum from T1 anatomicals

  (b) Get transformation files for deforming native spaces cerebelli into a group template (we used MNI Symmetric cerebellum-only template)

  (c) Normalise native space cerebelli (T1, grey matter segment, white matter segment) to the group template of the cerebellum

  The result is an image (T1 or tissue) normalised to a group template.

  All algorithms described above are from [SUITPy](https://github.com/DiedrichsenLab/SUITPy), developed by the Diedrichsen Lab.

  **4. Volume modulation**

  Images of the segments normalised to a template will have voxel values denoting the probability of that segment in a given voxel. Modulated volume images can be used to analyse volume in template space.

  
```mermaid

flowchart TB
    A[("<b> native space anatomicals</b> <br>{subj}_{week}T1.nii")] --> P1["scipts/sc_anat.m <br> ANAT:coreg()"]
    P1 --> B[("<b>coregistered native space anatomicals</b> <br>{subj}{week}_T1.nii<br>")]
    B --> P2["scripts/sc_anat.m ANAT:segment()"] & P3["scripts/tissue_extractor.py <br> isolate()"]
    P2 --> C[("<b>grey matter volume image</b><br> c1{subj}_{week}_T1.nii<br> <b> white matter volume image </b> c2{subj}_{week}_T1.nii <br> <b>cerebrospinalfluid volume image </b> c3{subj}_{week}_T1.nii")]
    
    P3 --> D[("<b>cerebellar isolation mask</b> <br>{subj}_{week}_T1_cerebellum_dseg.nii.gz<br>")]
    D --> P4["scripts/issue_extractor.py <br> transformation_file()"] & F["scripts/tissue_extractor.py <br> reslice()"]
    P4 --> E[("<b>transformation files</b><br>T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz<br>")]
    C --> F
    E --> F
    F --> G[("<b>normalised T1 anatomical</b><br>{subj}_{week}_MNISymC_T1.nii.gz<br>")] & H[("<b>grey matter probability</b><br>{subj}_{week}_MNISymC_GM.nii.gz <br><b>white matter probability</b><br>{subj}_{week}_MNISymC_WM.nii.gz")]
    H --> P5["scripts/modulate_volume.py"]
    P5 --> I[("<b>modulated GM volume</b><br>{subj}_{week}_MNISymC_GM_mod.nii.gz<br><b>modulated WM volume</b><br>{subj}_{week}_MNISymC_WM.nii.gz")]

     A:::nativeNode
     P1:::processNode
     B:::nativeNode
     P2:::processNode
     P3:::processNode
     C:::nativeNode
     D:::nativeNode
     P4:::processNode
     F:::processNode
     E:::templateNode
     G:::templateNode
     H:::templateNode
     P5:::processNode
     I:::templateNode
    classDef nativeNode fill:#eff4ff,stroke:#a8bce0,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef templateNode fill:#f1ddf4,stroke:#ce9bd9,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px

```

### Regression analysis of anatomicals

We performed a voxel-wise linear regression to see the average change over a year within individuals, and used a linear mixed effects (LME) model to see the time course. These regressions are performed on the T1-intensity (normalised to MNISymC), and on the segmentations fro WM, GM, and CSF (modulated volumes).

**Voxel-wise linear regression**: average change over time in an individual; run with `voxelwise_regression.py`. Produces two images per subject: an intercept image, and a slope image (showing the average change). Must have images from at least two weeks. These images can then be summarized into a mean or median slope image within each group (patients, controls) using `slope_summary_img.py`. We can also look at the mean slope in a given ROI (e.g. cerebellar ROIs or the CST): use `dataframes_cerebellum.py` for cerebellar ROIs and `dataframes_CST.py` for the CST (or other WM tracts).

**lme**: time course for change; run wtih `roi_lme.py`. Model is fit separately for patients and controls to the mean T1 intensity (normalised T1) or segment volume (modulated WM, GM) for a given ROI.

Analysis of the cerebellar cortex uses the functional parcellations of the cerebellum defined by the Nettekoven atlas [(Nettekoven et al., 2024)](https://doi.org/10.1038/s41467-024-52371-w).

```mermaid

flowchart TB
    A[("<b>normalised T1 anatomicals</b> {subj}_{week}_MNISymC_T1.nii.gz")] --> P1["scripts/voxelwise_regression.py"]
    B[("<b>modulated WMV images</b> {subj}_{week}_MNISymC_WM_mod.nii.gz")] --> P1
    C[("<b>modulated GMV images</b> {subj}_{week}_MNISymC_GM_mod.nii.gz")] --> P1
    P1 --> D[("<b>slope images</b> {subj}_{week}_MNISymC_{segment}_slope.nii.gz")]
    D --> P2["scripts/slope_summary_img.py"] & P3["scripts/dataframes_cerebellum.py"] & P4["scripts/dataframes_CST.py"]
    P2 --> E[("<b>mean slope image </b>{group}_MNISymC_{segment}_slope_mean.nii.gz")]
    P3 --> F[("<b>mean slope for ROIs in atlas </b>summary_MNISymC_{atlas}_{segment}_slope.tsv" )]
    P4 --> G[("<b>mean slope in CST by hemisphere </b>summary_MNISymC_CST_{segment}_slope.tsv")]

   
     A:::templateNode
     P1:::processNode
     B:::templateNode
     C:::templateNode
     D:::templateNode
     P2:::processNode
     P3:::processNode
     P4:::processNode
     E:::templateNode
     F:::templateNode
     G:::templateNode
    classDef templateNode fill:#f1ddf4,stroke:#ce9bd9,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px

```

## DTI analysis pipeline

DTI images give grey-scale FA maps in JHU-MNI space; a white matter atlas (WMPM Type II) [(Mori et al., 2008)](https://doi.org/10.1016/j.neuroimage.2007.12.035) gives the following metrics in 189 WM ROIs: FaMap, trace, eigenvalues 1, 2, 3. FA Map means are analyzed using a linear regression for the average slope and an LME for time course.

```mermaid
flowchart TB
    A[("<b>DTI metrics for each subj-week </b>{subj}/{week} <br>JHU_MNI_SS_WMPM_TypeII_ver2.1_dti.txt")] --> P1["scripts/make_dti_dataframes.py"]
    P1 --> B[("<b>DTI metrics (right lesion flipped)</b> <br>JHU_MNI_DTI_flip.tsv<br>")]
    B --> P2["scripts/roi_regression.py"] & P3["scripts/roi_lme_DTI.py"]
    P2 --> C[("<b>FA slope</b> <br> regression_DTI.tsv")]
    P3 --> D[("<b>FA time course</b> <br> patients_lme_DTI.tsv")]

     A:::nativeNode
     P1:::processNode
     B:::nativeNode
     P2:::processNode
     P3:::processNode
     C:::nativeNode
     D:::nativeNode
    classDef nativeNode fill:#f2fff2,stroke:#bbd7bc,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px
    style A fill:#f2fff2,stroke:#bbd7bc
```
