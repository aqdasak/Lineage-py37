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
        print('FROM Person__init__:  ', id)

    def id(self) -> int:
        return self.__id

    def name(self):
        return self.__graph.nodes[self.__id]['name']

    def _get_parents_dict(self) -> dict[str, Person]:
        parents = {}

        for neighbors_id in self.__graph.neighbors(self.__id):
            if self.__graph.edges[self.__id, neighbors_id]['rel'] == Relation.father:
                parents[Relation.father] = Person(self.__graph, neighbors_id)
            elif self.__graph.edges[self.__id, neighbors_id]['rel'] == Relation.mother:
                parents[Relation.mother] = Person(self.__graph, neighbors_id)

        return parents

    def parents(self) -> list[Person]:
        return list(self._get_parents_dict().values())

    def father(self) -> Person:
        return self._get_parents_dict()[Relation.father]

    def mother(self) -> Person:
        return self._get_parents_dict()[Relation.mother]

    def _get_children_dict(self) -> dict[str, Person]:
        children = {Relation.son: [], Relation.daughter: []}

        for neighbors_id in self.__graph.neighbors(self.__id):
            if self.__graph.edges[self.__id, neighbors_id]['rel'] == Relation.son:
                children[Relation.son].append(
                    Person(self.__graph, neighbors_id))
            elif self.__graph.edges[self.__id, neighbors_id]['rel'] == Relation.daughter:
                children[Relation.daughter].append(
                    Person(self.__graph, neighbors_id))

        return children

    def children(self) -> list[Person]:
        children = self._get_children_dict()
        return [*children[Relation.son], *children[Relation.daughter]]

    def sons(self) -> list[Person]:
        return self._get_children_dict()[Relation.son]

    def daughters(self) -> list[Person]:
        return self._get_children_dict()[Relation.daughter]

    def husband(self):
        pass

    def wife(self):
        pass

    def __repr__(self) -> str:
        return f'Person({self.__id})'


class Lineage:
    def __init__(self) -> None:
        self._graph = DiGraph()
        # self.__counter=len(self._graph.nodes)
        self.__counter = 0

    def get_name(self, node: int) -> str:
        return self._graph.nodes[node]['name']

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
        id = self.__new_id()
        self._graph.add_nodes_from([(id, {'name': name, 'gender': gender}), ])

        child = Relation.son if gender == 'm' else Relation.daughter
        if father is not None:
            # self._graph.add_edges_from([(father, id, {'rel': child}), ])
            # self._graph.add_edges_from(
            #     [(id, father, _relation(Relation.father)), ])
            self._add_relation(father.id(), id, child)
            self._add_relation(id, father.id(), Relation.father)
        if mother is not None:
            # self._graph.add_edges_from([(mother, id, {'rel': child}), ])
            # self._graph.add_edges_from(
            #     [(id, mother, {'rel': Relation.mother}), ])
            self._add_relation(mother.id(), id, child)
            self._add_relation(id, mother.id(), Relation.mother)
        return Person(self._graph, id)

    # # def add_children(self, D, parent: id, children: list[int]):
    # #     pass

    # def add_spouse(self, husband: int, wife: int):
    #     if Relation.wife not in self._graph.nodes[husband]:
    #         self._graph.nodes[husband][Relation.wife] = []
    #     if Relation.husband not in self._graph.nodes[wife]:
    #         self._graph.nodes[wife][Relation.husband] = []

    #     self._graph.nodes[husband][Relation.wife].append(wife)
    #     self._graph.nodes[wife][Relation.husband].append(husband)

    # def find_wife(self, id: int) -> int:
    #     return self._graph.nodes[id][Relation.wife]

    # def find_husband(self, id: int) -> int:
    #     return self._graph.nodes[id][Relation.husband]

    def persons(self):
        return self._graph.nodes
