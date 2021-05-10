# -*- coding: utf-8 -*-
"""
Created on Fri May  7 13:33:19 2021

@author: Ben
"""

''' 
for each file
    store all title line numbers with:
        title line (could be blank)
        blank line
        day of the week
        number time with AM or PM
            import time
    
            def isTimeFormat(input):
                try:
                    time.strptime(input, '%H:%M')
                    return True
                except ValueError:
                    return False
            
            isTimeFormat('12:12')
            
    for each section of text:
        create file with name as title line. if blank set title line to first 5 words of text
        build create date with day of week plus time. datetime to unix timestamp
            from datetime import datetime
            from time import mktime
            t = datetime.now()
            unix_secs = mktime(t.timetuple())
        set file to new create date
            from win32_setctime import setctime
            setctime("my_file.txt", 1561675987.509)
        read text in line by line
'''   

from collections import deque
import time
import datetime as dt
from pytz import timezone
from win32_setctime import setctime
from os import utime

def isTimeFormat(i):
    try:
        time.strptime(i, '%H:%M')
        return True
    except ValueError:
        return False

eastern = timezone('US/Eastern')
note_lines = set()
prev_lines = deque([], maxlen=4)
dow = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

with open(r"C:\Users\Ben\Downloads\onenote_journal.txt","r", errors="ignore") as file:
    for line_num, curr_line in enumerate(file, 1):
        prev_lines.appendleft(curr_line)
        if line_num < 6:
            if line_num == 1:
                note_lines.add(line_num)
            continue
        
        if (":" in curr_line and isTimeFormat(curr_line.split()[0]) and 
            prev_lines[1].split(",")[0] in dow):
                note_lines.add(line_num - 3)

curr_file_loc = None
curr_title = None
curr_datetime = None
lines = []
invalid_chars = ['<','>',':','"','/','\\','|','?','*']

with open(r"C:\Users\Ben\Downloads\onenote_journal.txt","r", encoding="utf-8") as file:
    for line_num, curr_line in enumerate(file, 1):
        # title found
        if line_num in note_lines:
            if curr_file_loc is not None:
                print("writing to", curr_file_loc)
                file = open(curr_file_loc, "w", errors="strict", encoding='utf-8')
                file.writelines(lines)
                file.close()
                setctime(curr_file_loc, curr_datetime)
                utime(curr_file_loc, (curr_datetime, curr_datetime))
                lines.clear()
                curr_file_loc = None
                
            curr_title = curr_line
        # Date found
        elif line_num - 2 in note_lines:
            curr_datetime = dt.datetime.strptime(curr_line.rstrip(), '%A, %B %d, %Y')
        # Time found
        elif line_num - 3 in note_lines:
            curr_datetime = dt.datetime.combine(curr_datetime, 
                                                dt.datetime.strptime(curr_line.split()[0], '%H:%M').time())
            curr_datetime = eastern.localize(curr_datetime)
            curr_datetime = time.mktime(curr_datetime.timetuple())
        else:
            if curr_file_loc is None and not curr_line.isspace():
                if curr_title.isspace():
                    curr_title = ' '.join(curr_line.split()[:7])
                else:
                    curr_title = curr_title[0:-1]
                
                for char in invalid_chars:
                    curr_title = curr_title.replace(char, " ")
                
                curr_file_loc = r"C:\Users\Ben\Documents\joplin_conversion\\" + curr_title + ".md"
                
                print("found", curr_file_loc)
            if curr_file_loc is not None:
                lines.append(curr_line)


file = open(curr_file_loc, "w", errors="strict", encoding='utf-8')
file.writelines(lines)
file.close()
setctime(curr_file_loc, curr_datetime)
utime(curr_file_loc, (curr_datetime, curr_datetime))
lines.clear()

