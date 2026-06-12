function varargout = sc_coreg_cerebellum(what, varargin)
% to run: function_name(case)

% part of the cerebellar_alignment pipeline (stage: processing images --> affine from cerebellar-only-alignment)

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
    cerebelDir = 'cerebellar_alignment'; % directory for cerebellar-only images

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
                
                srcFile = fullfile(baseDir, anatomicalDir, subj_id, cerebelDir, week, sprintf('%s_%s_T1_cerebellum_only.nii', subj_id, week));
                refFile = fullfile(baseDir, anatomicalDir, subj_id, cerebelDir, refT1, sprintf('%s_%s_T1_cerebellum_only.nii', subj_id, refT1));
            
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
            
        end
    end
end