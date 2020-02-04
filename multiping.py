#!/usr/bin/env python


''' MULTIPING

Purpose: Pinge multiple IP/FQDN for i en tiemly fashion for å se etter noen drops og latency. Use-cases kan være monitorere ett sett med servere, alle upstream IP-adresser

Arguments
 - Frequency 0.5sec, 1 sec, osv
 
 Ping every 500ms
 Print result every 5000ms

Benytte eget library da Wincommand Ping ikke er spesifikk nok


Libraries used
pythonping 1.0.8   (pip install pythonping)

Modes
 Ping ips in list
 Ping IPs passed in argument
 Ping --upstream > Kjør traceroute og pinge alle upstreams 
'''

'''
[1] https://www.pythonforbeginners.com/system/python-sys-argv
[2] https://www.guru99.com/learn-python-main-function-with-examples-understand-main.html
[3] https://pypi.org/project/pythonping/
[4] https://docs.python.org/3/library/threading.html
[5] https://pymotw.com/2/threading/
'''

'''
1) Få inn IP/FQDN som arguments
2) Optional: Sanatize input 
3) Resolve any FQDN (Trengs ikke)


'''

# Requirement. Hack executor.py i Pythonping for å gi hver ping en egen ICMP ID. 
# Eller så vil pythonping behandle alle ping consequtive pings som samme request. Gg coding guy.


#    C:\Users\Gos\AppData\Local\Programs\Python\Python38\Lib\site-packages\pythonping
'''        if self.seed_id is None:
            #self.seed_id = os.getpid() & 0xFFFF
            self.seed_id = random.randrange(1000,9999) & 0xFFFF
'''

from pythonping import ping # [3] Pythonping 1.0.8
import sys
import threading            # [4] [5]
import time                 # For time.sleep funksjon

def pingworker(pingarg):
    # Ping Thread worker
    tname=threading.currentThread().getName()
    varname=ping(pingarg, count=1,timeout=1)            # Pythonping
    print(tname, pingarg,'-----',varname.rtt_min_ms,"\n",80*"-","\n")
    
# NEXT blir å få presentert dette i tabellformat.
# Dernest å få loopet ping
    
 



def main():
    #Definer threads array
    threads = []
    #Definer en local-thread variant av arg slik at data ikke kan endres på tvers av workers.
    # print command line arguments [1]
    for arg in sys.argv[1:]:
        #santize()
        #Bruker threading [4][5] for å fyre av ping kommandoer samtidig
        
        t=threading.Thread(target=pingworker, args=(arg,))
        threads.append(t)
        t.start()
        #time.sleep(0.1)  # Problemet her er at pingarg som kalles i pingworker er global og det blir noe buggy
        #print(arg)
        
        #print(ping(arg, timeout=0.5, count=1))
    # Alle threads er definert i for loop og startes her
    
    
        #ping all args
        #format and display result
        #Loop back into main
        
    
    
# Trengs for aa kjore some standalone [2]   
if __name__== "__main__":
    main()