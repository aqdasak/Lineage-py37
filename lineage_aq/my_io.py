from colorama import Fore as c, Style


def arg_parse(*args):
    return " ".join(tuple(map(lambda x: str(x), args)))


def take_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.LIGHTYELLOW_EX
    inp = input(arg)
    print(c.RESET, end="")
    return inp


def non_empty_input(arg):
    arg = c.LIGHTGREEN_EX + arg + c.LIGHTYELLOW_EX
    while True:
        inp = input(arg)
        if inp != "":
            print(c.RESET, end="")
            return inp


def input_from(msg, from_: tuple, *, IGNORE_CASE=True):
    from2 = from_
    if IGNORE_CASE:
        from2 = [i.lower() for i in from_]

        while True:
            inp = non_empty_input(msg).lower()
            if inp in from2:
                return inp
            print_red(f"Warning: Input from {from_}")

    else:
        while True:
            inp = non_empty_input(msg)
            if inp in from2:
                return inp
            print_red(f"Warning: Input from {from_}")


def input_in_range(msg: str, a: int, b: int = None) -> float:
    if b is not None:
        if b <= a:
            raise ValueError("Upper bound should be greater than lower bound")
        lb = a
        ub = b
    else:
        if a <= 0:
            raise ValueError("Upper bound should be greater than 0")
        lb = 0
        ub = a

    while True:
        inp = non_empty_input(msg)
        try:
            inp = float(inp)
            if lb <= inp < ub:
                return inp
            print_red(f"Warning: Input range is [{lb},{ub})")
        except Exception:
            print_red("Warning: Please input a number")


def print_red(*args, end="\n"):
    end = c.LIGHTRED_EX + end + c.RESET
    print(c.LIGHTRED_EX + arg_parse(*args) + c.RESET, end=end)


def print_green(*args, end="\n"):
    end = c.LIGHTGREEN_EX + end + c.RESET
    print(c.LIGHTGREEN_EX + arg_parse(*args) + c.RESET, end=end)


def print_blue(*args, end="\n"):
    end = c.LIGHTBLUE_EX + end + c.RESET
    print(c.LIGHTBLUE_EX + arg_parse(*args) + c.RESET, end=end)


def print_yellow(*args, end="\n"):
    end = c.LIGHTYELLOW_EX + end + c.RESET
    print(c.LIGHTYELLOW_EX + arg_parse(*args) + c.RESET, end=end)


def print_cyan(*args, end="\n"):
    end = c.LIGHTCYAN_EX + end + c.RESET
    print(c.LIGHTCYAN_EX + arg_parse(*args) + c.RESET, end=end)


def print_grey(*args, end="\n"):
    end = c.LIGHTBLACK_EX + end + c.RESET
    print(c.LIGHTBLACK_EX + arg_parse(*args) + c.RESET, end=end)


def print_heading(*args):
    print()
    print(Style.BRIGHT + c.LIGHTBLUE_EX, end="")
    st = arg_parse(*args)
    print(st)
    print("-" * len(st), end="")
    print(c.RESET + Style.NORMAL)


def print_id_name_in_box(id: str, name: str):
    n_len = len(name)
    i_len = len(id)
    print_yellow("\t ╭" + "─" * (max(n_len, i_len) + 2) + "╮")

    print_blue("ID:\t", end=" ")
    print_yellow("│", end=" ")
    print_cyan(id, end=" ")
    print_yellow(" " * max(n_len - i_len, 0) + "│")

    print_blue("Name:\t", end=" ")
    print_yellow("│", end=" ")
    print_cyan(name, end=" ")
    print_yellow(" " * max(i_len - n_len, 0) + "│")
    print_yellow("\t ╰" + "─" * (max(n_len, i_len) + 2) + "╯")
