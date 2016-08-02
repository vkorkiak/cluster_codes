
"""
\brief Finds a value defined in a text file.

The value must be defined as
<pre>
   VARNAME=VARVAL
</pre>
in the given text file.

\param fname    the text file where value is looked for
\param varname  the name of the variable
\param numval   the numerical value (in double format), if it exists
"""

import numpy as np
import os
import re
import time

def findval(fname, varname, isnum):

    uval=0;
    
    f = open(fname, 'r');
    count = 0;
    
    for line in f:
        #print(count)
        strs = line.split(' =')
        if len(strs) > 1:
            if varname == strs[0]:
                    uval = strs[1];
                    uval = uval.replace('"', '')
                    uval = uval.replace('\n', '')
                    uval = uval.lstrip().rstrip()

                    if isnum==0:
                        return uval
                    return int(uval)
        # print(strs)
        count += 1



"""
 Expands a base script. The multiple values given in the script are
 enumerated into single script files.
 
 """
def replace_basescriptval(all_lines, path, fname, curnick, \
                          batchlen, all_nicks, all_batchfiles, dowrite=0, 
                          strid='"', nickstr='__theNICK'):

    #fprintf('%s\n', curnick);
    reg = re.compile('\{\{.*\}\}')
    
    for cli, curline in enumerate(all_lines):
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
                indent = len(curline) - len(curline.lstrip(' '))
                all_lines2[cli] = ' '*indent+nick+'='+valstr.lstrip().rstrip()                
                curnick2 = curnick+'_'+nick+valstr.lstrip().rstrip()

                # Continue expansion
                batchlen, all_nicks, all_batchfiles = \
                    replace_basescriptval(all_lines2, path, fname, curnick2, 
                                          batchlen, all_nicks, all_batchfiles, dowrite=dowrite, 
                                          nickstr=nickstr, strid=strid)
    
            return (batchlen, all_nicks, all_batchfiles)

    # print, curnick
    fname2 = path+'/'+fname+'__'+curnick
    
    # Here could be other replacements...
    all_lines_print = all_lines.copy()
    
    # Replace known strings
    for curline in all_lines_print:
        curline.replace('__NICKS__', curnick);
    
    # Write the new file
    if dowrite:
        print('%s' % (fname2))
    
        fid = open(fname2, 'wt');
        # Nice idea, but gets wrong if the executor has another comment sign
        #  fprintf(fid, '%% AUTOMATICALLY GENERATED FROM FILE:\n');
        #  fprintf(fid, '%% %s\n', fname);
        #  fprintf(fid, '\n');
    
        # TODO -- make this somehow optional/reformattable.
        print('\n%s = %s%s%s;\n\n' % (nickstr, strid, curnick, strid), file=fid)
    
        for curline in all_lines_print:
            print('%s' % (curline), file=fid)
      
        fid.close()

    all_nicks.append(curnick)
    all_batchfiles.append(fname2)
    batchlen += 1
    return (batchlen, all_nicks, all_batchfiles)




