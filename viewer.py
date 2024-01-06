#!/usr/bin/python3

import socket
import curses
from curses.textpad import Textbox, rectangle

HOST='192.168.0.222'
PORT=11000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.settimeout(2)

SPEEDFORMAT="KTS"
HEIGHTFORMAT="M "


def formatSpeed(speed):
    if SPEEDFORMAT=="KTS":
        return speed + " KTS"
    elif SPEEDFORMAT=="KPH":
        return (str(round(float(speed) * 1.852,1)) + " kph ")
    elif SPEEDFORMAT=="MPH":
        return (str(round(float(speed)  * 1.15078,1))+ " mph ")
    elif SPEEDFORMAT=="MS":
        return (str(round(float(speed) * 0.51444469144779115,1)) + " M/S ")
    else:
        return 0        
def formatHeight(height):
    if HEIGHTFORMAT=="M":
        return height + " M"
    elif HEIGHTFORMAT=="FT":
        return (str(round(float(height) *  3.28084,1)) + " ft ")
    else:
        return 0


rxBufferStr=""
rxBufferArray=""

def addSpeedFormatBtn():
    stdscr.move(15, 2)
    stdscr.addstr("[ s: " )
    stdscr.addstr(SPEEDFORMAT + " ")
    stdscr.addstr(" ]")

def addHeightFormatBtn():
    stdscr.move(15, 14)
    stdscr.addstr("[ h: " )
    stdscr.addstr(HEIGHTFORMAT+" ")
    stdscr.addstr(" ]")   

def addQuitBtn():
    stdscr.move(15, 25)
    stdscr.addstr("[ q: quit ]" )


def cleanup():
    curses.echo()
    stdscr.keypad(False)
    curses.nocbreak()
    curses.endwin()


isRunning=True
isError=False

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.nodelay(True)


stdscr.clear()

editwin = curses.newwin(5,30, 2,1)
rectangle(stdscr, 1,0, 12, 40)
rectangle(stdscr, 14,0, 16, 40)


stdscr.move(2, 2)
stdscr.addstr("Time:")
stdscr.move(2, 20)
stdscr.addstr("Date:")

stdscr.move(4, 2)
stdscr.addstr("Lat:")
stdscr.move(4, 20)
stdscr.addstr("Long:")

stdscr.move(6, 2)
stdscr.addstr("Speed:")
stdscr.move(6, 20)
stdscr.addstr("Heading:")
stdscr.move(8, 2)
stdscr.addstr("Height:")

stdscr.move(10, 2)
stdscr.addstr("Sats In View:")

addSpeedFormatBtn()
addHeightFormatBtn()
addQuitBtn();

stdscr.refresh()

while isRunning:
    ch = stdscr.getch()

    if ch==27 or ch==ord('q') or ch==ord('Q'): #escape
        isRunning=False
    if ch==ord('s') or ch==ord('S'):
        if SPEEDFORMAT=="KTS":
            SPEEDFORMAT="MPH"
        elif SPEEDFORMAT=="MPH":
            SPEEDFORMAT="KPH"
        elif SPEEDFORMAT=="KPH":
            SPEEDFORMAT="MS"
        else:    
            SPEEDFORMAT="KTS"

        addSpeedFormatBtn()
    if ch==ord('h') or ch==ord('H'):
        if HEIGHTFORMAT=="M":
            HEIGHTFORMAT="FT"
        else:
            HEIGHTFORMAT="M"

        addHeightFormatBtn()

    #Handle socket
        
    try:

        recvstr=s.recv(1024).decode('utf-8')
        data = rxBufferStr + recvstr

        data=data.replace('\0','')
        
        rxBufferArray=data.split('\r\n')

        if data[-2:]=='\r\n':
            rxBufferStr=""        
        else:
            rxBufferStr=rxBufferArray.pop()

        #Process Message
        
        for thisLine in rxBufferArray:
            #stdscr.move(0, 24)
            #stdscr.addstr(thisLine)

            #values,checksum=thisLine.split('*')
            values=thisLine

            elements=values.split(',')

            if elements[0]=="$GPRMC":
                stdscr.move(2, 8) #time
                stdscr.addstr(elements[1])

                stdscr.move(2,25) #date
                stdscr.addstr(elements[9])

                stdscr.move(4,8) #lat
                stdscr.addstr(elements[3] + elements[4])

                stdscr.move(4,26) #long
                stdscr.addstr(elements[5] + elements[6])

                stdscr.move(6, 8) #speed
                stdscr.addstr(formatSpeed(elements[7]))

                stdscr.move(6,26) #heading
                stdscr.addstr(elements[8])
            elif elements[0]=="$GPGGA":
                stdscr.move(2, 8) #time
                stdscr.addstr(elements[1])

                stdscr.move(4,8) #lat
                stdscr.addstr(elements[2] + elements[3])

                stdscr.move(4,26) #long
                stdscr.addstr(elements[4] + elements[5])

                stdscr.move(8,10) #height
                stdscr.addstr(formatHeight(elements[9]))

                stdscr.move(10,16) #sats in view
                stdscr.addstr(elements[7])

            

    except socket.timeout as e:
        err = e.args[0]
    except socket.error as e:    
        cleanup()
        print(e)
        isRunning=False
        isError=True


if isError==False:
    cleanup()
        
