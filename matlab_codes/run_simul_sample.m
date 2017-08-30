
%
% Launches the batches for SPD simulation
%

simulfile  = 'the_base_file.py';
runcmd     = 'python';

% How many jobs can run simultaneously
nsimulbatch = 128; % Default

% See how the many simulations we would get (no disk operations)
[len, nicks, files] = create_batches_func(simulfile, [], 0, runcmd);

% Create the individual script files
[len, nicks, files] = create_batches_func(simulfile, [], 1, runcmd);


% Run the simulation using the scheduler
run_batches_func(files, nsimulbatch, 'runcmd', runcmd, 'resufile', '_results.mat');


