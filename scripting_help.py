
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
import subprocess
import socket
import copy
import glob
import random

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




def replace_basescriptval(all_lines, fname, curnick, \
                          batchlen, all_nicks, all_batchfiles, dowrite=0, 
                          strid='"', nickstr='__theNICK', commentid=None,
                          batchid='DEBUG', file_extension=''):
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
                                          batchid=batchid, file_extension=file_extension)
    
            return (batchlen, all_nicks, all_batchfiles)

    # print, curnick
    fname2 = fname+'__'+curnick+file_extension
    
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




def create_batches_func(basefile, localdir, commondir, dowrite=0, runcmd='python', strid='"', 
                        nickstr='__theNICK', commentid=None, batchid='DEBUGfunc',
                        all_lines=None, file_extension='', only_simulfiles=False):
    """
    Creates the batches to launch simulations.
    Parameter basefile needs to contain the full path.
    """

    #
    # Create a set of batch files.
    #
    
    # Do the expand
    batchlen = 0;
    fname = basefile
    
    if all_lines is None:
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
                                                        strid=strid, commentid=commentid, batchid=batchid,
                                                        file_extension=file_extension)

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
            if os.path.dirname(fname) != commondir:
                os.system('mv '+ fname +' ' +commondir);
      
        # Create launcher scripts
        if only_simulfiles == False:
            for fname in batchfiles:
                batchname = os.path.basename(fname)
                fid = open(commondir+'/'+batchname + '_launcher', 'wt');
                
                print('', file=fid);
                print('# Launch application', file=fid);
                print(runcmd+' '+batchname+' > '+localdir+'/'+batchname+'.log', file=fid);
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


def add2base2(allbases, curval, params2modify):
    if len(params2modify)==0:
        allbases.append(copy.copy(curval))
        return
    param, vals = params2modify[0][0], params2modify[0][1]
    for val in vals:
        curval[param] = val
        add2base2(allbases, curval, params2modify[1:])
    return allbases

def get_paramvals(params2modify):
    return add2base2([], dict(), params2modify)

def get_paraminds(params2modify, conditions):
    """ 
    Returns the indices of the sets in params2modify that fulfill the
    given conditions.
    """
    paramvals = get_paramvals(params2modify)
    for pi, paramval in enumerate(paramvals):
        for cond in conditions:
            if paramval[cond[0]] != cond[1]:
                paramvals[pi] = None
                break
    inds = [i for i,va in enumerate(paramvals) if va is not None]
    return inds


def add2base(allbases, curval, params2modify):
    if len(params2modify)==0:
        allbases.append(curval)
        return
    param, vals = params2modify[0][0], params2modify[0][1]
    for val in vals:
        add2base(allbases, curval+'_'+param+str(val), params2modify[1:])
    return allbases

def get_logfiles(basename, params2modify, file_extension=''):
    """
    Returns a list of log files that results from a base script.
    """
    localdir = extract_value(basename+file_extension, '_localdir')
    logfiles = add2base([], localdir+'/'+basename+'__', params2modify)
    for ii in range(len(logfiles)):
        logfiles[ii] += '.log'
    return logfiles

def get_scriptfiles(basename, params2modify):
    """
    Returns a list of script files that are created when using the given base script.
    """
    localdir = extract_value(basename, '_localdir')
    files = add2base([], localdir+'/'+basename+'__', params2modify)
    return files



def get_batchcmd(nmachines, machinename, batchpos, batchname, localdir):
    """
    Gives the launch command to start a background job.
    Suited for platforms w/o scheduler.
    """

    machineid = ''
    #machineid = 1 + mod(batchpos, nmachines)
    #localcmd = ['"cd ' localdir ' ; bash ' file_basename(batchname) '_launcher"'];
    #cmd = ['ssh -o "BatchMode yes" voyager' num2str(machineid) ' ' localcmd ' &']

    localcmd = '"cd '+localdir+' ; bash '+os.path.basename(batchname)+'_launcher"'
    cmd = 'ssh -q -o "BatchMode yes" '+machinename+machineid+' '+localcmd+' &'
    return cmd
    



