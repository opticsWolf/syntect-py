# Type stubs for syntect-py
# Generated from actual Rust bindings — matches current API exactly

from typing import List, Optional, Tuple, Union, Iterator
from dataclasses import dataclass


# ============================================================================
# Core Types
# ============================================================================

@dataclass
class Color:
    """RGB color with alpha channel."""
    r: int
    g: int
    b: int
    a: int
    
    @staticmethod
    def from_hex(hex_str: str) -> "Color":
        """Create Color from hex string (e.g., '#FF0000' or 'FF0000')."""
        ...
    
    def to_hex(self) -> str:
        """Convert to hex string (e.g., '#FF0000')."""
        ...


@dataclass
class FontStyle:
    """Font style flags (bitmask)."""
    bits: int
    
    BOLD: "FontStyle"
    ITALIC: "FontStyle"
    UNDERLINE: "FontStyle"
    
    def __or__(self, other: "FontStyle") -> "FontStyle": ...
    def __and__(self, other: "FontStyle") -> "FontStyle": ...
    def __xor__(self, other: "FontStyle") -> "FontStyle": ...
    def __invert__(self) -> "FontStyle": ...


@dataclass
class Style:
    """Highlighting style with foreground, background, and font style."""
    foreground: Color
    background: Color
    font_style: FontStyle
    
    @staticmethod
    def from_hex_styles(fg_hex: str, bg_hex: str, font_bits: int) -> "Style":
        """Create Style from hex colors and font style bits."""
        ...


@dataclass
class StyleModifier:
    """Optional style modifier for theme items."""
    foreground: Optional[Color]
    background: Optional[Color]
    font_style: Optional[FontStyle]


# ============================================================================
# Syntax Management
# ============================================================================

@dataclass
class SyntaxReference:
    """Reference to a loaded syntax definition."""
    name: str
    scope: str
    file_extensions: List[str]
    hidden: bool
    first_line_match: Optional[str]
    version: int
    variables: List[Tuple[str, str]]


@dataclass
class SyntaxSet:
    """Collection of syntax definitions."""
    
    def __len__(self) -> int: ...
    
    @staticmethod
    def load_defaults(newlines: bool = False) -> "SyntaxSet":
        """Load default syntax set from built-in syntaxes."""
        ...
    
    @staticmethod
    def load_from_folder(path: str, newlines: bool = False) -> "SyntaxSet":
        """Load syntaxes from a folder."""
        ...
    
    def find_syntax_by_name(self, name: str) -> Optional[SyntaxReference]:
        """Find syntax by name."""
        ...
    
    def find_syntax_by_extension(self, ext: str) -> Optional[SyntaxReference]:
        """Find syntax by file extension."""
        ...
    
    def find_syntax_by_scope(self, scope: str) -> Optional[SyntaxReference]:
        """Find syntax by scope string."""
        ...
    
    def syntaxes(self) -> List[SyntaxReference]:
        """Return all syntax definitions."""
        ...
    
    def into_builder(self) -> "SyntaxSetBuilder":
        """Convert to builder for adding more syntaxes."""
        ...
    
    def find_unlinked_contexts(self) -> List[str]:
        """Find unlinked context references."""
        ...
    
    def metadata(self) -> Optional["Metadata"]:
        """Get metadata from .tmPreferences files."""
        ...
    
    @staticmethod
    def builder() -> "SyntaxSetBuilder":
        """Create a builder to load syntaxes from disk."""
        ...
    
    def find_syntax_for_file(self, path: str) -> Optional[SyntaxReference]:
        """Find syntax by file path."""
        ...
    
    def find_syntax_plain_text(self) -> SyntaxReference:
        """Get the plain text syntax."""
        ...
    
    def warnings(self) -> List[str]:
        """Get warnings collected during syntax loading."""
        ...
    
    @staticmethod
    def from_dump(path: str) -> "SyntaxSet":
        """Load syntax set from .packdump file."""
        ...
    
    def to_dump(self, path: str) -> None:
        """Save syntax set to .packdump file."""
        ...


