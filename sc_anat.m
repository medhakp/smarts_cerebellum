% Segmentation + Normalization. Manually check results when
% done. This step creates five files named
% c1<subj_id>_anatomical.nii, c2<subj_id>_anatomical.nii,
% c3<subj_id>_anatomical.nii, c4<subj_id>_anatomical.nii,
% c5<subj_id>_anatomical.nii, in the
% <project_id>/anatomicals/<subj_id>/ directory. Each of these
% files contains a segment (e.g., white matter, grey matter) of
% the centered anatomical image.

% The output images correspond to the native parameter. For the
% first five tissues, native is set to [1 0], which means that
% the native space segmented images are saved. For the sixth
% tissue (background), native is set to [0 0], which means that
% no native space segmented image is saved for this tissue.

% Thus, the code is designed to create segmentation for six tissue classes,
% but only the first five are saved as output files (c1 to c5). The sixth
% tissue class (background) does not produce an output image because its
% native parameter is set to [0 0]. This is why you only see five output
% images, despite the code handling six tissue classes.

participant_list = {'CU_2310', 'CU_2538', 'CU_2663', 'CU_2697', 'CU_2925'...
    'JHU_2282', 'JHU_2374', 'JHU_2395', 'JHU_2531', 'JHU_2577', 'JHU_2650'...
    'JHU_2684', 'JHU_2713', 'JHU_2789', 'JHU_3175', 'JHU_3176'....
    'UZ_2365', 'UZ_2450', 'UZ_2565', 'UZ_2595', 'UZ_2652', 'UZ_2654'...
    'UZ_2906', 'UZ_3030', 'UZ_3057', 'UZ_3151', 'UZ_3158','UZ_3166'...
    'UZ_3224', 'UZ_3226', 'UZ_3227', 'UZ_3228', 'UZ_3238', 'UZ_3239'...
    'UZ_3240', 'UZ_3241', 'UZ_3243', 'UZ_3246', 'UZ_3247', 'UZ_3248'...
    'CUP_1001', 'CUP_1002', 'JHP_1001', 'JHP_1002', 'JHP_1004'...
    'UZP_1001', 'UZP_1002', 'UZP_1004', 'UZP_1005', 'UZP_1006', 'UZP_1006'...
    'UZP_1007', 'UZP_1008'};

for p = 1:length(participant_list)

    subj_id = participant_list{p};

    % remote desktop
    path = ['/cifs/diedrichsen/data/smarts_cerebellum/' subj_id];

    % local machine
    %path = ['/Users/medha/Desktop/USRI 2026/smarts_cerebellum/anatomicals' subj_id];

    week_list = {'W0', 'W4', 'W12', 'W24', 'W52'};

    for w = 1:length(week_list)
        week = week_list{w};
        
        subj_anat = fullfile(path, week, sprintf('%s_%s_T1.nii', subj_id, week));

    end

    SPMhome=fileparts(which('spm.m'));
    J=[];

    J.channel.vols     = {subj_anat};
    J.channel.biasreg  = 0.001;
    J.channel.biasfwhm = 60;
    J.channel.write    = [1 0];
    J.tissue(1).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,1')};
    J.tissue(1).ngaus  = 1;
    J.tissue(1).native = [1 0];
    J.tissue(1).warped = [0 0];
    J.tissue(2).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,2')};
    J.tissue(2).ngaus  = 1;
    J.tissue(2).native = [1 0];
    J.tissue(2).warped = [0 0];
    J.tissue(3).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,3')};
    J.tissue(3).ngaus  = 2;
    J.tissue(3).native = [1 0];
    J.tissue(3).warped = [0 0];
    J.tissue(4).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,4')};
    J.tissue(4).ngaus  = 3;
    J.tissue(4).native = [1 0];
    J.tissue(4).warped = [0 0];
    J.tissue(5).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,5')};
    J.tissue(5).ngaus  = 4;
    J.tissue(5).native = [1 0];
    J.tissue(5).warped = [0 0];
    J.tissue(6).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,6')};
    J.tissue(6).ngaus  = 2;
    J.tissue(6).native = [0 0];
    J.tissue(6).warped = [0 0];

    J.warp.mrf     = 1;
    J.warp.cleanup = 1;
    J.warp.reg     = [0 0.001 0.5 0.05 0.2];
    J.warp.affreg  = 'mni';
    J.warp.fwhm    = 0;
    J.warp.samp    = 3;
    J.warp.write   = [1 1];
    matlabbatch{1}.spm.spatial.preproc=J;
    spm_jobman('run',matlabbatch);

end