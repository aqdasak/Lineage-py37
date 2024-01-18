from __future__ import annotations
from collections import defaultdict
from datetime import datetime
import json
import os
from pathlib import Path
from lineage_aq import Lineage, Person, Relation
import signal
from sys import exit
from time import sleep
from lineage_aq.my_io import (
    input_from,
    input_in_range,
    non_empty_input,
    print_blue,
    print_cyan,
    print_green,
    print_grey,
    print_heading,
    print_id_name_in_box,
    print_yellow,
    print_red,
    take_input,
)


lineage_modified = False


def add_new_person(lineage: Lineage):
    def get_person_by_id(id: str) -> Person | None:
        try:
            if id:
                return lineage.find_person_by_id(int(id))
        except Exception as e:
            print_red("Error in ID", id)
            print_red(e)

    def find_same_name_persons(name: str) -> list[Person]:
        new_person_name = name.lower()
        all_persons = {
            person: person.name.lower().split(" ") for person in lineage.all_persons()
        }

        found = []
        for name in new_person_name.split(" "):
            found2 = []
            for person, fullname in all_persons.items():
                if name in fullname:
                    found2.append(person)

            # name may be a common name
            if len(found2) > 8:
                found2 = []
            found += found2

        # Fullname exact match
        for person in lineage.all_persons():
            if new_person_name == person.name.lower():
                found.append(person)

        return list(set(found))

    def do_continue_if_found(name: str) -> bool:
        same_name_persons = find_same_name_persons(name)
        if same_name_persons:
            print_blue("\nPeople found with same name.")
            for person in same_name_persons:
                print_grey("-" * 50)
                _print_person_details(person)

            inp = input_from(
                "Do you want to continue to add new person? (y/n): ",
                ("y", "n", "yes", "no"),
            )
            print()
            return True if inp in ("y", "yes") else False
        return True

    print_heading("ADD NEW PERSON")
    name = non_empty_input("Input name: ")
    if not do_continue_if_found(name):
        return

    gender = input_from("Input gender (m/f): ", ("m", "f"))
    parent1 = get_person_by_id(take_input("Input ID of parent1 or leave blank: "))
    parent2 = get_person_by_id(take_input("Input ID of parent2 or leave blank: "))

    person = lineage.add_person(name, gender)
    try:
        if parent1:
            person.add_parent(parent1)
        if parent2:
            person.add_parent(parent2)
        print_yellow("Person added successfully")
    except ValueError as e:
        print_red("Parent2 not added")
        print_red(e)
    _print_person_details(person)

    global lineage_modified
    lineage_modified = True


def edit_name(lineage: Lineage):
    print_heading("EDIT NAME")
    person = lineage.find_person_by_id(int(non_empty_input("Enter ID of person: ")))
    print_cyan("Current name:", person.name)
    person.name = non_empty_input("Enter new name: ")
    _print_person_details(person)

    global lineage_modified
    lineage_modified = True


def add_parent(lineage: Lineage):
    print_heading("ADD PARENT")
    person = lineage.find_person_by_id(int(non_empty_input("Enter ID of person: ")))
    parent = lineage.find_person_by_id(int(non_empty_input("Enter ID of parent: ")))
    person.add_parent(parent)
    _print_person_details(person)

    global lineage_modified
    lineage_modified = True


def add_child(lineage: Lineage):
    print_heading("ADD CHILD")
    person = lineage.find_person_by_id(int(non_empty_input("Enter ID of person: ")))
    child = lineage.find_person_by_id(int(non_empty_input("Enter ID of child: ")))
    person.add_child(child)
    _print_person_details(person)

    global lineage_modified
    lineage_modified = True


def add_spouse(lineage: Lineage):
    print_heading("ADD SPOUSE")
    person1 = lineage.find_person_by_id(int(non_empty_input("Enter ID I of person: ")))
    person2 = lineage.find_person_by_id(int(non_empty_input("Enter ID II of person: ")))
    try:
        person1.add_spouse(person2)
        print_yellow("Added successfully")
        _print_person_details(person1)
    except Exception as e:
        print_red("Something went wrong")
        print_red(e)

    global lineage_modified
    lineage_modified = True


def remove_person(lineage: Lineage):
    def is_any_relative_present(person) -> bool:
        for _, relatives in person.relatives_dict().items():
            if len(relatives) > 0:
                return True
        return False

    print_heading("REMOVE PERSON")
    person = lineage.find_person_by_id(int(non_empty_input("Enter ID of the person: ")))

    if is_any_relative_present(person):
        print_red("Relative(s) are present. First remove relations.")
    else:
        lineage.remove_person(person)
        print_cyan("Person removed")

    global lineage_modified
    lineage_modified = True


def remove_relation(lineage: Lineage):
    print_heading("REMOVE RELATION")
    person = lineage.find_person_by_id(int(non_empty_input("Enter ID I of person: ")))
    relative = lineage.find_person_by_id(
        int(non_empty_input("Enter ID II of person: "))
    )
    person.remove_relative(relative)
    print_cyan("Relation removed")
    _print_person_details(person)

    global lineage_modified
    lineage_modified = True