def bare_launch_jobs(batchnames, localdir, machinename,
                     nmachines=1, npermachine=8, start_delay=0):
    """
    Launches a series of simulations.

    Jobs are launched directly on the local machine.
    
    This is a modification of Visa's earlier script to launch yao simulations
    in parallel on a cluster without scheduler.
    """

    nsimulbatch = npermachine * nmachines
    
    nbatch    = len(batchnames)
    batchinds = np.zeros(nsimulbatch)
    batchruns = np.zeros(nsimulbatch)
    
    for i in range(0,nbatch):
        # Is there space in the batch?
        # Lets wait until there is space
        while np.sum(batchruns) >= nsimulbatch:
            for u in range(0, nsimulbatch):
                if batchruns[u]:
                    # Check if the job is finished. By default, we think it is running.
                    batchruns[u] = 1
                    logname = localdir+'/'+os.path.basename(batchnames[int(batchinds[u])])+'.log'
                    if os.path.exists(logname):
                        if os.system('grep COUCOU '+logname+' > /dev/null') == 0:
                            batchruns[u] = 0
            time.sleep(2)

        batchpos = np.min(np.where(batchruns == 0))
    
        if 1==1:
            # Start the background job
            isFinished = False
            logname = localdir+'/'+os.path.basename(batchnames[i])+'.log'
            if os.path.exists(logname):
                cmd = 'grep COUCOU '+ logname + ' > /dev/null'
                isFinished = not os.system(cmd)
    
            if isFinished:
                print('%d: --- batchfile %s ALREADY DONE.' % (i, batchnames[i]))
            else:
                print('%d: --- batchfile %s starts...' % (i, batchnames[i]))
                cmd = get_batchcmd(nmachines, machinename, batchpos, batchnames[i], localdir)
                os.system(cmd)
                # Wait a moment before next launch
                time.sleep(start_delay)
    
        batchinds[batchpos] = i
        batchruns[batchpos] = 1



def gcp_check_instance_zone(instance_name):
    print('Checking the zone of %s' % instance_name)
    try:
        cmd = 'gcloud compute instances list'
        proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
        output = (proc.communicate()[0]).decode()
        lines = output.split('\n')
        for line in lines:
            if len(line)==0: continue
            fields = line.split()
            # print('Found instance %s.' % fields[0])
            if fields[0] == instance_name:
                print('Zone found: %s' % fields[1])
                return fields[1] # the zone name
    except Exception as e:
        print('Failed to extract name. %s.' % str(e))
    print('Did not find any instance: %s' % instance_name)


def gcp_get_instance_groups():
    print('Looking for existing instance groups...')
    try:
        cmd = 'gcloud compute instance-groups list'
        proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
        output = (proc.communicate()[0]).decode()
        lines = output.split('\n')
        lines = lines[1:-1]
        instance_groups = [str(li.split()[0]) for li in lines]
        nintances       = [int(li.split()[5]) for li in lines]
        print('%d instance groups found' % len(instance_groups))
        return (instance_groups, nintances)
    except Exception as e:
        print('%s' % str(e))


def gcp_instance_names(instance_group_name, zone):
    # Then, find the names of the machines in an instance group
    for ii in range(100):
        try:
            cmd = 'gcloud compute instance-groups managed list-instances '+instance_group_name+' --zone '+zone
            proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
            output = (proc.communicate()[0]).decode()
            lines = output.split('\n')
            lines = lines[1:]
            if lines[-1] == '': lines=lines[:-1]
            slave_names = [str(li.split()[0]) for li in lines]
            return slave_names
        except Exception as e:
            print('Problems getting instance names. %s.' % str(e))
        time.sleep(5)
    raise(ValueError('Giving up with instance names...'))


