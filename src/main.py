from __future__ import annotations
from datetime import datetime
from pathlib import Path
from lineage import Lineage
from lineage.lineage import Person
from my_io import clear_terminal, input_from, input_in_range, non_empty_input, print_cyan, print_green, print_grey, print_heading, print_yellow, print_red, take_input

lineage_modified = False


def add_new_person(lineage: Lineage):
    def get_person_by_id(id: str) -> Person | None:
        try:
            if id:
                return lineage.find_person_by_id(int(id))
        except Exception as e:
            print_red('Error in ID', id)
            print_red(e)

    print_heading('ADD NEW PERSON')
    name = non_empty_input('Input name: ')
    gender = input_from('Input gender (m/f): ', ('m', 'f'))
    father = get_person_by_id(take_input(
        'Input ID of father or leave blank: '))
    mother = get_person_by_id(take_input(
        'Input ID of mother or leave blank: '))

    person = lineage.add_person(name, gender, father, mother)
    print_yellow('Person added successfully')
    _print_person_details(lineage, person)

    global lineage_modified
    lineage_modified = True


def add_parent(lineage: Lineage):
    print_heading('ADD PARENT')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of person: ')))
    parent = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of parent: ')))
    person.add_parent(parent)

    global lineage_modified
    lineage_modified = True


def add_child(lineage: Lineage):
    print_heading('ADD CHILD')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of person: ')))
    child = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of child: ')))
    person.add_child(child)

    global lineage_modified
    lineage_modified = True


def add_spouse(lineage: Lineage):
    print_heading('ADD SPOUSE')
    person1 = lineage.find_person_by_id(
        int(non_empty_input('Enter ID I of person: ')))
    person2 = lineage.find_person_by_id(
        int(non_empty_input('Enter ID II of person: ')))
    person1.add_spouse(person2)

    global lineage_modified
    lineage_modified = True


def remove_person(lineage: Lineage):
    print_heading('REMOVE PERSON')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of the person: ')))
    lineage.remove_person(person)
    print_cyan('Person removed')

    global lineage_modified
    lineage_modified = True


def remove_relation(lineage: Lineage):
    print_heading('REMOVE RELATION')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID I of person: ')))
    relative = lineage.find_person_by_id(
        int(non_empty_input('Enter ID II of person: ')))
    person.remove_relative(relative)
    print_cyan('Relation removed')

    global lineage_modified
    lineage_modified = True


def _print_person_details(lineage: Lineage, person: Person):
    print_cyan('ID:\t', person.id)
    print_cyan('Name:\t', person.name)
    father = person.father
    mother = person.mother
    sons = person.sons
    daughters = person.daughters
    husband = person.husband
    wife = person.wife

    if father:
        print_cyan('Father:\t', father)
    if mother:
        print_cyan('Mother:\t', mother)
    if sons:
        print_cyan('Son:\t', sons)
    if daughters:
        print_cyan('Daughter:\t', daughters)
    if husband:
        print_cyan('Husband:\t', husband)
    if wife:
        print_cyan('Wife:\t  ', wife)


def _find_by_id(lineage: Lineage, id: int):
    person = lineage.find_person_by_id(id)
    if person:
        _print_person_details(lineage, person)
    else:
        print_red('ID not found')


def _find_by_name(lineage: Lineage, name: str):
    for person in lineage.find_person_by_name(name):
        print_grey(' - '*17)
        _print_person_details(lineage, person)


def find(lineage: Lineage):
    print_heading('FIND PERSON')
    id_or_name = non_empty_input('Enter name or ID to search: ')
    if id_or_name.isdigit():
        _find_by_id(lineage, int(id_or_name))
    else:
        _find_by_name(lineage, id_or_name)


def all_persons(lineage: Lineage):
    print_heading('ALL PERSONS IN LINEAGE')
    print_cyan(lineage.all_persons())


def all_relations(lineage: Lineage):
    print_heading('ALL RELATIONS IN LINEAGE')
    print_cyan(lineage.all_relations())


