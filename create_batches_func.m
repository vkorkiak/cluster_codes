%
% Creates the batches (m-files) to launch simulations.
% Run this:
%  create_batches(basefile, modparams)
%
function [batchlen, all_nicks, all_batchfiles] = ...
      create_batches_func(basefile, modvals, dowrite, runcmd)

if ~exist('dowrite', 'var')
  dowrite=1;  % By default, write to disk
else
  dowrite=0;  % Do not write the scripts to disk
end

if ~exist('basefile', 'var')
  error('basefile not defined');
end

if ~exist('runcmd', 'var')
  runcmd = 'octave'; % Default run command
end


workdir = pwd;
fprintf('The working directory is: %s\n', workdir);


full_basescriptfile = [workdir '/' basefile];

%
% Create a set of batch files.
%

% Do the expand
if ~exist('modvals', 'var')
  [batchlen, all_nicks, all_batchfiles] = ...
      expand_basescript(workdir, basefile, {}, dowrite);
else
  [batchlen, all_nicks, all_batchfiles] = ...
      expand_basescript(workdir, basefile, modvals, dowrite);
end
  
fprintf('\n');
fprintf('Batches created.\n');

nbatch = size(all_batchfiles, 1);

if dowrite
  
  % Move them to the results folder
  for i=1:nbatch
    system(['mv ' all_batchfiles{i} ' ./results/']);
  end
  
  % Create a launcher scripts
  for i=1:nbatch
    batchname = file_basename(all_batchfiles{i});
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
    fprintf(fid, [runcmd ' ' batchname ' > ' batchname '.log\n']);
    fprintf(fid, ['\n']);
    fprintf(fid, ['\n']);
    fclose(fid);
  end
end

% Run the batches by monitoring script that keep trach how many jobs are
% going on.
%
%   run_batches

end
