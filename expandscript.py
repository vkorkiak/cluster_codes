# -*- coding: utf-8 -*-
"""
Created on Tue May  3 12:48:39 2016

@author: vkorkiak
"""

import re

"""
 Expands a base script. The multiple values given in the script are
 enumerated into single script files.
 
 """
def replace_basescriptval(all_lines, path, fname, curnick, \
                          batchlen, all_nicks, all_batchfiles, dowrite=0):

    #fprintf('%s\n', curnick);
    reg = re.compile('\{\{.*\}\}')
    
    
    for cli, curline in all_lines:
        # Check if we find a line to enumerate
        vals = reg.search(curline)
    
        if vals:
            # Copy the lines
            all_lines2 = all_lines.copy();
    
            # Enumerate the values of the line
            slp = curline.split('=')
            nick = slp[0].lstrip().rstrip()
            allvals = slp[1].replace('{','').replace('}','').split(',')
            for valstr in allvals:
                all_lines2[cli] = nick+'='+valstr.lstrip().rstrip()                
                curnick2 = curnick+'_'+nick+valstr.lstrip().rstrip()

                # Continue expansion
                batchlen, all_nicks, all_batchfiles = \
                    replace_basescriptval(all_lines2, path, fname, curnick2, 
                                          batchlen, all_nicks, all_batchfiles, dowrite=dowrite)
    
            return

    # print, curnick
    fname2 = path+'/'+fname+'__'+curnick
    
    # Here could be other replacements...
    all_lines_print = all_lines.copy()
    
    # Replace known strings
    for curline in all_lines_print:
        curline.replace('__NICKS__', curnick);
    
    
    # Write the new file
    if dowrite:
        print('%s\n' % (fname2))
    
        fid = open(fname2, 'wt');
        # Nice idea, but gets wrong if the executor has another comment sign
        #  fprintf(fid, '%% AUTOMATICALLY GENERATED FROM FILE:\n');
        #  fprintf(fid, '%% %s\n', fname);
        #  fprintf(fid, '\n');
    
        # TODO -- make this somehow optional/reformattable.
        print('\n__theNICK = "%s";\n\n', (curnick), file=fid)
    
        for curline in all_lines_print:
            print('%s' % (curline), file=fid)
      
        fid.close()

    
    all_nicks.append(curnick)
    all_batchfiles.append(fname2)
    batchlen += 1
    
