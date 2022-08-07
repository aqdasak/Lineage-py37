from __future__ import annotations
from datetime import datetime
from pathlib import Path
from lineage import Lineage
from lineage.lineage import Person
from my_io import clear_terminal, input_from, non_empty_input, print_cyan, print_green, print_grey, print_heading, print_yellow, print_red, take_input


def add_new_person(lineage: Lineage):
    def get_person_by_id(id: str) -> Person | None:
        try:
            if id:
                return lineage.find_person_by_id(int(id))
        except Exception:
            print_red('Error in ID', id)

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


def add_parent(lineage: Lineage):
    print_heading('ADD PARENT')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of person: ')))
    parent = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of parent: ')))
    person.add_parent(parent)


def add_child(lineage: Lineage):
    print_heading('ADD CHILD')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of person: ')))
    child = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of child: ')))
    person.add_child(child)


def add_spouse(lineage: Lineage):
    print_heading('ADD SPOUSE')
    person1 = lineage.find_person_by_id(
        int(non_empty_input('Enter ID I of person: ')))
    person2 = lineage.find_person_by_id(
        int(non_empty_input('Enter ID II of person: ')))
    person1.add_spouse(person2)

def remove_person(lineage:Lineage):
    print_heading('REMOVE PERSON')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID of the person: ')))
    lineage.remove_person(person)


def remove_relation(lineage: Lineage):
    print_heading('REMOVE RELATION')
    person = lineage.find_person_by_id(
        int(non_empty_input('Enter ID I of person: ')))
    relative = lineage.find_person_by_id(
        int(non_empty_input('Enter ID II of person: ')))
    person.remove_relative(relative)


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


def find_by_id(lineage: Lineage):
    print_heading('FIND BY ID')
    id = int(non_empty_input('Enter ID to search: '))
    person = lineage.find_person_by_id(id)
    if person:
        _print_person_details(lineage, person)
    else:
        print_red('ID not found')


def find_by_name(lineage: Lineage):
    print_heading('FIND BY NAME')
    name = non_empty_input('Enter name to search: ')
    for person in lineage.find_person_by_name(name):
        print_grey(' - '*16)
        _print_person_details(lineage, person)


def all_persons(lineage: Lineage):
    print_heading('ALL PERSONS IN LINEAGE')
    print_cyan(lineage.all_persons())


def all_relations(lineage: Lineage):
    print_heading('ALL RELATIONS IN LINEAGE')
    print_cyan(lineage.all_relations())


def save_to_file(lineage: Lineage) -> bool:
    path = Path().home()/'.lineage'
    if not path.exists():
        path.mkdir()

    filename = path / \
        f'lineage {datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.json'

    try:
        lineage.save_to_file(filename)
        print_green('Saved successfully at', filename)
        return True
    except Exception as e:
        print_red('Some error occured while saving file')
        print_red(e)
        return False


def load_from_file() -> Lineage | None:
    path = Path().home()/'.lineage'
    if not (path.exists() and path.is_dir()):
        print_red('Directory not found', path)
        return

    files = list(path.glob('*.json'))

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

        inp = int(non_empty_input('Select the file to load: '))

    return Lineage.load_from_file(files[inp-1])


def save_and_exit(lineage: Lineage):
    if save_to_file(lineage):
        print_yellow('Exiting...')
        exit()
    inp = non_empty_input('Do you really want to exit (y/n): ').lower()
    if inp in ('y', 'yes'):
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
        show:\t\tFind person by id
        showbyname:\tFind person by name
        showall:\tShow all persons in lineage
        showallrel:\tShow all relations in lineage
        sp:\t\tShortest path between two persons
        rmrel:\t\tRemove relation between two persons
        rmperson:\tRemove person from lineage
        save:\t\tSave lineage to file
        exit:\t\tSave lineage and exit
        help:\t\tShow this help
        """
                 )


def main():
    print_heading('LINEAGE')
    lineage = None

    inp = non_empty_input(
        'Do you want to load lineage from file (y/n)? ').lower()
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
        'rmperson':remove_person,
        'rmrel': remove_relation,
        'save': save_to_file,
        'show': find_by_id,
        'showbyname': find_by_name,
        'showall': all_persons,
        'showallrel': all_relations,
        'sp': shortest_path,
        'exit': save_and_exit,
        'help': show_help,
    }

    def wrong_input(_):
        print_red('Wrong input')

    show_help(None)

    try: 
        while True:
            try:
                commands.get(non_empty_input('# ').lower(), wrong_input)(lineage)
            except Exception as e:
                # print_warning('Something went wrong')
                print_red(e)

            print_grey('_'*50)

    except KeyboardInterrupt:
        print_red('\nAborted')
        save_and_exit(lineage)


if __name__ == '__main__':
    clear_terminal()
    main()
