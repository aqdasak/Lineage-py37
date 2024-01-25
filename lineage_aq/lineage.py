from __future__ import annotations
from collections import defaultdict
import json
from pathlib import Path
import networkx
from networkx import DiGraph
from enum import Enum, auto


class InvalidRelationError(ValueError):
    pass


class Relation(Enum):
    FATHER = auto()
    MOTHER = auto()
    SON = auto()
    DAUGHTER = auto()
    HUSBAND = auto()
    WIFE = auto()

    def __repr__(self) -> str:
        return str(self)


class Person:
    def __init__(self, digraph: DiGraph, id: int, name: str, gender: str) -> None:
        if gender not in ("m", "f"):
            raise ValueError("Gender should be either male(m) or female(f)")
        self.__graph = digraph
        self.__id = id
        self.name = name
        self.__gender = gender[0].lower()
        self.__relatives_dict: dict[Relation, list[Person]] = defaultdict(list)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name.title()

    @property
    def gender(self) -> str:
        return self.__gender

    @property
    def parents(self) -> list[Person]:
        relatives = self.relatives_dict()
        return [*relatives[Relation.FATHER], *relatives[Relation.MOTHER]]

    @property
    def father(self) -> Person | None:
        father_list = self.relatives_dict()[Relation.FATHER]
        if father_list:
            return father_list[0]
        return None

    @property
    def mother(self) -> Person | None:
        mother_list = self.relatives_dict()[Relation.MOTHER]
        if mother_list:
            return mother_list[0]
        return None

    @property
    def children(self) -> list[Person]:
        relatives = self.relatives_dict()
        return [*relatives[Relation.SON], *relatives[Relation.DAUGHTER]]

    @property
    def sons(self) -> list[Person]:
        return self.relatives_dict()[Relation.SON]

    @property
    def daughters(self) -> list[Person]:
        return self.relatives_dict()[Relation.DAUGHTER]

    @property
    def husband(self) -> list[Person]:
        return self.relatives_dict()[Relation.HUSBAND]

    @property
    def wife(self) -> list[Person]:
        return self.relatives_dict()[Relation.WIFE]

    def relation_with(self, relative: Person) -> Relation | None:
        try:
            return self.__graph.edges[self, relative][Relation]
        except KeyError:
            return

    def relatives_dict(self) -> dict[Relation, list[Person]]:
        return self.__relatives_dict

    def __add_relation(self, to: Person, relation: Relation) -> None:
        if self is to:
            raise InvalidRelationError("Can't be related to self")
        if self.relation_with(to) is not None:
            raise InvalidRelationError(
                f"Relation is already present ({self.relation_with(to)})"
            )

        self.__graph.add_edges_from([(self, to, {Relation: relation})])
        self.__relatives_dict[relation].append(to)

    def remove_relative(self, relative: Person) -> None:
        def remove_from_one_side(person1: Person, person2: Person):
            relation: Relation = person1.relation_with(person2)
            if relation is not None:
                person1.__relatives_dict[relation].remove(person2)
                person1.__graph.remove_edge(person1, person2)
            else:
                raise InvalidRelationError("Relation not present")

        remove_from_one_side(self, relative)
        remove_from_one_side(relative, self)

    def self_remove(self):
        person = self

        # Removing this person from relatives' reltives_dict
        # This can be done using self.remove_relative(relative), but it removes from both sides, which is not required here, since the person object will be deleted
        for _, relatives in person.relatives_dict().items():
            for relative in relatives:
                relative.__relatives_dict[relative.relation_with(person)].remove(person)

        person.__graph.remove_node(person)

    @staticmethod
    def __validate_is_Person_object(x):
        if not isinstance(x, Person):
            raise ValueError(f"{x} is not a 'Person' object")

    def add_child(self, child: Person) -> None:
        self.__validate_is_Person_object(child)

        child_rel = Relation.SON if child.__gender == "m" else Relation.DAUGHTER
        parent_rel = Relation.FATHER if self.__gender == "m" else Relation.MOTHER

        if self.relation_with(child) is not None:
            raise InvalidRelationError(
                f"Relation is already present ({self.relation_with(child)})"
            )

        if len(child.relatives_dict()[parent_rel]) >= 1:
            raise InvalidRelationError("Can't have multiple father or mother values")

        if parent_rel == Relation.FATHER:
            if (
                child.mother is not None
                and self.relation_with(child.mother) != Relation.WIFE
            ):
                raise InvalidRelationError(
                    f"{self} and {child.mother} are not spouse. {child.mother} is mother of {child}"
                )
        else:
            if (
                child.father is not None
                and self.relation_with(child.father) != Relation.HUSBAND
            ):
                raise InvalidRelationError(
                    f"{child.father} and {self} are not spouse. {child.father} is father of {child}"
                )

        self.__add_relation(child, child_rel)
        child.__add_relation(self, parent_rel)

    def add_parent(self, parent: Person) -> None:
        parent.add_child(self)

    def add_spouse(self, other: Person) -> None:
        self.__validate_is_Person_object(other)

        # if {self.__gender, other.__gender} != {'m', 'f'}:
        if self.__gender == other.__gender:
            raise ValueError("Gender is same")

        if self.__gender == "m":
            husband = self
            wife = other
        else:
            husband = other
            wife = self

        husband.__add_relation(wife, Relation.WIFE)
        wife.__add_relation(husband, Relation.HUSBAND)

    def __repr__(self) -> str:
        # return f'P{self.id}({self.name.split(" ")[0]})'
        return f"P{self.id}({self.name})"


