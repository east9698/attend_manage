#! /usr/bin/python3.6

import sys, re, json
#from pathlib import Path


#### Regex Patterns ####

ptn_event = r"eventmgr: EVENT\[\d+\]" # patterns of required log line
ptn_macaddr = r"(?P<mac_addr>([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})" # patterns of MAC address
ptn_connect = r"Client .*? has successfully authenticated" # patterns of logs when the client associate connection with the AP
ptn_disconnect = r"AP received a disassociation request" # patterns of logs when user turned off the client Wi-Fi controller or switch another AP
ptn_outrange = r"No response was received" # patterns of logs when client goes out of the AP range

reg_log = re.compile(ptn_event)
reg_mac = re.compile(ptn_macaddr)
reg_con = re.compile(ptn_connect)
reg_dis = re.compile(ptn_disconnect)
reg_out = re.compile(ptn_outrange)

#### End ####


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
            #msg = msg[:-1]
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
   
    #global log_file
    global log_path
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
    if detect_required_log(msg):
        log_file = open(log_path, 'a')
        #log_file.write(str(msg) + "\n")
        detect_log_type(msg, log_file)
        log_file.flush()
        log_file.close()

    sys.stderr.write("msg wrote")
    sys.stderr.flush()

    
def onExit():

    #log_file.close()
    sys.stderr.write("onExit!")
    sys.stderr.flush()


def detect_required_log(line):
    return reg_log.search(line)

def detect_mac_addr(line):
    try:
        m = reg_mac.search(line)
        return m.group("mac_addr")
    except AttributeError:
        return None


def detect_log_type(line, file):
    
    mac_adder = detect_mac_addr(line)

    if reg_con.search(line):
        file.write(line)
        file.write("#####The client (%s) is connected and successfully authorized.\n\n" % (mac_adder))
    if reg_dis.search(line):
        file.write(line)
        file.write("#####The client (%s) is disconnected by user's operation.\n\n" % (mac_adder))
    if reg_out.search(line):
        file.write(line)
        file.write("#####The client (%s) is disconnected since the client went to out of the coverage area.\n\n" % (mac_adder)) # after 5 min from the first disconnect detection


if __name__ == "__main__":
    main()
