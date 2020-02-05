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
[6] http://zetcode.com/lang/python/lists/
'''



# Requirement. Hack executor.py i Pythonping for å gi hver ping en egen ICMP ID. 
# Eller så vil pythonping behandle alle ping consequtive pings som samme request. Gg coding guy.


#    C:\Users\Gos\AppData\Local\Programs\Python\Python38\Lib\site-packages\pythonping
'''        if self.seed_id is None:
            #self.seed_id = os.getpid() & 0xFFFF
            self.seed_id = random.randrange(1000,9999) & 0xFFFF
'''

# TODO LIST
'''
* Legg til timestamp på start og intermediate headers 
* Tidy og dokumenter kode
* Lag help-funksjon --help -h /?
* Vurder santization på input
* Implementer upstream funksjon
'''




from pythonping import ping # [3] Pythonping 1.0.8
import sys                  # Her Sys. Den liker a vaere med pa leken tydeligvis. Skal dokumentere hvorfor naar jeg vet. *face palm*
import threading            # [4] [5]
import time                 # For time.sleep funksjon
import socket               # For FQDN-resolving

version = "v0.1-05feb2020"
author = "Gos"


#Definer results-list Denne vil bli brukt til aa passe ping-resultater tilbake fra workers til main for print.
pingresults = []

def pingworker(pingarg,pingid):
    # Ping Thread worker
    tname=threading.currentThread().getName()           # Thread name. Debug.
    varname=ping(pingarg, count=1,timeout=0.5)            # Pythonping
    if varname.rtt_min_ms == 500:
        result = " >> TIMEOUT <<"
    else:
        result = str(varname.rtt_min_ms)+'ms'   # Konverter float varname.rtt_min_ms til string og append ms

    pingresults.insert(pingid,result) # Insert [6] resultat i predefinert slot i listen. 
    #print(threading.current_thread())
      
 


def main():

    # Print header
    print("\n\n __  __ _   _ _  _____ ___ ___ ___ _  _  ___ ")
    print("|  \/  | | | | ||_   _|_ _| _ \_ _| \| |/ __|")
    print("| |\/| | |_| | |__| |  | ||  _/| || .` | (_ |")
    print("|_|  |_|\___/|____|_| |___|_| |___|_|\_|\___|      (" + version + " by " + author + ")\n\n")
    
    #print("Number of args:",len(sys.argv[1:])) # Debug. Forste argument er self (.py), sa regn kun fra argument 2 og utover.
    
    
    # Definer variabler som skal brukes direkte med method.
    headerlist = sys.argv[1:]   # Liste-objekt med alle arguments passed via Command line.
    threads = []                # Definer threads list-object. Brukes for aa kalle pingworker
    argcount = 0                # Define argcount, sa den kan references og increments i for loop
    loopcount = 0               # Loops counter
    totalcount = 0              # Total loops counters
    headerlisttrunc = []        # Truncate targetlist for display.
    headerlistresolved = []     # List for IP-adresser resolved fra oppgitt FQDN
    
    # Lag ett objekt for formattering. Vi onsker format med variabel-objekter som henter verdi i fra headerlisttrunc
    # Saa coloumns er en string som vi multipliserer (basic string formatting) med antall arguments passed inn til main.
    coloumns = str("{:^17}"*len(sys.argv[1:]))
    
    # Truncate potensielle lange arguments (FQDN - f.eks.  http://thelongestlistofthelongeststuffatthelongestdomainnameatlonglast[.com)
    for header in headerlist:
        headerlisttrunc.append((header[:14] + '..') if len(header) > 16 else header)
        headerlistresolved.append("("+socket.gethostbyname(header)+")")
    
    # Print header 
    print(coloumns.format(*headerlisttrunc))
    print(coloumns.format(*headerlistresolved))
    print("+---------------+"*len(sys.argv[1:]))
    
    
    while 1:
        for arg in sys.argv[1:]:
            #santize()
            #Bruker threading [4][5] for å fyre av ping kommandoer samtidig
            argcount += 1
            #print(argcount)
            t=threading.Thread(target=pingworker, args=(arg,argcount,))
            threads.append(t)
            t.start()
            #time.sleep(0.1)  # Problemet her er at pingarg som kalles i pingworker er global og det blir noe buggy
            #print(arg)
            
            #print(ping(arg, timeout=0.5, count=1))
        # Alle threads er definert i for loop og startes her
        time.sleep(0.6)
        loopcount+=1
        totalcount+=1
        print(coloumns.format(*pingresults))
        #print("{:^18}{:^18}{:^18}{:^18}".format(*pingresults)) 
        # For each 30 ping - også print headers
        #print(threading.active_count())
        argcount=0
        
        del pingresults[:] # [6] Clear results for new iteration
        #ping all args
        #format and display result
        #Loop back into main
        if loopcount==30:
                print("+---------------+"*len(sys.argv[1:]))
                print(coloumns.format(*headerlisttrunc))
                print(coloumns.format(*headerlistresolved))
                print("+---------------+"*len(sys.argv[1:]))
                loopcount=0
        
    
    
# Trengs for aa kjore some standalone [2]   
if __name__== "__main__":
    main()