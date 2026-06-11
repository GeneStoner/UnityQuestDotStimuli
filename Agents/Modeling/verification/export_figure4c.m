% export_figure4c.m
%
% Run R&H 2009 Figure 4C (Martinez-Trujillo & Treue 2002 attentional
% modulation as a function of contrast) and export the raw attCRF /
% unattCRF arrays plus the contrasts to a CSV.  The CSV is the ground
% truth our Python port has to match.
%
% Run from this directory after adding the attentionModel/ folder to
% the path:
%
%     addpath('../reference_code/attentionModel');
%     numContrasts = 9;
%     export_figure4c
%

addpath('../reference_code/attentionModel');

if ~exist('numContrasts', 'var')
  numContrasts = 9;
end

% Figure4C.m sets up the scenario and ends with a plot; capture the
% variables it leaves in the workspace.
Figure4C;

% Save: contrast, response with attention "away", response with
% attention on the null stimulus inside the RF.
T = table(contrasts(:), unattCRF(:), attCRF(:), ...
    'VariableNames', {'contrast', 'unattCRF', 'attCRF'});
out_path = 'figure4c_matlab.csv';
writetable(T, out_path);

fprintf('wrote %s with %d contrast points\n', out_path, numContrasts);
fprintf('cRange = [%.1e .. %.1e]\n', contrasts(1), contrasts(end));
disp(T);
