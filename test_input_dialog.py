from input_dialog import InputDialog


def test_input_dialog():
    title = 'test title'
    inp_dialog = InputDialog(title, 'test text')
    assert inp_dialog.__pt_container__().title == title
