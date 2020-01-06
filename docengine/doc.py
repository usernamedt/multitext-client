import json
from typing import List

from sortedcontainers import SortedList

from .allocator import Allocator
from .character import Character
from .char_position import CharPosition


class Doc:
    def __init__(self, site=0) -> None:
        """
        Create a new document
        :param site: author id
        :type site: int
        """
        self.__site: int = site
        self._alloc = Allocator(self.site)
        self.__clock: int = 0
        self.__doc: SortedList[Character] = SortedList()
        self.__doc.add(Character("", CharPosition([0], [-1]), self.__clock))
        base_bits = CharPosition.BASE_BITS
        self.__doc.add(Character("", CharPosition([2 ** base_bits - 1], [-1]),
                                 self.__clock))

    def insert(self, position, char) -> str:
        """
        Insert char at specified document pos
        :param position: flat pos index in document text
        :type position: int
        :param char: character to insert
        :type char: str
        :return: patch with specified insert operation
        """
        self.__clock += 1
        p, q = self.__doc[position].position, self.__doc[position + 1].position

        new_char = Character(char, self._alloc(p, q), self.__clock)
        self.__doc.add(new_char)

        return self.__export("i", new_char)

    def delete(self, position) -> str:
        """
        Delete char from specified document pos
        :param position: flat pos index in document text
        :type position: int
        :return: patch with specified delete operation
        """
        self.__clock += 1
        old_char = self.__doc[position + 1]
        self.__doc.remove(old_char)
        return self.__export("d", old_char)

    def apply_patch(self, raw_patch) -> None:
        """
        Apply existing patch to internal document
        :param raw_patch: raw patch
        :type raw_patch: str
        """
        patch = json.loads(raw_patch)
        if patch["op"] == "i":
            patch = Character(patch["char"], CharPosition(
                patch["pos"], patch["sites"]), patch["clock"])
            self.__doc.add(patch)
        elif patch["op"] == "d":
            patch = next(c for c in self.__doc if
                         c.position.position == patch["pos"] and
                         c.position.sites == patch["sites"] and
                         c.clock == patch["clock"]
                         )
            self.__doc.remove(patch)

    @staticmethod
    def __export(op, char) -> str:
        """
        Export serialized operation on specified character.
        :param op: operation (insert/delete)
        :param char: character
        :type op: str
        :type char: Character
        :return: operation serialized as json
        """
        patch = {
            "op": op,
            "char": char.char,
            "pos": char.position.position,
            "sites": char.position.sites,
            "clock": char.clock,
        }
        return json.dumps(patch, sort_keys=True)

    def get_real_position(self, patch):
        json_char = json.loads(patch)
        idx = next((i for i, c in enumerate(self.__doc) if
                    c.position.position == json_char["pos"] and
                    c.position.sites == json_char["sites"] and
                    c.clock == json_char["clock"]
                    ), None)
        return idx

    @property
    def site(self) -> int:
        return self.__site

    @site.setter
    def site(self, value) -> None:
        """
        On site change, refresh Allocator
        :param value: author site id
        :type value: int
        """
        self.__site = value
        self._alloc = Allocator(value)

    @property
    def text(self) -> str:
        return "".join([c.char for c in self.__doc])

    @property
    def authors(self) -> List[int]:
        return [c.author for c in self.__doc]

    @property
    def patch_set(self) -> set:
        return {self.__export("i", c) for c in self.__doc[1:-1]}