def gcp_create_slaves(gcp_params, do_checks=True):
    """
    Create slave instances using given template.
    """
    instance_group_name    = gcp_params['instance_group_name']
    instance_template_name = gcp_params['instance_template_name']
    ninstances             = gcp_params['ninstances']
    base_instance_name     = 'slave'

    master_instance = socket.gethostname()
    zone = gcp_check_instance_zone(master_instance)

    # Is the instance group already there?
    instance_group_exists = False
    try:
        running_instance_groups,runnig_nintances = gcp_get_instance_groups()
        if instance_group_name in running_instance_groups:
            instance_group_exists = True
    except:
        pass

    if not instance_group_exists:
        print('Creating instance group %s of %d instances.' % (instance_group_name, ninstances))

        cmd = "gcloud compute instance-groups managed create "+instance_group_name+\
              " --base-instance-name "+base_instance_name+\
              " --size "+str(ninstances)+\
              " --template "+instance_template_name+\
              " --zone "+zone

        print('Launching command:')
        print(cmd)
        ret = os.system(cmd)
        if ret != 0:
            print('FAIL!')
            raise(ValueError('Could not start slaves.'))
        else:
            print('Instance group created succesfully.')

        if do_checks == False:
            return

        # It will take a while until the instance group is ready
        while True:
            time.sleep(3)

            cmd = 'gcloud compute instance-groups managed list-instances '+instance_group_name+' --zone '+zone
            proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
            output = (proc.communicate()[0]).decode()
            lines = output.split('\n')
            lines = lines[1:-1]
            ok2go = np.zeros(len(lines))
            for li, line in enumerate(lines):
                # print('%d: %s' % (li, line))
                if 'RUNNING' in line:
                    ok2go[li] = 1
            if np.all(ok2go==1):
                break
            print('Monitoring the creation of the instance group. %d instances running.' % int(np.sum(ok2go)))

    else:
        print('Instance group exists: %s' % instance_group_name)

    # Then, find the names of the machines in an instance group
    slave_names = gcp_instance_names(instance_group_name, zone)

    print('Slaves:')
    for si, slave in enumerate(slave_names):
        print('%d: %s' % (si, slave))

    return (slave_names, zone)



def cluster_batchcmd(remotemachine, batchname, commondir):
    """
    Gives the launch command to start a background job.
    Suited for platforms w/o scheduler.
    """
    # machineid = ''
    localcmd = '"cd '+commondir+' ; bash '+os.path.basename(batchname)+'_launcher"'
    cmd = 'ssh -q -o "BatchMode yes" -oStrictHostKeyChecking=no '+remotemachine+' '+localcmd+' &'
    return cmd


