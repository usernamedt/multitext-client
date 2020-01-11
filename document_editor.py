import json
import random
from typing import Tuple

from prompt_toolkit.application import get_app
from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import SearchToolbar

from author_lexer import AuthorLexer
from docengine import Doc
from message_service import MessageService
from text_editor import TextEditor


class DocumentEditor:
    """
    Document Editor responds to keypress events and copy/cut/paste/delete
    events by applying patches to internal CRDT document and then updating
    the changed text on outer TextEditor document object.
    """
    WINDOWS_LINE_ENDING = '\r\n'
    UNIX_LINE_ENDING = '\n'
    CR_CHAR = '\r'

    def __init__(self, msg_service: MessageService):
        self.doc = Doc()
        self.doc.site = int(random.getrandbits(32))
        self.patch_set = []
        self.msg_service = msg_service
        self.text_field = TextEditor(
            scrollbar=True,
            line_numbers=False,
            search_field=SearchToolbar(),
            key_bindings=self.__init_bindings(),
            lexer=AuthorLexer(self.doc)
        )

    def __register_patch(self, patch) -> None:
        """
        Put provided patch to internal patch set and send patch to
        the server using Message Service
        :type patch: str
        """
        self.patch_set.append(patch)
        message = self.msg_service.prepare_send_request({"type": "patch",
                                                         "content": patch})
        self.msg_service.put_message(message)

    def do_cut(self) -> None:
        """
        Handle selection cut.
        """
        new_doc, cut_data = self.__get_selection(cut=True)
        get_app().clipboard.set_data(cut_data)
        self.text_field.document = new_doc

    def do_copy(self) -> None:
        """
        Handle selection copy
        """
        _, cut_data = self.__get_selection(cut=False)
        get_app().clipboard.set_data(cut_data)

    def do_delete(self) -> None:
        """
        Handle selection delete
        """
        self.text_field.document, _ = self.__get_selection(cut=True)

    def do_paste(self) -> None:
        """
        Handle paste from clipboard
        """
        paste_text = get_app().clipboard.get_data().text
        # replace CRLF with LF
        paste_text = paste_text.replace(self.WINDOWS_LINE_ENDING,
                                        self.UNIX_LINE_ENDING)
        paste_text = paste_text.replace(self.CR_CHAR, self.UNIX_LINE_ENDING)
        cursor_pos = self.text_field.buffer.cursor_position
        for idx, char in enumerate(paste_text):
            self.text_field.buffer.text += str(idx)
            patch = self.doc.insert(cursor_pos + idx, char)
            self.__register_patch(patch)

        self.text_field.buffer.text = self.doc.text
        self.text_field.buffer.cursor_position += len(paste_text)

    def __get_selection(self, cut=False) -> Tuple[Document, ClipboardData]:
        """
        Get selection from document selection and the resulting document.
        If cut is true, remove selection from internal CRDT document
        immediately.
        :param cut: cut selected part of document
        :type cut: bool
        :return: resulting document and selection text fragment
        """
        if self.text_field.document.selection:
            cut_parts = []
            remaining_parts = []
            new_cursor_position = self.text_field.document.cursor_position

            last_end = 0
            for start, end in self.text_field.document.selection_ranges():
                if cut:
                    # remove from internal doc
                    for pos in range(end, start, -1):
                        patch = self.doc.delete(pos - 1)
                        self.__register_patch(patch)

                if last_end == 0:
                    new_cursor_position = start

                remaining_parts.append(
                    self.text_field.document.text[last_end:start])
                cut_parts.append(self.text_field.document.text[start:end])
                last_end = end

            remaining_parts.append(self.text_field.document.text[last_end:])

            cut_text = "\n".join(cut_parts)

            return (
                Document(text=self.doc.text,
                         cursor_position=new_cursor_position),
                ClipboardData(cut_text,
                              self.text_field.document.selection.type),
            )
        else:
            return self.text_field.document, ClipboardData("")

    def __init_bindings(self) -> KeyBindings:
        """
        Generate bindings that handles KeyPress events, make changes to
        internal doc and then displaying them in outer TextEdit buffer.
        :return:
        """
        bindings = KeyBindings()
        @bindings.add('delete')
        def handle_delete(event: KeyPressEvent) -> None:
            """
            Captures Delete KeyPress event
            and removes char next to cursor pos from internal Doc
            """
            if not self.text_field.buffer.text:
                return

            if self.text_field.buffer.selection_state:
                self.do_delete()
            elif self.text_field.buffer.cursor_position \
                    != len(self.text_field.buffer.text):
                cursor_pos = self.text_field.buffer.cursor_position
                patch = self.doc.delete(cursor_pos)

                self.text_field.buffer.text = self.doc.text

                self.__register_patch(patch)

        @bindings.add('c-h')
        def handle_backspace(event: KeyPressEvent) -> None:
            """
            Captures Backspace KeyPress event
            and removes char before cursor pos from internal Doc
            """
            if not self.text_field.buffer.text or \
                    self.text_field.buffer.cursor_position == 0:
                return

            if self.text_field.buffer.selection_state:
                self.do_delete()
            else:
                cursor_pos = self.text_field.buffer.cursor_position
                patch = self.doc.delete(cursor_pos - 1)

                if cursor_pos != len(self.text_field.buffer.text):
                    self.text_field.buffer.cursor_position -= 1

                self.text_field.buffer.text = self.doc.text

                self.__register_patch(patch)

        @bindings.add('c-m')
        def handle_enter(event: KeyPressEvent) -> None:
            """
            Captures Enter KeyPress events and applies it to internal Doc
            """
            if self.text_field.buffer.selection_state:
                self.do_delete()

            cursor_pos = self.text_field.buffer.cursor_position
            patch = self.doc.insert(cursor_pos, self.UNIX_LINE_ENDING)

            self.text_field.buffer.text = self.doc.text
            self.text_field.buffer.cursor_position += 1

            self.__register_patch(patch)

        @bindings.add('c-i')
        @bindings.add('<any>')
        def handle_text_enter(event: KeyPressEvent) -> None:
            """
            Captures General / Tab
            KeyPress events and applies it to internal Doc
            """
            if self.text_field.buffer.selection_state:
                self.do_delete()

            cursor_pos = self.text_field.buffer.cursor_position
            patch = self.doc.insert(cursor_pos, event.data)

            self.text_field.buffer.text = self.doc.text
            self.text_field.buffer.cursor_right()

            self.__register_patch(patch)

        @bindings.add(Keys.BracketedPaste)
        def handle_paste(event: KeyPressEvent) -> None:
            """
            Handle paste event from terminal.
            :param event:
            :return:
            """
            self.do_paste()

        return bindings

    def update_text(self, patch) -> None:
        """
        Apply patch to internal document and update
        TextEdit window buffer.
        :param patch: raw patch
        :type patch: str
        """
        json_patch = json.loads(patch)
        operation = json_patch["op"]

        if operation == "d":
            patch_pos = self.doc.get_real_position(patch)
            self.doc.apply_patch(patch)
        else:
            self.doc.apply_patch(patch)
            patch_pos = self.doc.get_real_position(patch)

        old_pos = self.text_field.buffer.cursor_position
        self.text_field.buffer.text = self.doc.text
        if patch_pos == -1 or patch_pos > old_pos + 1:
            self.text_field.buffer.cursor_position = old_pos
        else:
            if operation == "i":
                self.text_field.buffer.cursor_right()
            if operation == "d":
                self.text_field.buffer.cursor_left()
