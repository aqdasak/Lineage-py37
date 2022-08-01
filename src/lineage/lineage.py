from __future__ import annotations
import networkx
from networkx import DiGraph
from enum import Enum


class Relation(Enum):
    father = 0
    mother = 1
    son = 2
    daughter = 3
    husband = 4
    wife = 5


class Person:
    def __init__(self, digraph: DiGraph, id: int, name: str, gender: str) -> None:
        self.__graph = digraph
        self.__id = id
        self.__name = name
        self.__gender = gender[0].lower()
        self.__relatives: dict[Relation, list[Person]] = {Relation.father: [], Relation.mother: [], Relation.son: [],
                         Relation.daughter: [], Relation.husband: [], Relation.wife: []}
        self.__relatives_rebuild_reqd = True

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def gender(self) -> str:
        return self.__gender

    @property
    def parents(self) -> list[Person]:
        relatives = self._relatives()
        return [*relatives[Relation.father], *relatives[Relation.mother]]

    @property
    def father(self) -> Person|None:
        father_list=self._relatives()[Relation.father]
        if father_list:
            return father_list[0]
        return None

    @property
    def mother(self) -> Person|None:
        mother_list=self._relatives()[Relation.mother]
        if mother_list:
            return mother_list[0]
        return None

    @property
    def children(self) -> list[Person]:
        relatives = self._relatives()
        return [*relatives[Relation.son], *relatives[Relation.daughter]]

    @property
    def sons(self) -> list[Person]:
        return self._relatives()[Relation.son]

    @property
    def daughters(self) -> list[Person]:
        return self._relatives()[Relation.daughter]

    @property
    def husband(self) -> list[Person]:
        return self._relatives()[Relation.husband]

    @property
    def wife(self) -> list[Person]:
        return self._relatives()[Relation.wife]

    def relation_with(self, relative: Person) -> Relation | None:
        try:
            return self.__graph.edges[self, relative][Relation]
        except KeyError:
            return

    def _relatives(self) -> dict[str, Person]:
        if self.__relatives_rebuild_reqd:
            relatives = {Relation.father: [], Relation.mother: [], Relation.son: [],
                         Relation.daughter: [], Relation.husband: [], Relation.wife: []}

            for relative in self.__graph.neighbors(self):
                if self.relation_with(relative) == Relation.son:
                    relatives[Relation.son].append(relative)
                elif self.relation_with(relative) == Relation.daughter:
                    relatives[Relation.daughter].append(relative)
                elif self.relation_with(relative) == Relation.father:
                    relatives[Relation.father].append(relative)
                elif self.relation_with(relative) == Relation.mother:
                    relatives[Relation.mother].append(relative)
                elif self.relation_with(relative) == Relation.husband:
                    relatives[Relation.husband].append(relative)
                elif self.relation_with(relative) == Relation.wife:
                    relatives[Relation.wife].append(relative)

            if len(relatives[Relation.father])>1 or len(relatives[Relation.mother])>1:
                raise Exception("Can't have multiple father or mother values")

            self.__relatives = relatives
            self.__relatives_rebuild_reqd = False

        return self.__relatives

    def _add_relation(self, to: Person, relation: Relation) -> None:
        if self is to:
            raise ValueError("Can't be related to self")

        self.__graph.add_edges_from([(self, to, {Relation: relation}), ])
        self.__relatives_rebuild_reqd = True

    def add_child(self, child: Person) -> None:
        child_rel = Relation.son if child.__gender == 'm' else Relation.daughter
        parent_rel = Relation.father if self.__gender == 'm' else Relation.mother

        # if len(child.__relatives[parent_rel])==1 and child.__relatives[parent_rel][0]!=self:
        print(child.__relatives[parent_rel])
        if len(child.__relatives[parent_rel])==1:
            raise Exception("Can't have multiple father or mother values")
        self._add_relation(child, child_rel)
        child._add_relation(self, parent_rel)

    def add_parent(self, parent: Person) -> None:
        parent.add_child(self)

    def add_spouse(self, other: Person) -> None:
        if {self.__gender, other.__gender} != {'m', 'f'}:
            raise ValueError

        if self.__gender == 'm':
            husband = self
            wife = other
        else:
            husband = other
            wife = self

        husband._add_relation(wife, Relation.wife)
        wife._add_relation(husband, Relation.husband)

    def __repr__(self) -> str:
        return f'P{self.id}({self.name.split(" ")[0]})'


class Lineage:
    def __init__(self) -> None:
        self._graph = DiGraph()
        self.__counter = -1

    def __new_id(self) -> int:
        self.__counter += 1
        return self.__counter

    def add_person(self, name: str, gender: str, father: Person = None, mother: Person = None) -> Person:
        return self._add_person_with_id(self.__new_id(), name, gender, father, mother)

    def _add_person_with_id(self, id: int, name: str, gender: str, father: Person = None, mother: Person = None) -> Person:
        person = Person(self._graph, id, name, gender)
        self._graph.add_node(person)

        if father:
            person.add_parent(father)
        if mother:
            person.add_parent(mother)

        return person

    def all_persons(self):
        return self._graph.nodes

    def all_relations(self) -> list:
        relations = []
        for relation in self._graph.edges:
            relations.append(
                [relation, self._graph.edges[relation[0], relation[1]][Relation].name])
        return relations

    def all_unique_relations(self) -> list:
        relations = []
        rel_set = []
        for rel in self._graph.edges:
            if rel not in rel_set and (rel[1], rel[0]) not in rel_set:
                rel_set.append(rel)

        for relation in rel_set:
            relations.append(
                [relation, self._graph.edges[relation[0], relation[1]][Relation].name])
        return relations

    def shortest_path(self, start, stop):
        return networkx.shortest_path(self._graph, start, stop)

    def save_to_file(self, filename: str) -> None:
        with open(filename, 'w') as f:
            f.write('id,name,gender\n')
            for person in self.all_persons():
                f.write(f'{person.id},{person.name},{person.gender}\n')

            f.write('='*30+'\n')
            f.write('id1,id2,relation')
            for relatives, relation in self.all_relations():
                f.write(f'{relatives[0].id},{relatives[1].id},{relation}\n')

    @classmethod
    def load_from_file(cls, filename: str) -> Lineage:
        lineage = cls()

        with open(filename) as f:
            persons_data, relations_data = f.read().split('='*30)

            for id in persons_data.split('\n')[1:]:
                try:
                    id, name, gender = id.split(',')
                    id = int(id)
                    lineage._add_person_with_id(id, name, gender)
                    lineage.__counter+=1
                except Exception:
                    pass

            rel = {
                'father': Relation.father,
                'mother': Relation.mother,
                'son': Relation.son,
                'daughter': Relation.daughter,
                'husband': Relation.husband,
                'wife': Relation.wife,
            }
            persons_dict: dict[int, Person] = {}
            for id in lineage.all_persons():
                persons_dict[id.id] = id

            for relation_tuple in relations_data.split('\n')[1:]:
                try:
                    id1, id2, relation = relation_tuple.split(',')
                    id1, id2 = int(id1), int(id2)
                    persons_dict[id1]._add_relation(
                        persons_dict[id2], rel[relation])
                except Exception:
                    pass

        return lineage

    def find_person_by_id(self, id: int) -> Person:
        for person in self.all_persons():
            if person.id == id:
                return person
