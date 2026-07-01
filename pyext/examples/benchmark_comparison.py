"""Performance comparison: syntect-py vs Pygments.

Usage:
    python benchmark_comparison.py                    # Run all benchmarks
    python benchmark_comparison.py --iterations 1000  # Custom iteration count
"""
import timeit
import syntect
from pygments import highlight as pygments_highlight
from pygments.lexers import get_lexer_by_name, find_lexer_class_for_filename
from pygments.formatters import get_formatter_by_name


# --- Rust code benchmarks ---

def bench_syntect_rust_highlight_string(iterations=100):
    """syntect-py: highlight_string with Rust code."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    code = 'fn main() {\n    let x = 42;\n    println!("Hello, world!");\n}'
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = 'fn main() {\\n    let x = 42;\\n    println!("Hello, world!");\\n}'
"""
    stmt = """
syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_rust_highlight_string(iterations=100):
    """Pygments: highlight with Rust code."""
    code = 'fn main() {\n    let x = 42;\n    println!("Hello, world!");\n}'
    
    setup = """
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
code = 'fn main() {\\n    let x = 42;\\n    println!("Hello, world!");\\n}'
lexer = get_lexer_by_name('rust')
formatter = get_formatter_by_name('html')
"""
    stmt = """
highlight(code, lexer, formatter)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_syntect_rust_highlight_line(iterations=100):
    """syntect-py: highlight_line with Rust code."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    line = "    let x = 42;"
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)
line = "    let x = 42;"
"""
    stmt = """
hl.highlight_line(line, ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_rust_highlight_line(iterations=100):
    """Pygments: lex + format a single line with Rust code."""
    line = "    let x = 42;"
    
    setup = """
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
line = "    let x = 42;"
lexer = get_lexer_by_name('rust')
formatter = get_formatter_by_name('html')
"""
    stmt = """
highlight(line, lexer, formatter)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- Python code benchmarks ---

def bench_syntect_python_highlight_string(iterations=10):
    """syntect-py: highlight_string with Python code."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    code = '''def main():
    """Main entry point."""
    items = [1, 2, 3, 4, 5]
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
        else:
            result.append(item * 3)
    return result

class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

if __name__ == "__main__":
    calc = Calculator()
    calc.add(10, 20)
    calc.multiply(5, 6)
    print(calc.history)
'''
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = '''def main():
    items = [1, 2, 3, 4, 5]
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
        else:
            result.append(item * 3)
    return result

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    calc = Calculator()
    calc.add(10, 20)
    calc.multiply(5, 6)'''
"""
    stmt = """
syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_python_highlight_string(iterations=10):
    """Pygments: highlight with Python code."""
    code = '''def main():
    """Main entry point."""
    items = [1, 2, 3, 4, 5]
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
        else:
            result.append(item * 3)
    return result

class Calculator:
    """Simple calculator class."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

if __name__ == "__main__":
    calc = Calculator()
    calc.add(10, 20)
    calc.multiply(5, 6)
    print(calc.history)
