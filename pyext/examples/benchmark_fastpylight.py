"""Performance comparison: syntect-py vs fastpylight.

Usage:
    python benchmark_fastpylight.py                    # Run all benchmarks
    python benchmark_fastpylight.py --iterations 1000  # Custom iteration count
"""
import timeit
import syntect
import fastpylight


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


def bench_fastpylight_rust_highlight(iterations=100):
    """fastpylight: highlight with Rust code."""
    code = 'fn main() {\n    let x = 42;\n    println!("Hello, world!");\n}'
    
    setup = """
from fastpylight import highlight
code = 'fn main() {\\n    let x = 42;\\n    println!("Hello, world!");\\n}'
"""
    stmt = """
highlight(code, "rust")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_rust_highlight_spans(iterations=100):
    """fastpylight: highlight_spans with Rust code."""
    code = 'fn main() {\n    let x = 42;\n    println!("Hello, world!");\n}'
    
    setup = """
from fastpylight import highlight_spans
code = 'fn main() {\\n    let x = 42;\\n    println!("Hello, world!");\\n}'
"""
    stmt = """
highlight_spans(code, "rust", "hl-")
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


def bench_fastpylight_python_highlight(iterations=10):
    """fastpylight: highlight with Python code."""
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
from fastpylight import highlight
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
highlight(code, "python")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_python_highlight_spans(iterations=10):
    """fastpylight: highlight_spans with Python code."""
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
    
    setup = """
from fastpylight import highlight_spans
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
highlight_spans(code, "python", "hl-")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- Large code benchmarks ---

def bench_syntect_rust_large(iterations=10):
    """syntect-py: highlight_string with larger Rust code."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    code = '''use std::collections::HashMap;

