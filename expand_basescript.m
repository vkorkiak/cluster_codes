%-
% Expands a base script. The multiple values given in the script are
% enumerated into single script files.
%
function [batchlen, all_nicks, all_batchfiles] = ...
      expand_basescript(path, scriptname, modvals, dowrite)

batchlen = 0;
fname    = [path '/' scriptname];

% At first, read all lines into memory
nlines = file_lines(fname);
all_lines = cell(nlines,1);

unit = fopen(fname);
str = '';
count = 1;
while ~feof(unit)
  str = fgets(unit);
  all_lines{count} = str;
  count = count + 1;
end
fclose(unit);


% Replace general modvals
if exist('modvals', 'var')
  for i=1:length(all_lines)
    for u=1:size(modvals,1)
      k = strfind(all_lines{i}, modvals{u,1});
      if ~isempty(k) 
	oldline = all_lines{i};
	newline = [oldline(1:k-1) ...
		   modvals{u,2} ...
		   oldline(k+length(modvals{u,1}):length(oldline))];
	all_lines{i} = newline;
      end
    end % modvals through
  end % lines through
end


% The recursive part
all_nicks      = cell(2048*8,1);
all_batchfiles = cell(2048*8,1);
[batchlen, all_nicks, all_batchfiles] = ...
    replace_basescriptval(all_lines, path, scriptname, '', ...
			  batchlen, all_nicks, all_batchfiles, dowrite);
  
all_nicks      = all_nicks(1:batchlen);
all_batchfiles = all_batchfiles(1:batchlen);

if dowrite
    fprintf('The batchfile %s was expanded to %d files:\n', ...
	    scriptname, batchlen);
    for i=1:batchlen
        fprintf('%d: %s\n', i, file_basename(all_batchfiles{i}));
    end
end

end
