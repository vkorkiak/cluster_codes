%
% Wait here if the cluster is too full. Max nidlemax pending jobs are
% allowed.
%
function wait_for_idles(nidlemax)
  
ready = 0;
while ~ready

  tmpbase = tempname;
  system(['qstat | grep batch | grep Q > ' tmpbase]);
  nwait = file_lines(tmpbase);
  system(['rm ' tmpbase]);

  if nwait < nidlemax 
    ready=1;
  else
    sleep(5);
  end
end

%print, nwait

end
