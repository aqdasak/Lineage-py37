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
        self.__relatives: dict[Relation, Person | list[Person]] = {}
        self.__relatives_rebuild_reqd = True

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

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
            relatives = {Relation.father: None, Relation.mother: None, Relation.son: [],
                         Relation.daughter: [], Relation.husband: None, Relation.wife: None}

            for relative in self.__graph.neighbors(self):
                if self.relation_with(relative) == Relation.son:
                    relatives[Relation.son].append(relative)
                elif self.relation_with(relative) == Relation.daughter:
                    relatives[Relation.daughter].append(relative)
                elif self.relation_with(relative) == Relation.father:
                    relatives[Relation.father] = relative
                elif self.relation_with(relative) == Relation.mother:
                    relatives[Relation.mother] = relative
                elif self.relation_with(relative) == Relation.husband:
                    relatives[Relation.husband] = relative
                elif self.relation_with(relative) == Relation.wife:
                    relatives[Relation.wife] = relative

                self.__relatives = relatives
                self.__relatives_rebuild_reqd = False

        return self.__relatives

    def _add_relation(self, to: Person, relation: Relation) -> None:
        self.__graph.add_edges_from([(self, to, {Relation: relation}), ])
        self.__relatives_rebuild_reqd = True

    def add_child(self, child: Person) -> None:
        child_rel = Relation.son if child.__gender == 'm' else Relation.daughter
        parent_rel = Relation.father if self.__gender == 'm' else Relation.mother

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
        person = Person(self._graph, self.__new_id(), name, gender)
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
                f'{relation[0]} --{self._graph.edges[relation[0],relation[1]][Relation].name}-> {relation[1]}')
        return relations

    def all_unique_relations(self) -> list:
        relations = []
        rel_set = []
        for rel in self._graph.edges:
            if rel not in rel_set and (rel[1], rel[0]) not in rel_set:
                rel_set.append(rel)

        for relation in rel_set:
            relations.append(
                f'{relation[0]} --{self._graph.edges[relation[0],relation[1]][Relation].name}-> {relation[1]}')
        return relations

    def shortest_path(self, start, stop):
        return networkx.shortest_path(self._graph, start, stop)