"""Performance comparison: syntect-py vs fastpylight vs Pygments.

Usage:
    python benchmark_comparison.py                     # Run all comparisons
    python benchmark_comparison.py --iterations 1000   # Custom iteration count
"""
import timeit
import syntect

try:
    from fastpylight import highlight as fastpylight_highlight
    from fastpylight import highlight_spans as fastpylight_spans
    HAS_FASTPYLIGHT = True
except ImportError:
    HAS_FASTPYLIGHT = False

try:
    from pygments import highlight as pygments_highlight
    from pygments.lexers import get_lexer_by_name, find_lexer_class_for_filename
    from pygments.formatters import get_formatter_by_name
    HAS_PYGRAMENTS = True
except ImportError:
    HAS_PYGRAMENTS = False


# ── Rust code benchmarks ──────────────────────────────────────────────────

RUST_SMALL = 'fn main() {\n    let x = 42;\n    println!("Hello, world!");\n}'
RUST_MEDIUM = '''use std::collections::HashMap;

fn main() {
    let mut map: HashMap<String, Vec<i32>> = HashMap::new();
    for i in 0..100 {
        let key = format!("key_{}", i % 10);
        if !map.contains_key(&key) {
            map.insert(key, Vec::new());
        }
        map[key].push(i);
    }
    for (key, values) in map {
        println!("{}: {} items, sum={}", key, values.len(), values.iter().sum::<i32>());
    }
}

struct Calculator {
    history: Vec<String>,
}

impl Calculator {
    fn new() -> Self {
        Calculator { history: Vec::new() }
    }
    
    fn add(&mut self, a: i32, b: i32) -> i32 {
        let result = a + b;
        self.history.push(format!("{} + {} = {}", a, b, result));
        result
    }
    
    fn multiply(&mut self, a: i32, b: i32) -> i32 {
        let result = a * b;
        self.history.push(format!("{} * {} = {}", a, b, result));
        result
    }
}'''


def bench_syntect_rust_highlight_string(iterations=100):
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    code = RUST_SMALL
    setup = f"""
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(RUST_SMALL)}
"""
    stmt = 'syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_rust_highlight(iterations=100):
    if not HAS_FASTPYLIGHT:
        return None
    setup = f"""
from fastpylight import highlight
code = {repr(RUST_SMALL)}
"""
    stmt = 'highlight(code, "rust")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_rust_spans(iterations=100):
    if not HAS_FASTPYLIGHT:
        return None
    setup = f"""
from fastpylight import highlight_spans
code = {repr(RUST_SMALL)}
"""
    stmt = 'highlight_spans(code, "rust", "hl-")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_rust_highlight_string(iterations=100):
    if not HAS_PYGRAMENTS:
        return None
    setup = f"""
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
code = {repr(RUST_SMALL)}
lexer = get_lexer_by_name('rust')
formatter = get_formatter_by_name('html')
"""
    stmt = 'highlight(code, lexer, formatter)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_syntect_rust_highlight_line(iterations=100):
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    line = "    let x = 42;"
    setup = f"""
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)
line = {repr(line)}
"""
    stmt = 'hl.highlight_line(line, ss, ts)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_rust_line(iterations=100):
    if not HAS_FASTPYLIGHT:
        return None
    line = "    let x = 42;"
    setup = f"""
from fastpylight import highlight
line = {repr(line)}
"""
    stmt = 'highlight(line, "rust")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_rust_highlight_line(iterations=100):
    if not HAS_PYGRAMENTS:
        return None
    line = "    let x = 42;"
    setup = f"""
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
line = {repr(line)}
lexer = get_lexer_by_name('rust')
formatter = get_formatter_by_name('html')
"""
    stmt = 'highlight(line, lexer, formatter)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── Python code benchmarks ────────────────────────────────────────────────

PYTHON_MEDIUM = '''def compute_primes(limit):
    """Sieve of Eratosthenes for finding prime numbers."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_prime in enumerate(sieve) if is_prime]


class DataProcessor:
    """Process and analyze data streams."""
    
    def __init__(self, buffer_size=1024):
        self.buffer_size = buffer_size
        self.data = []
        self.stats = {}
    
    def add_batch(self, batch):
        """Add a batch of data points."""
        self.data.extend(batch)
        if len(self.data) > self.buffer_size * 10:
            self.data = self.data[-self.buffer_size * 5:]
        self._update_stats()
    
    def _update_stats(self):
        if not self.data:
            return
        self.stats = {
            "count": len(self.data),
            "mean": sum(self.data) / len(self.data),
            "min": min(self.data),
            "max": max(self.data),
        }
    
    def export(self, fmt="csv"):
        """Export data in the specified format."""
        if fmt == "csv":
            return "\\n".join(str(v) for v in self.data)
        elif fmt == "json":
            import json
            return json.dumps({"data": self.data, "stats": self.stats})
        return str(self.data)


if __name__ == "__main__":
    processor = DataProcessor()
    primes = compute_primes(1000)
    processor.add_batch(primes[:100])
    print(processor.export("json"))'''


def bench_syntect_python_highlight_string(iterations=10):
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    code = PYTHON_MEDIUM
    setup = f"""
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(PYTHON_MEDIUM)}
"""
    stmt = 'syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_python_highlight(iterations=10):
    if not HAS_FASTPYLIGHT:
        return None
    setup = f"""
from fastpylight import highlight
code = {repr(PYTHON_MEDIUM)}
"""
    stmt = 'highlight(code, "python")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_python_spans(iterations=10):
    if not HAS_FASTPYLIGHT:
        return None
    setup = f"""
from fastpylight import highlight_spans
code = {repr(PYTHON_MEDIUM)}
"""
    stmt = 'highlight_spans(code, "python", "hl-")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_python_highlight_string(iterations=10):
    if not HAS_PYGRAMENTS:
        return None
    setup = f"""
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
code = {repr(PYTHON_MEDIUM)}
lexer = get_lexer_by_name('python')
formatter = get_formatter_by_name('html')
"""
    stmt = 'highlight(code, lexer, formatter)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── Lexer detection benchmarks ────────────────────────────────────────────

