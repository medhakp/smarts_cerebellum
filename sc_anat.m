function varargout = sc_anat(what, varargin)

% to run: function_name(case)

    path = 'Documents/';
    addpath([path 'GitHub/spmj_tools/'])
    addpath([path 'GitHub/dataframe/pivot/'])
    
    % paths for my directories
    addpath('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum')
    addpath('Documents/GitHub/dataframe/util/') % read tsv as MAT
    addpath('/home/UWO/mporwal2/Downloads/spm12-main')
    addpath('/home/UWO/mporwal2/Downloads/spmj_tools-main')
    
    if isfolder("/cifs/diedrichsen/data/smarts_cerebellum/")
        baseDir = "/cifs/diedrichsen/data/smarts_cerebellum/";
    else
        fprintf('Workdir not found. Mount or connect to server and try again.');
    end
    
    anatomicalDir = 'anatomicals'; % anatomical files (individual space)

    pinfo = dload(fullfile(baseDir,'participants_anat.tsv'));
    
    for i = 1:length(pinfo.ID)
        % get ID, center, week from each row
        sn = pinfo.ID(i);
        centre = pinfo.Centre{i};
        week = pinfo.Week{i};
        subj_id = [centre '_' num2str(sn)];
    
        % need to check if that row is for reference image; if yes, skip
        refT1 = pinfo.RefT1{i};
        if strcmp(week, refT1)
            continue % skips this row if row's T1 is the reference - compare the weeks
        end

        % now call function with params
        %vararginoptions(varargin,{'sn', sn, 'week', week, 'centre', centre})
    
        % from template_anat in spmj_tools, toolbox for SPM by Diedrichsen Lab
        % --> need to cite this properly!
        switch(what)

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
            
                %{
                if exist(srcFile, 'file') ~= 2
                    error('sc_anat:sourceMissing', 'Source image not found: %s', srcFile);
                end
                %}

                % need to have ref exist.
                if exist(refFile, 'file') ~= 2
                    error('sc_anat:refMissing', 'Reference image not found: %s', refFile);
                end
                
                %{
                % check which files are missing but in .tsv
                if ~isfile(srcFile)
                    disp(srcFile)
                end
                %}

                
                % skips if source file not found
                if isfile(srcFile)
                    
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
    
                subj_anat = fullfile(baseDir, anatomicalDir, subj_id, week, sprintf('%s_%s_T1.nii', subj_id, week));
   
                
                
                
                if isfile(subj_anat) % just in case
                    anat_path = fullfile(baseDir, anatomicalDir, subj_id, week, sprintf('%s_%s_T1.nii', subj_id, week));
                    anat_path = char(anat_path); % must be chars, not string

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


                end

            
        end
    end
end