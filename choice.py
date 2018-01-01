# -*- coding:utf-8 -*-
import getch
import platform


def choice(prompt, choices):
    print(prompt, end='', flush=True)
    while True:
        userChoice = getch.getch()
        for c in choices:
            if userChoice == c:
                print(c)
                return choices.index(c)

def pause():
    getch.pause()
