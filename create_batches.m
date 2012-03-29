
%
% Creates the batches (m-files) to launch simulations.
% Run this:
%  create_batches

global baui ba_uivals ba_stat

%basefile = 'phdiv_pixscaletestmar12.m'
%basefile = 'phdiv_pixscaletest_gersamar12.m'

%basefile = 'runPD0.m'
%basefile = 'runGS.m'

if ~exist('basefile', 'var')
  basefile = input('Give the basefile: ', 's');
end

fprintf('basefile: %s\n', basefile);
reply = input('Correct? (y/n): ', 's');
if reply ~= 'y'
  fprintf('ARGHH!!');
  pause
end

workdir = pwd;
fprintf('The working directory is: %s\n', workdir);


nsimulbatch = 128;

ba_stat.nsimulbatch     = nsimulbatch;
ba_uivals.max_batchsize = 10000;
ba_stat.n_basescriptfiles = 1;
ba_stat.basescriptfiles = ...
    {[workdir '/' basefile]};

% Create a set of batch files.
ba_bx

nbatch = ba_stat.n_batchfiles(1);

% Move them to the results folder
for i=1:nbatch
  system(['mv ' ba_stat.batchfiles{1, i} ' ./results/']);
end

% Create a launcher scripts
for i=1:nbatch
  batchname = file_basename(ba_stat.batchfiles{1, i});
  fid = fopen(['./results/' batchname  '_launcher'], 'wt');
  fprintf(fid, ['']);
  % fprintf(fid, ['#PBS -l nodes=1:ppn=8\n']);
  % fprintf(fid, ['#PBS -l nodes=1:ppn=4\n']);
  fprintf(fid, ['#PBS -l procs=1\n']);
  fprintf(fid, ['#PBS -l walltime=4:24:30:00\n']);
  fprintf(fid, ['#PBS -q batch \n']);
  fprintf(fid, ['#PBS -V \n']);
  fprintf(fid, ['cd $PBS_O_WORKDIR \n']);
  fprintf(fid, ['# Launch application \n']);
  fprintf(fid, ['octave ' batchname ' > ' batchname '.log\n']);
  fprintf(fid, ['\n']);
  fprintf(fid, ['\n']);
  fclose(fid);
end


% Run the batches by monitoring script that keep trach how many jobs are
% going on.
%
%   run_batches
