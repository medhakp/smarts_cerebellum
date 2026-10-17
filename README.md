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
  
```mermaid
flowchart TB
 subgraph S1["1. <b>native space</b>"]
        P1@{ label: "scripts/sc_anat('ANAT:coreg')" }
        A[("<b>raw T1w anatomicals: </b> <br>anatomicals/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;T1.nii")]
        B[("<b>coregistered T1w anatomicals (to time point 1): </b> <br>anatomicals/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;T1.nii<br>")]
        P2@{ label: "scripts/sc_anat('ANAT:segment')" }
        P3["scripts/tissue_extractor.isolate()"]
        C[("<b>grey matter volume image</b><br>c1&lt;subj&gt;_&lt;week&gt;_T1.nii<br><b>white matter volume image</b><br>c2&lt;subj&gt;_&lt;week&gt;_T1.nii<br><b>cerebrospinalfluid volume image</b><br>c3&lt;subj&gt;_&lt;week&gt;_T1.nii<br><i>(c4, c5 not used)</i>")]
  end
 subgraph S2["2. <b>normalization</b>"]
        D[("<b>cerebellar isolation mask</b> <br>&lt;subj&gt;_&lt;week&gt;_T1_cerebellum_dseg.nii.gz<br>")]
        P4["scripts/tissue_extractor.transformation_files()"]
        E[("<b>transformation files</b><br>MNISymC_trans/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz<br>")]
        F["scripts/tissue_extractor.reslice()"]
        G[("<b>normalised T1 anatomical</b><br>MNISymC_T1/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_T1.nii.gz<br>")]
        H[("<b>grey matter probability</b><br>MNISymC_GM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_GM.nii.gz <br><b>white matter probability</b><br>MNISymC_WM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_WM.nii.gz")]
  end
 subgraph S3["3. <b> modulated tissue volume</b>"]
        P5["scripts/modulate_volume.py"]
        I[("<b>modulated GM volume</b><br>MNISymC_GM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_GM_mod.nii.gz<br><b>modulated WM volume</b><br>MNISymC_WM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_WM_mod.nii.gz")]
  end
 subgraph S4["4. <b>flip lesion</b>"]
        P6["scripts/flip_lesion.py"]
        J@{ label: "<span style=\"--tw-border-spacing-y:\">**normalised T1 anatomical (left lesion flipped to right)**</span><br style=\"--tw-border-spacing-y:\">MNISymC_T1/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_T1.nii.gz<br>MNISymC_T1/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_T1_FlipLR.nii.gz" }
        K[("<b>modulated GM volume (left lesions flipped to right)</b><br>MNISymC_GM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_GM_mod.nii.gz<br>MNISymC_GM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_GM_mod_FlipLR.nii.gz<br><b>modulated WM volume (left lesions flipped to right)</b><br>MNISymC_WM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_WM_mod.nii.gz<br>MNISymC_WM/&lt;subj&gt;/&lt;week&gt;/&lt;subj&gt;_&lt;week&gt;_MNISymC_WM_mod_FlipLR.nii.gz")]
  end
    A --> P1
    P1 --> B
    B --> P2 & P3
    P2 --> C
    P3 --> D
    D --> P4
    P4 --> E
    C --> F
    E --> F
    F --> G & H
    H --> P5
    P5 --> I
    I --> P6
    G --> P6
    P6 --> J & K

    P1@{ shape: rect}
    P2@{ shape: rect}
    J@{ shape: cylinder}
     P1:::processNode
     A:::nativeNode
     B:::nativeNode
     P2:::processNode
     P3:::processNode
     C:::nativeNode
     D:::nativeNode
     P4:::processNode
     E:::templateNode
     F:::processNode
     G:::templateNode
     H:::templateNode
     P5:::processNode
     I:::templateNode
     P6:::processNode
     J:::templateNode
     K:::templateNode
    classDef nativeNode fill:#eff4ff,stroke:#a8bce0,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef templateNode fill:#f1ddf4,stroke:#ce9bd9,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px
    style S1 stroke:transparent,fill:#f2fff2
    style S2 fill:#f2fff2,stroke:transparent
    style S3 fill:#f2fff2,stroke:transparent
    style S4 fill:#f2fff2,stroke:transparent
```

### Regression analysis of anatomicals

We performed a voxel-wise linear regression to see the average change over a year within individuals, and used a linear mixed effects (LME) model to see the time course. These regressions are performed on the T1-intensity (normalised to MNISymC), and on the segmentations fro WM, GM, and CSF (modulated volumes).

**Voxel-wise linear regression**: average change over time in an individual; run with `voxelwise_regression.py`. Produces two images per subject: an intercept image, and a slope image (showing the average change). Must have images from at least two weeks. These images can then be summarized into a mean or median slope image within each group (patients, controls) using `slope_summary_img.py`. We can also look at the mean slope in a given ROI (e.g. cerebellar ROIs or the CST): use `dataframes_cerebellum.py` for cerebellar ROIs and `dataframes_CST.py` for the CST (or other WM tracts).

**lme**: time course for change; run wtih `roi_lme.py`. Model is fit separately for patients and controls to the mean T1 intensity (normalised T1) or segment volume (modulated WM, GM) for a given ROI.

Analysis of the cerebellar cortex uses the functional parcellations of the cerebellum defined by the Nettekoven atlas [(Nettekoven et al., 2024)](https://doi.org/10.1038/s41467-024-52371-w).


## DTI analysis pipeline

DTI images give grey-scale FA maps in JHU-MNI space; a white matter atlas (WMPM Type II) [(Mori et al., 2008)](https://doi.org/10.1016/j.neuroimage.2007.12.035) gives the following metrics in 189 WM ROIs: FaMap, trace, eigenvalues 1, 2, 3. FA Map means are analyzed using a linear regression for the average slope and an LME for time course.

