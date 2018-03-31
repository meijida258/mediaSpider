#-*- coding: UTF-8 -*-
import curses

width, length = 40, 60
score = 0
stdscr = curses.initscr()
curses.nocbreak()
curses.echo()
stdscr.nodelay(0)



def draw():
    global stdscr, score
    stdscr.addstr(0,0, '—'*5 + 'score: %s' % score + '—'*(width-5))
    for each_len in range(1, length):
        stdscr.addstr(0,each_len,'|')
        stdscr.addstr(width, each_len, '|')
    stdscr.addstr(width, 0, '—' * 5 + 'score: %s' % score + '—' * (width - 5))


draw()
ch=stdscr.getstr()
stdscr.nodelay(1)
curses.endwin()
