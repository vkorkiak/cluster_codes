%
% Extracts the file base name.
%
function fname = file_basename(fname)

  [pathstr, name, ext] = fileparts(fname);
  fname = [name ext];

end