@dataclass
class SyntaxSetBuilder:
    """Builder for loading syntax definitions from disk."""
    
    def add_from_folder(self, path: str, newlines: bool = False) -> List[str]:
        """Load .sublime-syntax files from folder. Returns warnings."""
        ...
    
    def add_plain_text_syntax(self) -> None: ...
    def build(self) -> SyntaxSet: ...
    def warnings(self) -> List[str]: ...


# ============================================================================
# Theme Management
# ============================================================================

@dataclass
class ThemeSettings:
    """Theme settings with all color options."""
    foreground: Optional[Color]
    background: Optional[Color]
    selection_background: Optional[Color]
    gutter_foreground: Optional[Color]
    gutter_background: Optional[Color]
    caret: Optional[Color]
    line_highlight: Optional[Color]
    misspelling: Optional[Color]
    minimap_border: Optional[Color]
    accent: Optional[Color]
    popup_css: Optional[str]
    phantom_css: Optional[str]
    bracket_contents_foreground: Optional[Color]
    bracket_contents_options: Optional["UnderlineOption"]
    brackets_foreground: Optional[Color]
    brackets_background: Optional[Color]
    brackets_options: Optional["UnderlineOption"]
    tags_foreground: Optional[Color]
    tags_options: Optional["UnderlineOption"]
    highlight: Optional[Color]
    find_highlight: Optional[Color]
    find_highlight_foreground: Optional[Color]
    selection_foreground: Optional[Color]
    selection_border: Optional[Color]
    inactive_selection: Optional[Color]
    inactive_selection_foreground: Optional[Color]
    guide: Optional[Color]
    active_guide: Optional[Color]
    stack_guide: Optional[Color]
    shadow: Optional[Color]


@dataclass
class ThemeItem:
    """A single scope rule in a theme."""
    scope: str
    foreground: Optional[Color]
    background: Optional[Color]
    font_style: int
    style_modifier: StyleModifier
    style: StyleModifier


@dataclass
class Theme:
    """A color theme for syntax highlighting."""
    key: str
    name: str
    author: str
    settings: ThemeSettings
    scopes: List[ThemeItem]


@dataclass
class ThemeSet:
    """Collection of themes."""
    
    @staticmethod
    def load_defaults() -> "ThemeSet":
        """Load default themes from built-in themes."""
        ...
    
    def add_from_folder(self, path: str) -> List[str]:
        """Load themes from folder. Returns warnings."""
        ...
    
    @staticmethod
    def builder() -> "ThemeSet":
        """Create empty theme set builder."""
        ...
    
    def get_theme(self, key: str) -> Optional[Theme]:
        """Get theme by key."""
        ...
    
    def theme_names(self) -> List[str]:
        """Return all theme names."""
        ...
    
    @staticmethod
    def from_dump(path: str) -> "ThemeSet":
        """Load theme set from .themedump file."""
        ...
    
    def to_dump(self, path: str) -> None:
        """Save theme set to .themedump file."""
        ...


@dataclass
class UnderlineOption:
    """Underline style for brackets/tags."""
    @staticmethod
    def none_() -> Optional["UnderlineOption"]: ...
    @staticmethod
    def underline() -> Optional["UnderlineOption"]: ...
    @staticmethod
    def stippled_underline() -> Optional["UnderlineOption"]: ...
    @staticmethod
    def squiggly_underline() -> Optional["UnderlineOption"]: ...


# ============================================================================
# Highlighting Engine
# ============================================================================

