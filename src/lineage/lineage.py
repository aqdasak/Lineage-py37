from __future__ import annotations
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
    def __init__(self, D: DiGraph, id: int) -> None:
        self.__graph = D
        self.__id = id

    # def id(self) -> int:
    #     return self.__id

    @property
    def name(self):
        return self.__graph.nodes[self]['name']

    def _relatives(self) -> dict[str, Person]:
        relatives = {Relation.father: None, Relation.mother: None, Relation.son: [
        ], Relation.daughter: [], Relation.husband: None, Relation.wife: None}

        for relative in self.__graph.neighbors(self):
            if self.__graph.edges[self, relative]['rel'] == Relation.son:
                relatives[Relation.son].append(relative)
            elif self.__graph.edges[self, relative]['rel'] == Relation.daughter:
                relatives[Relation.daughter].append(relative)
            elif self.__graph.edges[self, relative]['rel'] == Relation.father:
                relatives[Relation.father] = relative
            elif self.__graph.edges[self, relative]['rel'] == Relation.mother:
                relatives[Relation.mother] = relative
            elif self.__graph.edges[self, relative]['rel'] == Relation.husband:
                relatives[Relation.husband] = relative
            elif self.__graph.edges[self, relative]['rel'] == Relation.wife:
                relatives[Relation.wife] = relative

        return relatives
    @property
    def parents(self) -> list[Person]:
        relatives = self._relatives()
        return [relatives[Relation.father], relatives[Relation.mother]]

    @property
    def father(self) -> Person:
        return self._relatives()[Relation.father]

    @property
    def mother(self) -> Person:
        return self._relatives()[Relation.mother]

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
    def husband(self):
        return self._relatives()[Relation.husband]

    @property
    def wife(self):
        return self._relatives()[Relation.wife]

    def __repr__(self) -> str:
        return f'Person({self.__id})'


class Lineage:
    def __init__(self) -> None:
        self._graph = DiGraph()
        self.__counter = 0

    def __new_id(self):
        id = self.__counter
        self.__counter += 1
        return id

    @staticmethod
    def _relation(relation: Relation) -> dict:
        return {'rel': relation}

    @staticmethod
    def _get_relation():
        pass

    def _add_relation(self, from_, to, relation):
        self._graph.add_edges_from([(from_, to, {'rel': relation}), ])

    def add_person(self, name: str, gender: str, father: Person = None, mother: Person = None) -> Person:
        person = Person(self._graph, self.__new_id())
        self._graph.add_nodes_from(
            [(person, {'name': name, 'gender': gender}), ])

        child = Relation.son if gender == 'm' else Relation.daughter
        if father is not None:
            self._add_relation(father, person, child)
            self._add_relation(person, father, Relation.father)
        if mother is not None:
            self._add_relation(mother, person, child)
            self._add_relation(person, mother, Relation.mother)
        return person

    def add_spouse(self, husband: Person, wife: Person):

        self._add_relation(husband, wife, Relation.wife)
        self._add_relation(wife, husband, Relation.husband)

    def persons(self):
        return self._graph.nodes
