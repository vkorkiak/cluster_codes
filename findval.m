%-
%\file findval.pro   \ingroup SCRIPT_TOOLS
%
%\brief Finds a value defined in a text file.
%
%The value must be defined as
%<pre>
%   VARNAME=VARVAL
%</pre>
%in the given text file.
%
%\param fname    the text file where value is looked for
%\param varname  the name of the variable
%\param numval   the numerical value (in double format), if it exists
%
function [val, vals]=findval(fname, varname, nonum)

clear uvals
uval =0;
fi=1; % for arrays

varval=0;
namelen = size(varname,2);
unit = fopen(fname);
str = ''; 
count = 0;

while ~feof(unit)
    
  [A, readed] = fgets(unit);
  count = count + 1;
  
  split = strtrim(strsplit(A, '='));
  if size(split,2) >= 2 
    if strcmp(split{1}, varname) 
      uval = strsplit(split{2}, ' #%'); % Remove comment
      uval = uval{1};
      if ~exist('nonum', 'var')
	if uval(end) == ';'
	  uval(end) = 0;
	end
	uval = str2num(uval);
	if ~isempty(uval)
	  uvals(fi)=uval;
	end
      else
	uvals{fi}=uval;
      end
      fi = fi+1;
    end
  end
  
end
fclose(unit);

if exist('uvals', 'var')
  if iscell(uvals)
    val = uvals{1};
  else
    val = uvals;
  end
  vals = uvals;
else
  error('Unknown var (%s) in file %s\n', varname, fname);
end

%val
%vals
end

