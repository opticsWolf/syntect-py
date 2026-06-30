"""Benchmark: syntect-py vs pure Python highlighting"""
import time
import syntect

def benchmark(func, name, iterations=100):
    """Run a function multiple times and print timing results."""
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)
    
    avg = sum(times) / len(times)
    min_t = min(times)
    max_t = max(times)
    print(f"{name}:")
    print(f"  Average: {avg*1000:.2f}ms")
    print(f"  Min: {min_t*1000:.2f}ms")
    print(f"  Max: {max_t*1000:.2f}ms")
    print()

# Load syntax set and theme
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)

# Code to highlight
code = """
fn main() {
    let x = 42;
    let y = "Hello, World!";
    println!("x = {}, y = {}", x, y);
    
    if x > 0 {
        println!("x is positive");
    }
    
    for i in 0..10 {
        println!("Iteration {}", i);
    }
}
"""

lines = code.strip().split('\n')

print("=== Benchmarking syntect-py ===\n")

# Benchmark line highlighting
def highlight_lines():
    for line in lines:
        hl.highlight_line(line, ss, ts)

benchmark(highlight_lines, "Line Highlighting", iterations=50)

# Benchmark full string highlighting
def highlight_string():
    syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)

benchmark(highlight_string, "Full String Highlighting", iterations=20)

# Benchmark HTML output
def html_output():
    result = syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
    result.as_html("if_different")
    result.as_terminal_escaped(True)
    result.as_latex_escaped()

benchmark(html_output, "All Output Formats", iterations=10)

print("=== Benchmark Complete ===")
