import time
import select
import sys
import threading
import os
import curses

def handleMessaging(test):
    pass
stdscr = curses.initscr()

maxY, maxX = stdscr.getmaxyx()

# Draw border
stdscr.border('|', '|', '-', '-', '+', '+', '+', '+')

# Draw message field
stdscr.addstr(maxY-3, 0, f"+{'-'*(maxX-2)}+")
stdscr.addstr(maxY-2, 2, "Zpráva:")

# Set cursor to the message field
stdscr.move(maxY-2, 10)

curses.noecho() # disable the keypress echo to prevent double input
curses.cbreak() # disable line buffers to run the keypress immediately
curses.curs_set(1)
stdscr.keypad(1) # enable keyboard use

lastMessageLine = 1

messageCharIndex = 0
message = ""

def spam():
    for i in range(10):
        global stdscr
        global lastMessageLine
        global messageCharIndex

        stdscr.addstr(lastMessageLine, 2, f"##: boo{i}")
        stdscr.move(maxY-2, 10 + messageCharIndex)
        stdscr.refresh()
        lastMessageLine += 1
        time.sleep(2)

threading.Thread(target=spam).start()
while True:
    char = stdscr.get_wch()
    if char == '\x03':
        # Exit on CTRL + C
        exit()
    elif char == '\n':
        stdscr.move(maxY-2, 10)
        stdscr.addstr(maxY-2, 10 , " "*(maxX - 11))

        stdscr.addstr(lastMessageLine, 2, f"Já: {message}")
        lastMessageLine += 1
        messageCharIndex = 0
        message = ""

        stdscr.move(maxY-2, 10)

        # Send message

    elif char == curses.KEY_BACKSPACE: # Backspace
        message = message[:-1]
        messageCharIndex -= 1
        if messageCharIndex < 0:
            messageCharIndex = 0

        stdscr.addstr(maxY-2, 10 + messageCharIndex, " ")
        stdscr.move(maxY - 2, 10 + messageCharIndex)

    else:
        message += char
        stdscr.addstr(maxY-2, 10 + messageCharIndex, char)
        messageCharIndex += 1
        stdscr.refresh()