class Lineage:
    def __init__(self) -> None:
        self._graph = DiGraph()
        self.__counter = -1

    def __new_id(self) -> int:
        self.__counter += 1
        return self.__counter

    # TODO Add id in graph node and person in node's attribute for faster search by id
    def add_person(self, name: str, gender: str) -> Person:
        person = Person(self._graph, self.__new_id(), name, gender)
        self._graph.add_node(person)

        return person

    def remove_person(self, person: Person) -> None:
        person.self_remove()

    def find_person_by_id(self, id: int) -> Person | None:
        for person in self.all_persons():
            if person.id == id:
                return person

    def find_person_by_name(self, name: str) -> list[Person]:
        name = name.lower()
        found = []
        for person in self.all_persons():
            if name in person.name.lower():
                found.append(person)
        return found

    def all_persons(self) -> list[Person]:
        return list(self._graph.nodes)

    def all_relations(self) -> list[(Person, Person, Relation)]:
        relations = []
        for p1, p2, relation in self._graph.edges.data():
            relations.append((p1, p2, relation[Relation]))
        return relations

    def all_unique_relations(self) -> list[(Person, Person, Relation)]:
        relations = []
        rel_set = []
        for p1, p2, relation in self._graph.edges.data():
            if (p1, p2) not in rel_set and (p2, p1) not in rel_set:
                rel_set.append((p1, p2))
                relations.append((p1, p2, relation[Relation]))

        return relations

    def shortest_path(self, start, stop):
        return networkx.shortest_path(self._graph, start, stop)

    def save_to_file(self, filename: Path | str) -> None:
        data = {
            "headers": {
                "persons": ["id", "name", "gender"],
                "relations": ["id1", "id2", "relation"],
            },
            "persons": [],
            "relations": [],
        }

        for person in self.all_persons():
            data["persons"].append([person.id, person.name, person.gender])

        for p1, p2, relation in self.all_relations():
            data["relations"].append([p1.id, p2.id, relation.name])

        with open(filename, "w") as f:
            json.dump(data, f, indent=0, separators=(",", ":"))

    @classmethod
    def load_from_file(cls, filename: Path | str) -> Lineage:
        lineage = cls()

        with open(filename) as f:
            data = json.load(f)
            persons_data = data["persons"]
            relations_data = data["relations"]

            persons_dict: dict[int, Person] = {}
            for prev_id, name, gender in persons_data:
                try:
                    # Here persons new id can be different or
                    # Lineage counter should be made equal to the highest id assigned plus 1
                    person = lineage.add_person(name, gender)

                    persons_dict[prev_id] = person
                except Exception:
                    pass

            for prev_id1, prev_id2, relation in relations_data:
                try:
                    prev_id1, prev_id2 = int(prev_id1), int(prev_id2)
                    persons_dict[prev_id1]._Person__add_relation(
                        persons_dict[prev_id2], Relation[relation]
                    )

                except Exception:
                    pass

        return lineage
