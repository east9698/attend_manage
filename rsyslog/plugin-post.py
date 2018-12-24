#! /usr/bin/python3.6

import sys, re, json
#from pathlib import Path
import urllib
import json
#### Regex Patterns ####

# patterns of required log line
ptn_event = r"eventmgr: EVENT\[\d+\]" 
ptn_gandalf = r"gandalf:"
'''
gandalf: Received RADIUS Packet (Length:'170',Code:'Access-Accept',Id:'35',Calling-Station-id='DC-0C-5C-79-48-0D') from RADIUS Server (Ip:'192.168.100.13',Port:'1812') for User (nas-port:'476',username:'east9698')
'''
'''
2018-12-25T08:18:14.150908+09:00 Disassociate request from gandalf for dc:0c:5c:79:48:0d
2018-12-25T08:18:14.150908+09:00 192.168.100.12 gandalf: Aborting RADIUS user login (mac-address='DC:0C:5C:79:48:0D') (cause='RADIUS timeout').
2018-12-25T08:18:14.150908+09:00 192.168.100.12 gandalf: Sending EAPOL (frame-length='22') EAP Failure (length='4',id='112') to station (mac-address='DC:0C:5C:79:48:0D').
2018-12-25T08:18:14.150908+09:00 192.168.100.12 gandalf: Disassociating wireless client DC:0C:5C:79:48:0D2018-12-25T08:18:14.151192+09:00 192.168.100.12 gandalf: RADIUS User (id='FACB7B6C') access request (id='00000000') ends unsuccessfully (aborted).
2018-12-25T08:18:14.151513+09:00 192.168.100.12 gandalf: Sending EAPOL (frame-length='22') EAP Failure (length='4',id='113') to station (mac-address='DC:0C:5C:79:48:0D').
2018-12-25T08:18:14.151513+09:00 192.168.100.12 gandalf: Disassociating wireless client DC:0C:5C:79:48:0D2018-12-25T08:18:14.151788+09:00 Disassociate request from gandalf for dc:0c:5c:79:48:0d
2018-12-25T08:18:14.157432+09:00 192.168.100.12 gandalf: [AccessControllerServer/AssociationMgr] Handling lost association (type='mac',mac-address='DC:0C:5C:79:48:0D)
2018-12-25T08:18:14.157600+09:00 192.168.100.12 gandalf: [AccessControllerServer] Received a lost association event (type='mac',mac-address='DC:0C:5C:79:48:0D)
2018-12-25T08:18:14.158087+09:00 192.168.100.12 gandalf: [AccessControllerServer] Terminating session (type='mac',mac-address='DC:0C:5C:79:48:0D) related to lost association (type='mac',mac-address='DC:0C:5C:79:48:0D)
2018-12-25T08:18:14.158087+09:00 192.168.100.12 gandalf: [AccessControllerServer] Received a terminated client session event (type='mac',mac-address='DC:0C:5C:79:48:0D)
2018-12-25T08:18:17.838850+09:00 192.168.100.12 rfmgr_ap: Wireless RRM event: Scan complete on Radio 1 (reason = 1) (appl=)
2018-12-25T08:18:17.839029+09:00 192.168.100.12 rfmgr_ap: Radio 1 RMAMLoadNeighborhood ioctl Query returned 19 entries
2018-12-25T08:18:18.169111+09:00 192.168.100.12 eventmgr: EVENT[5989] No response was received from RADIUS server for request sent by client (mac='DC:0C:5C:79:48:0D') on interface (value='r1v1')
2018-12-25T08:18:18.170768+09:00 192.168.100.12 eventmgr: EVENT[5990] Request to RADIUS server from client (mac='DC:0C:5C:79:48:0D') on interface (value='r1v1') timed out while performing 802.1x Authentication
2018-12-25T08:18:18.172150+09:00 192.168.100.12 eventmgr: EVENT[5991] AP sent a deauthentication request to client (mac='DC:0C:5C:79:48:0D') on interface (value='r1v1') using SSID (value='attend-manage') with a reason code (value='Unspecified')

'''
ptn_macaddr = r"(?P<mac_addr>([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})" # patterns of MAC address
#ptn_connect = r"Client .*? has successfully authenticated" # patterns of logs when the client associate connection with the AP
ptn_connect = r"Received RADIUS Packet.*?Code:'Access-Accept'.*?Calling-Station-id='(?P<mac_addr>([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2})'.*?username:'(?P<username>(/w)'"
ptn_disconnect = r"AP received a disassociation request" # patterns of logs when user turned off the client Wi-Fi controller or switch another AP
ptn_outrange = r"Received a lost association event.*?mac=address='(?P<mac_addr>[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})'" # patterns of logs when client goes out of the AP range
ptn_timeout = r"No response was received"

reg_evn = re.compile(ptn_event)
reg_gnd = re.cpomile(ptn_gandalf)
reg_mac = re.compile(ptn_macaddr)
reg_con = re.compile(ptn_connect)
reg_dis = re.compile(ptn_disconnect)
reg_out = re.compile(ptn_outrange)
reg_tim = re.compile(ptn_timeout)

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
    global post_url
    post_url = 'http://192.168.100.13/log/'

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
        post_data = detect_log_type(msg, log_file)
        post_log(post_url, post_data, log_file)
        log_file.flush()
        log_file.close()

    sys.stderr.write("msg wrote")
    sys.stderr.flush()

    
def onExit():

    #log_file.close()
    sys.stderr.write("onExit!")
    sys.stderr.flush()


def detect_required_log(line):
    if reg_gnd.search(line):
        log = reg_gnd.search(line)
    elif reg_evn.search(line):
        log = reg_evn.search(line)
    return log

def detect_mac_addr(line):
    try:
        m = reg_mac.search(line)
        return m.group("mac_addr")
    except AttributeError:
        return None

def detect_username(line):
    try:
        m = reg_mac.search(line)
        return m.group('username')
    except AttributeError:
        return None

def detect_log_type(line, file):
    
    mac_addr = detect_mac_addr(line)

    if reg_con.search(line):
        username = detect_username(line)
        post_data = {
            'status': True,
            'username': username,
            'mac_addr': mac_addr
        }
        file.write(line)
        file.write("#####The client (%s) is connected and successfully authorized.\n\n" % (mac_addr))
    elif reg_dis.search(line) or reg_out.search(line) or reg_tim.search(line):
        post_data = {
            'status': False,
            'mac_addr': mac_addr
        }
        file.write(line)
        file.write("#####The client (%s) is disconnected by user's operation.\n\n" % (mac_addr))
    elif reg_out.search(line):
        post_data = {
            'status': False,
            'mac_addr': mac_addr
        }
        file.write(line)
        file.write("#####The client (%s) is disconnected since the client went to out of the coverage area.\n\n" % (mac_addr)) # after 5 min from the first disconnect detection
    elif reg_tim.search(line):
        post_data = {
            'status': False,
            'mac_addr': mac_addr
        }
        file.write(line)
        file.write("#####The client (%s) is disconnected by connection timeout.\n\n" % (mac_addr)) # after 5 min from the first disconnect detection
   
    return post_data

def post_log(url, data, log):

    headers = {'Content-Type': 'application/json'}
    method = 'POST'
    json_data = json.dumps(data).encode('utf-8')

    reqest = urllib.request.Request(url, data=json_data, method=method, headers=headers)

    try:
        with urllib.request.urlopen(reqest) as res:
            log.write(res.getcode())
    except urllib.error.HTTPError as err:
        log.write(err.code)
    except urllib.error.URLError as err:
        log.write(err.reason)


if __name__ == "__main__":
    main()