@dataclass
class Highlighter:
    """Syntax highlighter for a specific syntax/theme combination."""
    
    def __init__(self, syntax_ref: SyntaxReference, theme: Theme): ...
    
    def highlight_line(self, line: str, syntax_set: SyntaxSet, theme_set: ThemeSet) -> List[Tuple[Style, str]]:
        """Highlight a single line. Returns [(Style, text), ...]."""
        ...
    
    def highlight_lines(self, code: str, syntax_set: SyntaxSet, theme_set: ThemeSet) -> List[List[Tuple[Style, str]]]:
        """Highlight all lines. Returns [[(Style, text), ...], ...]."""
        ...
    
    def highlight_file(self, path: str, syntax_set: SyntaxSet, theme_set: ThemeSet) -> List[List[Tuple[Style, str]]]:
        """Highlight file by path. Auto-detects syntax from extension."""
        ...
    
    def save_state(self, syntax_set: SyntaxSet, theme_set: ThemeSet) -> "HighlightState":
        """Save highlighting state for incremental highlighting."""
        ...
    
    @staticmethod
    def from_state(state: "HighlightState", theme: Theme) -> "Highlighter":
        """Create highlighter from saved state."""
        ...


@dataclass
class HighlightState:
    """State for incremental highlighting."""
    path_scope_stack: List["Scope"]
    styles_stack: List[Style]
    
    @property
    def path_scope_string(self) -> str: ...
    @property
    def styles_count(self) -> int: ...


@dataclass
class HighlightLines:
    """Stateful highlighter maintaining parse state across lines."""
    
    def __init__(self, syntax_ref: SyntaxReference, syntax_set: SyntaxSet, 
                 theme_set: ThemeSet, theme_name: str): ...
    
    def highlight_line(self, line: str, syntax_set: SyntaxSet) -> List[Tuple[Style, str]]:
        """Highlight a single line. Returns [(Style, text), ...]."""
        ...


@dataclass
class HighlightResult:
    """Result of highlighting a string."""
    tokens: List[Tuple[Style, str]]
    html: str
    terminal_escaped: str
    
    def as_html(self, include_bg: str = "if_different", 
                default_bg: Optional[Color] = None) -> str:
        """Convert tokens to HTML string."""
        ...
    
    def as_terminal_escaped(self, include_bg: bool = False) -> str:
        """Convert tokens to terminal escape string."""
        ...
    
    def as_latex_escaped(self) -> str:
        """Convert tokens to LaTeX \\textcolor output."""
        ...


# ============================================================================
# Advanced Highlighting Types
# ============================================================================

@dataclass
class ScoredStyle:
    """Style with match scores for debugging."""
    foreground_r: int
    foreground_g: int
    foreground_b: int
    foreground_a: int
    foreground_score: float
    background_r: int
    background_g: int
    background_b: int
    background_a: int
    background_score: float
    font_style: int
    font_style_score: float


@dataclass
class ScopeRangeIterator:
    """Iterator yielding (start, end, scope) for a line."""
    
    def __init__(self, ops: List[Tuple[int, str]], line: str): ...
    def __iter__(self) -> "ScopeRangeIterator": ...
    def __next__(self) -> Tuple[int, int, str]: ...


# ============================================================================
# Parsing
# ============================================================================

@dataclass
class Scope:
    """A scope representing semantic classification."""
    
    @staticmethod
    def from_string(s: str) -> "Scope":
        """Create scope from string (e.g., 'source.rust')."""
        ...
    
    def to_string(self) -> str: ...
    def len(self) -> int: ...
    def is_empty(self) -> bool: ...
    def is_prefix_of(self, other: "Scope") -> bool: ...


@dataclass
class ScopeStack:
    """Stack of scopes for parsing state."""
    
    @staticmethod
    def from_string(s: str) -> "ScopeStack":
        """Create stack from space-separated scopes."""
        ...
    
    def push(self, scope: Scope) -> None: ...
    def pop(self) -> None: ...
    def apply(self, op: "ScopeStackOp") -> None: ...
    def as_string(self) -> str: ...
    def len(self) -> int: ...
    def is_empty(self) -> bool: ...


@dataclass
class ScopeStackOp:
    """Operation on scope stack."""
    
    @staticmethod
    def push(scope: Scope) -> "ScopeStackOp": ...
    @staticmethod
    def pop(count: int) -> "ScopeStackOp": ...
    @staticmethod
    def clear_all() -> "ScopeStackOp": ...
    @staticmethod
    def clear_top(n: int) -> "ScopeStackOp": ...
    @staticmethod
    def restore() -> "ScopeStackOp": ...
    @staticmethod
    def noop() -> "ScopeStackOp": ...


