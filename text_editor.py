from typing import List, Optional

from prompt_toolkit.filters import (
    Condition,
    FilterOrBool,
    has_focus,
    is_done,
    is_true,
    to_filter,
)
from prompt_toolkit.formatted_text import (
    AnyFormattedText,
)
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    Window,
)
from prompt_toolkit.layout.controls import (
    BufferControl,
    GetLinePrefixCallable,
)
from prompt_toolkit.layout.dimension import AnyDimension
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.margins import NumberedMargin, ScrollbarMargin
from prompt_toolkit.layout.processors import (
    AppendAutoSuggestion,
    BeforeInput,
    ConditionalProcessor,
    PasswordProcessor,
    Processor,
)
from prompt_toolkit.lexers import DynamicLexer
from prompt_toolkit.widgets import (
    SearchToolbar,
    TextArea,
)


class TextEditor(TextArea):
    """
    Wrapper of default prompt toolkit textarea to
    redefine buffer control component init with provided keybindings
    """
    def __init__(self, multiline: FilterOrBool = True,
                 password: FilterOrBool = False,
                 focusable: FilterOrBool = True,
                 focus_on_click: FilterOrBool = False,
                 width: AnyDimension = None,
                 height: AnyDimension = None,
                 dont_extend_height: FilterOrBool = False,
                 dont_extend_width: FilterOrBool = False,
                 line_numbers: bool = False,
                 get_line_prefix: Optional[GetLinePrefixCallable] = None,
                 scrollbar: bool = False, style: str = "",
                 search_field: Optional[SearchToolbar] = None,
                 preview_search: FilterOrBool = True,
                 prompt: AnyFormattedText = "",
                 input_processors: Optional[List[Processor]] = None,
                 key_bindings: KeyBindings = None, **kwargs) -> None:

        super().__init__(multiline=multiline, password=password,
                         focusable=focusable, focus_on_click=focus_on_click,
                         width=width, height=height,
                         dont_extend_height=dont_extend_height,
                         dont_extend_width=dont_extend_width,
                         line_numbers=line_numbers,
                         get_line_prefix=get_line_prefix,
                         scrollbar=scrollbar, style=style,
                         search_field=search_field,
                         preview_search=preview_search, prompt=prompt,
                         input_processors=input_processors, **kwargs)

        if search_field is None:
            search_control = None
        elif isinstance(search_field, SearchToolbar):
            search_control = search_field.control

        if input_processors is None:
            input_processors = []

        self.control = BufferControl(
            buffer=self.buffer,
            lexer=DynamicLexer(lambda: self.lexer),
            input_processors=[
                                 ConditionalProcessor(
                                     AppendAutoSuggestion(),
                                     has_focus(self.buffer) & ~is_done
                                 ),
                                 ConditionalProcessor(
                                     processor=PasswordProcessor(),
                                     filter=to_filter(password)
                                 ),
                                 BeforeInput(prompt,
                                             style="class:text-area.prompt"),
                             ] + input_processors,
            search_buffer_control=search_control,
            preview_search=preview_search,
            focusable=focusable,
            focus_on_click=focus_on_click,
            key_bindings=key_bindings
        )

        if multiline:
            right_margins = [ScrollbarMargin(display_arrows=True)] \
                if scrollbar else []

            left_margins = [NumberedMargin()] if line_numbers else []

        else:
            height = D.exact(1)
            left_margins = []
            right_margins = []

        style = "class:text-area " + style

        self.window = Window(
            height=height,
            width=width,
            dont_extend_height=dont_extend_height,
            dont_extend_width=dont_extend_width,
            content=self.control,
            style=style,
            wrap_lines=Condition(lambda: is_true(self.wrap_lines)),
            left_margins=left_margins,
            right_margins=right_margins,
            get_line_prefix=get_line_prefix
        )