def initialize_save_directories():
    path = Path().home()/'.lineage'
    if not path.exists():
        path.mkdir()

    path = path/'autosave'
    if not path.exists():
        path.mkdir()


def save_to_file(lineage: Lineage):
    global lineage_modified
    if not lineage_modified:
        print_red('No change since last save')
        return

    filename = Path().home() / \
        f'.lineage/lineage {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'
    try:
        lineage.save_to_file(filename)
        print_green('Saved successfully at', filename)

        lineage_modified = False

    except Exception as e:
        print_red('Some error occured while saving file')


def autosave(lineage: Lineage):
    global lineage_modified
    if not lineage_modified:
        return

    filename = Path().home() / \
        f'.lineage/autosave/autosave-lineage {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'
    try:
        lineage.save_to_file(filename)

        lineage_modified = False
    except Exception:
        pass


def load_from_file() -> Lineage | None:
    path = Path().home()/'.lineage'
    if not (path.exists() and path.is_dir()):
        print_red('Directory not found', path)
        return

    files = list(path.glob('*.json'))
    files.sort(reverse=True)

    if len(files) == 0:
        print_red('No csv file found in', path)
        return

    i = 1
    if len(files) == 1:
        print_yellow(file[0].name, 'found')
    else:
        for file in files:
            print_cyan(f'{i}: {file.name}')
            i += 1

        inp = int(input_in_range('Select the file to load: ', 1, len(files)+1))

    return Lineage.load_from_file(files[inp-1])


def safe_exit(lineage: Lineage):
    global lineage_modified
    if not lineage_modified:
        print_yellow('Exiting...')
        exit()

    inp = non_empty_input(
        'You have unsaved data. Do you really want to exit without saving (y/n): ')
    if inp in ('y', 'yes'):
        autosave(lineage)
        exit()

    print_red('Exit aborted')


def shortest_path(lineage: Lineage):
    print_heading('SHORTEST PATH')
    person1_id = int(non_empty_input('Enter ID of I person: '))
    person2_id = int(non_empty_input('Enter ID of II person: '))

    print_cyan(
        lineage.shortest_path(
            lineage.find_person_by_id(person1_id),
            lineage.find_person_by_id(person2_id)
        )
    )


def show_help(_):
    print_yellow('USAGE: Type following commands to do respective action')
    print_yellow("""\
        new:\t\tAdd new person
        addp:\t\tAdd parent of a person
        addc:\t\tAdd child of a person
        adds:\t\tAdd spouse of a person
        show:\t\tFind and show matching person
        showall:\tShow all persons in lineage
        showallrel:\tShow all relations in lineage
        sp:\t\tShortest path between two persons
        rmrel:\t\tRemove relation between two persons
        rmperson:\tRemove person from lineage
        save:\t\tSave lineage to file
        exit:\t\tExit the lineage prompt
        help:\t\tShow this help
        """
                 )


def main():
    print_heading('LINEAGE')
    lineage = None

    inp = input_from(
        'Do you want to load lineage from file (y/n)? ', ('y', 'n', 'yes', 'no')).lower()
    if inp in ('y', 'yes'):
        lineage = load_from_file()

    if lineage is None:
        print_yellow('Creating new lineage')
        lineage = Lineage()

    commands = {
        'new': add_new_person,
        'addp': add_parent,
        'addc': add_child,
        'adds': add_spouse,
        'rmperson': remove_person,
        'rmrel': remove_relation,
        'save': save_to_file,
        'show': find,
        'showall': all_persons,
        'showallrel': all_relations,
        'sp': shortest_path,
        'exit': safe_exit,
        'help': show_help,
    }

    def wrong_input(_):
        print_red('Wrong input')

    show_help(None)

    while True:
        try:
            commands.get(non_empty_input('# ').lower(),
                         wrong_input)(lineage)

        except KeyboardInterrupt:
            print_red('\nAborted')
            autosave(lineage)
            exit()

        except Exception as e:
            print_red(e)

        print_grey('_'*50)


if __name__ == '__main__':
    clear_terminal()
    initialize_save_directories()
    main()
