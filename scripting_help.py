
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
            if varname in strs[0]:
                uval = strs[1];
                uval = uval.replace('"', '')
                uval = uval.replace('\n', '')
                uval = uval.lstrip().rstrip()
    
                if isnum==0:
                    return uval
                return float(eval(uval.replace(';', '').replace('f', '')))
        # print(strs)
        count += 1



def replace_basescriptval(all_lines, fname, curnick, \
                          batchlen, all_nicks, all_batchfiles, dowrite=0, 
                          strid='"', nickstr='__theNICK', commentid=None,
                          batchid='DEBUG'):
    """
     Expands a base script. The multiple values given in the script are
     enumerated into single script files.
    """

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
                    replace_basescriptval(all_lines2, fname, curnick2, 
                                          batchlen, all_nicks, all_batchfiles, dowrite=dowrite, 
                                          nickstr=nickstr, strid=strid, commentid=commentid,
                                          batchid=batchid)
    
            return (batchlen, all_nicks, all_batchfiles)

    # print, curnick
    fname2 = fname+'__'+curnick
    
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
        if commentid is not None:
            print('%s' % (commentid), file=fid);
            print('%s  AUTOMATICALLY GENERATED FROM FILE:' % (commentid), file=fid);
            print('%s  %s' % (commentid, fname), file=fid);
            print('%s' % (commentid), file=fid);
    
        # TODO -- make this somehow optional/reformattable.
        print('\n%s = %s%s%s;' % (nickstr, strid, curnick, strid), file=fid)
        print('BATCH_ID = %s%s%s;\n\n'  % (strid, batchid, strid), file=fid)
    
        for curline in all_lines_print:
            print('%s' % (curline), file=fid)
      
        fid.close()

    all_nicks.append(curnick)
    all_batchfiles.append(fname2)
    batchlen += 1
    return (batchlen, all_nicks, all_batchfiles)




def create_batches_func(basefile, resudir, dowrite=0, runcmd='python', strid='"', 
                        nickstr='__theNICK', commentid=None, batchid='DEBUGfunc'):
    """
    Creates the batches to launch simulations.
    Parameter basefile needs to contain the full path.
    """

    # Is the results directory there?
    #if os.path.isdir(resudir) == False
    #    error('Directory results does not exist.')
    
    
    #
    # Create a set of batch files.
    #
    
    # Do the expand
    batchlen = 0;
    fname = basefile
    
    # At first, read all lines into memory
    all_lines = []
    f = open(fname, 'r')
    count = 0;
    for line in f: 
        all_lines.append(line.replace('\n', ''))
        count += 1;
    
    # The recursive part
    batchlen, nicks, batchfiles = replace_basescriptval(all_lines, basefile, '', \
                                                        batchlen, [], [], dowrite=dowrite, nickstr=nickstr, 
                                                        strid=strid, commentid=commentid, batchid=batchid)

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
            if os.path.dirname(fname) != resudir:
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



def get_batchcmd(nmachines, machinename, batchpos, batchname, resudir):
    """
     Gives the launch command to start a background job.
     Suited for platforms w/o scheduler.
    """

    machineid = ''
    #machineid = 1 + mod(batchpos, nmachines)
    #localcmd = ['"cd ' resudir ' ; bash ' file_basename(batchname) '_launcher"'];
    #cmd = ['ssh -o "BatchMode yes" voyager' num2str(machineid) ' ' localcmd ' &']

    localcmd = '"cd '+resudir+' ; bash '+os.path.basename(batchname)+'_launcher"'
    cmd = 'ssh -o "BatchMode yes" '+machinename+machineid+' '+localcmd+' &'
    return cmd
    



def bare_launch_jobs(batchnames, resudir, machinename, runcmd='python', 
                     nmachines=1, npermachine=8, usermaster=0, useqsub=0,
                     start_delay=0):
    """
     Launches a series of simulations.
    
     This is a modification of Visa's earlier script to launch yao simulations
     in parallel on a cluster without scheduler.
    """

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
                    # Check if the job is finished. By default, we think it is running.
                    batchruns[u] = 1
                    logname = resudir+'/'+os.path.basename(batchnames[int(batchinds[u])])+'.log'
                    if os.path.exists(logname):
                        if os.system('grep COUCOU '+logname+' > /dev/null') == 0:
                            batchruns[u] = 0
            time.sleep(2)

        batchpos = np.min(np.where(batchruns == 0))
    
        if 1==1:
            # Start the background job
            isFinished = False
            logname = resudir+'/'+os.path.basename(batchnames[i])+'.log'
            if os.path.exists(logname):
                cmd = 'grep COUCOU '+ logname + ' > /dev/null'
                isFinished = not os.system(cmd)
    
            if isFinished:
                print('%d: --- batchfile %s ALREADY DONE.' % (i, batchnames[i]))
            else:
                print('%d: --- batchfile %s starts...' % (i, batchnames[i]))
                cmd = get_batchcmd(nmachines, machinename, batchpos, batchnames[i], resudir)
                os.system(cmd)
                # Wait a moment before next launch
                time.sleep(start_delay)
    
        batchinds[batchpos] = i
        batchruns[batchpos] = 1
  
  

