
%
% Runs the batches created by script create_batches.
%

nsimulbatch = ba_stat.nsimulbatch;
nbatch      = ba_stat.n_batchfiles(1);
batchnames  = ba_stat.batchfiles;

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
	outfile = ['./results/' file_basename(batchnames{1,batchinds(u)}) '_results.mat']; 
	if exist(outfile, 'file')
	  batchruns(u) = 0;
	end
      end
    end
    sleep(2);
  end

    
  batchpos = min(find(batchruns == 0));
  outfile    = ['./results/' file_basename(batchnames{1,i}) '_results.mat']; 
  
  % Start the background job
  if exist(outfile, 'file')
    fprintf('EXISTS: %s\n', outfile);
  else
    fprintf('%d: --- batchfile %s starts...\n', i, batchnames{1,i});
    system(['cd results ; qsub ' file_basename(batchnames{1,i}) '_launcher']);
  end

  batchinds(batchpos) = i;
  batchruns(batchpos) = 1;
end