def gcp_launch_jobs_fixed(batchnames, localdir, machinename, platformparams,
                          overwrite=False, npermachine=8, start_delay=0):
    """
    Launches a series of simulations. The number of machines is expected to be fixed.

    Jobs are launched on a cluster, depending in the settings defined in
    platformparams.
    
    This is a modification of Visa's earlier script to launch yao simulations
    in parallel on a cluster without scheduler.
    """

    # How many slaves do we have?
    slaves, zone = gcp_create_slaves(platformparams)
    nmachines = len(slaves)

    # Check that ssh works to the slaves. Try a few times, because the slaves might
    # not wake up immediately...
    for ii in range(4):
        print('Checking that we can access slaves with an SSH connection...')
        cmd = 'ssh -oStrictHostKeyChecking=no '+slaves[0]+' "ls"'
        proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,)
        output = (proc.communicate()[0]).decode()
        if 'ultimateglao' in output: break # slave should have directory "ultimateglao" in home
        print('Could not yet access the slaves')
        time.sleep(3)
    else:
        print('Run this: ')
        print('ssh-agent bash')
        print('ssh-add ~/.ssh/google_compute_engine')
        raise(ValueError('Failed to have ssh connection to slaves.'))
    print('SSH access to slaves granted!')

    delete_instancegroup = True
    if 'delete_instancegroup' in platformparams:
        delete_instancegroup = platformparams['delete_instancegroup']

    nbatch    = len(batchnames)
    batchinds = np.zeros((nmachines, npermachine))
    batchruns = np.zeros((nmachines, npermachine))
    nparallel = npermachine * nmachines

    
    for i in range(nbatch):
        # Is there space in the batch?
        # Lets wait until there is space
        while np.sum(batchruns) >= nparallel:
            for u1 in range(nmachines):
                for u2 in range(npermachine):
                    if batchruns[u1,u2]:
                        # Check if the job is finished.  We expect the
                        # log file to found, becase the code below has
                        # started a simulation that will output to
                        # this file.
                        logname = localdir+'/'+os.path.basename(batchnames[int(batchinds[u1,u2])])+'.log'
                        if os.path.exists(logname):
                            if os.system('grep COUCOU '+logname+' > /dev/null') == 0:
                                batchruns[u1,u2] = 0
            time.sleep(2)

        # Where to start the new batch
        batchpos1 = batchpos2 = None
        for u1 in range(nmachines):
            for u2 in range(npermachine):
                if batchruns[u1,u2] == 0:                    
                    batchpos1 = u1
                    batchpos2 = u2
                    break
    
        # Start the background job
        prev_status = 'not_started'
        logname = localdir+'/'+os.path.basename(batchnames[i])+'.log'
        if overwrite == False:
            if os.path.exists(logname):
                prev_status = 'started'
                cmd = 'grep COUCOU '+ logname + ' > /dev/null'
                if os.system(cmd)==0:
                    prev_status = 'finished'
    
        if prev_status == 'finished':
            print('%d: --- batchfile %s ALREADY DONE.' % (i, batchnames[i]))
        elif prev_status == 'started':
            print('%d: --- batchfile %s EXISTS. Not overwriting.' % (i, batchnames[i]))
        else:
            remotemachine = slaves[batchpos1]
            print('%d: --- batchfile %s starts on %s. Job %d/%d there.' % (i, batchnames[i], remotemachine, batchpos2, npermachine))
            cmd = cluster_batchcmd(remotemachine, batchnames[i], commondir)
            os.system(cmd)
            # Wait a moment before next launch
            time.sleep(start_delay)
    
        batchinds[batchpos1,batchpos2] = i
        batchruns[batchpos1,batchpos2] = 1


    print('Last job has been dispatched!')
    print('Waiting for all the jobs to finish')

    while np.sum(batchruns) !=0:        
        for u1 in range(nmachines):
            for u2 in range(npermachine):
                if batchruns[u1,u2]:
                    logname = localdir+'/'+os.path.basename(batchnames[int(batchinds[u1,u2])])+'.log'
                    if os.path.exists(logname):
                        if os.system('grep COUCOU '+logname+' > /dev/null') == 0:
                            batchruns[u1,u2] = 0
                            print('Still %d jobs to finish...' % np.sum(batchruns))
                            # Resize the instance group
                            cmd = 'gcloud compute instance-groups managed resize '+platformparams['instance_group_name']+\
                                  ' --size '+str(int(np.sum(batchruns)))+\
                                  ' --zone '+zone
                            print('Running: %s' % cmd)
                            ret = os.system(cmd)
                            if ret != 0:
                                print('Instance group resize failed')
        time.sleep(2)

    print('All the jobs are finished!')

    if delete_instancegroup:
        instance_group_name = platformparams['instance_group_name']
        print('Deleting instance group %s' % instance_group_name)

        cmd = 'gcloud compute instance-groups managed delete '+instance_group_name+\
              ' --zone '+zone+' --no-user-output-enabled --quiet'
        ret = os.system(cmd)
        if ret != 0:
            print('FAILURE TO DELETE. !!')
        else:
            print('Instance group deleted.')

    print('ALL DONE.')
 


def check_ssh_access(slave):
    # Check that ssh works to the slaves. Try a few times, because the slaves might
    # not wake up immediately...
    for ii in range(4):
        cmd = 'ssh -q -oStrictHostKeyChecking=no '+slave+' "ls"'
        proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,)
        output = (proc.communicate()[0]).decode()
        if 'ultimateglao' in output: break # slave should have directory "ultimateglao" in home
        print('Could not yet access: %s' % slave)
        time.sleep(3)
    else:
        return False
    return True


