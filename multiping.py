#!/usr/bin/env python


''' MULTIPING

=== Purpose
Pinge multiple IP/FQDN for i en tiemly fashion for å se etter noen drops og latency. Use-cases kan være monitorere ett sett med servere, alle upstream IP-adresser
 Ping every 500ms

=== Libraries used
pythonping 1.0.8   (pip install pythonping)

=== Arguments
Indef. adresser som skal pinges pinges.

=== Design
For hver ping-cycle, så lager main threads (pingworker) slik at alle ping går samtidig.
Når alle threads er kalt, så sover while-loop i 0.6 slik at alle threads kan gjøre seg ferdig før den printer resultat og starter loop på nytt

'''

''' REFERANSER
[1] https://www.pythonforbeginners.com/system/python-sys-argv
[2] https://www.guru99.com/learn-python-main-function-with-examples-understand-main.html
[3] https://pypi.org/project/pythonping/
[4] https://docs.python.org/3/library/threading.html
[5] https://pymotw.com/2/threading/
[6] http://zetcode.com/lang/python/lists/
[7] https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
[8] https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-12.php
'''

''' Pythonping hack requirement
Hack executor.py i Pythonping for å gi hver ping en egen ICMP ID. 
Eller så vil pythonping behandle alle ping consequtive pings som samme request. Gg coding guy.

#    C:\ Users\ USERNAME\ AppData\ Local\ Programs\ Python\ ython38\ Lib\ site-packages\ pythonping
          #  if self.seed_id is None:
            #self.seed_id = os.getpid() & 0xFFFF
        #    self.seed_id = random.randrange(1000,9999) & 0xFFFF
'''
 
''' Version log
v0.1-19feb2020, Gos, Laget kolonne for timestamp og ryddet i koden
'''

 
''' TODO LIST
        * Legg til timestamp på start og intermediate headers. Legg til en kolonne med sek+ms  (ss.nn). De gir nok insights  
        * Tidy og dokumenter kode - More documentation the better
* Lag en argument parser, --targets --t (parserkode her: https://packetstormsecurity.com/files/156592/Microsoft-Exchange-2019-15.2.221.12-Remote-Code-Execution.html)
* Gjor om så IP som pinges faktisk er samme some gethostnameaddr-thingy, i fall round robin DNS. (Den kan ha både headerresolved, og targetlist i stedet for syv.arghs)
* Implementer upstream funksjon
* Lag en result-summary etter stopp (Ala ordinær ping)
* Lag binary 

* Lag help-funksjon --help -h /?
* Vurder santization på input

* Implementer input fil -input 
* Fargekoding? Er det mulig? (Timeout kan være rød)
* OPT: 
 - Implementer --debug function som viser ip/FQDN, thread name/ID, loop counts og all annen fornuftig info
 - Implementer -c/--count for antall pings

'''




from pythonping import ping # [3] Pythonping 1.0.8
import sys                  # Her Sys. Den liker a vaere med pa leken tydeligvis. Skal dokumentere hvorfor naar jeg vet. *face palm*
import threading            # [4] [5]
import time                 # For time.sleep funksjon
import socket               # For FQDN-resolving


version = "v0.1-19feb2020"
author = "Gos"


pingresults = []            #Definer results-list Denne vil bli brukt til aa passe ping-resultater tilbake fra workers til main for print.


def pingworker(pingarg,pingid):                         # Function - Ping Thread worker - for passed ett target og pingid-index-verdi.
    #tname=threading.currentThread().getName()          # Thread name. Debug.
    pingcmd=ping(pingarg, count=1,timeout=0.5)          #
    if pingcmd.rtt_min_ms == 500:                       # Dersom RTT er 500(ms), så er resultat timeout
        result = "|>>  TIMEOUT  <<|"                    #
    else:                                               #
        result = str(pingcmd.rtt_min_ms)+'ms'           # Pingresultat er en convert av float pingcmd.rtt_min_ms til str og append "ms".
                                                        #
    pingresults.insert(pingid,result)                   # Insert [6] resultat i predefinert slot(pingid-index-verdi) i listen. 
    
      

def checktime():                                            # Function - Sjekker tid og gir result tilbake til caller.
    msint=str(int(round(time.time() * 1000)))               # Henter time og legger på 3 ekstra desimaler (ms) [8]
    ms=msint[-3:]                                           # Variabel ms er en slice av de tre siste chars i msint.
    return str(time.strftime("%H:%M:%S") + "." + ms)        # Time, minutt, sek, ms (00:24:10.452)
    