'''
    
    setup = """
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
code = '''def main():
    items = [1, 2, 3, 4, 5]
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
        else:
            result.append(item * 3)
    return result

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    calc = Calculator()
    calc.add(10, 20)
    calc.multiply(5, 6)'''
lexer = get_lexer_by_name('python')
formatter = get_formatter_by_name('html')
"""
    stmt = """
highlight(code, lexer, formatter)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- Lexer detection benchmarks ---

def bench_syntect_syntax_detection(iterations=1000):
    """syntect-py: find_syntax_by_extension."""
    ss = syntect.SyntaxSet.load_defaults(False)
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
"""
    stmt = """
ss.find_syntax_by_extension("rs")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_lexer_detection(iterations=1000):
    """Pygments: find_lexer_class_for_filename."""
    setup = """
from pygments.lexers import find_lexer_class_for_filename
"""
    stmt = """
find_lexer_class_for_filename("main.rs")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- CSS Generation (syntect only) ---

def bench_syntect_css(iterations=100):
    """syntect-py: css_for_theme."""
    ts = syntect.ThemeSet.load_defaults()
    theme = ts.get_theme("base16-ocean.dark")
    
    setup = """
import syntect
ts = syntect.ThemeSet.load_defaults()
theme = ts.get_theme("base16-ocean.dark")
"""
    stmt = """
syntect.css_for_theme(theme, "spaced")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def run_comparison(name, iterations=100, syntect_fn=None, pygments_fn=None):
    """Run a comparison benchmark and print results."""
    print(f"\n--- {name} ---")
    
    if syntect_fn is None:
        syntect_fn = f"bench_syntect_{name.lower().replace(' ', '_').replace('-', '_')}"
    if pygments_fn is None:
        pygments_fn = f"bench_pygments_{name.lower().replace(' ', '_').replace('-', '_')}"
    
    # syntect
    t1 = timeit.timeit(
        f"{syntect_fn}({iterations})",
        globals=globals(),
        number=1
    )
    
    # pygments
    t2 = timeit.timeit(
        f"{pygments_fn}({iterations})",
        globals=globals(),
        number=1
    )
    
    speedup = t2 / t1 if t1 > 0 else float('inf')
    
    print(f"  syntect-py:    {t1:8.3f}ms")
    print(f"  Pygments:      {t2:8.3f}ms")
    print(f"  syntect is     {speedup:6.1f}x faster")
    
    return {"syntect": t1, "pygments": t2, "speedup": speedup}


def run_all_comparisons(iterations=100):
    """Run all comparison benchmarks."""
    print("\n" + "=" * 70)
    print("  syntect-py vs Pygments — Performance Comparison")
    print("=" * 70)
    print("\n  Note: syntect-py uses Rust (regex-fancy, pure Rust regex engine)")
    print("        Pygments is pure Python (uses Python's re module)")
    print("\n  Lower is better (fewer milliseconds per operation)")
    print("=" * 70)
    
    results = {}
    
    # Rust code
    results["Rust highlight_string"] = run_comparison("Rust highlight_string", max(10, iterations // 5))
    results["Rust highlight_line"] = run_comparison("Rust highlight_line", max(10, iterations // 5))
    
    # Python code
    results["Python highlight_string"] = run_comparison("Python highlight_string", max(5, iterations // 20))
    
    # Lexer detection
    results["Lexer detection (.rs)"] = run_comparison(
        "Lexer detection",
        max(500, iterations * 5),
        syntect_fn="bench_syntect_syntax_detection",
        pygments_fn="bench_pygments_lexer_detection"
    )
    
    # CSS (syntect only)
    print(f"\n--- CSS Generation (syntect only) ---")
    t_css = timeit.timeit(
        "bench_syntect_css(100)",
        globals=globals(),
        number=1
    )
    print(f"  syntect-py:    {t_css:8.3f}ms")
    results["CSS Generation"] = {"syntect": t_css, "pygments": None, "speedup": None}
    
    # Summary
    print("\n" + "=" * 70)
    print("  Summary (fastest syntect time first)")
    print("=" * 70)
    
    syntect_times = {k: v["syntect"] for k, v in results.items() if v["pygments"] is not None}
    for name, time_ms in sorted(syntect_times.items(), key=lambda x: x[1]):
        pyg = results[name]["pygments"]
        speedup = results[name]["speedup"]
        bar = "#" * int(time_ms / max(0.01, min(syntect_times.values())))
        print(f"  {name:30s} {time_ms:8.3f}ms  Pygments:{pyg:8.3f}ms  {speedup:6.1f}x  {bar}")
    
    print(f"\n  Fastest syntect: {min(syntect_times, key=syntect_times.get)}")
    print(f"  Slowest syntect: {max(syntect_times, key=syntect_times.get)}")
    print("=" * 70 + "\n")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare syntect-py vs Pygments")
    parser.add_argument("--iterations", type=int, default=100, help="Base iteration count")
    args = parser.parse_args()
    
    run_all_comparisons(args.iterations)
