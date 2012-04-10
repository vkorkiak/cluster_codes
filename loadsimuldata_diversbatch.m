%
% Loads the simulation data.
%
function [simdatao orgvals1 orgvals2] = loadsimuldata_diversbatch(fnames, orgvars, dirs)

if ~exist('dirs', 'var')
  dirs = {'./results'};
end

orgvals1 = 0;
orgvals2 = 0;

ndims = length(orgvars);

simdata = cell(length(fnames), 1);
orgvals = zeros(length(fnames), ndims);

for i=1:length(fnames)

  found=0;
  for di=1:length(dirs)
    
    paraname = [dirs{di} '/' file_basename(fnames{i})];    
    
    if exist(paraname, 'file')
      matname = [dirs{di} '/' file_basename(fnames{i}) '_results.mat'];
      if exist(matname, 'file')
	found=1;
	simdata{i} = load(matname);
      end
    
      for oi=1:ndims
	orgvals(i, oi) = findval(paraname, orgvars{oi});
	fprintf('%d>  %s:  %f\n', i, orgvars{oi}, orgvals(i, oi));	
      end
      break;
    end % paraname is found
  end
  if ~found
    fprintf('Not found: %s\n', matname);
  end
end


% The simulation results should be re-arranged based on orgvars
nds = zeros(ndims,1);
for i=1:ndims
  uniqvals = unique(orgvals(:,i));
  nds(i) = length(find(uniqvals ~= 0));
end

if 1==0
  vals1 = vals(:,1);
  vals2 = vals(:,2);
  vals3 = vals(:,3);
  jee1 = reshape(vals1, [8, 6]);
  jee2 = reshape(vals2, nds);
  jee3 = reshape(vals3, nds);
end

simdatao = reshape(simdata, nds);
orgvals1 = reshape(orgvals(:,1), nds);
orgvals2 = reshape(orgvals(:,2), nds);

end