def is_param_def(linestr, params2modify):
    params = [pa[0] for pa in params2modify]
    strs = linestr.split(' =')
    if len(strs) > 1:
        potential_paramname = strs[0].rstrip().lstrip()
        if potential_paramname in params:
            param_values = params2modify[params.index(potential_paramname)]
            return param_values
    return

def extract_value(simulfile, param):
    try:
        value    = findval(simulfile, param, 0)
        value    = value.replace('"', '')
        value    = value.replace("'", '')
        value    = value.replace(";", '')
    except Exception as e:
        print('Problem: %s' % str(e))
        value    = None
    if value is None:
        raise(ValueError('%s not found in %s' % (param, simulfile)))
    return value


def run_simus(simulfile, params2modify, batchid='DEBUGruns',
              machinename='localhost', npermachine=1):
    """
    Run simulations as defined in the simulation file.

    Takes in a script file that contains all the necessary info to run 
    simulation and a list of parameters that need to be modified.

    At first, creates a basescript that is accepted by create_batches_func.

    Then, creates the individual scripts (but yet write on disk).
    Then, if user permits, writes the scripts to disk.
    Finally, launches simulations.


    params2modify is a list having the format:
      [parameter1, [value1_1, value1_2, ...]]
      [parameter2, [value2_1, value2_2, ...]]
    """

    print('Creating script files using a base: %s' % simulfile)

    if not os.path.exists(simulfile):
        raise(ValueError('Could not find %s' % simulfile))

    
    resudir     = extract_value(simulfile, '_resudir')
    runcmd      = extract_value(simulfile, '_runcmd') + ' '
    nickstr     = extract_value(simulfile, '_nickstr')
    files2copy  = extract_value(simulfile, '_files2copy')
    commentid   = extract_value(simulfile, '_commentid')
    if machinename is None:
        machinename = extract_value(simulfile, '_machinename') # try this
    if npermachine is None:
        npermachine = int(findval(simulfile, '_npermachine', 1)) # try this
    stridnum    = findval(simulfile, '_strid', 1)
    if stridnum == 1:
        strid = "'"
    elif stridnum == 2:
        strid = '"'
    else:
        raise(ValueError('Unknown string id: %s' % str(stridnum)))
                    
    print('Result directory: %s'  % (resudir))
    print('Running command: "%s"' % runcmd)
    print('Nick string:      %s'  % nickstr)
    print('String ID:        %s'  % strid)
    print('Comment ID:       %s'  % commentid)
    print('Files to copy:    %s'  % files2copy)
    print('Master machine:   %s'  % machinename)
    print('#simus / machine: %d'  % npermachine)

    actual2base = resudir+'/'+simulfile
    # Wait until there is no chance of replacing anything
    while os.path.exists(actual2base):
        print('Waiting until this is removed: %s' % actual2base)
        time.sleep(5)

    # Then, create the temporary base file    
    fid2write = open(actual2base, 'wt');
    fid2read  = open(simulfile, 'rt');

    for line in fid2read: 
        # Do we need to replace this file?
        param_values = is_param_def(line, params2modify)
        if param_values is None:
            # -1 for the linefeed at the end of the line. Hope this doesn't 
            # depend on the file format...
            print('%s' % line[:-1], file=fid2write)
        else:
            param  = param_values[0]
            values = param_values[1]
            line2write = param + ' = {{'
            first = True
            for value in values:
                if not first:
                    line2write += ', '
                first = False
                line2write += str(value)
            line2write += '}}'
            print(line2write, file=fid2write)
    
    fid2write.close();
    fid2read.close();

    
    # Then, expand the base script
    batchlen, nicks, files = create_batches_func(actual2base, resudir, dowrite=0, 
                                                 runcmd=runcmd, strid=strid, nickstr=nickstr)

    # Create the individual script files
    print('%d scripts ready for writing. e.g. %s' % (batchlen, files[0]))
    reply = input('Go on? (Y/n)?')
    if len(reply)==0:
        reply='y'
    if reply=='y':
        batchlen, nicks, batchfiles = create_batches_func(actual2base, resudir, 
                                                          dowrite=1, runcmd=runcmd, 
                                                          strid=strid, nickstr=nickstr,
                                                          commentid=commentid, batchid=batchid)

    # Then, remove temporary base file
    os.system('rm '+actual2base)

    # Copy necessary files to resudir, if so needed
    for file2copy in files2copy.split(', '):
        if len(file2copy) == 0:
            continue
        if not os.path.exists(file2copy):
            raise(ValueError('File to copy not found: %s' % file2copy))
        print('Copying %s to %s' % (file2copy, resudir))
        os.system('cp '+file2copy +' '+ resudir)


    # Then, we are ready to run
    print('')
    reply = input('Should we launch the scripts (y/N)?')
    if len(reply)==0:
        reply='n'
    if reply=='y':
        print("OK, let's launch the scripts...")
        bare_launch_jobs(batchfiles, resudir, machinename, 
                         runcmd=runcmd, npermachine=npermachine)
    else:
        print('Scripts not laucnhed.')
