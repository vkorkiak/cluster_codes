#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 12:04:17 2017

Implements a server that monitors local slave jobs.

@author: vkorkiak
"""

import subprocess
import socket
import os

monitor_tcpport = 6669


def slave_running(program_name):
    """
    Checks if a slave is running.
    """
    
    cmd = 'ps aux | grep '+program_name+' | grep -v grep'
    # print(cmd)
    proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
    output = (proc.communicate()[0]).decode()
    if len(output)==0:
        return False
    return True




def monitor_loop():
    """
    Implements a monitoring loop.
    Wait for clients to contact. Tell them if a process is running.
    """

    #create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #bind the socket to a public host,
    # and a well-known port
    serversocket.bind((socket.gethostname(), monitor_tcpport))
    #become a server socket
    serversocket.listen(5)
    
    while True:
        try:
            (conn, address) = serversocket.accept()
        except KeyboardInterrupt:
            print('Time to go')
            break
            
        try:
            print('Woke up...')
            data = conn.recv(1024)
                        
            if data.startswith(b'REQ#STATUS'):
                try:
                    toask = data[len('REQ#STATUS'):].decode()
                    if slave_running(toask):
                        answer = b'1'
                    else:
                        answer = b'0'
                        
                except Exception as e:
                    print('Error in slave_running. %s.' % str(e))
                    answer = b'NACK'
                    
                    
            elif data.startswith(b'REQ#EXISTS'):
                try:
                    toask = data[len('REQ#EXISTS'):].decode()
                    if os.path.exists(toask):
                        answer = b'1'
                    else:
                        answer = b'0'
                        
                except Exception as e:
                    print('Error in os.path.exists. %s.' % str(e))
                    answer = b'NACK'
                

            elif data.startswith(b'REQ#STARTJOB'):
                try:
                    job = data[len('REQ#STARTJOB'):].decode()
                    ret = os.system(job)
                    if ret==0:
                        answer = b'ok'
                    else:
                        answer = str(ret)
                        
                except Exception as e:
                    print('Error in job launch. %s.' % str(e))
                    answer = b'NACK'

                    
            else:            
                print(data)
                answer = b'NACK'
                
            conn.send(answer)
        except Exception as e:
            print('Error in loop. %s.' % str(e))
            
    try:
        conn.close()    
    except:
        pass
    try:
        serversocket.close()
    except Exception as e:
            print('Error. %s.' % str(e))
        
  
    
    
    
def request_status(server_addr, program_name):
    """
    A client side program can use this method to request status.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_addr, monitor_tcpport))
    s.send(b'REQ#STATUS'+program_name.encode('utf-8'))
    data = s.recv(1024)
    s.close()
    return data


def exists(server_addr, fname):
    """
    A client side program can use this method to check if files exist.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_addr, monitor_tcpport))
    s.send(b'REQ#EXISTS'+fname.encode('utf-8'))
    data = s.recv(1024)
    s.close()
    return data

def launch_job(server_addr, cmd):
    """
    A client side program can use this method to launch jobs.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_addr, monitor_tcpport))
    s.send(b'REQ#STARTJOB'+cmd.encode('utf-8'))
    data = s.recv(1024)
    s.close()
    return data








if __name__ == "__main__":
    
    #isrunning = slave_running('yorick')    
    #print(isrunning)
    
    print('Monitor loop begins...')
    monitor_loop()
