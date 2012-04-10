%
% Loads the simulation data.
%
function [simdatao varargout] = loadsimuldata_diversbatch(fnames, orgvars, dirs)

if ~exist('dirs', 'var')
  dirs = {'./results'};
end

orgvals1 = 0;
orgvals2 = 0;

ndims = length(orgvars);

simdata = cell(length(fnames), 1);
orgvals = zeros(length(fnames), ndims);
founds  = zeros(length(fnames), 1);

for i=1:length(fnames)

  found=0;
  for di=1:length(dirs)
    
    paraname = [dirs{di} '/' file_basename(fnames{i})];    
    
    if exist(paraname, 'file')
      matname = [dirs{di} '/' file_basename(fnames{i}) '_results.mat'];
      if exist(matname, 'file')
	found=1;
	simdata{i} = load(matname);
	founds(i) = 1;
      end
    
      for oi=1:ndims
	orgvals(i, oi) = find_val(paraname, orgvars{oi});
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
  uniqvals = unique(orgvals(founds==1,i));
  nds(i) = length(uniqvals);
end

if 1==0
  vals1 = vals(:,1);
  vals2 = vals(:,2);
  vals3 = vals(:,3);
  jee1 = reshape(vals1, [8, 6]);
  jee2 = reshape(vals2, nds);
  jee3 = reshape(vals3, nds);
end


if prod(nds) == length(simdata)
  simdatao = reshape(simdata, nds);

  nout = max(nargout,1) - 1;
  maxnout = size(orgvals, 2);
  nuout = max([nout, maxnout]);
  for i=1:nuout
    varargout{i} = reshape(orgvals(:,i), nds);
  end
else
  % Something wrong with the parameters!
  fprintf('loadsimuldata_diversbatch: Something wrong!!\n');
  simdatao = simdata;

  nout = max(nargout,1) - 1;
  maxnout = size(orgvals, 2);
  nuout = max([nout, maxnout]);
  for i=1:nuout
    varargout{i} = orgvals(:,i);
  end
  
end
  


end
