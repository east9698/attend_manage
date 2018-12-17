#! /usr/bin/python3.6

import sys, time
#from pathlib import Path


def main():

    #global i 
    i = 0
    onInit()

    while True:
        
        i += 1
        sys.stderr.write('loop')
        sys.stderr.flush()
        sys.stderr.write(str(i)+"\n")
        sys.stderr.flush()
        
        msg = sys.stdin.readline()

        if msg:
            sys.stderr.write('msg read')
            msg = msg[:-1]
            onReceive(msg)
        else:
            sys.stderr.write('loop broken')
            #time.sleep(0.01)
            break

    onExit()
    sys.stdout.flush()
    

def onInit():

    #sys.stdout.write('OK') # responce confirm message to rsyslog
    #sys.stdout.flush()

    global log_path
    #global log_file
    log_path = "/var/log/attend-manage.log" # Caution!:: check the permission of "/var/log/" directory for syslog:syslog(needs FULL permission)

def onReceive(msg):
    '''
    file_path = Path(log_path)

    if file_path.exists():
        pass
    else:
        check_file = create_file(log_path)
        #pass
    '''
    
    with open(log_path, 'a') as log_file:
        #log_file.write(str(msg) + "\n")
        log_file.write(str(msg) + "\n")
        log_file.flush()
    sys.stderr.write("msg wrote")
    sys.stderr.flush()

    
def onExit():

    #log_file.close()
    sys.stderr.write("onExit!")
    sys.stderr.flush()

if __name__ == "__main__":
    main()
