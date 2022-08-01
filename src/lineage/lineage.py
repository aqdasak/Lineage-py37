from networkx import DiGraph
from enum import Enum


class Relation(Enum):
    father = 0
    mother = 1
    son = 2
    daughter = 3
    husband = 4
    wife = 5


class Lineage:
    def __init__(self) -> None:
        self._graph = DiGraph()
        # self.__counter=len(self._graph.nodes)
        self.__counter = 0

    def find_parents_dict(self, child_id: int) -> dict[str, int]:
        parents = {}

        for id in self._graph.neighbors(child_id):
            if self._graph.edges[child_id, id]['rel'] == Relation.father:
                parents[Relation.father] = id
            elif self._graph.edges[child_id, id]['rel'] == Relation.mother:
                parents[Relation.mother] = id

        return parents

    def find_parents(self, child_id: int) -> list[int]:
        return list(self.find_parents_dict(child_id).values())

    def find_father(self, child_id: int) -> int:
        return self.find_parents_dict(child_id)[Relation.father]

    def find_mother(self, child_id: int) -> int:
        return self.find_parents_dict(child_id)[Relation.mother]

    def find_children_dict(self, parent_id: int) -> dict[str, int]:
        children = {Relation.son: [], Relation.daughter: []}

        for id in self._graph.neighbors(parent_id):
            if self._graph.edges[parent_id, id]['rel'] == Relation.son:
                children[Relation.son].append(id)
            elif self._graph.edges[parent_id, id]['rel'] == Relation.daughter:
                children[Relation.daughter].append(id)

        return children

    def find_children(self, parent_id: int) -> list[int]:
        children = self.find_children_dict(parent_id)
        return [*children[Relation.son], *children[Relation.daughter]]

    def get_name(self, node: int) -> str:
        return self._graph.nodes[node]['name']

    def __new_id(self):
        id = self.__counter
        self.__counter += 1
        return id

    def add_person(self, name: str, gender: str, father: int = None, mother: int = None) -> int:
        id = self.__new_id()
        self._graph.add_nodes_from([(id, {'name': name, 'gender': gender}), ])

        child = Relation.son if gender == 'm' else Relation.daughter
        if father is not None:
            self._graph.add_edges_from([(father, id, {'rel': child}), ])
            self._graph.add_edges_from(
                [(id, father, {'rel': Relation.father}), ])
        if mother is not None:
            self._graph.add_edges_from([(mother, id, {'rel': child}), ])
            self._graph.add_edges_from(
                [(id, mother, {'rel': Relation.mother}), ])
        return id

    # # def add_children(self, D, parent: id, children: list[int]):
    # #     pass

    def add_spouse(self, husband: int, wife: int):
        if Relation.wife not in self._graph.nodes[husband]:
            self._graph.nodes[husband][Relation.wife] = []
        if Relation.husband not in self._graph.nodes[wife]:
            self._graph.nodes[wife][Relation.husband] = []

        self._graph.nodes[husband][Relation.wife].append(wife)
        self._graph.nodes[wife][Relation.husband].append(husband)

    def find_wife(self, id: int) -> int:
        return self._graph.nodes[id][Relation.wife]

    def find_husband(self, id: int) -> int:
        return self._graph.nodes[id][Relation.husband]

    def persons(self):
        return self._graph.nodes
