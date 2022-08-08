import string
from src.lineage import Lineage
from src.lineage.lineage import Person, Relation


def factory():
    lineage = Lineage()
    father = lineage.add_person('Father', 'm')
    mother = lineage.add_person('Mother', 'f')
    child = lineage.add_person('Child', 'm')
    father.add_spouse(mother)
    child.add_parent(father)
    child.add_parent(mother)

    return lineage, father, mother, child


def test_relation():
    _, father, mother, child = factory()
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


def test_relatives():
    _, father, mother, child = factory()

    for person in father, mother, child:
        for relation, relatives in person.relatives_dict().items():
            assert type(relation) == Relation
            assert type(relatives) == list
            assert type(relatives[0]) == Person
            assert len(relatives) >= 1


def test_relation_with():
    lineage, father, mother, child = factory()
    person = lineage.add_person('Person', 'm')
    persons = (father, mother, child, person)

    for person1 in persons:
        for person2 in persons:
            relation = person1.relation_with(person2)
            assert type(relation) == Relation or relation == None


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
    lineage, _, _, _ = factory()

    all_persons1 = list(lineage.all_persons())
    person = lineage.add_person('Person', 'm')
    all_persons2 = list(lineage.all_persons())

    assert all_persons1 is not all_persons2

    assert person not in all_persons1
    assert person in all_persons2


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
    lineage, _, _, _ = factory()
    person_a1 = lineage.add_person('Person1', 'm')
    person_a2 = lineage.add_person('Person2', 'f')
    person_a1.add_spouse(person_a2)
    assert person_a1.wife[0] == person_a2
    assert person_a2.husband[0] == person_a1

    person_b1 = lineage.add_person('Person1', 'm')
    person_b2 = lineage.add_person('Person2', 'f')
    person_b2.add_spouse(person_b1)
    assert person_b2.husband[0] == person_b1
    assert person_b1.wife[0] == person_b2


def test_remove_relative():
    _, father, mother, child = factory()
    assert father.relation_with(child) is not None
    assert mother.relation_with(child) is not None
    assert child.relation_with(father) is not None
    assert child.relation_with(mother) is not None

    father.remove_relative(child)
    child.remove_relative(mother)

    assert father.relation_with(child) is None
    assert mother.relation_with(child) is None
    assert child.relation_with(father) is None
    assert child.relation_with(mother) is None

    for _, relatives_list in father.relatives_dict().items():
        assert child not in relatives_list

    for _, relatives_list in mother.relatives_dict().items():
        assert child not in relatives_list

    for _, relatives_list in child.relatives_dict().items():
        assert father not in relatives_list
        assert mother not in relatives_list

    error_raised = [False]*4
    # Removing relation which is not present
    # Following must raise exception
    try:
        father.remove_relative(child)
    except Exception:
        error_raised[0] = True

    try:
        child.remove_relative(father)
    except Exception:
        error_raised[1] = True
    try:
        mother.remove_relative(child)
    except Exception:
        error_raised[2] = True
    try:
        child.remove_relative(mother)
    except Exception:
        error_raised[3] = True

    assert all(error_raised)


def test_remove_and_add_relative():
    _, father, _, child = factory()
    father.remove_relative(child)
    father.add_child(child)
    assert father.children[0] == child
    assert child.father == father


def test_multiple_additions():
    _, father, mother, _ = factory()

    error_raised = False
    try:
        # This must raise exception
        father.add_spouse(mother)
    except Exception:
        error_raised = True

    assert error_raised


def test_change_relation_not_allowed():
    _, father, mother, _ = factory()

    error_raised = False
    try:
        # This must raise exception
        father.add_child(mother)
    except Exception:
        error_raised = True

    assert error_raised


def test_add_multiple_father_not_allowed():
    lineage, _, _, child = factory()
    person = lineage.add_person('Person', 'm')

    error_raised = False
    try:
        # This must raise exception
        child.add_parent(person)
    except Exception:
        error_raised = True

    assert error_raised


def test_add_multiple_mother_not_allowed():
    lineage, _, _, child = factory()
    person = lineage.add_person('Person', 'f')

    error_raised = False
    try:
        # This must raise exception
        child.add_parent(person)
    except Exception:
        error_raised = True

    assert error_raised


