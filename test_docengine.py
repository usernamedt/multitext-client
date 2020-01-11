from docengine import Doc
from docengine.allocator import Allocator
from docengine.char_position import CharPosition


def test_docengine_allocator():
    """
    Test correctness of position allocation between two existing ones
    """
    left_position = [0]
    left_authors = [-1]
    right_position = [0, 1]
    right_authors = [-1, 0]
    base_bits = CharPosition.BASE_BITS

    test_allocator = Allocator(0)
    left_char_pos = CharPosition(left_position, left_authors,
                                 base_bits=base_bits)
    right_char_pos = CharPosition(right_position, right_authors,
                                  base_bits=base_bits)

    interval_at_depth = left_char_pos.interval_at(3)
    res_pos = test_allocator(left_char_pos, right_char_pos).position

    assert (0 < res_pos[-1] <= 5 or 123 <=
            res_pos[-1] < interval_at_depth)


def test_docengine_insert():
    """
    test Doc line insertion
    """
    test_str = "test insert of line"
    doc = Doc()

    for c in test_str:
        doc.insert(0, c)

    assert doc.text == test_str[::-1]


def test_docengine_to_int():
    """
    Test conversion from tree path to integer position in Doc sequence
    """
    position = [1, 2]
    authors = [0, 0]
    base_bits = 1

    test_pos = CharPosition(position, authors, base_bits=base_bits)

    assert test_pos.convert_to_int() == 6


def test_docengine_trim():
    """
    Test Doc tree position trimming function.
    """
    position = [1, 2]
    authors = [0, 0]
    trim_level = 1

    test_pos = CharPosition(position, authors,
                            base_bits=CharPosition.BASE_BITS)

    assert test_pos.convert_to_int(trim=trim_level) == 1


def test_docengine_comparator():
    """
    Comparator of pos for sorted list test
    """
    left_position = [0]
    left_authors = [-1]
    right_position = [0, 1]
    right_authors = [-1, 0]
    base_bits = CharPosition.BASE_BITS

    left_char_pos = CharPosition(left_position, left_authors,
                                 base_bits=base_bits)
    right_char_pos = CharPosition(right_position, right_authors,
                                  base_bits=base_bits)

    assert left_char_pos < right_char_pos
