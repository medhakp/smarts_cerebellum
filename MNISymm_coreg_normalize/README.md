# MNISymm_coreg_normalize

## ROUGH readme

**Pipeline**

- [x] native space images --> whole-image coregistration to reference image (where *reference* is the first image available from that subject)
- [ ] (rerun) isolate cerebellum
- [ ] (rerun) Using the coregistered images: create normalization files for MNI symmetric template
- [ ] normalize to the MNI symmetric template (using `reslice`) (for each subject-week):
    - [ ] white matter segmentations
    - [ ] grey matter segmentations
    - [ ] T1 anatomicals 
