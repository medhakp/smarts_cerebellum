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
---
config:
  layout: dagre
---
flowchart TB
    A[("<b>raw T1w anatomicals: </b> <br>anatomicals/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;T1.nii")] --> P1@{ label: "scripts/sc_anat('ANAT:coreg')" }
    P1 --> B[("<b>coregistered T1w anatomicals (to time point 1): </b> <br>anatomicals/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;T1.nii<br>")]
    B --> P2@{ label: "scripts/sc_anat('ANAT:segment')" } & P3["scripts/tissue_extractor.isolate()"]
    P2 --> C[("<b>grey matter volume image</b><br>c1#60;subj#62;_#60;week#62;_T1.nii<br><b>white matter volume image</b><br>c2#60;subj#62;_#60;week#62;_T1.nii<br><b>cerebrospinalfluid volume image</b><br>c3#60;subj#62;_#60;week#62;_T1.nii<br><i>(c4, c5 not used)</i>")]
    P3 --> D[("<b>cerebellar isolation mask</b> <br>#60;subj#62;_#60;week#62;_T1_cerebellum_dseg.nii.gz<br>")]
    D --> P4["scripts/tissue_extractor.transformation_files()"]
    P4 --> E[("<b>transformation files</b><br>MNISymC_trans/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz<br>")]
    C --> F["scripts/tissue_extractor.reslice()"]
    E --> F
    F --> G[("<b>normalised T1 anatomical</b><br>MNISymC_T1/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_T1.nii.gz<br>")] & H[("<b>grey matter probability</b><br>MNISymC_GM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_GM.nii.gz <br><b>white matter probability</b><br>MNISymC_WM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_WM.nii.gz")]
    H --> P5["scripts/modulate_volume.py"]
    P5 --> I[("<b>modulated GM volume</b><br>MNISymC_GM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_GM_mod.nii.gz<br><b>modulated WM volume</b><br>MNISymC_WM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_WM_mod.nii.gz")]
    I --> P6["scripts/flip_lesion.py"]
    G --> P6
    P6 --> J@{ label: "<span style=\"--tw-border-spacing-y:\">**normalised T1 anatomical (left lesion flipped to right)**<br></span>MNISymC_T1/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_T1(_FlipLR).nii.gz<br>" } & K[("<b>modulated GM volume (left lesions flipped to right)</b><br>MNISymC_GM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_GM_mod.nii.gz<br>MNISymC_GM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_GM_mod(_FlipLR).nii.gz<br><b>modulated WM volume (left lesions flipped to right)</b><br>MNISymC_WM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#62;_MNISymC_WM_mod.nii.gz<br>MNISymC_WM/#60;subj#62;/#60;week#62;/#60;subj#62;_#60;week#gt_MNISymC_WM_mod(_FlipLR).nii.gz")]

    P1@{ shape: rect}
    P2@{ shape: rect}
    J@{ shape: cylinder}
     A:::nativeNode
     P1:::processNode
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
    style A fill:#BBDEFB
    style B fill:#BBDEFB
    style C fill:#BBDEFB
    style D fill:#BBDEFB
```

### Voxel-wise analysis of anatomicals

```mermaid
---
config:
  layout: fixed
---
flowchart TB
    B[("<b>modulated WMV<br></b>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_WM_mod.nii.gz")] --> P1["scripts/voxelwise_regression()"]
    P1 --> D[("<b>slope images<br></b>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_WM_mod_slope.nii.gz")]
    D --> P5["scripts/flip_lesion.py"]
    P5 --> I[("<b>left lesions flipped right</b><br>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_WM_mod_slope_FlipLR.nii.gz<br><b>right lesions</b><br>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_WM_mod_slope.nii.gz")]
    I --> P4["scripts/dataframes_anat_tracts.py"] & P6["scripts/slope_summary_images.py"]
    P6 --> H[("<b>mean, median slope images</b><br>regression/ﬂ°°60¶ßmeans/mediansﬂ°°62¶ß/ﬂ°°60¶ßgroupﬂ°°62¶ß_WM_mod_slope_ﬂ°°60¶ßmean/medianﬂ°°62¶ß")]
    P3["scripts/dataframes_anat_cerebellum.py"] --> F[("<b>mean slope for cerebellar ROIs<br></b>regression/summary_MNISymC_Nettekoven2024_ﬂ°lt¶ßsegmentﬂ°gt¶ß_ﬂ°lt¶ßslopeﬂ°gt¶ß.tsv")]
    P4 --> G[("<b>mean slope in CST or MCP<br></b>regression/summary_MNISymC_ﬂ°lt¶ßCST/MCPﬂ°gt¶ß_WM_mod_slope.tsv")]
    C[("<b>modulated GMV</b><br>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_GM_mod.nii.gz")] --> n2["scripts/voxelwise_regression()"]
    n2 --> n3[("<b>slope images<br></b>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_WM_mod_slope.nii.gz")]
    n3 --> n4["scripts/flip_lesion.py"]
    n4 --> n5[("<b>left lesions flipped right</b><br>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_GM_mod_slope_FlipLR.nii.gz<br><b>right lesions</b><br>ﬂ°lt¶ßsubjﬂ°gt¶ß/ﬂ°lt¶ßweekﬂ°gt¶ß/ﬂ°lt¶ßsubjﬂ°gt¶ß_ﬂ°lt¶ßweekﬂ°gt¶ß_MNISymC_GM_mod_slope.nii.gz")]
    n5 --> P3 & n6["scripts/slope_summary_images.py"]
    n6 --> n7[("<b>mean, median slope images</b><br>regression/ﬂ°°60¶ßmeans/mediansﬂ°°62¶ß/ﬂ°°60¶ßgroupﬂ°°62¶ß_WM_mod_slope_ﬂ°°60¶ßmean/medianﬂ°°62¶ß")]

    n2@{ shape: rect}
    n4@{ shape: rect}
    n6@{ shape: rect}
     B:::templateNode
     P1:::processNode
     D:::templateNode
     P5:::processNode
     I:::templateNode
     P4:::processNode
     P6:::processNode
     H:::templateNode
     P3:::processNode
     F:::templateNode
     G:::templateNode
     C:::templateNode
     n2:::processNode
     n3:::templateNode
     n4:::processNode
     n5:::templateNode
     n6:::processNode
     n7:::templateNode
    classDef templateNode fill:#f1ddf4,stroke:#ce9bd9,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px
