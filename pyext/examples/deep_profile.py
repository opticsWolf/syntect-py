"""Deep profiling: break down every component of syntect-py vs Pygments."""
import timeit
import syntect
import os
from pygments.lexers import PythonLexer
from pygments import highlight as pygments_highlight

# Find python.py
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

# ===== SYNECT COMPONENTS =====
print("=" * 70)
print("SYNECT COMPONENT BREAKDOWN")
print("=" * 70)

# 1. Split lines + lex (no token collection)
setup1 = f'''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
hl = syntect.Highlighter(ss.find_syntax_by_name("Python"), ts.get_theme("base16-ocean.dark"))
code = {repr(code)}
'''
t1 = timeit.timeit(
    'for (line, _) in syntect.lines_with_endings(code): hl.highlight_line(line, ss, ts)',
    setup=setup1,
    number=5
) / 5 * 1000
print(f"1. Split lines + lex (no token collection): {t1:8.3f}ms ({t1/lines*1000:8.4f}ms/100lines)")

# 2. Full highlight_string (lex + 3x output)
setup2 = f'''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(code)}
'''
t2 = timeit.timeit(
    'syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)',
    setup=setup2,
    number=5
) / 5 * 1000
print(f"2. Full highlight_string:                   {t2:8.3f}ms ({t2/lines*1000:8.4f}ms/100lines)")

# 3. Just output from tokens (no lex)
setup3 = '''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
hl = syntect.Highlighter(ss.find_syntax_by_name("Python"), ts.get_theme("base16-ocean.dark"))
tokens = hl.highlight_line("def main(): pass", ss, ts)
'''
t3 = timeit.timeit(
    '''
syntect.as_html(tokens, "if_different", None)
syntect.as_terminal_escaped(tokens, False)
syntect.as_latex_escaped(tokens)
''',
    setup=setup3,
    number=1000
) / 1000 * 1000
print(f"3. Output gen (3 formats, 1 line):          {t3:8.3f}ms")

# ===== PYGMENTS COMPONENTS =====
print()
print("=" * 70)
print("PYGMENTS COMPONENT BREAKDOWN")
print("=" * 70)

# 5. Pygments JUST lex
setup5 = f'''
from pygments.lexers import PythonLexer
code = {repr(code)}
'''
t5 = timeit.timeit(
    'list(PythonLexer().get_tokens(code))',
    setup=setup5,
    number=5
) / 5 * 1000
print(f"5. Pygments JUST lex:                       {t5:8.3f}ms ({t5/lines*1000:8.4f}ms/100lines)")

# 6. Pygments highlight (lex + format)
setup6 = f'''
from pygments import highlight as pygments_highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
code = {repr(code)}
'''
t6 = timeit.timeit(
    'pygments_highlight(code, PythonLexer(), HtmlFormatter())',
    setup=setup6,
    number=5
) / 5 * 1000
print(f"6. Pygments highlight (lex+format):         {t6:8.3f}ms ({t6/lines*1000:8.4f}ms/100lines)")

# 7. Pygments format only
setup7 = f'''
from pygments import highlight as pygments_highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
code = {repr(code)}
tokens = list(PythonLexer().get_tokens(code))
'''
t7 = timeit.timeit(
    'pygments_highlight(code, PythonLexer(), HtmlFormatter())',
    setup=setup7,
    number=5
) / 5 * 1000
print(f"7. Pygments JUST format:                    {t7:8.3f}ms ({t7/lines*1000:8.4f}ms/100lines)")

# ===== ANALYSIS =====
print()
print("=" * 70)
print("ANALYSIS")
print("=" * 70)
print()
print(f"  Syntect lex:     {t1/lines*1000:.4f}ms/100 lines")
print(f"  Pygments lex:    {t5/lines*1000:.4f}ms/100 lines")
print(f"  Lex ratio:       {t1/t5:.2f}x")
print()
print(f"  Syntect output:  {(t2-t1)/lines*1000:.4f}ms/100 lines")
print(f"  Pygments format: {t7/lines*1000:.4f}ms/100 lines")
print(f"  Output ratio:    {(t2-t1)/t7:.2f}x")
print()
print(f"  Syntect total:   {t2/lines*1000:.4f}ms/100 lines")
print(f"  Pygments total:  {t6/lines*1000:.4f}ms/100 lines")
print(f"  Total ratio:     {t2/t6:.2f}x")
print()
print(f"  Output overhead: {t2-t1:.1f}ms ({(t2-t1)/t2*100:.1f}% of total)")
print(f"  Syntect does 3x output (HTML+TERM+LaTeX)")
print(f"  Pygments does 1x output (HTML only)")

# ===== SCALING TEST =====
print()
print("=" * 70)
print("SCALING TEST (varying file sizes)")
print("=" * 70)

for chunk_pct in [10, 25, 50, 100]:
    chunk = code[:len(code)//100*chunk_pct]
    chunk_lines = chunk.count('\n') + 1
    
    t_s = timeit.timeit(
        'syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)',
        setup=f'''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(chunk)}
''',
        number=10
    ) / 10 * 1000
    
    t_p = timeit.timeit(
        'pygments_highlight(code, PythonLexer(), HtmlFormatter())',
        setup=f'''
from pygments import highlight as pygments_highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
code = {repr(chunk)}
''',
        number=10
    ) / 10 * 1000
    
    ratio = t_s / t_p if t_p > 0 else 0
    print(f"  {chunk_pct:3d}% ({chunk_lines:5d} lines): syntect={t_s:8.3f}ms  pygments={t_p:8.3f}ms  ratio={ratio:5.1f}x")
