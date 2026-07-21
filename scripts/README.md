# Scripts for cerebellar analysis

## Pipeline

1. Manually align images
2. coregister each T1 anatomical to its reference anatomical (`sc_anat.m`)
3. segment tissues (`sc_anat.m`)
4. isolate cerebellum
5. generate transformation files
6. normalize images: T1 anatomical, segmentations of wm, gm, csf
7. modulate tissue volumes (for wm, gm, csf)
8. run regression on T1 anatomical and on modulated tissue volumes
9. flip slope image to right (for patients with left lesion)
10. summarize data: create summary image (mean, median of slope); summarize ROIs in dataframe
