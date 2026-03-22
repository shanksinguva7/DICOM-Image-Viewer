%% dicom_viewer.m
%  MATLAB parallel to the Python DICOM Viewer.
%  Loads a folder of .dcm files, displays axial/sagittal/coronal slices,
%  and exports key metadata to a CSV file.
%
%  Usage:
%    Run directly in MATLAB — set DATA_FOLDER to your .dcm directory.
%    >> dicom_viewer

% ── Configuration ────────────────────────────────────────────────────────────
DATA_FOLDER  = fullfile('..', 'data');      % folder with .dcm files
OUTPUT_CSV   = fullfile('..', 'output', 'metadata.csv');

% ── 1. LOAD ───────────────────────────────────────────────────────────────────
files = dir(fullfile(DATA_FOLDER, '*.dcm'));
if isempty(files)
    error('[loader] No .dcm files found in: %s', DATA_FOLDER);
end

fprintf('[loader] Found %d DICOM files.\n', numel(files));

% Read first slice to get dimensions
info1 = dicominfo(fullfile(DATA_FOLDER, files(1).name));
[rows, cols] = deal(info1.Rows, info1.Columns);

% Pre-allocate 3D volume  (H x W x Z)
volume = zeros(rows, cols, numel(files), 'double');

% Sort by ImagePositionPatient Z, fallback to filename order
zPos = zeros(numel(files), 1);
for k = 1:numel(files)
    try
        inf = dicominfo(fullfile(DATA_FOLDER, files(k).name));
        zPos(k) = inf.ImagePositionPatient(3);
    catch
        zPos(k) = k;
    end
end
[~, sortIdx] = sort(zPos);

for k = 1:numel(files)
    idx  = sortIdx(k);
    path = fullfile(DATA_FOLDER, files(idx).name);
    img  = double(dicomread(path));

    % Apply rescale slope / intercept if present
    inf = dicominfo(path);
    slope     = 1;  intercept = 0;
    if isfield(inf, 'RescaleSlope'),     slope     = inf.RescaleSlope;     end
    if isfield(inf, 'RescaleIntercept'), intercept = inf.RescaleIntercept; end
    volume(:, :, k) = img .* slope + intercept;
end

fprintf('[loader] Volume size: %d x %d x %d\n', rows, cols, numel(files));

% ── 2. DISPLAY ────────────────────────────────────────────────────────────────
Z  = size(volume, 3);
Hz = round(Z / 2);
Hx = round(cols / 2);
Hy = round(rows / 2);

fig = figure('Color', [0.08 0.08 0.14], 'Name', 'DICOM Viewer', ...
             'NumberTitle', 'off', 'Position', [100 100 1200 420]);

% Helper: normalize slice to [0,1]
norm_slice = @(sl) (sl - min(sl(:))) / max(max(sl(:)) - min(sl(:)), eps);

subplot(1,3,1);
imagesc(norm_slice(volume(:,:,Hz))); colormap gray; axis image off;
title('Axial',    'Color', 'w', 'FontSize', 12, 'FontWeight', 'bold');

subplot(1,3,2);
imagesc(norm_slice(squeeze(volume(:,Hx,:)))); colormap gray; axis image off;
title('Sagittal', 'Color', 'w', 'FontSize', 12, 'FontWeight', 'bold');

subplot(1,3,3);
imagesc(norm_slice(squeeze(volume(Hy,:,:)))); colormap gray; axis image off;
title('Coronal',  'Color', 'w', 'FontSize', 12, 'FontWeight', 'bold');

set(gcf, 'Color', [0.08 0.08 0.14]);

% ── 3. METADATA EXPORT ────────────────────────────────────────────────────────
TAGS = { ...
    'PatientName',              'PatientID',            'PatientAge', ...
    'PatientSex',               'Modality',             'StudyDate', ...
    'StudyDescription',         'SeriesDescription',    'SliceThickness', ...
    'Rows',                     'Columns',              'BitsAllocated', ...
    'Manufacturer',             'InstitutionName',      'InstanceNumber' ...
};

% Build cell array: rows = slices, columns = tags
nSlices = numel(files);
nTags   = numel(TAGS);
tableData = cell(nSlices, nTags + 1);   % +1 for Filename column

for k = 1:nSlices
    idx  = sortIdx(k);
    path = fullfile(DATA_FOLDER, files(idx).name);
    inf  = dicominfo(path);

    tableData{k, 1} = files(idx).name;
    for t = 1:nTags
        tag = TAGS{t};
        if isfield(inf, tag)
            val = inf.(tag);
            if isnumeric(val)
                tableData{k, t+1} = num2str(val);
            elseif ischar(val)
                tableData{k, t+1} = val;
            else
                tableData{k, t+1} = char(val);
            end
        else
            tableData{k, t+1} = 'N/A';
        end
    end
end

% Write CSV
outDir = fileparts(OUTPUT_CSV);
if ~isfolder(outDir), mkdir(outDir); end

fid = fopen(OUTPUT_CSV, 'w');
headers = ['Filename', TAGS];
fprintf(fid, '%s\n', strjoin(headers, ','));
for k = 1:nSlices
    row = tableData(k, :);
    % Escape commas within fields
    row = cellfun(@(s) ['"' strrep(s, '"', '""') '"'], row, 'UniformOutput', false);
    fprintf(fid, '%s\n', strjoin(row, ','));
end
fclose(fid);

fprintf('[metadata] Exported → %s\n', fullfile(pwd, OUTPUT_CSV));
fprintf('[main] Done.\n');