def test_multiple_same_gender_people_adding_same_child_not_allowed():
    lineage, _, _, child = factory()
    person_m = lineage.add_person('Person', 'm')
    person_f = lineage.add_person('Person', 'f')

    error_raised = [False]*2
    # Following must raise exception
    try:
        person_m.add_child(child)
    except Exception:
        error_raised[0] = True

    try:
        person_f.add_child(child)
    except Exception:
        error_raised[1] = True

    assert all(error_raised)


def test_same_gender_spouse_error():
    lineage, _, _, _ = factory()
    person1 = lineage.add_person('Person1', 'm')
    person2 = lineage.add_person('Person2', 'm')
    person3 = lineage.add_person('Person3', 'f')
    person4 = lineage.add_person('Person4', 'f')

    error_raised = [False]*2
    # Following must raise exception
    try:
        person1.add_spouse(person2)
    except Exception:
        error_raised[0] = True
    try:
        person3.add_spouse(person4)
    except Exception:
        error_raised[1] = True

    assert all(error_raised)


def test_unknown_gender_error():
    lineage, _, _, _ = factory()

    invalid_genders = list(string.ascii_lowercase)
    invalid_genders.remove('m')
    invalid_genders.remove('f')
    error_raised = [False]*len(invalid_genders)
    # Following must raise exception
    for i, gender in enumerate(invalid_genders):
        try:
            lineage.add_person('P', gender)
        except Exception:
            error_raised[i] = True

    assert all(error_raised)


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

    error_raised = [False]*3
    # Following must raise exception
    try:
        person.add_child(person)
    except Exception:
        error_raised[0] = True

    try:
        person.add_parent(person)
    except Exception:
        error_raised[1] = True

    try:
        person.add_spouse(person)
    except Exception:
        error_raised[2] = True

    assert all(error_raised)


def test_shortest_path():
    lineage, father, mother, _ = factory()

    child = lineage.add_person('Child', 'm')
    child.add_parent(father)

    assert len(lineage.shortest_path(child, mother)) == 3
    child.add_parent(mother)
    assert len(lineage.shortest_path(child, mother)) == 2


def test_save_and_load_file():
    lineage, father, mother, child = factory()

    filename = 'test_lineage.json'
    lineage.save_to_file(filename)

    new_lineage = Lineage.load_from_file(filename)
    assert type(new_lineage) == Lineage
    father_b = new_lineage.find_person_by_id(father.id)
    mother_b = new_lineage.find_person_by_id(mother.id)
    child_b = new_lineage.find_person_by_id(child.id)

    assert father_b.id == father.id
    assert mother_b.id == mother.id
    assert child_b.id == child.id

    assert father_b.name == father.name
    assert mother_b.name == mother.name
    assert child_b.name == child.name

    family = (father, mother, child)
    family_b = (father_b, mother_b, child_b)

    for person_b, person in zip(family_b, family):
        assert len(person_b.parents) == len(person.parents)
        assert len(person_b.children) == len(person.children)
        assert len(person_b.sons) == len(person.sons)
        assert len(person_b.daughters) == len(person.daughters)
        assert len(person_b.husband) == len(person.husband)
        assert len(person_b.wife) == len(person.wife)

    assert father_b.children[0] == child_b
    assert mother_b.children[0] == child_b
    assert child_b.father == father_b
    assert child_b.mother == mother_b
    assert father_b.wife[0] == mother_b
    assert mother_b.husband[0] == father_b

    assert len(lineage.all_persons()) == len(new_lineage.all_persons())
    assert len(lineage.all_relations()) == len(new_lineage.all_relations())

    from os import remove
    remove(filename)


def test_find_by_id():
    lineage, father, mother, child = factory()
    assert lineage.find_person_by_id(father.id) == father
    assert lineage.find_person_by_id(mother.id) == mother
    assert lineage.find_person_by_id(child.id) == child


def test_find_by_name():
    lineage, father, mother, child = factory()
    assert lineage.find_person_by_name('fAth')[0] == father
    assert lineage.find_person_by_name('AthEr')[0] == father
    assert lineage.find_person_by_name('oTheR')[0] == mother
    assert lineage.find_person_by_name('ild')[0] == child
