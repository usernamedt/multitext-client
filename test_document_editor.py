import unittest
from unittest import mock
from unittest.mock import PropertyMock

from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.document import Document
from prompt_toolkit.selection import SelectionState, SelectionType

from docengine import Doc
from document_editor import DocumentEditor


@unittest.mock.patch("document_editor.get_app")
@unittest.mock.patch("document_editor.MessageService")
def test_document_editor_do_cut(mock_msg_service, mock_get_app):
    # get sample patches
    doc = Doc()
    doc.site = 0
    test_str = "Test string, quite a long one! Yeah, sure..."
    patches = []
    for idx, c in enumerate(test_str):
        patches.append(doc.insert(idx, c))
    msg_srv_instance = mock_msg_service.return_value()
    mock_msg_service.return_value.prepare_send_request.return_value = None
    mock_msg_service.return_value.put_message.return_value = None

    document_editor = DocumentEditor(msg_srv_instance)
    for patch in patches:
        document_editor.update_text(patch)
    document_editor.text_field.buffer.selection_state = \
        SelectionState(4, SelectionType.CHARACTERS)

    document_editor.do_cut()
    # check if only Test word left
    assert document_editor.doc.text == "Test"
    cut_data = mock_get_app.return_value.clipboard.set_data\
        .call_args[0][0]

    # check if correct text was sent to clipboard
    assert cut_data.text == ' string, quite a long one! Yeah, sure...'


@unittest.mock.patch("document_editor.MessageService")
def test_document_editor_do_del(mock_msg_service):
    # get sample patches
    doc = Doc()
    doc.site = 0
    test_str = "Test string, quite a long one! Yeah, sure..."
    patches = []
    for idx, c in enumerate(test_str):
        patches.append(doc.insert(idx, c))
    msg_srv_instance = mock_msg_service.return_value()
    mock_msg_service.return_value.prepare_send_request.return_value = None
    mock_msg_service.return_value.put_message.return_value = None

    document_editor = DocumentEditor(msg_srv_instance)
    for patch in patches:
        document_editor.update_text(patch)
    document_editor.text_field.buffer.selection_state = \
        SelectionState(4, SelectionType.CHARACTERS)

    document_editor.do_delete()
    assert document_editor.doc.text == "Test"


@unittest.mock.patch("document_editor.get_app")
@unittest.mock.patch("document_editor.MessageService")
def test_document_editor_do_copy(mock_msg_service, mock_get_app):
    # get sample patches
    doc = Doc()
    doc.site = 0
    test_str = "Test string, quite a long one! Yeah, sure..."
    patches = []
    for idx, c in enumerate(test_str):
        patches.append(doc.insert(idx, c))
    msg_srv_instance = mock_msg_service.return_value()
    mock_msg_service.return_value.prepare_send_request.return_value = None
    mock_msg_service.return_value.put_message.return_value = None

    document_editor = DocumentEditor(msg_srv_instance)
    for patch in patches:
        document_editor.update_text(patch)
    document_editor.text_field.buffer.selection_state = \
        SelectionState(4, SelectionType.CHARACTERS)

    document_editor.do_copy()
    # assert that document remains unchanged
    assert document_editor.doc.text == "Test string, quite a long one!" \
                                       " Yeah, sure..."
    copied_data = mock_get_app.return_value.clipboard.set_data \
        .call_args[0][0]

    # check if correct text was sent to clipboard
    assert copied_data.text == ' string, quite a long one! Yeah, sure...'


@unittest.mock.patch("document_editor.get_app")
@unittest.mock.patch("document_editor.MessageService")
def test_document_editor_do_paste(mock_msg_service, mock_get_app):
    # get sample patches
    doc = Doc()
    doc.site = 0
    test_str = "Test string, quite a long one! Yeah, sure..."
    patches = []
    for idx, c in enumerate(test_str):
        patches.append(doc.insert(idx, c))
    msg_srv_instance = mock_msg_service.return_value()
    mock_msg_service.return_value.prepare_send_request.return_value = None
    mock_msg_service.return_value.put_message.return_value = None

    document_editor = DocumentEditor(msg_srv_instance)
    for patch in patches:
        document_editor.update_text(patch)
    document_editor.text_field.buffer.selection_state = \
        SelectionState(4, SelectionType.CHARACTERS)

    mock_get_app.return_value.clipboard.get_data.return_value = \
        ClipboardData("TEST")
    document_editor.do_paste()
    # assert that document remains unchanged
    assert document_editor.doc.text == "Test string, quite a long one!" \
                                       " Yeah, sure...TEST"