def is_localjob_finished(slavename, localdir, batchname, commondir):

    local_logname = localdir+'/'+os.path.basename(batchname)+'.log'
    cmd = 'ssh -q -oStrictHostKeyChecking=no '+slavename+' "grep -s COUCOU '+local_logname+'"'
    proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
    output = (proc.communicate()[0]).decode()
    if len(output)==0:
        return False # Not finished
    # Move the log file to a common place
    cmd = 'scp -q -oStrictHostKeyChecking=no '+slavename+':'+local_logname+' '+commondir
    # print(cmd)
    ret = os.system(cmd)
    if ret != 0:
        print('scp failed: %s' % cmd)        
    return True


def gcp_launch_jobs_flex(batchnames, localdir, commondir, machinename, platformparams,
                         overwrite=False, npermachine=8, start_delay=0, runcmd='python3'):
    """
    Launches a series of simulations. The number of machines is flexible.
    For the moment, only one job per remote machine.

    Jobs are launched on a cluster, depending in the settings defined in
    platformparams.
    
    This is a modification of Visa's earlier script to launch yao simulations
    in parallel on a cluster without scheduler.
    """
    # How many slaves do we have?
    gcp_create_slaves(platformparams, do_checks=False)
    
    instance_group_name = platformparams['instance_group_name']
    master_instance = socket.gethostname()
    zone = gcp_check_instance_zone(master_instance)
    runcmd1st = runcmd.split()[0]

    delete_instancegroup = True
    if 'delete_instancegroup' in platformparams:
        delete_instancegroup = platformparams['delete_instancegroup']

    nbatch      = len(batchnames)
    jobs2do     = np.ones(nbatch)
    jobsdone    = np.zeros(nbatch)
    slavejobs   = [] # will get a tuple (slavename, batch ID)

    print('Going to start the job launching loop...')
    loopcnt = 1
    while np.sum(jobsdone) < nbatch:
        # Take the job to do
        curjobid = np.argmax(jobs2do>0)

        batchname = batchnames[curjobid]
        logname = commondir+'/'+os.path.basename(batchname)+'.log'
        
        # Check, if the job is already done
        prev_status = 'not_started'
        if overwrite == False and jobs2do[curjobid]:
            if os.path.exists(logname):
                prev_status = 'started'
                cmd = 'grep COUCOU '+ logname + ' > /dev/null'
                if os.system(cmd)==0:
                    prev_status = 'finished'
    
        if prev_status == 'finished':
            print('%d: --- batchfile %s ALREADY DONE.' % (curjobid, batchname))
            jobsdone[curjobid] = 1
            jobs2do[curjobid]  = 0
            continue
        elif prev_status == 'started':
            print('%d: --- batchfile %s EXISTS. Not overwriting.' % (curjobid, batchname))
            jobsdone[curjobid] = 1
            jobs2do[curjobid]  = 0
            continue


        # Where to launch the next job?
        slave_names = gcp_instance_names(instance_group_name, zone)
        if len(slave_names) == 0:
            print('No slaves yet...')
            time.sleep(5)
            continue
        # Pick a slave
        slaves_used = [s[0] for s in slavejobs]
        randslaves = copy.copy(slave_names); random.shuffle(randslaves)
        for slave in randslaves:
            if not slave in slaves_used:
                slave2use = slave
                break
        else:
            slave2use = None

        # Lauch the job
        if (slave2use is not None) and  jobs2do[curjobid]:
            # Is the slave ready to go?
            for iter in range(4):
                if check_ssh_access(slave):
                    break
                print('Waiting for SSH access to slave %s' % slave2use)
                time.sleep(4)
            else:
                continue # slave didn't work out

            # Start the background job
            jobs2do[curjobid] = 0
            remotemachine = slave2use
            print('%d: --- batchfile %s starts on %s. Job %d/%d there.' % (curjobid, batchname, remotemachine, 0, npermachine))
            cmd = cluster_batchcmd(remotemachine, batchname, commondir)
            os.system(cmd)
            # Wait a moment before next launch
            time.sleep(start_delay)
            # Indicate the job has started
            slavejobs.append((slave2use, curjobid))


        # Are some of the jobs (that we started) finished?
        for slavejob in slavejobs:
            slavename, jobid = slavejob
            if is_localjob_finished(slavename, localdir, batchnames[jobid], commondir):
                jobsdone[jobid] = 1
                slavejobs.pop(slavejobs.index(slavejob))


        # Have some slaves died? Have some jobs crashed?
        if loopcnt % 100 == 0:
            for slavejob in slavejobs:
                slavename, jobid = slavejob
                restart_job = False
                if check_ssh_access(slavename) == False:
                    print('No SSH acess to %s. Restarting job %d: %s' % (slavename, jobid, batchnames[jobid]))
                    restart_job = True
                else:
                    # Check if the job there is still running
                    cmd = 'ssh -q -oStrictHostKeyChecking=no '+slavename+' "ps aux | grep '+runcmd1st+' | grep -v grep"'
                    print(cmd)
                    proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
                    output = (proc.communicate()[0]).decode()
                    if len(output)==0:
                        # Our job is not running there.
                        # Final check, is it finished?
                        if is_localjob_finished(slavename, localdir, batchnames[jobid], commondir):
                            jobsdone[jobid] = 1
                            slavejobs.pop(slavejobs.index(slavejob))
                        else:
                            #  No, it is not finished
                            print('Job %d (%s) seems dead on slave %s. Restarting it.' % 
                                  (jobid, batchnames[jobid], slavename))
                            restart_job = True

                if restart_job:
                    jobs2do[jobid] = 1
                    slavejobs.pop(slavejobs.index(slavejob))
            
        # Wait before next checks
        loopcnt += 1
        time.sleep(2)

    print('All the jobs are finished!')

    if delete_instancegroup:
        instance_group_name = platformparams['instance_group_name']
        print('Deleting instance group %s' % instance_group_name)

        cmd = 'gcloud compute instance-groups managed delete '+instance_group_name+\
              ' --zone '+zone+' --no-user-output-enabled --quiet'
        ret = os.system(cmd)
        if ret != 0:
            print('FAILURE TO DELETE. !!')
        else:
            print('Instance group deleted.')

    print('ALL DONE.')
 



