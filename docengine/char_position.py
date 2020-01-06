from typing import List, Tuple


class CharPosition:
    """
    Defines a character pos in CRDT document tree.
    Every element is part of the tree path.
    """
    BASE_BITS = 5

    def __init__(self, position=None, sites=None, base_bits=0) -> None:
        """
        :param position: array of int specifying char pos
        :param sites: array of author ids for each tree level
        :param base_bits:
        :type position: List[int]
        :type sites: List[int]
        :type base_bits: int
        """
        self.position = position or []
        self.sites = sites or []
        self.base_bits = base_bits or self.BASE_BITS

    @classmethod
    def create_from_int(cls, position, depth, sites, base_bits=0) -> \
            'CharPosition':
        """
        Create new pos from values
        :param position: pos index
        :param depth: pos depth
        :param sites: pos sites
        :param base_bits: pos base bits
        :type position: int
        :type depth: int
        :type sites: List[int]
        :type base_bits: int
        :return: generated CharPosition object
        """
        result = cls(sites=sites, base_bits=base_bits)

        for curr_depth in range(depth, 0, -1):
            shift = base_bits + curr_depth - 1

            # ref to pdf algorithm
            result.position.insert(0, position & (1 << shift) - 1)
            position >>= shift

        return result

    def convert_to_int(self, trim=0) -> int:
        """
        Convert pos to integer representation
        :param trim: trim level
        :type trim: int
        :return: integer representation of pos object
        """
        pos_as_list = self.__cut_position(self.position, trim) if trim \
            else self.position

        result = 0
        for curr_depth, i in enumerate(pos_as_list):

            # Append '0' and place 'i'
            result = (result << (self.base_bits + curr_depth)) | int(i)

        return result

    def get_interval_between(self, other_pos, depth) -> \
            Tuple[int, bool]:
        """
        Get interval between current pos and other one
        :param other_pos:other CharPosition
        :param depth: depth level
        :type other_pos: CharPosition
        :type depth: int
        """
        if self.position == other_pos.position and self.sites[-1] \
                != other_pos.sites[-1] and depth > len(self.position):
            return self.interval_at(depth), True

        return other_pos.convert_to_int(depth) - self.convert_to_int(
            depth) - 1, False

    def interval_at(self, depth) -> int:
        """
        Get interval at specified depth level
        :param depth: depth level
        :type depth: int
        :return: interval at specified depth
        """
        return 2 ** (self.base_bits + depth - 1) - 1

    @staticmethod
    def __cut_position(position, depth) -> List[int]:
        """
        Cut pos to specified depth
        :param position: char pos
        :param depth: tree depth
        :type position: List[int]
        :type depth: int
        :return: resulting pos as List of int
        """
        result = []
        for curr_depth in range(depth):
            if curr_depth < len(position):
                result.append(position[curr_depth])
            else:
                result.append(0)

        return result

    def __lt__(self, other):
        """
        :type other: CharPosition
        """
        # order by pos
        # if equal positions, order by site id
        return list(zip(self.position, self.sites)) < list(
            zip(other.position, other.sites))
