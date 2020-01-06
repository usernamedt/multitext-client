from .char_position import CharPosition


class Character:
    """
    Represents a character in CRDT document.
    """
    def __init__(self, char, position, clock) -> None:
        """
        :param char: character symbol
        :type char: str
        :param position: pos of char in document tree
        :type position: CharPosition
        :param clock: document clock at the moment of char creation
        :type clock: int
        """
        self.char = char
        self.position = position
        self.clock = clock

    @property
    def author(self) -> int:
        """
        Getter for author of character
        :return: author site id of character
        """
        return self.position.sites[-1]

    def __lt__(self, other) -> bool:
        return self.position < other.position
