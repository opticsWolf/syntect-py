"""Performance benchmarks for syntect-py.

Usage:
    python benchmark.py                    # Run all benchmarks
    python benchmark.py --only highlight   # Run only highlight benchmarks
    python benchmark.py --iterations 1000  # Custom iteration count
"""
import timeit
import time
import syntect


def benchmark_highlight_string(iterations=100):
    """Benchmark highlight_string with Rust code."""
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
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  highlight_string({iterations} iterations):")
    print(f"    Min: {min_time:.3f}ms | Avg: {avg_time:.3f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_highlighter_line(iterations=100):
    """Benchmark Highlighter.highlight_line."""
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
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  Highlighter.highlight_line({iterations} iterations):")
    print(f"    Min: {min_time:.3f}ms | Avg: {avg_time:.3f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_highlight_lines(iterations=100):
    """Benchmark Highlighter.highlight_lines."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    code = 'fn main() {\n    let x = 42;\n    println!("Hello");\n}'
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)
code = 'fn main() {\\n    let x = 42;\\n    println!("Hello");\\n}'
"""
    stmt = """
hl.highlight_lines(code, ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  Highlighter.highlight_lines({iterations} iterations):")
    print(f"    Min: {min_time:.3f}ms | Avg: {avg_time:.3f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_as_html(iterations=1000):
    """Benchmark as_html function."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    tokens = hl.highlight_line("fn main() {", ss, ts)
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)
tokens = hl.highlight_line("fn main() {", ss, ts)
"""
    stmt = """
syntect.as_html(tokens, "if_different", None)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  as_html({iterations} iterations):")
    print(f"    Min: {min_time:.4f}ms | Avg: {avg_time:.4f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_as_terminal_escaped(iterations=1000):
    """Benchmark as_terminal_escaped function."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    tokens = hl.highlight_line("fn main() {", ss, ts)
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)
tokens = hl.highlight_line("fn main() {", ss, ts)
"""
    stmt = """
syntect.as_terminal_escaped(tokens, False)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  as_terminal_escaped({iterations} iterations):")
    print(f"    Min: {min_time:.4f}ms | Avg: {avg_time:.4f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_css_for_theme(iterations=100):
    """Benchmark css_for_theme function."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    theme = ts.get_theme("base16-ocean.dark")
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
theme = ts.get_theme("base16-ocean.dark")
"""
    stmt = """
syntect.css_for_theme(theme, "spaced")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  css_for_theme({iterations} iterations):")
    print(f"    Min: {min_time:.3f}ms | Avg: {avg_time:.3f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_css_for_theme_class(iterations=100):
    """Benchmark css_for_theme_class function."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    theme = ts.get_theme("base16-ocean.dark")
    class_style = syntect.ClassStyle.spaced_prefixed("syn-")
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
theme = ts.get_theme("base16-ocean.dark")
class_style = syntect.ClassStyle.spaced_prefixed("syn-")
"""
    stmt = """
syntect.css_for_theme_class(theme, class_style)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  css_for_theme_class({iterations} iterations):")
    print(f"    Min: {min_time:.3f}ms | Avg: {avg_time:.3f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def benchmark_highlight_string_large(iterations=10):
    """Benchmark highlight_string with larger code snippet."""
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
    min_time = min(times) / iterations * 1000
    avg_time = sum(times) / len(times) / iterations * 1000
    print(f"  highlight_string (Python, {iterations} iterations):")
    print(f"    Min: {min_time:.3f}ms | Avg: {avg_time:.3f}ms | Total: {sum(times)/iterations*1000:.1f}ms")
    return min_time


def run_all_benchmarks(iterations=100):
    """Run all benchmarks and print summary."""
    print("\n" + "=" * 60)
    print("  syntect-py Performance Benchmarks")
    print("=" * 60)
    
    results = {}
    
    print("\n--- Core Highlighting ---")
    results["highlight_string"] = benchmark_highlight_string(iterations)
    results["highlighter_line"] = benchmark_highlighter_line(iterations)
    results["highlight_lines"] = benchmark_highlight_lines(iterations)
    
    print("\n--- Output Generation ---")
    results["as_html"] = benchmark_as_html(iterations * 10)
    results["as_terminal"] = benchmark_as_terminal_escaped(iterations * 10)
    
    print("\n--- CSS Generation ---")
    results["css_for_theme"] = benchmark_css_for_theme(iterations)
    results["css_for_theme_class"] = benchmark_css_for_theme_class(iterations)
    
    print("\n--- Large Code ---")
    results["highlight_string_large"] = benchmark_highlight_string_large(max(1, iterations // 10))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Summary (fastest operation first)")
    print("=" * 60)
    for name, time_ms in sorted(results.items(), key=lambda x: x[1]):
        bar = "#" * int(time_ms / max(0.01, min(results.values())))
        print(f"  {name:30s} {time_ms:8.3f}ms  {bar}")
    
    print(f"\n  Fastest: {min(results, key=results.get)}")
    print(f"  Slowest: {max(results, key=results.get)}")
    print("=" * 60 + "\n")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark syntect-py")
    parser.add_argument("--iterations", type=int, default=100, help="Number of iterations per benchmark")
    parser.add_argument("--only", type=str, default=None, help="Run only specific benchmark (highlight, output, css, large)")
    args = parser.parse_args()
    
    if args.only == "highlight":
        print("\n--- Core Highlighting Benchmarks ---")
        benchmark_highlight_string(args.iterations)
        benchmark_highlighter_line(args.iterations)
        benchmark_highlight_lines(args.iterations)
    elif args.only == "output":
        print("\n--- Output Generation Benchmarks ---")
        benchmark_as_html(args.iterations * 10)
        benchmark_as_terminal_escaped(args.iterations * 10)
    elif args.only == "css":
        print("\n--- CSS Generation Benchmarks ---")
        benchmark_css_for_theme(args.iterations)
        benchmark_css_for_theme_class(args.iterations)
    elif args.only == "large":
        print("\n--- Large Code Benchmark ---")
        benchmark_highlight_string_large(max(1, args.iterations // 10))
    else:
        run_all_benchmarks(args.iterations)