def bench_syntect_detection(iterations=1000):
    ss = syntect.SyntaxSet.load_defaults(False)
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
"""
    stmt = 'ss.find_syntax_by_extension("rs")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_lexer_detection(iterations=1000):
    if not HAS_PYGRAMENTS:
        return None
    setup = """
from pygments.lexers import find_lexer_class_for_filename
"""
    stmt = 'find_lexer_class_for_filename("main.rs")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── CSS Generation ────────────────────────────────────────────────────────

def bench_syntect_css(iterations=100):
    ts = syntect.ThemeSet.load_defaults()
    theme = ts.get_theme("base16-ocean.dark")
    setup = """
import syntect
ts = syntect.ThemeSet.load_defaults()
theme = ts.get_theme("base16-ocean.dark")
"""
    stmt = 'syntect.css_for_theme(theme, "spaced")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_css(iterations=100):
    if not HAS_FASTPYLIGHT:
        return None
    setup = """
from fastpylight import theme_css
"""
    stmt = 'theme_css("github_light")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── Comparison runner ─────────────────────────────────────────────────────

def run_comparison(name, iterations, **benchmarks):
    """Run a comparison benchmark and print results."""
    print(f"\n--- {name} ---")
    
    results = {}
    for lib_name, (fn, enabled) in benchmarks.items():
        if not enabled:
            print(f"  {lib_name:25s} SKIPPED")
            continue
        t = timeit.timeit(
            f"{fn.__name__}({iterations})",
            globals=globals(),
            number=1
        )
        results[lib_name] = t
        print(f"  {lib_name:25s} {t:8.3f}ms")
    
    return results


def run_all_comparisons(iterations=100):
    """Run all comparison benchmarks."""
    print("\n" + "=" * 70)
    print("  syntect-py vs fastpylight vs Pygments — Performance Comparison")
    print("=" * 70)
    print("\n  syntect-py:    Rust (Syntect, regex-fancy, Sublime Text grammars)")
    print("  fastpylight:   Rust (Tree-sitter, Lumis)")
    print("  Pygments:      Python (re module)")
    print("\n  Lower is better (fewer milliseconds per operation)")
    print("=" * 70)
    
    all_results = {}
    
    # Rust small
    rust_iter = max(10, iterations // 5)
    all_results["Rust highlight_string"] = run_comparison(
        "Rust highlight_string", rust_iter,
        **{
            "syntect-py": (bench_syntect_rust_highlight_string, True),
            "fastpylight (toks)": (bench_fastpylight_rust_highlight, HAS_FASTPYLIGHT),
            "fastpylight (spans)": (bench_fastpylight_rust_spans, HAS_FASTPYLIGHT),
            "Pygments": (bench_pygments_rust_highlight_string, HAS_PYGRAMENTS),
        }
    )
    
    # Rust highlight_line
    all_results["Rust highlight_line"] = run_comparison(
        "Rust highlight_line", rust_iter,
        **{
            "syntect-py": (bench_syntect_rust_highlight_line, True),
            "fastpylight": (bench_fastpylight_rust_line, HAS_FASTPYLIGHT),
            "Pygments": (bench_pygments_rust_highlight_line, HAS_PYGRAMENTS),
        }
    )
    
    # Python highlight_string
    py_iter = max(5, iterations // 20)
    all_results["Python highlight_string"] = run_comparison(
        "Python highlight_string", py_iter,
        **{
            "syntect-py": (bench_syntect_python_highlight_string, True),
            "fastpylight (toks)": (bench_fastpylight_python_highlight, HAS_FASTPYLIGHT),
            "fastpylight (spans)": (bench_fastpylight_python_spans, HAS_FASTPYLIGHT),
            "Pygments": (bench_pygments_python_highlight_string, HAS_PYGRAMENTS),
        }
    )
    
    # Lexer detection
    det_iter = max(500, iterations * 5)
    all_results["Lexer detection (.rs)"] = run_comparison(
        "Lexer detection (.rs)", det_iter,
        **{
            "syntect-py (by ext)": (bench_syntect_detection, True),
            "Pygments": (bench_pygments_lexer_detection, HAS_PYGRAMENTS),
        }
    )
    
    # CSS Generation
    css_iter = max(10, iterations // 5)
    all_results["CSS Generation"] = run_comparison(
        "CSS Generation", css_iter,
        **{
            "syntect-py": (bench_syntect_css, True),
            "fastpylight": (bench_fastpylight_css, HAS_FASTPYLIGHT),
        }
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("  Summary (fastest syntect time first)")
    print("=" * 70)
    
    for cat_name, cat_results in all_results.items():
        print(f"\n  {cat_name}:")
        min_t = min(v for v in cat_results.values() if v is not None)
        for lib_name, t in sorted(cat_results.items(), key=lambda x: x[1] if x[1] is not None else float('inf')):
            if t is None:
                continue
            relative = t / min_t if min_t > 0 else float('inf')
            bar = "#" * int(relative * 2)
            print(f"    {lib_name:30s} {t:8.3f}ms  ({relative:5.1f}x)  {bar}")
    
    print(f"\n{'=' * 70}\n")
    
    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare syntect-py vs fastpylight vs Pygments")
    parser.add_argument("--iterations", type=int, default=100, help="Base iteration count")
    args = parser.parse_args()
    run_all_comparisons(args.iterations)