def _print_person_details(person: Person):
    def print_person(person: Person | list[Person], end="\n"):
        if isinstance(person, list):
            for p in person[:-1]:
                print_person(p, end=", ")
            print_person(person[-1])
        else:
            print_cyan(f"P{person.id}({person.name})", end=end)

    father = person.father
    mother = person.mother
    sons = person.sons
    daughters = person.daughters
    husband = person.husband
    wife = person.wife

    if father:
        print_blue("Father:\t", end=" ")
        print_person(father)
    if mother:
        print_blue("Mother:\t", end=" ")
        print_person(mother)

    print_id_name_in_box(str(person.id), person.name)

    if husband:
        print_blue("Husband:", end=" ")
        print_person(husband)

    if wife:
        print_blue("Wife:\t", end=" ")
        print_person(wife)
    if sons:
        print_blue("Son:\t", end=" ")
        print_person(sons)
    if daughters:
        print_blue("Daughter:", end="")
        print_person(daughters)


def _find_by_id(lineage: Lineage, id: int):
    person = lineage.find_person_by_id(id)
    if person:
        _print_person_details(person)
    else:
        print_red("ID not found")


def _find_by_name(lineage: Lineage, name: str):
    persons = lineage.find_person_by_name(name)
    if len(persons) == 0:
        print_red("Name not found")
        return

    for person in persons:
        print_grey("─" * 50)
        _print_person_details(person)


def find(lineage: Lineage):
    print_heading("FIND PERSON")
    id_or_name = non_empty_input("Enter name or ID to search: ")
    if id_or_name.isdigit():
        _find_by_id(lineage, int(id_or_name))
    else:
        _find_by_name(lineage, id_or_name)


def all_persons(lineage: Lineage):
    print_heading("ALL PERSONS IN LINEAGE")
    for person in lineage.all_persons():
        print_cyan(person)


def all_relations(lineage: Lineage):
    print_heading("ALL RELATIONS IN LINEAGE")
    for relation in lineage.all_relations():
        print_cyan(relation)


def initialize_save_directories():
    path = Path().home() / ".lineage"
    if not path.exists():
        path.mkdir()

    path = path / "autosave"
    if not path.exists():
        path.mkdir()


def save_to_file(lineage: Lineage):
    global lineage_modified
    if not lineage_modified:
        print_red("No change since last save")
        inp = non_empty_input("Do you want to save again (y/n): ")
        if inp not in ("y", "yes"):
            return

    filename = (
        Path().home()
        / f'.lineage/lineage {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'
    )
    try:
        lineage.save_to_file(filename)
        print_green("Saved successfully at", filename)

        lineage_modified = False

    except Exception:
        print_red("Some error occured while saving file")


def autosave(lineage: Lineage):
    global lineage_modified
    if not lineage_modified:
        return

    filename = (
        Path().home()
        / f'.lineage/autosave/autosave-lineage {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'
    )
    try:
        lineage.save_to_file(filename)

        # lineage_modified = False
    except Exception:
        pass


def load_from_file() -> Lineage | None:
    def print_num_persons_and_relations(file):
        with open(file) as f:
            data: dict = json.load(f)

        num_persons = len(data["persons"])
        num_relations = len(data["relations"])

        if num_persons > 0:
            print_grey(f"   [{num_persons}]", end="")

        if num_relations > 0:
            print_grey(f"\t[{num_relations}]", end="")

    def print_all_files(files: list):
        padding = len(str(len(files)))
        print_yellow(" " * (padding - 1), end="")
        print("# ", "Filenames", " " * 23, "Persons  Relations")

        print(f"{1:{padding}d}:", files[0].name, end="")
        print_num_persons_and_relations(files[0])
        print_green(" (latest)")

        for i, file in enumerate(files[1:], 2):
            print(f"{i:{padding}d}:", file.name, end="")
            print_num_persons_and_relations(file)
            print()

    path = Path().home() / ".lineage"
    if not (path.exists() and path.is_dir()):
        print_red("Directory not found", path)
        return

    files = list(path.glob("*.json"))
    files.sort(reverse=True)

    if len(files) == 0:
        print_red("No saved file found in", path)
        return

    print_all_files(files)
    inp = int(input_in_range("Select the file to load: ", 1, len(files) + 1))

    return Lineage.load_from_file(files[inp - 1])


def safe_exit(lineage: Lineage):
    global lineage_modified
    if not lineage_modified:
        print_yellow("Exiting...")

        # st = "Closing................"
        # for i in st:
        #     sleep(0.05)
        #     print(i, sep="", end="", flush=True)

        exit(0)

    inp = non_empty_input(
        "You have unsaved data. Do you really want to exit without saving (y/n): "
    )
    if inp in ("y", "yes"):
        autosave(lineage)

        st = "Closing................"
        for i in st:
            sleep(0.05)
            print(i, sep="", end="", flush=True)

        exit(0)

    print_red("Exit aborted")