@dataclass
class ParseState:
    """Stateful parser for incremental syntax parsing."""
    
    def __init__(self, syntax_name: str, syntax_set: SyntaxSet): ...
    
    def parse_line(self, line: str, syntax_set: SyntaxSet) -> "ParseLineOutput":
        """Parse a line. State persists between calls."""
        ...
    
    def is_speculative(self) -> bool:
        """Check if parser is in speculative (backtracking) mode."""
        ...
    
    @property
    def syntax_name(self) -> str:
        """Get the syntax name."""
        ...


@dataclass
class ParseLineOutput:
    """Output from parsing a line."""
    ops: List[Tuple[int, str]]
    replayed: List[List[Tuple[int, str]]]
    warnings: List[str]
    
    def get_scope_stack_op(self, index: int) -> "ScopeStackOp": ...
    def get_op_type(self, index: int) -> str: ...
    def get_replayed_scope_stack_op(self, line: int, op: int) -> "ScopeStackOp": ...


# ============================================================================
# Match Power / Clear Amount / Context IDs
# ============================================================================

@dataclass
class MatchPower:
    """Scope matching score."""
    
    def __init__(self, value: float): ...
    @property
    def value(self) -> float: ...


@dataclass
class ClearAmount:
    """Clear operation parameter."""
    
    @staticmethod
    def all_() -> "ClearAmount": ...
    @staticmethod
    def top_n(n: int) -> "ClearAmount": ...
    
    @property
    def kind(self) -> str: ...
    @property
    def value(self) -> int: ...


@dataclass
class ContextId:
    """Context identifier."""
    
    def __init__(self, syntax_index: int, context_index: int): ...
    @property
    def syntax_index(self) -> int: ...
    @property
    def context_index(self) -> int: ...


# ============================================================================
# Output Utilities
# ============================================================================

@dataclass
class ClassStyle:
    """CSS class style for HTML output."""
    
    @staticmethod
    def spaced() -> "ClassStyle": ...
    @staticmethod
    def spaced_prefixed(prefix: str) -> "ClassStyle": ...
    @staticmethod
    def class_attribute() -> "ClassStyle": ...


@dataclass
class IncludeBg:
    """Include background color policy."""
    
    @staticmethod
    def no() -> "IncludeBg": ...
    @staticmethod
    def yes() -> "IncludeBg": ...
    @staticmethod
    def if_different() -> "IncludeBg": ...


@dataclass
class ClassedHTMLGenerator:
    """Generator for class-based HTML output."""
    
    def __init__(self, syntax_ref: SyntaxReference, syntax_set: SyntaxSet,
                 class_style: ClassStyle): ...
    
    def parse_html_for_line_which_includes_newline(self, line: str) -> None: ...
    def parse_html_for_line(self, line: str) -> None: ...
    def finalize(self) -> str: ...


def as_terminal_escaped(tokens: List[Tuple[Style, str]], 
                        include_bg: bool) -> str:
    """Convert tokens to 24-bit terminal escape string."""
    ...


def as_html(tokens: List[Tuple[Style, str]], include_bg: str,
            default_bg: Optional[Color] = None) -> str:
    """Convert tokens to HTML with inline styles."""
    ...


def as_latex_escaped(tokens: List[Tuple[Style, str]]) -> str:
    """Convert tokens to LaTeX \\textcolor output."""
    ...


def css_for_theme(theme: Theme, class_style: str) -> str:
    """Generate CSS for a theme."""
    ...


def css_for_theme_class(theme: Theme, class_style: ClassStyle) -> str:
    """Generate CSS for a theme using ClassStyle object."""
    ...


def generate_css(theme: Theme, class_style: str) -> str:
    """Alias for css_for_theme."""
    ...


def tokens_to_classed_spans(tokens: List[Tuple[Style, str]],
                            class_style: ClassStyle) -> str:
    """Convert tokens to class-based HTML spans."""
    ...


