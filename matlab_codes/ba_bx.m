%-
%\file pe_bx.m
%
%\brief Expands all the PESCA UI basescriptfiles.
%
%This procedure does the basescript file expansion for all the
%basescripts listed in the main batch file. 
%
function ba_bx
 
global ba_stat

% Clear previously possibly chosen files
pe_stat.fnamexe_main = '';

% Number of base script files
n_basescripts = ba_stat.n_basescriptfiles;

ids = 1:n_basescripts;


% Go the required base script files through
for idind=1:length(ids)
  id = ids(idind);
  % Current base script file id
  ba_stat.cur_basescriptid = id;

  fnametot = ba_stat.basescriptfiles{id};
  
  % Extract the path
  path  = file_dirname(fnametot);
  fname = file_basename(fnametot);
  
  % Do the expand
  [batchlen, all_nicks, all_batchfiles] = expand_basescript(path, fname);
  
  % Fill PESCA UI status
  ba_stat.n_batchfiles(id) = batchlen;
  for i=1:batchlen
    ba_stat.nicks{     id, i} = all_nicks{i};
    ba_stat.batchfiles{id, i} = all_batchfiles{i};
  end
  
  
  fprintf('\n');
  if idind == length(ids)
    fprintf('Launch the batch with a command run_batches.m\n', id);
  end
end

end