def main():

    # Print header
    print("\n\n     __  __ _   _ _  _____ ___ ___ ___ _  _  ___ ")
    print("    |  \/  | | | | ||_   _|_ _| _ \_ _| \| |/ __|")
    print("    | |\/| | |_| | |__| |  | ||  _/| || .` | (_ |")
    print("    |_|  |_|\___/|____|_| |___|_| |___|_|\_|\___|      (" + version + " by " + author + ")\n\n")
    
    #print("Number of args:",len(sys.argv[1:]))         # Debug. Forste argument er self (.py), sa regn kun fra argument 2 og utover.
    
    
    # Definer variabler som skal brukes direkte med method.
    headerlist = sys.argv[1:]   # Liste-objekt med alle arguments passed via Command line.
    threads = []                # Definer threads list-object. Brukes for aa kalle pingworker
    argcount = 0                # Define argcount, sa den kan references og increments i for loop
    loopcount = 0               # Loops counter
    totalcount = 0              # Total loops counters
    headerlisttrunc = []        # Truncate targetlist for display.
    headerlistresolved = []     # List for IP-adresser resolved fra oppgitt FQDN for display
    
    # Lag ett objekt for formattering. Vi onsker format med variabel-objekter (som henter verdi i fra headerlisttrunc)
    # Saa coloumns er en string som vi multipliserer (basic string formatting) med antall arguments (+1 for timekolonne) som ble passed inn til main.
    coloumns = str("{:^17}"*(len(sys.argv[1:])+1))      # string Kolonne er 17chars wide med sentrert tekst * multiplisert med ant. arg+1
                                                        # Ex:  "{:^17}{:^17}{:^17}{:^17}"
    
    
    # I headerlist - Legg til "tid" i forste kolonne
    headerlisttrunc.append(time.strftime("%Y-%m-%d"))                          # Populerer display header med dato
    headerlistresolved.append(""+time.strftime("%H:%M:%S")+"")                 # Populerer display header med klokkeslett
    
    
    # Truncate potensielle lange arguments (FQDN - f.eks.  http://thelongestlistofthelongeststuffatthelongestdomainnameatlonglast[.com)
    
    for header in headerlist:
        headerlisttrunc.append((header[:14] + '..') if len(header) > 16 else header)    # append 14chars+.. dersom header er over 16 chars, ellers append verdi i "header"
        headerlistresolved.append("("+socket.gethostbyname(header)+")")                 # Resolver FQDN  
    # Print header 
    print(coloumns.format(*headerlisttrunc))                # Print x antall kolonner (Variable coloumns) og populer med verdier fra variable (headerlisttrunc). 
    print(coloumns.format(*headerlistresolved))             # Ex:  {:^17}{:^17}{:^17}{:^17}.format(*variablelist)
    print("+---------------+"*(len(sys.argv[1:])+1))        # Print en header divider.
    
    
    
    
    while 1:                                                                # While-loop - hovedfunksjonalitet
        pingresults.insert(0,checktime())                                   # Insert [6] time i fremst i listen pingresults. 
        for arg in sys.argv[1:]:                                            # Handter hvert argument passed inn via CLI (OBS - skal endres til TARGETLIST)
            argcount += 1                                                   # Iterer argcount for aa bruke some pingid-verdi-index
            t=threading.Thread(target=pingworker, args=(arg,argcount,))     # Bruker threading [4][5] for å fyre av ping kommandoer samtidig vha func. pingworker
            threads.append(t)                                       
            t.start()                                                       # Start thread

        time.sleep(0.6)                                                     # Sleep i 0.6 sec, til alle threads er ferdig/gått i timeout(500ms)
        print(coloumns.format(*pingresults))                                # Print resultatet som er i listen pingresults. Formater som headers.
        
        argcount=0                                                          # Resett argcounter brukt i for-loop 
        del pingresults[:] # [6] Clear results for new iteration            # Slett alle verdier i pingresults for ny loop
        
        loopcount+=1                                                        # Iterer loopcount
        #totalcount+=1                                                      # Iterer totalcount - skal brukes til sluttrapport
        if loopcount==50:                                                   # For hvert 50. pingcycle, display header igjen
                print("+---------------+"*(len(sys.argv[1:])+1))
                print(coloumns.format(*headerlisttrunc))
                print(coloumns.format(*headerlistresolved))
                print("+---------------+"*(len(sys.argv[1:])+1))
                loopcount=0                                                 # Resett loop counter
        
    
    
# Trengs for aa kjore some standalone [2]   
if __name__== "__main__":
    main()