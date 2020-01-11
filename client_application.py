from prompt_toolkit import Application
from prompt_toolkit.key_binding.bindings.emacs import \
    load_emacs_shift_selection_bindings
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from prompt_toolkit.key_binding.key_bindings import (
    KeyBindings,
    merge_key_bindings)
from prompt_toolkit.key_binding.key_processor import KeyPressEvent

try:
    import contextvars
except ImportError:
    import prompt_toolkit.eventloop.dummy_contextvars as contextvars


class ClientApplication(Application):
    """
    ClientApplication wrapper of prompt toolkit application
    with modified keybindings initialization
    """
    def __init__(self, show_message, **kwargs):
        self.show_message = show_message
        super().__init__(**kwargs)
        key_bindings = KeyBindings()
        handle = key_bindings.add

        # Readline-style bindings.
        handle("home")(get_by_name("beginning-of-line"))
        handle("end")(get_by_name("end-of-line"))
        handle("left")(get_by_name("backward-char"))
        handle("right")(get_by_name("forward-char"))

        @handle("up")
        def _(event: KeyPressEvent) -> None:
            event.current_buffer.auto_up(count=event.arg)

        @handle("down")
        def _(event: KeyPressEvent) -> None:
            event.current_buffer.auto_down(count=event.arg)

        self._default_bindings = merge_key_bindings(
            [
                key_bindings,
                load_emacs_shift_selection_bindings()
            ])
