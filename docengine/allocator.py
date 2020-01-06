from random import randint, getrandbits
from typing import Dict
from .char_position import CharPosition


class Allocator:
    """
    Allocate position between provided p and q positions
    https://hal.archives-ouvertes.fr/hal-00921633/document
    section 3.3
    """
    BOUNDARY = 5
    MAX_DEPTH = 32 - CharPosition.BASE_BITS

    def __init__(self, site: int) -> None:
        self.__strategy_history: Dict[int, bool] = {}
        self._site = site

    def allocate(self, p, q) -> CharPosition:
        """
        Generate new pos between provided positions
        :param p: character pos
        :param q: character pos
        :type p: CharPosition
        :type q: CharPosition
        :return: allocated pos
        """
        if p.position == q.position and p.sites == q.sites:
            raise Exception("Provided p and q are equal. Cannot allocate.")

        depth = 0
        interval = 0
        is_equal = False
        while interval < 1:
            depth += 1
            interval, is_equal = p.get_interval_between(q, depth)

            if depth > self.MAX_DEPTH:
                raise Exception("Max depth reached. Aborting.")

        alloc_step = min(self.BOUNDARY, randint(0, interval - 1) + 1)

        if self.get_strategy(depth) or is_equal:
            res = p.convert_to_int(depth) + alloc_step
        else:
            res = q.convert_to_int(depth) - alloc_step

        sites_len = depth - len(p.sites)
        sites = p.sites + [self._site] * sites_len
        sites[-1] = self._site

        return CharPosition.create_from_int(res, depth, sites,
                                            base_bits=p.base_bits)

    def get_strategy(self, depth: int):
        """
        If it was not allocated before, picks random allocation strategy
        (boundary+ or boundary-) for specified depth.
        :param depth: depth level
        :type depth: int
        :return True if boundary+, False if boundary-
        """
        if depth not in self.__strategy_history:
            self.__strategy_history[depth] = bool(getrandbits(1))

        return self.__strategy_history[depth]

    def __call__(self, p, q) -> CharPosition:
        """
        Allocate a new pos between existing ones.
        :type p: CharPosition
        :type q: CharPosition
        :return: CharPosition
        """
        return self.allocate(p, q)
