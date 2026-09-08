# Structural changes in the cerebellum following cortical stroke

This project investigates structural changes to the cerebellum and brain stem following (sub)cortical stroke in N = 40 patients and N = 12 healthy controls. T1-weighted structural MRIs are taken of individuals over the course of 1 year, from within 2 weeks post-stroke to 52 weeks post-stroke (in patients) - healthy controls are also imaged at the same time points.

## Image processing pipeline for T1w anatomicals

A pipeline for processing anatomicals, using mainly SUITPy and SPM12

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
    A[("folder: <b> anatomicals</b> <br>{subj}_{week}T1.nii <br> <i>native space anatomicals</i>")] --> P1["sc_anat.m: ANAT:coreg"]
    P1 --> B[("<b> anatomicals</b> <br>{subj}{week}_T1.nii<br><i>full image coregistered native space anatomicals (affine updated)</i>")]
    B --> P2["sc_anat.m ANAT:segment"] & P3["tissue_extractor.py - isolate"]
    P2 --> C[("folder: <b>anatomicals</b><br> c1{subj}_{week}_T1.nii - <i>grey matter volume</i><br>c2{subj}_{week}_T1.nii - <i>white matter volume</i><br>c3{subj}_{week}_T1.nii - <i>cerebrospinal fluid volume</i>")]
    P3 --> D[("{subj}_{week}_T1_cerebellum_dseg.nii.gz<br><i>cerebellar isolation (binary) mask</i>")]
    D --> P4["tissue_extractor.py - transformation_file"] & F["tissue_extractor.py - reslice"]
    P4 --> E[("folder: <b>MNISymC_trans</b><br>T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz<br><i>transformation files (to template: MNI Symmetric cerebellum (MNISymC))</i>")]
    C --> F
    E --> F
    F --> G[("<b>MNISymC_T1</b><br>{subj}_{week}_MNISymC_T1.nii.gz<br><i>normalised T1 anatomical</i>")] & H[("<b>MNISymC_GM</b><br>{subj}_{week}_MNISymC_GM.nii.gz - <i>grey matter probability</i><br><b>MNISymC_WM</b><br>{subj}_{week}_MNISymC_WM.nii.gz - <i>white matter probability</i>")]
    H --> P5["modulate_volume.py"]
    P5 --> I[("<b>MNISymC_GM</b><br>{subj}_{week}_MNISymC_GM_mod.nii.gz - <i>modulated GM volume</i><br><b>MNISymC_WM</b><br>{subj}_{week}_MNISymC_WM.nii.gz - <i>modulated WM volume</i>")]

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

## Regression analysis of anatomicals

We performed a voxel-wise linear regression to see the average change over a year within individuals, and used a linear mixed effects (LME) model to see the time course. These regressions are performed on the T1-intensity (normalised to MNISymC), and on the segmentations fro WM, GM, and CSF (modulated volumes).

**Voxel-wise linear regression**: average change over time in an individual; run with `voxelwise_regression.py`. Produces two images per subject: an intercept image, and a slope image (showing the average change). Must have images from at least two weeks. These images can then be summarized into a mean or median slope image within each group (patients, controls) using `slope_summary_img.py`. We can also look at the mean slope in a given ROI (e.g. cerebellar ROIs or the CST): use `dataframes_cerebellum.py` for cerebellar ROIs and `dataframes_CST.py` for the CST (or other WM tracts).

**lme**: time course for change; run wtih `roi_lme.py`. Model is fit separately for patients and controls to the mean T1 intensity (normalised T1) or segment volume (modulated WM, GM) for a given ROI.

```mermaid
flowchart TB
    A[("{subj}_{week}_MNISymC_T1.nii.gz <br> <i>anatomicals for all weeks</i>")] --> P1["voxelwise_regression.py"]
    B[("{subj}_{week}_MNISymC_WM_mod.nii.gz <br> <i>modulated WMV images for all weeks</i>")] --> P1
    C[("{subj}_{week}_MNISymC_GM_mod.nii.gz <br> *modulated GMV images for all weeks*")] --> P1
    P1 --> D[("{subj}_{week}_MNISymC_{segment}_{intercept/slope}.nii.gz <br> <i>intercept, slope images for given segment (T1, WM_mod, GM_mod)</i>")]
    D --> P2["slope_summary_img.py"] & P3["dataframes_cerebellum.py"] & P4["dataframes_CST.py"]
    P2 --> E[("{group}_MNISymC_{segment}_slope_mean.nii.gz <br> <i>mean slope image for group (patients, controls)</i>")]
    P3 --> F@{ label: "summary_MNISymC_{atlas}_{segment}_slope.tsv <br> <i>tsv with mean slope in each cerebellar ROI for each subject in a given segment. We used the functional cerebellar atlas 'Nettekoven_2024' (symmetric, 32-region)</i>" }
    P4 --> G[("summary_MNISymC_CST_{segment}_slope.tsv <br> <i>tsv with mean slope in CST for each subject</i>")]

    F@{ shape: cylinder}
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
