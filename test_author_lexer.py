import pytest

from author_lexer import AuthorLexer
from docengine import Doc


def test_author_lexer_single_author():
    """
    Test that lexer returns single color and original string
    if there is only one author
    """
    doc = Doc()
    doc.site = 0
    test_str = "Test string"
    for idx, c in enumerate(test_str):
        doc.insert(idx, c)

    lexer = AuthorLexer(doc)
    lex_func = lexer.lex_document(None)
    colors, chars = zip(*lex_func(0))

    assert len(set(colors)) == 1
    assert "".join(chars) == test_str


def test_author_lexer_multiple_authors():
    """
    Test that lexer returns three colors for three
    different authors.
    :return:
    """
    doc = Doc()
    doc.site = 0
    author_inserts = ["first", "second", "third"]
    for insert in author_inserts:
        for idx, c in enumerate(insert):
            doc.insert(idx, c)
        doc.site += 1

    lexer = AuthorLexer(doc)
    lex_func = lexer.lex_document(None)
    colors = [item[0] for item in lex_func(0)]

    assert len(set(colors)) == 3
