import os
from colorama import Fore as c, Style


def arg_parse(*args):
    return ' '.join(tuple(map(lambda x: str(x), args)))


def take_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.LIGHTYELLOW_EX
    inp = input(arg)
    print(c.RESET, end='')
    return inp


def non_empty_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.LIGHTYELLOW_EX
    while True:
        inp = input(arg)
        if inp != '':
            print(c.RESET, end='')
            return inp


def input_from(msg,from_:tuple):
    while True:
        inp=non_empty_input(msg)
        if inp in from_:
            return inp
        print_red(f'Warning: Input from {from_}')


def print_yellow(*args):
    print(c.LIGHTYELLOW_EX + arg_parse(*args) + c.RESET)


def print_red(*args):
    print(c.LIGHTRED_EX + arg_parse(*args) + c.RESET)


def print_cyan(*args):
    print(c.LIGHTCYAN_EX + arg_parse(*args) + c.RESET)


def print_green(*args):
    print(c.LIGHTGREEN_EX + arg_parse(*args) + c.RESET)


def print_grey(*args):
    print(c.LIGHTBLACK_EX + arg_parse(*args) + c.RESET)


def print_heading(*args):
    print()
    print(Style.BRIGHT+c.LIGHTBLUE_EX, end='')
    st = arg_parse(*args)
    print(st)
    print('-'*len(st), end='')
    print(c.RESET + Style.NORMAL)


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
