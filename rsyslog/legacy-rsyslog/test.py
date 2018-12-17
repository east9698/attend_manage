#! /usr/bin/python3.6
import sys
import fcntl
import os
import time
import tty
import termios

class raw(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)





def main():

    with raw(sys.stdin):
        with nonblocking(sys.stdin):
            while True:
                input = sys.stdin.read(1)
                if input:
                    print(repr(input))
                else:
                    print('not ready')

    sys.stdout.write(input)
    out_file(input)
    sys.stdin.flush()
    time.sleep(.1)


def out_file(input):

    path = '/tmp/test.py.log'

    with open(path, mode='a') as file:
        file.write(input)
    

if __name__ == "__main__":
    main()
