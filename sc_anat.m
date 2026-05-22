function varargout = sc_anat(what, varargin)
    % DESCRIPTION:
    % 

    % Requires a participants.tsv file in the baseDir with columns
    % sn: subject number (int)

    % Use a different baseDir when using your local machine or the cbs
    % server. Add more directory if needed.
    
    path = 'Documents/';
    addpath([path 'GitHub/spmj_tools/'])
    addpath([path 'GitHub/dataframe/pivot/'])

    % paths for my directories
    addpath('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum')

    if isfolder("/cifs/diedrichsen/data/smarts_cerebellum/")
        baseDir = "/cifs/diedrichsen/data/smarts_cerebellum/";
    else
        fprintf('Workdir not found. Mount or connect to server and try again.');
    end

    anatomicalDir = 'anatomicals'; % anatomical files (individual space)

    sn=[];
    week=[];
    centre=[];
    vararginoptions(varargin,{'sn', 'week', 'centre'})
    if isempty(sn)
        error('''sn'' must be passed to this function.')
    end

    if isempty(week)
        error('''week'' must be passed to this function.')
    end

    if isempty(week)
        error('''centre'' must be passed to this function.')
    end
    
    pinfo = dload(fullfile(baseDir,'participants.tsv'));

    subj_row=getrow(pinfo, pinfo.ID==sn & strcmp(pinfo.Centre, centre) & strcmp(pinfo.Week, week));
    refT1 = subj_row.RefT1{1};
    subj_id = [centre '_' num2str(sn)];

    switch(what)

        case 'ANAT:segment'
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

            anat_path = fullfile(baseDir,anatomicalDir,subj_id,[subj_id '_anatomical.nii,1']);

            % spmj_segmentation(anat_path);
            SPMhome=fileparts(which('spm.m'));
            J=[];
            % for s=sn WE DONT NEED THIS FOR LOOP 
            J.channel.vols = {anat_path};
            J.channel.biasreg = 0.001;
            J.channel.biasfwhm = 60;
            J.channel.write = [0 0];
            J.tissue(1).tpm = {fullfile(SPMhome,'tpm/TPM.nii,1')}; % grey matter
            J.tissue(1).ngaus = 1;
            J.tissue(1).native = [1 0];
            J.tissue(1).warped = [0 0];
            J.tissue(2).tpm = {fullfile(SPMhome,'tpm/TPM.nii,2')}; % white matter
            J.tissue(2).ngaus = 1;
            J.tissue(2).native = [1 0];
            J.tissue(2).warped = [0 0];
            J.tissue(3).tpm = {fullfile(SPMhome,'tpm/TPM.nii,3')}; % CSF
            J.tissue(3).ngaus = 2; 
            J.tissue(3).native = [1 0];
            J.tissue(3).warped = [0 0];
            J.tissue(4).tpm = {fullfile(SPMhome,'tpm/TPM.nii,4')}; % soft tissue
            J.tissue(4).ngaus = 3;
            J.tissue(4).native = [1 0];
            J.tissue(4).warped = [0 0];
            J.tissue(5).tpm = {fullfile(SPMhome,'tpm/TPM.nii,5')}; % bone
            J.tissue(5).ngaus = 4;
            J.tissue(5).native = [1 0];
            J.tissue(5).warped = [0 0];
            J.tissue(6).tpm = {fullfile(SPMhome,'tpm/TPM.nii,6')}; % NOT SAVED
            J.tissue(6).ngaus = 2;
            J.tissue(6).native = [0 0];
            J.tissue(6).warped = [0 0];
            J.warp.mrf = 1;
            J.warp.cleanup = 1;
            J.warp.reg = [0 0.001 0.5 0.05 0.2];
            J.warp.affreg = 'mni';
            J.warp.fwhm = 0;
            J.warp.samp = 3;
            J.warp.write = [1 1];
            matlabbatch{1}.spm.spatial.preproc=J;
            spm_jobman('run',matlabbatch);

        case 'ANAT:coreg'                                                      
            % coregister rbumean image to anatomical image for each session

            % (1) Manually seed the functional/anatomical registration
            % - Open fsleyes
            % - Add anatomical image and b*mean*.nii (bias corrected mean) image to overlay
            % - click on the bias corrected mean image in the 'Overlay
            %   list' in the bottom left of the fsleyes window.
            %   list to highlight it.
            % - Open tools -> Nudge
            % - Manually adjust b*mean*.nii image to the anatomical by 
            %   changing the 6 paramters (tranlation xyz and rotation xyz) 
            %   and Do not change the scales! 
            % - When done, click apply and close the tool tab. Then to save
            %   the changes, click on the save icon next to the mean image 
            %   name in the 'Overlay list' and save the new image by adding
            %   'r' in the beginning of the name: rb*mean*.nii. If you don't
            %   set the format to be .nii, fsleyes automatically saves it as
            %   a .nii.gz so either set it or gunzip afterwards to make it
            %   compatible with SPM.
            
            % (2) Run automated co-registration to register bias-corrected meanimage to anatomical image

            srcFile = fullfile(baseDir, anatomicalDir, subj_id, week, sprintf('%s_%s_T1.nii', subj_id, week));
            refFile = fullfile(baseDir, anatomicalDir, subj_id, refT1, sprintf('%s_%s_T1.nii', subj_id, refT1));
            
            if exist(srcFile, 'file') ~= 2
                error('sc_anat:sourceMissing', 'Source image not found: %s', srcFile);
            end
            if exist(refFile, 'file') ~= 2
                error('sc_anat:refMissing', 'Reference image not found: %s', refFile);
            end
            
            % Force char (guards against string type sneaking in from subj_id/week/refT1)
            srcFile = char(srcFile);
            refFile = char(refFile);
            
            J.source = {srcFile};
            J.ref    = {refFile};
            J.other  = {''};
            
            % Validate that source and ref are proper cellstr (what SPM requires)
            if ~iscellstr(J.source)
                error('sc_anat:badSource', ...
                    'J.source must be a cellstr. Got class %s, inner class %s.', ...
                    class(J.source), class(J.source{1}));
            end
            if ~iscellstr(J.ref)
                error('sc_anat:badRef', ...
                    'J.ref must be a cellstr. Got class %s, inner class %s.', ...
                    class(J.ref), class(J.ref{1}));
            end

            J.other = {''};
            J.eoptions.cost_fun = 'nmi';
            J.eoptions.sep = [4 2];
            J.eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];
            J.eoptions.fwhm = [7 7];
            matlabbatch{1}.spm.spatial.coreg.estimate=J;
            spm_jobman('run',matlabbatch);
                
    end

end


% % Segmentation + Normalization. Manually check results when
% % done. This step creates five files named
% % c1<subj_id>_anatomical.nii, c2<subj_id>_anatomical.nii,
% % c3<subj_id>_anatomical.nii, c4<subj_id>_anatomical.nii,
% % c5<subj_id>_anatomical.nii, in the
% % <project_id>/anatomicals/<subj_id>/ directory. Each of these
% % files contains a segment (e.g., white matter, grey matter) of
% % the centered anatomical image.
% 
% % The output images correspond to the native parameter. For the
% % first five tissues, native is set to [1 0], which means that
% % the native space segmented images are saved. For the sixth
% % tissue (background), native is set to [0 0], which means that
% % no native space segmented image is saved for this tissue.
% 
% % Thus, the code is designed to create segmentation for six tissue classes,
% % but only the first five are saved as output files (c1 to c5). The sixth
% % tissue class (background) does not produce an output image because its
% % native parameter is set to [0 0]. This is why you only see five output
% % images, despite the code handling six tissue classes.
% 
% clear
% clc
% close all
% 
% 
% participant_list = { 'CU_2538', 'CU_2663', 'CU_2697', 'CU_2925'...
%     'JHU_2282', 'JHU_2374', 'JHU_2395', 'JHU_2531', 'JHU_2577', 'JHU_2650'...
%     'JHU_2684', 'JHU_2713', 'JHU_2789', 'JHU_3175', 'JHU_3176'....
%     'UZ_2365', 'UZ_2450', 'UZ_2565', 'UZ_2595', 'UZ_2652', 'UZ_2654'...
%     'UZ_2906', 'UZ_3030', 'UZ_3057', 'UZ_3151', 'UZ_3158','UZ_3166'...
%     'UZ_3224', 'UZ_3226', 'UZ_3227', 'UZ_3228', 'UZ_3238', 'UZ_3239'...
%     'UZ_3240', 'UZ_3241', 'UZ_3243', 'UZ_3246', 'UZ_3247', 'UZ_3248'...
%     'CUP_1001', 'CUP_1002', 'JHP_1001', 'JHP_1002', 'JHP_1004'...
%     'UZP_1001', 'UZP_1002', 'UZP_1004', 'UZP_1005', 'UZP_1006', 'UZP_1006'...
%     'UZP_1007', 'UZP_1008'};
% 
% 
% for p = 1:length(participant_list)
% 
%     subj_id = participant_list{p};
% 
%     % remote desktop
%     path = ['/cifs/diedrichsen/data/smarts_cerebellum/anatomicals/' subj_id];
% 
%     % local machine
%     %path = ['/Users/medha/Desktop/USRI 2026/smarts_cerebellum/anatomicals' subj_id];
% 
%     week_list = {'W0', 'W4', 'W12', 'W24', 'W52'};
% 
%     for w = 1:length(week_list)
%         week = week_list{w};
% 
%         % Reslice anatomical image within LPI coordinate systems
%         % packages: 
%         	% https://github.com/jdiedrichsen/suit/blob/master/vararginoptions.m and 
%         	% https://github.com/DiedrichsenLab/spmj_tools/tree/main
% 
%             % (1) Reslice anatomical image to set it within LPI co-ordinate frames
%             source  = fullfile(path, week, sprintf('%s_%s_T1.nii', subj_id, week));
%             if isfile(source)
%                 dest = fullfile(path,week,sprintf('%s_%s_T1w_LPI.nii', subj_id, week));
%                 spmj_reslice_LPI(source,'name', dest);
%                 fprintf('Manually retrieve the location of the anterior commissure (x,y,z) before continuing')
% 
%             end
% 
%         subj_anat = fullfile(path, week, sprintf('%s_%s_T1w_LPI.nii', subj_id, week)); % use LPI resliced img
% 
%         SPMhome=fileparts(which('spm.m'));
% 
%         if isfile(subj_anat)
% 
%             J=[];
%             J.channel.vols     = {subj_anat};
%             J.channel.biasreg  = 0.001;
%             J.channel.biasfwhm = 60;
%             J.channel.write    = [1 0];
%             J.tissue(1).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,1')};
%             J.tissue(1).ngaus  = 1;
%             J.tissue(1).native = [1 0];
%             J.tissue(1).warped = [0 0];
%             J.tissue(2).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,2')};
%             J.tissue(2).ngaus  = 1;
%             J.tissue(2).native = [1 0];
%             J.tissue(2).warped = [0 0];
%             J.tissue(3).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,3')};
%             J.tissue(3).ngaus  = 2;
%             J.tissue(3).native = [1 0];
%             J.tissue(3).warped = [0 0];
%             J.tissue(4).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,4')};
%             J.tissue(4).ngaus  = 3;
%             J.tissue(4).native = [1 0];
%             J.tissue(4).warped = [0 0];
%             J.tissue(5).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,5')};
%             J.tissue(5).ngaus  = 4;
%             J.tissue(5).native = [1 0];
%             J.tissue(5).warped = [0 0];
%             J.tissue(6).tpm    = {fullfile(SPMhome,'tpm/TPM.nii,6')};
%             J.tissue(6).ngaus  = 2;
%             J.tissue(6).native = [0 0];
%             J.tissue(6).warped = [0 0];
% 
%             J.warp.mrf     = 1;
%             J.warp.cleanup = 1;
%             J.warp.reg     = [0 0.001 0.5 0.05 0.2];
%             J.warp.affreg  = 'mni';
%             J.warp.fwhm    = 0;
%             J.warp.samp    = 3;
%             J.warp.write   = [1 1];
%             matlabbatch{1}.spm.spatial.preproc=J;
%             spm_jobman('run',matlabbatch);
%         end
%     end
% end
