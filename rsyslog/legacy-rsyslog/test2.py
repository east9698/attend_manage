#! /usr/bin/python3.6

import sys, select, fcntl, os

log_path = '/home/east9698/test2.py.txt'


def main():

    fd = sys.stdin.fileno() # file descripter for standerd input
    fl = fcntl.fcntl(fd, fcntl.F_GETFL) # get file status flag of "fd"
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # set "fd" as non-blocking file

    epoll = select.epoll() # create instance of epoll object
    epoll.register(fd, select.EPOLLIN) # register stdin stream to watching object with epoll

    try:
        while True:
            events = epoll.poll()
            for fileno, event in events:
                data = ""
                while True:
                    line = sys.stdin.read(64)
                    if not line:
                        break
                    data += line
                #out_file(data, log_path)
                print(data.upper(), end=";;\n")
    finally:
        epoll.unregister(fd)
        epoll.close()

        
def out_file(input, path):

    with open(path, mode='a') as file:
        file.write(input)
    

if __name__ == "__main__":
    main()


'''
    log_data = sys.stdin.read()
    inputs = [log_data]
    outputs = []

    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    while inputs:
        out_file(inputs, log_path)


        except:
            pass
        except OSError:

            print(sys.stdin.readable())
            select.select(sys.stdin.readline(), [], [], 0)
            input = sys.stdin.readline()
            out_file(input, log_path)
    exit()
'''