```
### LME for time course
```mermaid
---
config:
  layout: fixed
---
flowchart TB
    C[("<b>modulated WM volume</b><br>MNISymC_WM/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßweekﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß_MNISymC_WM_mod(_FlipLR).nii.gz")] --> P1["scripts/lme_anat_tracts.py"]
    P1 --> D[("<b>time course for WMV in CST/MCP<br></b>lme/ﬂ°°60¶ßgroupﬂ°°62¶ß_MNISymC_WM_mod_ﬂ°°60¶ßCST/MCPﬂ°°62¶ß_lme.tsv")]
    n1[("<b>modulated GM volume</b><br>MNISymC_GM/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßweekﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß_MNISymC_GM_mod(_FlipLR).nii.gz")] --> n2["scripts/lme_cerebellum_tracts.py"]
    n2 --> n3[("<b>time course for GMV in cerebellar ROIs<br></b>lme/ﬂ°°60¶ßgroupﬂ°°62¶ß_MNISymC_GM_mod_Nettekoven2024_lme.tsv")]

    n2@{ shape: rect}
     C:::templateNode
     P1:::processNode
     D:::templateNode
     n1:::templateNode
     n2:::processNode
     n3:::templateNode
    classDef templateNode fill:#f1ddf4,stroke:#ce9bd9,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px
```
Analysis of the cerebellar cortex uses the functional parcellations of the cerebellum defined by the Nettekoven atlas [(Nettekoven et al., 2024)](https://doi.org/10.1038/s41467-024-52371-w).


## FaMap analysis pipeline

FaMap images are manually aligned and coregistered to the reference T1w anatomical (from first time point).
```mermaid
---
config:
  layout: fixed
---
flowchart TB
    C[("`**grey-scale FA map hdr, img**<br>DTI/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßweekﬂ°°62¶ß/coreg_T1MNI_TP1/FaMap_dc_ss.hdr<br>DTI/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßweekﬂ°°62¶ß/coreg_T1MNI_TP1/FaMap_dc_ss.img`")] --> P1["make_nifti_dti.py"]
    P1 --> D[("<b>grey-scale FA map Nifti<br></b>DTI/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßweekﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß_FaMap.nii")]
    D --> n1@{ label: "manual alignment<br>sc_anat('ANAT:coreg')" }
    n1 --> n2[("<b>co-registered grey-scale FA map Nifti<br></b>DTI/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßweekﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß_FaMap.nii")]
    n2 --> n3["te.reslice()"]
    n3 --> n4[("<b>normalized FaMap images<br></b>MNISymC_trans/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß_MNISymC_FaMap.nii")]
    n4 --> n5["flip_lesion.py"]
    n5 --> n6@{ label: "<b>left lesion flipped FaMap images<br></b>MNISymC_trans/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß__MNISymC_FaMap_FlipLR.nii<br><span style=\"--tw-border-spacing-y:\">**right lesion flipped FaMap images**</span><br>MNISymC_trans/ﬂ°°60¶ßsubjﬂ°°62¶ß/ﬂ°°60¶ßsubjﬂ°°62¶ß_ﬂ°°60¶ßweekﬂ°°62¶ß_MNISymC_FaMap.nii" }
    n6 --> n7["dataframes_FaMap_tracts.py"] & n8["lme_FaMap_tracts.py"]
    n7 --> n9[("<b>FA metrics in CST/MCP<br></b>MNISymC_trans/summary_MNISymC_CST_FaMap.tsv<br>MNISymC_trans/summary_MNISymC_CST_FaMap.tsv")]
    n8 --> n10@{ label: "<b>time course for FA metrics in CST/MCP<br></b>lme/patients_MNISymC_FaMap_CST_lme.tsv<br>lme/patients_MNISymC_FaMap_CST_lme.tsv<br style=\"--tw-border-spacing-y:\">" }

    n1@{ shape: rect}
    n3@{ shape: rect}
    n5@{ shape: rect}
    n6@{ shape: cylinder}
    n7@{ shape: rect}
    n8@{ shape: rect}
    n10@{ shape: cylinder}
     C:::templateNode
     P1:::processNode
     D:::templateNode
     n1:::processNode
     n2:::templateNode
     n3:::processNode
     n4:::templateNode
     n5:::processNode
     n6:::templateNode
     n7:::processNode
     n8:::processNode
     n9:::templateNode
     n10:::templateNode
    classDef templateNode fill:#f1ddf4,stroke:#ce9bd9,stroke-width:1.5px,color:#333,font-family:Arial,font-size:12px
    classDef processNode fill:#f7f5e4,stroke:#e0b96a,stroke-width:1.5px,color:#333,font-family:monospace,font-size:12px
    style C fill:#C8E6C9,stroke:#00C853
    style D fill:#C8E6C9,stroke:#00C853
    style n2 stroke:#00C853,fill:#C8E6C9
    style n4 fill:#C8E6C9,stroke:#00C853
    style n6 stroke:#00C853,fill:#C8E6C9
    style n9 stroke:#00C853,fill:#C8E6C9
    style n10 stroke:#00C853,fill:#C8E6C9
```
