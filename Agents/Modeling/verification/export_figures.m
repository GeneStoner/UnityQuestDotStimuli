% export_figures.m
%
% Run every R&H 2009 figure-reproduction script and export its primary
% output arrays to per-figure CSV files. The Python comparison harness
% (compare_figures.py) reads these CSVs and diffs them against its
% port of attentionModel.m.
%
% Run from this directory:
%     /Applications/MATLAB_R2026a.app/bin/matlab -batch "numContrasts = 9; numOrientations = 9; export_figures"
%

addpath('../reference_code/attentionModel');

if ~exist('numContrasts',   'var'); numContrasts   = 9; end
if ~exist('numOrientations','var'); numOrientations = 9; end

% Wrap each Figure script so the variables it leaves in the workspace
% can be picked up and written out.

% ---- CRF figures (output: contrasts, unattCRF, attCRF) -----------------
crf_figs = {'Figure2A', 'Figure2B', 'Figure3C', 'Figure3F', 'Figure4C', 'Figure4E'};
for k = 1:length(crf_figs)
  name = crf_figs{k};
  clear contrasts unattCRF attCRF;
  evalin('base', name);
  out_path = sprintf('%s_matlab.csv', lower(name));
  T = table(contrasts(:), unattCRF(:), attCRF(:), ...
            'VariableNames', {'contrast', 'unattCRF', 'attCRF'});
  writetable(T, out_path);
  fprintf('wrote %s\n', out_path);
end

% ---- Tuning-curve figures (output: theta, unattCRF, attCRF over θ) -----
tc_figs = {'Figure5C', 'Figure6C'};
for k = 1:length(tc_figs)
  name = tc_figs{k};
  clear theta unattCRF attCRF;
  evalin('base', name);
  out_path = sprintf('%s_matlab.csv', lower(name));
  T = table(theta(:), unattCRF(:), attCRF(:), ...
            'VariableNames', {'theta', 'unattCRF', 'attCRF'});
  writetable(T, out_path);
  fprintf('wrote %s\n', out_path);
end

% ---- Figure 7C: orientation sweep with 6 attention conditions ----------
clear orientations pair_att_vars pair_att_nulls pair_att_aways ...
      Var_att_vars Null_att_nulls Var_att_aways;
evalin('base', 'Figure7C');
T = table(orientations(:), pair_att_vars(:), pair_att_nulls(:), ...
          pair_att_aways(:), Var_att_vars(:), Null_att_nulls(:), ...
          Var_att_aways(:), ...
          'VariableNames', {'orientation', 'pair_att_var', ...
                            'pair_att_null', 'pair_att_away', ...
                            'Var_att_var', 'Null_att_null', ...
                            'Var_att_away'});
writetable(T, 'figure7c_matlab.csv');
fprintf('wrote figure7c_matlab.csv\n');

fprintf('\nAll figures exported.\n');