def gcp_create_default_slavetemplate():
    template2create = 'slave-template-c1-mem6'
    print('Checking instance templates for: %s' % template2create)
    cmd = 'gcloud compute instance-templates list';
    # cmd = 'gcloud compute instances list'
    proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
    output = (proc.communicate()[0]).decode()
    lines = output.split('\n')
    for line in lines:
        if len(line)==0: continue
        fields = line.split()
        # print('Found instance %s.' % fields[0])
        if fields[0] == template2create:
            print('Template found: %s' % template2create)
            return

    cmd = """gcloud compute instance-templates create slave-template-c1-mem6 \
--custom-memory=6656MiB \
--custom-cpu=1 \
--no-address \
--preemptible \
--image-family slave-family-1 \
--metadata startup-script='#! /bin/bash 
sudo mount -t nfs singlefs-1-vm:/data /common-slavedisk 
sudo mkdir -p /local_disk/temp_results
sudo chmod -R a+wrx /local_disk
EOF'"""
    print('Launching:')
    print(cmd)
    os.system(cmd)

  

def run_simus(simulfile, params2modify, batchid='DEBUGruns',
              machinename='localhost', npermachine=1, platformparams=None,
              overwrite=False, only_simulfiles=False, file_extension=None):
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

    
    localdir    = extract_value(simulfile, '_localdir')
    commondir   = extract_value(simulfile, '_commondir')
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
                    
    print('Local directory:  %s'  % (localdir))
    print('Common directory: %s'  % (commondir))
    print('Running command: "%s"' % runcmd)
    print('Nick string:      %s'  % nickstr)
    print('String ID:        %s'  % strid)
    print('Comment ID:       %s'  % commentid)
    print('Files to copy:    %s'  % files2copy)
    print('Master machine:   %s'  % machinename)
    print('#simus / machine: %d'  % npermachine)

    # If not there, let's create the result directory
    if not os.path.exists(commondir):
        print('Common directory not found: %s' % commondir)
        reply = input('Create directory? (N/y)?')
        if len(reply)==0:
            reply='n'
        if reply=='y':
            os.system('mkdir -p ' + commondir)
        else:
            return

    # Then, get the lines of a temporary base file    
    fid2read  = open(simulfile, 'rt');
    all_lines = []
    for line in fid2read: 
        # Do we need to replace this file?
        param_values = is_param_def(line, params2modify)
        if param_values is None:
            if line.split('=')[0].strip() == '_masternode':
                line = '_masternode = '+strid+socket.gethostname()+strid+';'+'f'

            # -1 for the linefeed at the end of the line. Hope this doesn't 
            # depend on the file format...
            all_lines.append('%s' % line[:-1])
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
            # print(line2write, file=fid2write)
            all_lines.append(line2write)
    
    fid2read.close();
    
    # No need for extension
    basename = os.path.splitext(simulfile)[0]
    try:
        if file_extension is None:
            file_extension = os.path.splitext(simulfile)[1]
    except Exception as e:
        print('Warning, no file extension used. %s.' % str(e))
        file_extension = ''

    print('File extension: %s' % file_extension)

    # Then, expand the base script
    batchlen, nicks, files = create_batches_func(basename, localdir, commondir, dowrite=0, 
                                                 runcmd=runcmd, strid=strid, nickstr=nickstr,
                                                 all_lines=all_lines, file_extension=file_extension)

    # Create the individual script files
    print('%d scripts ready for writing. e.g. %s' % (batchlen, files[0]))
    reply = input('Go on? (Y/n)?')
    if len(reply)==0:
        reply='y'
    if reply=='y':
        batchlen, nicks, batchfiles = create_batches_func(basename, localdir, commondir, 
                                                          dowrite=1, runcmd=runcmd, 
                                                          strid=strid, nickstr=nickstr,
                                                          commentid=commentid, batchid=batchid,
                                                          all_lines=all_lines, file_extension=file_extension,
                                                          only_simulfiles=only_simulfiles)
    if reply != 'y':
        return

    if only_simulfiles:
        return

    # Copy necessary files to commondir, if so needed
    for file2copy in files2copy.split(', '):
        if len(file2copy) == 0:
            continue
        #if not os.path.exists(file2copy): # does not work with wildcards
        all2copy = glob.glob(file2copy)
        if len(all2copy)==0:
            raise(ValueError('File to copy not found: %s' % file2copy))

        for thecopy in all2copy:    
            # Let's not copy large binaries since that takes very long...
            docopy = True
            if thecopy.endswith('.fits'):
                if os.path.exists(commondir+'/'+thecopy):
                    docopy = False
    
            if docopy:
                print('Copying %s to %s' % (thecopy, commondir))
                os.system('cp '+thecopy +' '+ commondir)
            else:
                print('File exists: %s/%s' % (commondir, thecopy))


    # Then, we are ready to run
    print('')
    reply = input('Should we launch the scripts (y/N)?')
    if len(reply)==0:
        reply='n'
    if reply=='y':
        print("OK, let's launch the scripts...")

        # Check, if the log files already exist
        if not overwrite:
            logfiles = get_logfiles(basename, params2modify, file_extension=file_extension)
            for logfile in logfiles:
                if not os.path.exists(logfile):
                    break
                else:
                    print('All the log files exist and overwrite forbidden. Nothing to do.')
                    return

        if platformparams is None:
            bare_launch_jobs(batchfiles, commondir, machinename, 
                             npermachine=npermachine)
        else:
            gcp_launch_jobs_flex(batchfiles, localdir, commondir, machinename, platformparams,
                                 npermachine=npermachine, overwrite=overwrite, runcmd=runcmd)
    else:
        print('Scripts not launched.')

