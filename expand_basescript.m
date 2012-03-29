%-
% Expands a base script. The multiple values given in the script are
% enumerated into single script files.
%
function [batchlen, all_nicks, all_batchfiles] = ...
      expand_basescript(path, scriptname)
global baui ba_uivals ba_stat

batchlen       = 0;
all_nicks      = cell(ba_uivals.max_batchsize,1);
all_batchfiles = cell(ba_uivals.max_batchsize,1);

curid = ba_stat.cur_basescriptid;

fname = [path '/' scriptname];

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

% The recursive part
[batchlen, all_nicks, all_batchfiles] = ...
    replace_basescriptval(all_lines, path, scriptname, '', ...
			  batchlen, all_nicks, all_batchfiles);

if 1==1
    fprintf('The batchfile %s was expanded to %d files:\n', ...
	    scriptname, batchlen);
    for i=1:batchlen
        fprintf('%d: %s\n', i, file_basename(all_batchfiles{i}));
    end
end

end