def shortest_path(lineage: Lineage):
    print_heading("SHORTEST PATH")
    person1_id = int(non_empty_input("Enter ID of I person: "))
    person2_id = int(non_empty_input("Enter ID of II person: "))

    sp = lineage.shortest_path(
        lineage.find_person_by_id(person1_id),
        lineage.find_person_by_id(person2_id),
    )

    for i in range(len(sp) - 1):
        print_cyan(sp[i], end=" ")
        print_blue(f"--{sp[i].relation_with(sp[i+1]).name}->", end=" ")
    print_cyan(sp[-1])

    print_cyan("Distance:", len(sp) - 1)


def _helper_no_and_single_parent(lineage: Lineage) -> (set, set):
    """Return set of persons having father and set of persons having mother"""

    relations = lineage.all_relations()
    rel = defaultdict(set)
    for p, _, r in relations:
        rel[r].add(p)

    return rel[Relation.FATHER], rel[Relation.MOTHER]


def no_parent(lineage: Lineage):
    print_heading("PERSONS HAVING NO PARENT")
    f, m = _helper_no_and_single_parent(lineage)

    allp = set(lineage.all_persons())
    no_parent = allp - f.union(m)

    if len(no_parent) == 0:
        print_red("All persons are having at least one parent")
        return

    no_parent = sorted(no_parent, key=lambda p: p.id)
    for i in no_parent:
        print(i)
    print_cyan("Total persons:", len(no_parent))


def one_parent(lineage: Lineage):
    print_heading("PERSONS HAVING SINGLE PARENT")
    f, m = _helper_no_and_single_parent(lineage)

    single_parent = f.union(m) - f.intersection(m)

    if len(single_parent) == 0:
        print_red("No person is having only single parent")
        return

    single_parent = sorted(single_parent, key=lambda p: p.id)
    for i in single_parent:
        print(i)

    print_cyan("Total persons:", len(single_parent))


def show_help(_=None, show_changes=False):
    print_yellow("USAGE: Type following commands to do respective action")
    help = f"""\
new:\t\tAdd new person
addp:\t\tAdd parent of a person
addc:\t\tAdd child of a person
adds:\t\tAdd spouse of a person
edit:\t\tEdit name of a person
show:\t\tFind and show matching person
find:\t\tFind and show matching person
showall:\tShow all persons in lineage
showallrel:\tShow all relations in lineage
sp:\t\tShortest path between two persons
rmrel:\t\tRemove relation between two persons
rmperson:\tRemove person from lineage
noparent:\tPersons whose no parent is present in lineage
oneparent:\tPersons whose only one parent is present in lineage
save:\t\tSave lineage to file
exit:\t\tExit the lineage prompt
help:\t\tShow this help
Press {'<Ctrl>Z then Enter' if os.name == 'nt' else '<Ctrl>D'} in empty input to cancel
Type ID or name directly in the command field to search
"""

    new = [7, 13, 14, 19]
    deprecated = []
    for i, line in enumerate(help.split("\n"), 1):
        if show_changes and i in new:
            print_green("(new)", end="")
            print_yellow(" " * 3, line)
        elif i in deprecated:
            print_yellow(" " * 8, line, end=" ")
            print_red("(deprecated)")
        else:
            print_yellow(" " * 8, line)

    if deprecated:
        print_grey("deprecated commands will be removed from future versions\n")


def set_keyboard_interrupt_signal_handler(lineage):
    def signal_handler(sig, frame):
        print()
        safe_exit(lineage)

    signal.signal(signal.SIGINT, signal_handler)


def _main():
    print_heading("LINEAGE")
    lineage = None

    inp = input_from(
        "Do you want to load lineage from file (y/n)? ", ("y", "n", "yes", "no")
    ).lower()
    if inp in ("y", "yes"):
        lineage = load_from_file()

    if lineage is None:
        print_yellow("Creating new lineage\n")
        lineage = Lineage()

    commands = {
        "new": add_new_person,
        "addp": add_parent,
        "addc": add_child,
        "adds": add_spouse,
        "edit": edit_name,
        "rmperson": remove_person,
        "rmrel": remove_relation,
        "noparent": no_parent,
        "oneparent": one_parent,
        "save": save_to_file,
        "show": find,
        "find": find,
        "showall": all_persons,
        "showallrel": all_relations,
        "sp": shortest_path,
        "exit": safe_exit,
        "help": show_help,
    }

    show_help(show_changes=True)

    set_keyboard_interrupt_signal_handler(lineage)
    while True:
        try:
            command = non_empty_input("# ")
            command_ = command.replace(" ", "").lower()
            if command_ in commands:
                commands[command_](lineage)
            else:
                print_heading("FIND PERSON")
                if command.isdigit():
                    _find_by_id(lineage, int(command))
                else:
                    _find_by_name(lineage, command)

        # except KeyboardInterrupt:
        #     handled by set_keyboard_interrupt_signal_handler

        #     print_red("\nAborted")
        #     autosave(lineage)
        #     exit(0)

        except Exception as e:
            print_red(e)

        print_grey("─" * 50)


def main():
    initialize_save_directories()
    try:
        _main()
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    main()
