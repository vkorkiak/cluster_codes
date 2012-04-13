
%
% Creates the batches (m-files) to launch simulations.
% Run this:
%  create_batches

more off

if ~exist('nsimulbatch', 'var')
  nsimulbatch=128;
  fprintf('nsimulbatch was set to %d. Please set it is nice!!\n', nsimulbatch);
end

if ~exist('basefile', 'var')
  basefile = input('Give the basefile: ', 's');
end

if ~exist('dowrite', 'var')
  dowrite = 0;
  fprintf('Your batches are not written to disk! To do that, type:\n');
  fprintf('dowrite=1\n');
end

fprintf('basefile: %s\n', basefile);
reply = input('Correct? (y/n): ', 's');
if reply ~= 'y'
  fprintf('ARGHH!!');
  pause
end

workdir = pwd;
fprintf('The working directory is: %s\n', workdir);

% No modvalsf
modvals = {'foo'};

fprintf('Creating the batches. dowrite = %d.\n', dowrite);
if ~dowrite
  [batchlen, all_nicks, all_batchfiles] = create_batches_func(basefile, modvals, 1);
else
  [batchlen, all_nicks, all_batchfiles] = create_batches_func(basefile, modvals);
end

fprintf('nsimulbatch is %d\n');
fprintf('Run your batches by writing:\n');
fprintf('run_batches\n');