fn main() {
    let mut map: HashMap<String, Vec<i32>> = HashMap::new();
    
    for i in 0..100 {
        let key = format!("key_{}", i % 10);
        if key not in map {
            map[key] = Vec::new();
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
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = '''use std::collections::HashMap;

fn main() {
    let mut map: HashMap<String, Vec<i32>> = HashMap::new();
    
    for i in 0..100 {
        let key = format!("key_{}", i % 10);
        if key not in map {
            map[key] = Vec::new();
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
"""
    stmt = """
syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_rust_large(iterations=10):
    """fastpylight: highlight with larger Rust code."""
    code = '''use std::collections::HashMap;

fn main() {
    let mut map: HashMap<String, Vec<i32>> = HashMap::new();
    
    for i in 0..100 {
        let key = format!("key_{}", i % 10);
        if key not in map {
            map[key] = Vec::new();
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
    
    setup = """
from fastpylight import highlight
code = '''use std::collections::HashMap;

fn main() {
    let mut map: HashMap<String, Vec<i32>> = HashMap::new();
    
    for i in 0..100 {
        let key = format!("key_{}", i % 10);
        if key not in map {
            map[key] = Vec::new();
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
"""
    stmt = """
highlight(code, "rust")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- CSS Generation ---

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


def bench_fastpylight_css(iterations=100):
    """fastpylight: theme_css."""
    setup = """
from fastpylight import theme_css
"""
    stmt = """
theme_css("github_light")
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- Language Detection ---

def bench_syntect_detection(iterations=1000):
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


def bench_fastpylight_languages(iterations=1000):
    """fastpylight: enumerate available languages."""
    setup = """
from fastpylight import languages
"""
    stmt = """
languages()
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# --- Multi-language benchmark ---

def bench_multi_language_syntect(iterations=5):
    """syntect-py: highlight across multiple languages."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    
    snippets = {
        "Rust": 'fn main() { let x = 42; }',
        "Python": 'def main(): x = 42',
        "JavaScript": 'function main() { let x = 42; }',
        "C": 'int main() { int x = 42; }',
        "C++": 'int main() { int x = 42; }',
        "Java": 'class Main { public static void main(String[] args) { int x = 42; } }',
        "TypeScript": 'function main() { const x: number = 42; }',
        "HTML": '<html><body><div>Hello</div></body></html>',
        "CSS": '.class { color: red; }',
        "YAML": 'key: value\nlist:\n  - item1\n  - item2',
    }
    
    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
snippets = {
    "Rust": 'fn main() { let x = 42; }',
    "Python": 'def main(): x = 42',
    "JavaScript": 'function main() { let x = 42; }',
    "C": 'int main() { int x = 42; }',
    "C++": 'int main() { int x = 42; }',
    "Java": 'class Main { public static void main(String[] args) { int x = 42; } }',
    "TypeScript": 'function main() { const x: number = 42; }',
    "HTML": '<html><body><div>Hello</div></body></html>',
    "CSS": '.class { color: red; }',
    "YAML": 'key: value\\nlist:\\n  - item1\\n  - item2',
}
"""
    stmt = """
for lang, code in snippets.items():
    syntect.highlight_string(code, lang, "base16-ocean.dark", ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_multi_language_fastpylight(iterations=5):
    """fastpylight: highlight across multiple languages."""
    snippets = {
        "rust": 'fn main() { let x = 42; }',
        "python": 'def main(): x = 42',
        "javascript": 'function main() { let x = 42; }',
        "go": 'func main() { var x = 42; }',
        "c": 'int main() { int x = 42; }',
        "java": 'class Main { public static void main(String[] args) { int x = 42; } }',
        "typescript": 'function main() { const x: number = 42; }',
        "html": '<html><body><div>Hello</div></body></html>',
        "css": '.class { color: red; }',
        "yaml": 'key: value\nlist:\n  - item1\n  - item2',
    }
    
    setup = """
from fastpylight import highlight
snippets = {
    "rust": 'fn main() { let x = 42; }',
    "python": 'def main(): x = 42',
    "javascript": 'function main() { let x = 42; }',
    "go": 'func main() { var x = 42; }',
    "c": 'int main() { int x = 42; }',
    "java": 'class Main { public static void main(String[] args) { int x = 42; } }',
    "typescript": 'function main() { const x: number = 42; }',
    "html": '<html><body><div>Hello</div></body></html>',
    "css": '.class { color: red; }',
    "yaml": 'key: value\\nlist:\\n  - item1\\n  - item2',
}
"""
    stmt = """
for lang, code in snippets.items():
    highlight(code, lang)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def run_comparison(name, iterations=100, **benchmarks):
    """Run a comparison benchmark and print results."""
    print(f"\n--- {name} ---")
    
    results = {}
    total_time = 0
    
    for name, (fn, iters) in benchmarks.items():
        t = timeit.timeit(
            f"{fn.__name__}({iters})",
            globals=globals(),
            number=1
        )
        results[name] = t
        total_time += t
        print(f"  {name:25s} {t:8.3f}ms")
    
    # Normalize to per-operation if needed
    speedups = {}
    for name, t in results.items():
        if "syntect" in name.lower():
            base = t
        else:
            # Find the syntect baseline for this comparison
            syntect_name = [k for k in results if "syntect" in k.lower()]
            if syntect_name:
                speedups[name] = results[syntect_name[0]] / t if results[syntect_name[0]] > 0 else float('inf')
    
    return results


def run_all_benchmarks(iterations=100):
    """Run all benchmarks and print summary."""
    print("\n" + "=" * 70)
    print("  syntect-py vs fastpylight — Performance Comparison")
    print("=" * 70)
    print("\n  syntect-py: Rust (Syntect, regex-fancy, Sublime Text grammars)")
    print("  fastpylight: Rust (Tree-sitter, Lumis)")
    print("\n  Lower is better (fewer milliseconds per operation)")
    print("=" * 70)
    
    results = {}
    
    # Rust code
    rust_iter = max(10, iterations // 5)
    results["Rust highlight"] = run_comparison(
        "Rust highlight_string", rust_iter,
        **{
            "syntect-py": (bench_syntect_rust_highlight_string, rust_iter),
            "fastpylight (toks)": (bench_fastpylight_rust_highlight, rust_iter),
            "fastpylight (spans)": (bench_fastpylight_rust_highlight_spans, rust_iter),
        }
    )
    
    # Python code
    py_iter = max(5, iterations // 20)
    results["Python highlight"] = run_comparison(
        "Python highlight_string", py_iter,
        **{
            "syntect-py": (bench_syntect_python_highlight_string, py_iter),
            "fastpylight (toks)": (bench_fastpylight_python_highlight, py_iter),
            "fastpylight (spans)": (bench_fastpylight_python_highlight_spans, py_iter),
        }
    )
    
    # Large Rust code
    large_iter = max(5, iterations // 20)
    results["Rust large"] = run_comparison(
        "Rust large code", large_iter,
        **{
            "syntect-py": (bench_syntect_rust_large, large_iter),
            "fastpylight": (bench_fastpylight_rust_large, large_iter),
        }
    )
    
    # Multi-language
    multi_iter = max(3, iterations // 30)
    results["Multi-language"] = run_comparison(
        "Multi-language (10 langs)", multi_iter,
        **{
            "syntect-py": (bench_multi_language_syntect, multi_iter),
            "fastpylight": (bench_multi_language_fastpylight, multi_iter),
        }
    )
    
    # CSS Generation
    css_iter = max(10, iterations // 5)
    results["CSS Generation"] = run_comparison(
        "CSS Generation", css_iter,
        **{
            "syntect-py": (bench_syntect_css, css_iter),
            "fastpylight": (bench_fastpylight_css, css_iter),
        }
    )
    
    # Language detection
    det_iter = max(500, iterations * 5)
    results["Language detection"] = run_comparison(
        "Language detection", det_iter,
        **{
            "syntect-py (by ext)": (bench_syntect_detection, det_iter),
            "fastpylight (languages list)": (bench_fastpylight_languages, det_iter),
        }
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    
    for cat_name, cat_results in results.items():
        print(f"\n  {cat_name}:")
        times = {k: v for k, v in cat_results.items()}
        min_time = min(times.values())
        for name, t in sorted(times.items(), key=lambda x: x[1]):
            relative = t / min_time if min_time > 0 else float('inf')
            bar = "#" * int(relative * 2)
            print(f"    {name:30s} {t:8.3f}ms  ({relative:5.1f}x)  {bar}")
    
    print(f"\n{'=' * 70}\n")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare syntect-py vs fastpylight")
    parser.add_argument("--iterations", type=int, default=100, help="Base iteration count")
    args = parser.parse_args()
    
    run_all_benchmarks(args.iterations)
