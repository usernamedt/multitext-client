"""
Base classes for prompt_toolkit lexers.
"""
from typing import Callable

from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.base import StyleAndTextTuples
from prompt_toolkit.lexers import Lexer

from docengine import Doc


class AuthorLexer(Lexer):
    """
    Lexer that highlights each char with it's author color
    from the COLORS palette
    """
    COLORS = (
        'fg:ansired',
        'fg:ansigreen',
        'fg:ansiyellow',
        'fg:ansiblue',
        'fg:ansimagenta',
        'fg:ansicyan',
        'fg:ansibrightblue'
    )

    NUM_COLORS = len(COLORS)

    def __init__(self, doc: Doc) -> None:
        self.doc = doc

    def __get_author_color(self, site_id) -> str:
        """
        Get color for document site id
        :param site_id: id of document site (author id)
        :return: str with ansi color
        """
        return self.COLORS[site_id % self.NUM_COLORS]

    def lex_document(self, document: Document)\
            -> Callable[[int], StyleAndTextTuples]:
        """
        Highlight document
        :param document: document object
        :return: function that returns line at line number as formatted text
        """
        colored_lines = []
        line_colors: StyleAndTextTuples = []
        closed_line = False

        for c, a in zip(self.doc.text, self.doc.authors[1:-1]):
            if c == "\n":
                colored_lines.append(line_colors)
                line_colors = []
                closed_line = True
                continue
            else:
                line_colors.append((self.__get_author_color(a), c))
                closed_line = False
        if not closed_line:
            colored_lines.append(line_colors)

        def get_line(line_number: int) -> StyleAndTextTuples:
            """
            Return the tokens for the provided line.
            """
            try:
                return colored_lines[line_number]
            except IndexError:
                return []

        return get_line
