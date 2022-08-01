from datetime import datetime
import string
from src.lineage import __version__, Lineage
from src.lineage.lineage import Person


def test_version():
    assert __version__ == '0.1.0'


def load_from_file_factory():
    lineage = Lineage.load_from_file('lineage 2022-08-01 00.10.39.csv')
    father = lineage.find_person_by_id(0)
    mother = lineage.find_person_by_id(1)
    child = lineage.find_person_by_id(2)

    return lineage, father, mother, child


def factory():
    lineage = Lineage()
    father = lineage.add_person('Father', 'm')
    mother = lineage.add_person('Mother', 'f')
    child = lineage.add_person('Child', 'm', father, mother)

    return lineage, father, mother, child


def test_relation():
    lineage, father, mother, child = factory()
    assert child.father == father
    assert child.mother == mother
    assert father.name == 'Father'
    assert mother.name == 'Mother'
    assert child.name == 'Child'

    assert set(child.parents) == set((mother, father))
    assert len(father.sons) <= len(father.children)

    assert len(father.children) == 1
    assert len(mother.children) == 1
    assert len(father.parents) == 0
    assert len(child.children) == 0

    # print(l.all_persons())
    # print(l.all_relations())


def test_type():
    _, father, mother, child = factory()
    assert type(father.children) == list
    assert type(father.sons) == list
    assert type(father.daughters) == list
    assert type(child.parents) == list
    assert type(child.father) == Person
    assert type(child.mother) == Person
    assert type(father.wife) == list
    assert type(mother.husband) == list


def test_add_person():
    lineage, father, mother, child = factory()
    assert set(father.children) == set((child,))
    assert set(mother.children) == set((child,))

    child2 = lineage.add_person('Child2', 'm', father, mother)
    assert set(father.children) == set((child, child2))
    assert set(mother.children) == set((child, child2))


def test_add_parent():
    lineage, father, mother, child = factory()
    child2 = lineage.add_person('Child2', 'm')

    assert set(father.children) == set((child,))
    assert set(mother.children) == set((child,))
    assert len(child2.parents) == 0

    child2.add_parent(father)
    assert set(father.children) == set((child, child2))
    assert set(mother.children) == set((child,))
    assert len(child2.parents) == 1

    child2.add_parent(mother)
    assert set(father.children) == set((child, child2))
    assert set(mother.children) == set((child, child2))
    assert len(child2.parents) == 2


def test_add_child():
    lineage, father, mother, child = factory()
    child2 = lineage.add_person('Child2', 'm')

    assert set(father.children) == set((child,))
    assert set(mother.children) == set((child,))

    father.add_child(child2)
    assert set(father.children) == set((child, child2))
    assert set(mother.children) == set((child,))

    mother.add_child(child2)
    assert set(father.children) == set((child, child2))
    assert set(mother.children) == set((child, child2))


def test_add_spouse():
    _, father_a, mother_a, _ = factory()
    father_a.add_spouse(mother_a)
    assert father_a.wife[0] == mother_a
    assert mother_a.husband[0] == father_a

    _, father_b, mother_b, _ = factory()
    mother_b.add_spouse(father_b)
    assert mother_b.husband[0] == father_b
    assert father_b.wife[0] == mother_b



def test_same_gender_spouse_error():
    lineage, _, _, _ = factory()
    person1 = lineage.add_person('Person1', 'm')
    person2 = lineage.add_person('Person2', 'm')
    person3 = lineage.add_person('Person3', 'f')
    person4 = lineage.add_person('Person4', 'f')

    error = [True]*2
    # Following must raise exception
    try:
        person1.add_spouse(person2)
    except Exception:
        error[0] = False
    try:
        person3.add_spouse(person4)
    except Exception:
        error[1] = False

    if any(error):
        raise Exception()



def test_empty_relatives():
    lineage, _, _, _ = factory()
    person = lineage.add_person('Person', 'm')
    assert person.children == []
    assert person.sons == []
    assert person.daughters == []
    assert person.parents == []
    assert person.father == None
    assert person.mother == None
    assert person.husband == []
    assert person.wife == []


def test_no_self_loop():
    _, _, _, person = factory()

    error = [True]*3
    # Following must raise exception
    try:
        person.add_child(person)
    except Exception:
        error[0] = False

    try:
        person.add_parent(person)
    except Exception:
        error[1] = False

    try:
        person.add_spouse(person)
    except Exception:
        error[2] = False

    if any(error):
        raise Exception()


def test_shortest_path():
    lineage, father, mother, child = factory()
    assert len(lineage.shortest_path(father, mother)) == 3
    father.add_spouse(mother)
    assert len(lineage.shortest_path(father, mother)) == 2


def test_():
    lineage, father, mother, child = factory()
    assert child.relation_with(1) == None


def test_save_and_load_file():
    lineage, father, mother, child = factory()
    father.add_spouse(mother)

    filename = 'test_lineage.csv'
    lineage.save_to_file(filename)
    print(lineage.load_from_file(filename))
