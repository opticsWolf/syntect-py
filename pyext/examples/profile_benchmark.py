"""Profile where time is spent in syntect-py vs Pygments."""
import timeit
import syntect
import os
from pygments import highlight as pygments_highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Find a medium Python file
import pygments
pygments_dir = os.path.dirname(pygments.__file__)
path = None
for root, dirs, fnames in os.walk(pygments_dir):
    for f in fnames:
        if f.endswith('.py') and 'python.py' in f:
            path = os.path.join(root, f)
            break
    if path:
        break

with open(path) as f:
    code = f.read()
lines = code.count('\n') + 1
print(f"File: {os.path.basename(path)} ({lines} lines, {len(code)//1024} KB)")
print()

ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()

# 1. Lex ONE line (syntect)
t1 = timeit.timeit(
    'hl.highlight_line("def main(): pass", ss, ts)',
    setup='''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
hl = syntect.Highlighter(ss.find_syntax_by_name("Python"), ts.get_theme("base16-ocean.dark"))
''',
    number=1000
) / 1000 * 1000
print(f"1. Syntect: lex ONE line (highlight_line)   = {t1:.3f}ms")

# 2. HTML output from tokens (syntect, no lexing)
t2 = timeit.timeit(
    'syntect.as_html(tokens, "if_different", None)',
    setup='''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
hl = syntect.Highlighter(ss.find_syntax_by_name("Python"), ts.get_theme("base16-ocean.dark"))
tokens = hl.highlight_line("def main(): pass", ss, ts)
''',
    number=1000
) / 1000 * 1000
print(f"2. Syntect: HTML from tokens (no lex)       = {t2:.3f}ms")

# 3. Full highlight_string (syntect)
setup3 = f'''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(code)}
'''
stmt3 = 'syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)'
t3 = timeit.timeit(stmt3, setup3, number=5) / 5 * 1000
print(f"3. Syntect: highlight_string ({lines} lines) = {t3:.3f}ms ({t3/lines*1000:.4f}ms/100lines)")

# 4. Pygments highlight (lex + HTML)
setup4 = f'''
from pygments import highlight as highlight_fn
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
code = {repr(code)}
'''
stmt4 = 'highlight_fn(code, PythonLexer(), HtmlFormatter())'
t4 = timeit.timeit(stmt4, setup4, number=5) / 5 * 1000
print(f"4. Pygments: highlight ({lines} lines)      = {t4:.3f}ms ({t4/lines*1000:.4f}ms/100lines)")

# 5. Pygments JUST lexing (no format)
setup5 = f'''
from pygments.lexers import PythonLexer
code = {repr(code)}
'''
stmt5 = 'list(PythonLexer().get_tokens(code))'
t5 = timeit.timeit(stmt5, setup5, number=5) / 5 * 1000
print(f"5. Pygments: JUST lexing ({lines} lines)    = {t5:.3f}ms ({t5/lines*1000:.4f}ms/100lines)")

# 6. Pygments JUST formatting (pre-lexed tokens)
setup6 = f'''
from pygments import highlight as highlight_fn
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
code = {repr(code)}
tokens = list(PythonLexer().get_tokens(code))
'''
stmt6 = 'highlight_fn(code, PythonLexer(), HtmlFormatter())'
t6 = timeit.timeit(stmt6, setup6, number=5) / 5 * 1000
print(f"6. Pygments: JUST format (pre-lexed)        = {t6:.3f}ms")

print()
print("=" * 60)
print("BREAKDOWN")
print("=" * 60)
print(f"  Syntect lex per line:     {t1:.3f}ms")
print(f"  Syntect HTML per line:    {t2:.3f}ms  ({t2/t1*100:.1f}% of lex)")
print()
print(f"  Syntect per 100 lines:    {t3/lines*1000:.4f}ms")
print(f"  Pygments per 100 lines:   {t4/lines*1000:.4f}ms")
print(f"  Pygments lex only:        {t5/lines*1000:.4f}ms")
print(f"  Pygments format only:     {t6:.3f}ms")
print()
print(f"  Lexing ratio:             {t3/lines*1000 / (t5/lines*1000):.1f}x")
print(f"  Full ratio:               {t3/t4:.1f}x")
print()
print("  Syntect does 3x output (HTML+TERM+LaTeX)")
print("  Pygments does 1x output (HTML only)")
print(f"  If we remove TERM+LaTeX overhead: ~{t3 * 1/3:.1f}ms estimated")
print(f"  Estimated lex-only ratio:      ~{t3/3/t5:.1f}x")
