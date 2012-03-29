%
% Returns the number of lines in a file.
%
function nlines = file_lines(fname)

fid = fopen(fname,'rt');
if fid <= 0
  fprintf('Unable to open file: %s\n', fname);
else
  nlines = 0;
  while (fgets(fid) ~= -1),
    nlines = nlines+1;
  end
  fclose(fid);
end

end

