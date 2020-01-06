#!/usr/bin/env python
"""
Multi-user text editor
"""
from asyncio import ensure_future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout.containers import (
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    MenuContainer,
    MenuItem,
)

from application_state import ApplicationState
from client_application import ClientApplication
from document_editor import DocumentEditor
from alert_dialog import AlertDialog
from message_service import MessageService
from text_editor import TextEditor
from input_dialog import InputDialog

# patch to fix tabulation issue
Char.display_mappings['\t'] = '  '


class ApplicationBuilder:
    """
    Builds a text editor user interface.
    """

    def __init__(self, app_state, doc_editor, msg_service, style):
        self.style: Style = style
        self.app_state: ApplicationState = app_state
        self.doc_editor: DocumentEditor = doc_editor
        self.text_field: TextEditor = self.doc_editor.text_field
        self.msg_service: MessageService = msg_service

        self.root_container = self.__build_root_container(
            body=self.__build_body(),
            do_save_file=self.__do_save_file,
            do_share_file=self.__do_share_file,
            do_file_info=self.__do_file_info,
            do_exit=self.__do_exit,
            do_cut=self.doc_editor.do_cut,
            do_copy=self.doc_editor.do_copy,
            do_paste=self.doc_editor.do_paste,
            do_delete=self.doc_editor.do_delete,
            do_about=self.__do_about,
            bindings=self.__build_root_bindings()
        )

    def build_app(self) -> ClientApplication:
        """
        Build CUI application with text editor.
        :return: ClientApplication
        """

        return ClientApplication(
            layout=Layout(self.root_container,
                          focused_element=self.text_field),
            enable_page_navigation_bindings=True,
            style=self.style,
            mouse_support=True,
            full_screen=True,
            clipboard=PyperclipClipboard(),
            show_message=self.show_message
        )

    def __get_statusbar_text(self) -> str:
        """
        Get text displayed on the left bottom corner
        :return: text string
        """
        if self.app_state.is_saving:
            return "Saving file to server..."
        return " Press Ctrl-C to open menu. "

    def __get_statusbar_right_text(self) -> str:
        """
        Get text displayed on the right bottom corner
        :return: text string
        """
        return " {}:{}  ".format(
            self.text_field.document.cursor_position_row + 1,
            self.text_field.document.cursor_position_col + 1,
        )

    def __build_body(self) -> HSplit:
        """
        Build body component that holds text editor and footer.
        :return HSplit component
        """
        return HSplit(
            [
                self.text_field,
                VSplit([
                            Window(
                                FormattedTextControl(
                                    self.__get_statusbar_text),
                                style="class:status"
                            ),
                            Window(
                                FormattedTextControl(
                                    self.__get_statusbar_right_text),
                                style="class:status.right",
                                width=9,
                                align=WindowAlign.RIGHT,
                            ),
                        ], height=1)
            ]
        )

    @staticmethod
    def __build_root_container(body, do_save_file, do_share_file,
                               do_file_info, do_exit, do_cut, do_copy,
                               do_paste, do_delete, do_about, bindings) -> \
            MenuContainer:
        """
        Build a container that holds all components inside.
        :type body: HSplit
        :type do_save_file: function
        :type do_share_file: function
        :type do_file_info: function
        :type do_exit: function
        :type do_cut: function
        :type do_copy: function
        :type do_paste: function
        :type do_delete: function
        :type do_about: function
        :type bindings: KeyBindings
        :return: MenuContainer component
        """
        return MenuContainer(
            body=body,
            menu_items=[
                MenuItem(
                    "File",
                    children=[
                        MenuItem("Save", handler=do_save_file),
                        MenuItem("Share", handler=do_share_file),
                        MenuItem("Info", handler=do_file_info),
                        MenuItem("-", disabled=True),
                        MenuItem("Exit", handler=do_exit),
                    ],
                ),
                MenuItem(
                    "Edit",
                    children=[
                        MenuItem("Cut", handler=do_cut),
                        MenuItem("Copy", handler=do_copy),
                        MenuItem("Paste", handler=do_paste),
                        MenuItem("Delete", handler=do_delete)
                    ],
                ),
                MenuItem("Info",
                         children=[MenuItem("About", handler=do_about)]),
            ],
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=16, scroll_offset=1),
                ),
            ],
            key_bindings=bindings,
        )

    def __build_root_bindings(self) -> KeyBindings:
        """
        Application menu keybindings (works on application-wide level)
        :return: KeyBindings component
        """
        bindings = KeyBindings()

        @bindings.add("c-c")
        def _(event: KeyPressEvent):
            """
            Control-C event handler
            """
            event.app.layout.focus(self.root_container.window)

        return bindings

    @staticmethod
    def __do_exit() -> None:
        """
        Terminate CUI application.
        """
        get_app().exit()

    def __do_about(self) -> None:
        """
        Show app info
        """
        self.show_message("About", "Multi-user text editor based on LSEQ "
                                   "CRDT.\nCreated by @usernamedt.")

    def show_message(self, title, text) -> None:
        """
        Show alert message with specified title and text
        :param title: message title
        :type title: str
        :param text: message text
        :type text: str
        """
        async def coroutine():
            dialog = AlertDialog(title, text)
            await self.__show_dialog_as_float(dialog)

        ensure_future(coroutine())

    async def __show_dialog_as_float(self, dialog) -> None:
        """
        Show dialog above main application window.
        :param dialog component
        """
        float_ = Float(content=dialog)
        self.root_container.floats.insert(0, float_)

        app = get_app()

        focused_before = app.layout.current_window
        app.layout.focus(dialog)
        result = await dialog.future
        app.layout.focus(focused_before)

        if float_ in self.root_container.floats:
            self.root_container.floats.remove(float_)

        return result

    def __do_save_file(self) -> None:
        """
        Send save file request on server
        """
        self.app_state.is_saving = True
        msg = self.msg_service.prepare_send_request(
            {"type": "save_file_request"})
        self.msg_service.put_message(msg)
        get_app().invalidate()

    def __do_share_file(self) -> None:
        """
        Send file share request with login of the recipient user.
        """
        async def coroutine():
            open_dialog = InputDialog(
                title="Recipient",
                label_text="Enter username to share a file with:",
            )
            username = await self.__show_dialog_as_float(open_dialog)

            if username is not None:
                encoded_message = self.msg_service.prepare_send_request(
                    {"type": "file_share_request",
                     "share_user": username})
                self.msg_service.put_message(encoded_message)

        ensure_future(coroutine())

    def __do_file_info(self) -> None:
        """
        Show general info for opened file.
        """
        filename = self.app_state.current_filename
        doc_text = self.doc_editor.doc.text
        for char in '-.,\n':
            doc_text = doc_text.replace(char, ' ')
        word_count = len(doc_text.split())
        length = len(self.doc_editor.doc.text)
        self.show_message(f"{filename} info",
                          f"{word_count} words\n{length} characters")
