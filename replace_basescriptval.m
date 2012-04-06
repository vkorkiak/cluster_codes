%-
% \file replace_basescriptval.pro
%
% \brief Does the recursive part in basescript expansion.
%
function [batchlen, all_nicks, all_batchfiles] = ...
      replace_basescriptval(all_lines, path, fname, curnick, ...
			    batchlen, all_nicks, all_batchfiles, dowrite)

%fprintf('%s\n', curnick);

nlines = length(all_lines);

for i=1:nlines
  curline = all_lines{i};

  % Check if we find a line to enumerate
  if ~isempty(regexp(curline,'\{\{.*\}\}'))
    % Copy the lines
    all_lines2 = all_lines;
    
    % Enumerate the values of the line
    split = strtrim(strsplit(curline, '={}, '));
    nevalvals = length(split);
    for s=2:nevalvals
      if length(strtrim(split{s})) > 0	
	all_lines2{i} = [split{1} '=' split{s} 10];

	% Find nick for the varname
	% nick = pe_getnickalias(split(0))
	nick = split{1};

	% Remove quation marks (like ')
	valstr = split{s};
	if valstr(1) == ''''
	  valstr = valstr(2:end-1);
	end
	
	curnick2 = [curnick '_' nick valstr];
      
	% Continue expansion
	[batchlen, all_nicks, all_batchfiles] = ...
	    replace_basescriptval(all_lines2, path, fname, curnick2, ...
				  batchlen, all_nicks, all_batchfiles, dowrite);
      end
    end
    return    
  end
end


% print, curnick
fname2 = [path '/' fname '__' curnick];

% Here could be other replacements...
all_lines_print = all_lines;

% Replace known strings
for i=1:length(all_lines_print)
  k = strfind(all_lines_print{i}, '__NICKS__');
  if ~isempty(k) 
    oldline = all_lines_print{i};
    newline = [oldline(1:k) curnick oldline(k+9:length(oldline))];
    all_lines_print{i} = newline;
  end
end


% Write the new file
if dowrite
  fprintf('%s\n', fname2);

  fid = fopen(fname2, 'wt');
  fprintf(fid, '%% AUTOMATICALLY GENERATED FROM FILE:\n');
  fprintf(fid, '%% %s\n', fname);
  fprintf(fid, '\n');
  for i=1:nlines
    fprintf(fid, '%s', all_lines_print{i});
  end
  fclose(fid);
end

all_nicks{batchlen+1}      = curnick;
all_batchfiles{batchlen+1} = fname2;
batchlen = batchlen+1;

%print, fname2
%print, batchlen
end