def line_tokens_to_classed_spans_py(line: str, ops: List[Tuple[int, str]],
                                     class_style: ClassStyle) -> Tuple[str, int]:
    """Convert line and ops to classed spans. Returns (html, span_delta)."""
    ...


def styled_line_to_highlighted_html(tokens: List[Tuple[Style, str]],
                                     include_bg: str) -> str:
    """Convert styled tokens to inline HTML."""
    ...


def highlighted_html_for_string_py(code: str, syntax_ref: SyntaxReference,
                                    theme: Theme, syntax_set: SyntaxSet,
                                    theme_set: ThemeSet,
                                    include_bg: str = "if_different",
                                    start_line: int = 1) -> str:
    """Generate full highlighted HTML for a string."""
    ...


def create_html_file(code: str, syntax_ref: SyntaxReference,
                     theme: Theme, syntax_set: SyntaxSet,
                     theme_set: ThemeSet) -> str:
    """Alias for highlighted_html_for_string_py."""
    ...


def highlighted_html_at_line_and_column_number(
    code: str, syntax_ref: SyntaxReference, theme: Theme,
    syntax_set: SyntaxSet, theme_set: ThemeSet,
    start_line: int = 1) -> str:
    """Generate HTML with line numbers."""
    ...


# ============================================================================
# Utility Functions
# ============================================================================

def split_at(tokens: List[Tuple[Style, str]], position: int) -> \
        Tuple[List[Tuple[Style, str]], List[Tuple[Style, str]]]:
    """Split tokens at character position. Position is in chars, not bytes."""
    ...


def modify_range(tokens: List[Tuple[Style, str]], range_start: int,
                 range_end: int, new_style: Style) -> List[Tuple[Style, str]]:
    """Replace style in character range. Range is in chars, not bytes."""
    ...


def lines_with_endings(content: str) -> "LinesWithEndings":
    """Create iterator yielding (line, ending) tuples."""
    ...


@dataclass
class LinesWithEndings:
    """Iterator yielding (line, ending) tuples from a string."""
    
    def __iter__(self) -> "LinesWithEndings": ...
    def __next__(self) -> Tuple[str, str]: ...


# ============================================================================
# Dump Utilities
# ============================================================================

def dump_syntax_set(ss: SyntaxSet, path: str) -> None:
    """Save syntax set to .packdump file."""
    ...


def load_syntax_set(path: str) -> SyntaxSet:
    """Load syntax set from .packdump file."""
    ...


def dump_theme_set(ts: ThemeSet, path: str) -> None:
    """Save theme set to .themedump file."""
    ...


def load_theme_set(path: str) -> ThemeSet:
    """Load theme set from .themedump file."""
    ...


# ============================================================================
# Metadata (tmPreferences)
# ============================================================================

@dataclass
class MetadataItem:
    """Items from .tmPreferences file."""
    increase_indent_pattern: Optional[str]
    decrease_indent_pattern: Optional[str]
    bracket_indent_next_line_pattern: Optional[str]
    disable_indent_next_line_pattern: Optional[str]
    unindented_line_pattern: Optional[str]
    indent_parens: Optional[bool]
    shell_variables: List[Tuple[str, str]]
    line_comment: Optional[str]
    block_comment: Optional[Tuple[str, str]]


@dataclass
class MetadataSet:
    """Metadata for a scope selector."""
    selector_string: str
    items: MetadataItem


@dataclass
class Metadata:
    """Collection of metadata sets."""
    sets: List[MetadataSet]
    
    def __len__(self) -> int: ...


# ============================================================================
# High-level Convenience
# ============================================================================

def highlight_string(code: str, syntax_name: str, theme_name: str,
                     syntax_set: SyntaxSet, theme_set: ThemeSet) -> HighlightResult:
    """High-level highlight function. Returns HighlightResult with tokens, HTML, terminal."""
    ...


# ============================================================================
# Error Types
# ============================================================================

class LoadingError(Exception): ...
class ParsingError(Exception): ...
class ParseSyntaxError(Exception): ...
class DumpError(Exception): ...
