from asyncio import Future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.layout.containers import (
    HSplit,
)
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
)

from text_editor import TextEditor


class InputDialog:
    """
    Message with text input and OK / cancel buttons
    """
    def __init__(self, title="", label_text="", completer=None):
        self.future = Future()

        def accept_text(buf) -> bool:
            """
            Change focus to OK button after user pressed enter on text field.
            """
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            """
            Set future result to text from text field if user pressed OK
            button.
            """
            self.future.set_result(self.text_area.text)

        def cancel():
            """
            Set future result to None if user pressed cancel button.
            """
            self.future.set_result(None)

        self.text_area = TextEditor(
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
            key_bindings=load_key_bindings(),
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog
