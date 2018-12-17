#! /usr/bin/python3.6


import sys, time


log_path = '/home/east9698/test3.py.txt'

def main():
    while True:
        time.sleep(0.05)
        if sys.stdin.isatty():
            sys.stderr.write("keybord input!")
            sys.stdout.flush()
            continue
        else:
            sys.stdout.write("standard stream!!")
            #print(sys.stdin.isatty())
            
            #try:
            input = sys.stdin.read()
            out_file(input, log_path)
            sys.stdout.flush()
            sys.stdout.write("DONE!!!")
'''
    except TypeError:
        print("exception!")
        continue

    except:
        print("noting to input")
'''

def out_file(input, path):

    with open(path, mode='a') as file:
        file.write(input)
    

if __name__ == "__main__":
    main()
