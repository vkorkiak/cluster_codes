%
% Runs the batches created by script create_batches.
%
function run_batches_func(batchnames, nsimulbatch, varargin)

usemaster = 0;
useqsub   = 1;
runcmd    = 'octave'; % default
resufile  = '_results.mat' 

sti=1;
while sti <= length(varargin)
  if ~ischar(varargin{sti})
    error('run_batches_func: problems with argument list\n.');
  end
  
  if strcmp(varargin{sti}, 'usemaster')
    usemaster = 1;
    useqsub   = 0;
    sti = sti+1;
  elseif strcmp(varargin{sti}, 'runcmd')
    runcmd = varargin{sti+1};
    sti = sti+2;
  elseif strcmp(varargin{sti}, 'resufile')
    resufile = varargin{sti+1};
    sti = sti+2;
  else
    fprintf('invalid argument list.')
    return;
  end
end
  
nbatch    = size(batchnames, 1);
batchinds = zeros(nsimulbatch,1);
batchruns = zeros(nsimulbatch,1);

for i=1:nbatch
  % Let's first wait for most idle processes to finish
  wait_for_idles(1);
  
  % Then, let's wait until at most nsimulbatch are running. Useful, if
  % more than one batches are launched simultaneously.
  % wait_for_runnings(nsimulbatch);

  % Is there space in the batch?
  % Lets wait until there is space
  while sum(batchruns) >= nsimulbatch
    for u=1:nsimulbatch
      if batchruns(u)
	outfile = ['./results/' file_basename(batchnames{batchinds(u)}) resufile]; 
	if exist(outfile, 'file')
	  batchruns(u) = 0;
	end
      end
    end
    sleep(2);
  end

    
  batchpos = min(find(batchruns == 0));
  outfile    = ['./results/' file_basename(batchnames{i}) '_results.mat']; 

  if useqsub
    % Start the background job
    if exist(outfile, 'file')
      fprintf('EXISTS: %s\n', outfile);
    else
      fprintf('%d: --- batchfile %s starts...\n', i, batchnames{i});
      system(['cd results ; qsub ' file_basename(batchnames{i}) '_launcher']);
    end
  end
  if usemaster
    fprintf('%d: --- launching on master %s...\n', i, batchnames{i});
    system(['cd results ; ' runcmd ' ' file_basename(batchnames{i})]);        
  end

  batchinds(batchpos) = i;
  batchruns(batchpos) = 1;
end

end