"""
 Creates the batches to launch simulations.
"""
def create_batches_func(basefile, resudir, dowrite=0, runcmd='python', strid='"', nickstr='__theNICK'):


    # Is the results directory there?
    #if os.path.isdir(resudir) == False
    #    error('Directory results does not exist.')
    
    
    workdir = os.getcwd()
    print('The working directory is: %s' % (workdir))
    
    
    #
    # Create a set of batch files.
    #
    
    # Do the expand
    batchlen = 0;
    fname    = workdir+'/'+basefile;
    
    # At first, read all lines into memory
    all_lines = []
    f = open(fname, 'r')
    count = 0;
    for line in f: 
        all_lines.append(line.replace('\n', ''))
        count += 1;
    
    # The recursive part
    batchlen, nicks, batchfiles = replace_basescriptval(all_lines, workdir, basefile, '', \
                              batchlen, [], [], dowrite=dowrite, nickstr=nickstr, strid=strid)

    # Finish the writeup      
    if dowrite:
        print('The batchfile %s was expanded to %d files:' % (basefile, len(batchfiles)))
        for (fi, fname) in enumerate(batchfiles):
            print('%d: %s' % (fi, fname))
    
      
    print('')
    print('Batches created.\n');
    

    if dowrite:
      
        # Move them to the results folder
        for fname in batchfiles:
            os.system('mv '+ fname +' ' +resudir);
      
        # Create launcher scripts
        for fname in batchfiles:
            batchname = os.path.basename(fname)
            fid = open(resudir+'/'+batchname + '_launcher', 'wt');
            
            print('', file=fid);
            print('# Launch application', file=fid);
            print(runcmd+' '+batchname+' > '+batchname+'.log', file=fid);
            print('\n', file=fid);
            print('\n', file=fid);
            fid.close();

            #fprintf(fid, ['']);
            #fprintf(fid, ['#PBS -l procs=1\n']);             # launcher specific
            #fprintf(fid, ['#PBS -l walltime=4:24:30:00\n']); # launcher specific
            #fprintf(fid, ['#PBS -q batch \n'])               # launcher specific
            #fprintf(fid, ['#PBS -V \n']);                    # launcher specific
            #fprintf(fid, ['cd $PBS_O_WORKDIR \n']);
            #fprintf(fid, ['# Launch application \n']);
            #fprintf(fid, [runcmd ' ' batchname ' > ' batchname '.log\n']);
            #fprintf(fid, ['\n']);
            #fprintf(fid, ['\n']);
            #fclose(fid);
    
    # Run the batches by monitoring script that keep trach how many jobs are
    # going on.
    # 
    #    run_batches

    return (batchlen, nicks, batchfiles)



"""
 Gives the launch command to start a background job.
 Suited for platforms w/o scheduler.
"""
def get_batchcmd(nmachines, machinename, batchpos, batchname, resudir):

    machineid = ''
    #machineid = 1 + mod(batchpos, nmachines)
    #localcmd = ['"cd ' resudir ' ; bash ' file_basename(batchname) '_launcher"'];
    #cmd = ['ssh -o "BatchMode yes" voyager' num2str(machineid) ' ' localcmd ' &']

    localcmd = '"cd '+resudir+' ; bash '+os.path.basename(batchname)+'_launcher"'
    cmd = 'ssh -o "BatchMode yes" '+machinename+machineid+' '+localcmd+' &'
    return cmd
    


"""
 Launches a series of simulations.

 This is a modification of Visa's earlier script to launch yao simulations
 in parallel on a cluster without scheduler.
"""

def bare_launch_jobs(batchnames, resudir, machinename, runcmd='python', 
                     nmachines=1, npermachine=8, usermaster=0, useqsub=0,
                     start_delay=0):

    nsimulbatch = npermachine * nmachines
    
    nbatch    = len(batchnames)
    batchinds = np.zeros(nsimulbatch)
    batchruns = np.zeros(nsimulbatch)
    
    for i in range(0,nbatch):
        # Then, let's wait until at most nsimulbatch are running. Useful, if
        # more than one batches are launched simultaneously.
        # wait_for_runnings(nsimulbatch);

        # Is there space in the batch?
        # Lets wait until there is space
        while np.sum(batchruns) >= nsimulbatch:
            for u in range(0, nsimulbatch):
                if batchruns[u]:
                    # Check if the job is finished
                    cmd = 'grep COUCOU '+resudir+'/'+ \
                             os.path.basename(batchnames[int(batchinds[u])])+'.log'
                    if not os.system(cmd):
                        batchruns[u] = 0
            time.sleep(2)

        batchpos = np.min(np.where(batchruns == 0))
    
        if 1==1:
            # Start the background job
            cmd = 'grep COUCOU '+ resudir+'/'+os.path.basename(batchnames[i])+'.log'
            isFinished = not os.system(cmd)
    
            if isFinished:
                print('DONE: %s\n' % (batchnames[i]))
            else:
                print('%d: --- batchfile %s starts...' % (i, batchnames[i]))
                cmd = get_batchcmd(nmachines, machinename, batchpos, batchnames[i], resudir)
                os.system(cmd)
                # Wait a moment before next launch
                time.sleep(start_delay)
    
        batchinds[batchpos] = i
        batchruns[batchpos] = 1
  
  
