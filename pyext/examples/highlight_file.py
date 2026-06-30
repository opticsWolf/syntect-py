"""Example: Highlight a file to terminal with colors."""
import syntect
import sys

# Load syntax set and theme set
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

# Get a theme
theme = ts.get_theme('base16-ocean.dark')

# Highlight a file
def highlight_file(filepath):
    """Highlight a file and print to terminal with ANSI colors."""
    # Get syntax from file extension
    syntax_ref = ss.find_syntax_for_file(filepath)
    if syntax_ref is None:
        print(f"Unknown syntax for {filepath}", file=sys.stderr)
        return
    
    # Create highlighter
    hl = syntect.Highlighter(syntax_ref, theme)
    
    # Read file
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Highlight all lines
    tokens = hl.highlight_file(filepath, ss, ts)
    
    # Print with terminal colors
    for line_tokens in tokens:
        escaped = syntect.as_terminal_escaped(line_tokens, True)
        print(escaped, end='')
        print()  # newline after each line

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        highlight_file(sys.argv[1])
    else:
        print("Usage: python highlight_file.py <filepath>")
