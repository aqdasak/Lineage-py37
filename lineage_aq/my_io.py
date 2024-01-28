from __future__ import annotations
from typing import Callable
from colorama import Fore as c, Style

from lineage_aq import Person


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
    print(Style.BRIGHT + c.LIGHTMAGENTA_EX, end="")
    st = arg_parse(*args)
    print(st)
    print("-" * len(st), end="")
    print(c.RESET + Style.NORMAL)


def print_id_name_in_box(id: str, name: str):
    n_len = len(name)
    i_len = len(id)
    print_green("\t ╭" + "─" * (max(n_len, i_len) + 2) + "╮")

    print_blue("ID:\t", end=" ")
    print_green("│", end=" ")
    print_green(id, end=" ")
    print_green(" " * max(n_len - i_len, 0) + "│")

    print_blue("Name:\t", end=" ")
    print_green("│", end=" ")
    print_green(name, end=" ")
    print_green(" " * max(i_len - n_len, 0) + "│")
    print_green("\t ╰" + "─" * (max(n_len, i_len) + 2) + "╯")


def print_tree(
    tree: dict[Person, dict],
    occurance: dict[Person, int] = {},
    person_repr: Callable[[Person], str] = repr,
):
    """
    Print the dict of dict into tree

    Parameters
    ----------
    tree: dict[Person, dict]
        recursive dict containing parent as key and dict containing children
    occurance: dict[Person, int]
        contains the number of occurances of any person in the tree
    person_repr: Callable[[Person], str]
        function which represent string representation of the person to be printed

    Example
    -------
    ```
    tree = {
        "foo": {
            "bar": {"a": {"1": {"2": {}, "3": {}}}, "b": {}},
            "baz": {},
            "qux": {"c\nd": {}},
        },
    }

    print_tree(tree)
    ```

    Output:
    foo
    ├── bar
    │   ├── a
    │   │   └── 1
    │   │       ├── 2
    │   │       └── 3
    │   └── b
    ├── baz
    └── qux
        └── c⏎d
    """
    VERTICAL = "│   "
    HORIZONTAL = "─── "
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    EMPTY = " " * len(BRANCH)
    LEN = len(BRANCH)

    def replace(st: str) -> str:
        return (
            st.replace(BRANCH, VERTICAL)
            .replace(LAST_BRANCH, EMPTY)
            .replace(HORIZONTAL, EMPTY)
        )

    def _print_tree(tree: dict[Person, dict], connector=""):
        print()
        if isinstance(tree, dict):
            connector = replace(connector) + BRANCH
            for i, (person, subtree) in enumerate(tree.items(), 1):
                if i == len(tree):
                    connector = replace(connector[:-LEN]) + LAST_BRANCH

                print(connector[LEN:], end="")
                if person in duplicates:
                    if duplicates[person]:
                        print_grey(person_repr(person), end="")
                        _print_tree(subtree, connector + c.LIGHTBLACK_EX)
                    else:
                        print(person_repr(person), end="")
                        duplicates[person] = True
                        _print_tree(subtree, connector)
                else:
                    print(person_repr(person), end="")
                    _print_tree(subtree, connector)

    # When False for first time print it in regular color, then print in grey for all occurances
    duplicates = {k: False for k, v in occurance.items() if v > 1}
    _print_tree(tree)
