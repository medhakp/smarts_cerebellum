# Scripts for cerebellar analysis

## Pipelines

Here we offer several pipelines for cerebellar analysis; these pipelines take an image (e.g. anatomical, segmenetation, slope from regression) from native space to a template space.

1. **native_coreg_regression**: full-image coregistration of each anatomical to its reference week; apply affine to segmenetations; perform regression on images in native space.\
    
  - images from this pipeline can be used as a "ground-truth"
    
2. **MNISym_coreg_normalize**: full-image coregistration of each anatomical to its reference week; use the affine from this step to get the segementations (c1, ..., c5); normalize to MNI Symmetric template.

3. **MNISym_coreg_regression**: follow-up to MNISym_coreg_normalize: take the normalized images from this pipeline and run regression.

4. **MNISym_coreg_cerebellum_normalize**: cerebellum-only coregistration (see cerebellar_alignment_tutorial - LINK COMING); normalize into MNI Symmetric space.


**Notes**

- All pipelines follow a **naming convention**: {level}_{algorithm} where *level* = native or template (specify - e.g. MNISym, SUIT); *algorithms* are written in order of application.

- Any pipeline or image with *just* **coreg** in the name refers to **full-image coregistration**, which is taken as the default; other types, such as cerebellum-only coregistration, are specified (e.g. coreg_cerebellum)
