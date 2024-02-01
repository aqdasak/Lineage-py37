from __future__ import annotations
from typing import Callable
from colorama import Fore as c, Style

from lineage_aq import Person


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


def _print_colored(color, *args, **kwargs):
    print(color, end="")
    print(*args, **kwargs)
    print(c.RESET, end="")


def print_red(*args, **kwargs):
    _print_colored(c.LIGHTRED_EX, *args, **kwargs)


def print_green(*args, **kwargs):
    _print_colored(c.LIGHTGREEN_EX, *args, **kwargs)


def print_blue(*args, **kwargs):
    _print_colored(c.LIGHTBLUE_EX, *args, **kwargs)


def print_yellow(*args, **kwargs):
    _print_colored(c.LIGHTYELLOW_EX, *args, **kwargs)


def print_cyan(*args, **kwargs):
    _print_colored(c.LIGHTCYAN_EX, *args, **kwargs)


def print_grey(*args, **kwargs):
    _print_colored(c.LIGHTBLACK_EX, *args, **kwargs)


def print_heading(*args):
    print()
    print(Style.BRIGHT + c.LIGHTMAGENTA_EX, end="")
    print(*args)
    print("-" * len(" ".join(args)), end="")
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
    print_spouse=True,
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

                spouse = ""
                if print_spouse:
                    if person.gender == "m":
                        spouse = person.wife
                    else:
                        spouse = person.husband
                    if spouse:
                        spouse = [person_repr(s) for s in spouse]
                        spouse = "- " + ",".join(spouse)
                    else:
                        spouse = ""

                print(connector[LEN:], end="")
                if person in duplicates:
                    if duplicates[person]:
                        print_grey(person_repr(person), spouse, end="")
                        _print_tree(subtree, connector + c.LIGHTBLACK_EX)
                    else:
                        print(person_repr(person), spouse, end="")
                        duplicates[person] = True
                        _print_tree(subtree, connector)
                else:
                    print(person_repr(person), spouse, end="")
                    _print_tree(subtree, connector)

    # When value is False for first time, print the person in regular color, and then print it in grey for all other occurances
    duplicates = {person: False for person, freq in occurance.items() if freq > 1}
    _print_tree(tree)
