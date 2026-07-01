"""Comprehensive benchmark: syntect-py vs fastpylight vs Pygments.

Covers small snippets, large files, multi-language, and output formats.

Usage:
    python benchmark_comprehensive.py                    # Run all benchmarks
    python benchmark_comprehensive.py --iterations 200   # Custom iterations
    python benchmark_comprehensive.py --files            # Large-file mode
    python benchmark_comprehensive.py --profile          # Profile breakdown
"""
import timeit
import os
import sys
import syntect


# ── Sample code snippets ──────────────────────────────────────────────────

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

PYTHON_SMALL = 'def main():\n    x = 42\n    return x * 2'

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
        """Update running statistics."""
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

JAVASCRIPT_MEDIUM = '''class EventEmitter {
    constructor() {
        this.listeners = new Map();
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
        return () => this.off(event, callback);
    }

    off(event, callback) {
        const cbs = this.listeners.get(event);
        if (cbs) {
            const idx = cbs.indexOf(callback);
            if (idx !== -1) cbs.splice(idx, 1);
        }
    }

    emit(event, ...args) {
        const cbs = this.listeners.get(event);
        if (cbs) {
            for (const cb of cbs) {
                try {
                    cb(...args);
                } catch (e) {
                    console.error(`Event "${event}" handler error:`, e);
                }
            }
        }
    }
}

async function fetchData(url, retries = 3) {
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            if (attempt === retries - 1) throw err;
            await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
        }
    }
}

const emitter = new EventEmitter();
emitter.on('data', (data) => console.log('Received:', data));
fetchData('/api/data').then(data => emitter.emit('data', data));'''

GO_CODE = '''package main

import (
    "fmt"
    "sync"
)

type Cache struct {
    data    map[string, string]
    mutex   sync.RWLock
    maxSize int
}

func NewCache(maxSize int) *Cache {
    return &Cache{
        data:    make(map[string, string]),
        maxSize: maxSize,
    }
}

func (c *Cache) Get(key string) (string, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    val, found := c.data[key]
    return val, found
}

func (c *Cache) Set(key, value string) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    if len(c.data) >= c.maxSize {
        c.evict()
    }
    c.data[key] = value
}

func (c *Cache) evict() {
    for key := range c.data {
        delete(c.data, key)
        break
    }
}

func main() {
    cache := NewCache(1000)
    cache.Set("greeting", "Hello, World!")
    val, found := cache.Get("greeting")
    if found {
        fmt.Println(val)
    }
}'''

HTML_CODE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <style>
        body {
            font-family: system-ui, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            padding: 1rem;
        }
        .card {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .card h3 {
            color: #64b5f3;
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="grid">
        <div class="card">
            <h3>Active Users</h3>
            <p>1,234 concurrent</p>
        </div>
        <div class="card">
            <h3>API Latency</h3>
            <p>42ms p99</p>
        </div>
        <div class="card">
            <h3>Error Rate</h3>
            <p>0.02%</p>
        </div>
    </div>
</body>
</html>'''

YAML_CODE = '''version: "3.9"
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://cache:6379
    depends_on:
      - cache
      - db
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
          cpus: 1.0
        reservations:
          memory: 256M
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - pg-data:/var/lib/postgresql/data
    secrets:
      - db_password
volumes:
  redis-data:
  pg-data:
secrets:
  db_password:
    external: true'''

# ── syntect helpers ───────────────────────────────────────────────────────

def _syntect_setup():
    return """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
"""


def bench_syntect_small(lang, code, setup_code="", iterations=100):
    """syntect-py: highlight_string on small snippet."""
    setup = f"""
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(code)}
{setup_code}
"""
    stmt = f'syntect.highlight_string(code, "{lang}", "base16-ocean.dark", ss, ts)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_syntect_medium(lang, code, setup_code="", iterations=10):
    """syntect-py: highlight_string on medium snippet."""
    setup = f"""
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(code)}
{setup_code}
"""
    stmt = f'syntect.highlight_string(code, "{lang}", "base16-ocean.dark", ss, ts)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── fastpylight helpers ───────────────────────────────────────────────────

def bench_fastpylight_small(lang, code, iterations=100):
    """fastpylight: highlight on small snippet."""
    setup = f"""
from fastpylight import highlight
code = {repr(code)}
"""
    stmt = f'highlight(code, "{lang}")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_spans_small(lang, code, iterations=100):
    """fastpylight: highlight_spans on small snippet."""
    setup = f"""
from fastpylight import highlight_spans
code = {repr(code)}
"""
    stmt = f'highlight_spans(code, "{lang}", "hl-")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_fastpylight_medium(lang, code, iterations=10):
    """fastpylight: highlight on medium snippet."""
    setup = f"""
from fastpylight import highlight
code = {repr(code)}
"""
    stmt = f'highlight(code, "{lang}")'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── Pygments helpers ──────────────────────────────────────────────────────

try:
    from pygments import highlight as pygments_highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    HAS_PYGRAMENTS = True
except ImportError:
    HAS_PYGRAMENTS = False


def bench_pygments_small(lang, code, iterations=100):
    """Pygments: highlight on small snippet."""
    if not HAS_PYGRAMENTS:
        return None
    setup = f"""
from pygments import highlight as h
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
code = {repr(code)}
lexer = get_lexer_by_name("{lang}")
formatter = HtmlFormatter()
"""
    stmt = 'h(code, lexer, formatter)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_pygments_medium(lang, code, iterations=10):
    """Pygments: highlight on medium snippet."""
    if not HAS_PYGRAMENTS:
        return None
    setup = f"""
from pygments import highlight as h
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
code = {repr(code)}
lexer = get_lexer_by_name("{lang}")
formatter = HtmlFormatter()
"""
    stmt = 'h(code, lexer, formatter)'
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── Multi-language benchmarks ─────────────────────────────────────────────

LANG_SNIPPETS = {
    "Rust": RUST_SMALL,
    "Python": PYTHON_SMALL,
    "JavaScript": JAVASCRIPT_MEDIUM[:200],
    "C": 'int main() { int x = 42; return 0; }',
    "C++": 'int main() { int x = 42; return 0; }',
    "Java": 'public class Main { public static void main(String[] a) { int x = 42; } }',
    "TypeScript": 'function main() { const x: number = 42; }',
    "Java": 'public class Main { public static void main(String[] a) { int x = 42; } }',
    "HTML": HTML_CODE[:300],
    "CSS": '.class { color: red; }',
    "YAML": YAML_CODE[:200],
    "TOML": 'name = "syntect"\nversion = "5.3.0"\n[dependencies]\nregex = "^1.0"',
    "JSON": '{"name": "syntect", "version": "5.3.0", "features": ["highlighting"]}',
}


def bench_multi_syntect(iterations=5):
    """syntect-py: highlight across all languages."""
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
    "Java": 'class Main { public static void main(String[] a) { int x = 42; } }',
    "TypeScript": 'function main() { const x: number = 42; }',
    "Java": 'public class Main { public static void main(String[] a) { int x = 42; } }',
    "HTML": '<html><body><div>Hello</div></body></html>',
    "CSS": '.class { color: red; }',
    "YAML": 'key: value\\nlist:\\n  - item1',
    "TOML": 'name = "test"\\nversion = "1.0"',
    "JSON": '{"name": "test"}',
}
"""
    stmt = """
for lang, code in snippets.items():
    syntect.highlight_string(code, lang, "base16-ocean.dark", ss, ts)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


def bench_multi_fastpylight(iterations=5):
    """fastpylight: highlight across all languages."""
    setup = """
from fastpylight import highlight
snippets = {
    "rust": 'fn main() { let x = 42; }',
    "python": 'def main(): x = 42',
    "javascript": 'function main() { let x = 42; }',
    "c": 'int main() { int x = 42; }',
    "cpp": 'int main() { int x = 42; }',
    "java": 'class Main { public static void main(String[] a) { int x = 42; } }',
    "typescript": 'function main() { const x: number = 42; }',
    "go": 'func main() { var x = 42; }',
    "html": '<html><body><div>Hello</div></body></html>',
    "css": '.class { color: red; }',
    "yaml": 'key: value\\nlist:\\n  - item1',
    "toml": 'name = "test"\\nversion = "1.0"',
    "json": '{"name": "test"}',
}
"""
    stmt = """
for lang, code in snippets.items():
    highlight(code, lang)
"""
    times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
    return min(times) / iterations * 1000


# ── Large-file benchmarks ─────────────────────────────────────────────────

def find_large_files(ext=".py", min_lines=500, n=3):
    """Find large files on the system."""
    candidates = []
    # Check common Python locations
    for base in ["/usr", "/opt", "C:\\Python", "C:\\Program Files"]:
        if not os.path.isdir(base):
            continue
        for root, dirs, fnames in os.walk(base):
            # Skip virtual envs and node_modules
            if "node_modules" in root or "__pycache__" in root:
                continue
            for f in fnames:
                if f.endswith(ext):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", errors="replace") as fh:
                            line_count = sum(1 for _ in fh)
                        if line_count > min_lines:
                            candidates.append((path, line_count))
                    except:
                        pass
            # Limit depth
            if len(candidates) > n * 10:
                break
        if len(candidates) > n * 10:
            break
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:n]


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def bench_large_file_syntect(code, lang, iterations=3):
    """syntect-py: highlight a large file."""
    setup = f"""
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(code)}
"""
    stmt = f'syntect.highlight_string(code, "{lang}", "base16-ocean.dark", ss, ts)'
    times = timeit.repeat(stmt, setup, repeat=3, number=iterations)
    return min(times) / iterations * 1000


def bench_large_file_fastpylight(code, lang, iterations=3):
    """fastpylight: highlight a large file."""
    setup = f"""
from fastpylight import highlight
code = {repr(code)}
"""
    stmt = f'highlight(code, "{lang}")'
    times = timeit.repeat(stmt, setup, repeat=3, number=iterations)
    return min(times) / iterations * 1000


def bench_large_file_pygments(code, lang, iterations=3):
    """Pygments: highlight a large file."""
    if not HAS_PYGRAMENTS:
        return None
    setup = f"""
from pygments import highlight as h
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
code = {repr(code)}
lexer = get_lexer_by_name("{lang}")
formatter = HtmlFormatter()
"""
    stmt = 'h(code, lexer, formatter)'
    times = timeit.repeat(stmt, setup, repeat=3, number=iterations)
    return min(times) / iterations * 1000


# ── Profile breakdown ─────────────────────────────────────────────────────

def profile_breakdown():
    """Detailed profile: where time is spent in each library."""
    code = PYTHON_MEDIUM
    lines = code.count('\n') + 1
    print(f"\n{'=' * 70}")
    print(f"  PROFILE BREAKDOWN — {lines} lines, {len(code)//1024} KB")
    print(f"{'=' * 70}\n")

    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()

    # 1. Syntect: lex ONE line
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
    print(f"  Syntect: lex ONE line (highlight_line)          = {t1:.4f}ms")

    # 2. Syntect: HTML from tokens (no lexing)
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
    print(f"  Syntect: HTML from tokens (no lex)              = {t2:.4f}ms")

    # 3. Syntect: full highlight_string
    t3 = timeit.timeit(
        f'syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)',
        setup=f'''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = {repr(code)}
''',
        number=5
    ) / 5 * 1000
    print(f"  Syntect: full highlight_string ({lines} lines)   = {t3:.3f}ms ({t3/lines*1000:.4f}ms/100 lines)")

    # 4. Syntect: terminal output
    t4 = timeit.timeit(
        'syntect.as_terminal_escaped(tokens, True)',
        setup='''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
hl = syntect.Highlighter(ss.find_syntax_by_name("Python"), ts.get_theme("base16-ocean.dark"))
tokens = hl.highlight_line("def main(): pass", ss, ts)
''',
        number=1000
    ) / 1000 * 1000
    print(f"  Syntect: terminal ANSI output (no lex)          = {t4:.4f}ms")

    # 5. Syntect: LaTeX output
    t5 = timeit.timeit(
        'syntect.as_latex_escaped(tokens)',
        setup='''
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
hl = syntect.Highlighter(ss.find_syntax_by_name("Python"), ts.get_theme("base16-ocean.dark"))
tokens = hl.highlight_line("def main(): pass", ss, ts)
''',
        number=1000
    ) / 1000 * 1000
    print(f"  Syntect: LaTeX output (no lex)                  = {t5:.4f}ms")

    # 6. fastpylight: highlight (toks)
    t6 = timeit.timeit(
        'highlight(code, "python")',
        setup=f'''
from fastpylight import highlight
code = {repr(code)}
''',
        number=5
    ) / 5 * 1000
    print(f"  fastpylight: highlight ({lines} lines)           = {t6:.3f}ms ({t6/lines*1000:.4f}ms/100 lines)")

    # 7. fastpylight: highlight_spans
    t7 = timeit.timeit(
        'highlight_spans(code, "python", "hl-")',
        setup=f'''
from fastpylight import highlight_spans
code = {repr(code)}
''',
        number=5
    ) / 5 * 1000
    print(f"  fastpylight: highlight_spans ({lines} lines)     = {t7:.3f}ms ({t7/lines*1000:.4f}ms/100 lines)")

    # 8. Pygments: full highlight
    if HAS_PYGRAMENTS:
        t8 = timeit.timeit(
            f'''
from pygments import highlight as h
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
code = {repr(code)}
lexer = get_lexer_by_name("python")
formatter = HtmlFormatter()
h(code, lexer, formatter)
''',
            number=5
        ) / 5 * 1000
        print(f"  Pygments: highlight ({lines} lines)             = {t8:.3f}ms ({t8/lines*1000:.4f}ms/100 lines)")

        # 9. Pygments: JUST lexing
        t9 = timeit.timeit(
            f'''
from pygments.lexers import get_lexer_by_name
code = {repr(code)}
lexer = get_lexer_by_name("python")
list(lexer.get_tokens(code))
''',
            number=5
        ) / 5 * 1000
        print(f"  Pygments: JUST lexing ({lines} lines)           = {t9:.3f}ms ({t9/lines*1000:.4f}ms/100 lines)")

    # Summary
    print(f"\n{'=' * 70}")
    print("  COMPARISON (per 100 lines)")
    print(f"{'=' * 70}")
    print(f"  {'Library':<25} {'Per 100 lines':>14} {'vs fastpylight':>15}")
    print(f"  {'-'*25} {'-'*14} {'-'*15}")
    
    fastpylight_per_100 = t6 / lines * 1000
    print(f"  {'fastpylight (toks)':<25} {t6/lines*1000:>13.4f}ms {'1.0x':>15}")
    print(f"  {'fastpylight (spans)':<25} {t7/lines*1000:>13.4f}ms {'1.0x':>15}")
    print(f"  {'syntect-py (full)':<25} {t3/lines*1000:>13.4f}ms {t3/t6:>14.1f}x")
    if HAS_PYGRAMENTS:
        print(f"  {'Pygments (full)':<25} {t8/lines*1000:>13.4f}ms {t8/t6:>14.1f}x")

    print(f"\n  Syntect does 3 outputs (HTML + ANSI + LaTeX)")
    print(f"  fastpylight does 1 output (HTML via CSS Highlight API)")
    print(f"  Pygments does 1 output (HTML only)")
    estimated_syntect_lex = t3 / 3
    print(f"  Estimated lex-only (net of 3 outputs): ~{estimated_syntect_lex:.1f}ms")
    print(f"  Lex-only vs fastpylight: ~{estimated_syntect_lex/t6:.1f}x")


# ── Output format comparison ──────────────────────────────────────────────

def bench_output_formats(iterations=50):
    """Compare output formats for syntect-py."""
    ss = syntect.SyntaxSet.load_defaults(False)
    ts = syntect.ThemeSet.load_defaults()
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    tokens = hl.highlight_line("fn main() { let x = 42; println!(\"Hello\"); }", ss, ts)

    setup = """
import syntect
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(rust, theme)
tokens = hl.highlight_line('fn main() { let x = 42; println!("Hello"); }', ss, ts)
"""

    formats = {
        "HTML (inline)": 'syntect.as_html(tokens, "if_different", None)',
        "HTML (class)": 'syntect.tokens_to_classed_spans(tokens, syntect.ClassStyle.spaced_prefixed("syn-"))',
        "Terminal (fg)": 'syntect.as_terminal_escaped(tokens, False)',
        "Terminal (fg+bg)": 'syntect.as_terminal_escaped(tokens, True)',
        "LaTeX": 'syntect.as_latex_escaped(tokens)',
    }

    print(f"\n{'=' * 70}")
    print("  OUTPUT FORMAT COMPARISON (syntect-py only)")
    print(f"{'=' * 70}")
    print(f"  {'Format':<30} {'Time':>10} {'Relative':>10}")
    print(f"  {'-'*30} {'-'*10} {'-'*10}")

    results = {}
    for name, stmt in formats.items():
        times = timeit.repeat(stmt, setup, repeat=5, number=iterations)
        t = min(times) / iterations * 1000
        results[name] = t
        print(f"  {name:<30} {t:>8.4f}ms {t/results[min(results, key=results.get)]:>9.1f}x")


# ── Scaling analysis ──────────────────────────────────────────────────────

def bench_scaling(iterations=5):
    """Benchmark highlighting at different file sizes to see scaling."""
    # Use Python medium as base
    full_code = PYTHON_MEDIUM
    full_lines = full_code.count('\n') + 1

    print(f"\n{'=' * 70}")
    print(f"  SCALING ANALYSIS (Python medium, {full_lines} lines)")
    print(f"{'=' * 70}")
    print(f"  {'Size':<15} {'syntect':>12} {'fastpy':>12} {'Ratio':>10}")
    print(f"  {'-'*15} {'-'*12} {'-'*12} {'-'*10}")

    for pct in [10, 25, 50, 100]:
        n_lines = max(1, full_lines * pct // 100)
        code = '\n'.join(full_code.split('\n')[:n_lines])
        
        s_t = bench_syntect_medium("Python", code, iterations=max(1, iterations * 5 // (100 // pct)))
        f_t = bench_fastpylight_medium("python", code, iterations=max(1, iterations * 5 // (100 // pct)))
        
        ratio = s_t / f_t if f_t > 0 else float('inf')
        print(f"  {pct:>3}% ({n_lines:>4} lines)  {s_t:>10.3f}ms {f_t:>10.3f}ms {ratio:>9.1f}x")


# ── Main runner ───────────────────────────────────────────────────────────

def run_all_benchmarks(iterations=100):
    """Run all benchmarks and print a comprehensive report."""
    print("\n" + "=" * 70)
    print("  COMPREHENSIVE BENCHMARK: syntect-py vs fastpylight")
    print("  syntect: Rust (Syntect, regex-fancy, Sublime Text grammars)")
    print("  fastpylight: Rust (Tree-sitter, Lumis)")
    if HAS_PYGRAMENTS:
        print("  Pygments: Python (re module)")
    else:
        print("  Pygments: NOT INSTALLED")
    print("\n  Lower is better (fewer milliseconds per operation)")
    print("=" * 70)

    results = {}

    # ── Small snippets ──
    print("\n" + "-" * 70)
    print("  SMALL SNIPPETS (single operation)")
    print("-" * 70)
    
    # fastpylight uses lowercase names
    small_tests = [
        ("Rust", RUST_SMALL, "rust", True, 200),
        ("Python", PYTHON_SMALL, "python", True, 200),
        ("JavaScript", JAVASCRIPT_MEDIUM[:200], "javascript", True, 100),
    ]

    for name, code, flang, has_spans, iters in small_tests:
        print(f"\n  [{name}]")
        s_t = bench_syntect_small(name, code, iterations=max(10, iters // 5))
        print(f"    syntect-py:                   {s_t:.4f}ms")
        f_t = bench_fastpylight_small(flang, code, iterations=max(10, iters // 5))
        print(f"    fastpylight (toks):           {f_t:.4f}ms ({s_t/f_t:.1f}x)")
        if has_spans:
            f_s = bench_fastpylight_spans_small(flang, code, iterations=max(10, iters // 5))
            print(f"    fastpylight (spans):          {f_s:.4f}ms ({s_t/f_s:.1f}x)")
        if HAS_PYGRAMENTS:
            p_t = bench_pygments_small(flang, code, iterations=max(10, iters // 5))
            if p_t is not None:
                print(f"    Pygments:                     {p_t:.4f}ms ({s_t/p_t:.1f}x)")
        results[f"small_{name}"] = {"syntect": s_t, "fastpylight": f_t}

    # ── Medium snippets ──
    print("\n" + "-" * 70)
    print("  MEDIUM SNIPPETS (multi-line code)")
    print("-" * 70)

    medium_tests = [
        ("Rust", RUST_MEDIUM, "rust"),
        ("Python", PYTHON_MEDIUM, "python"),
        ("JavaScript", JAVASCRIPT_MEDIUM, "javascript"),
        ("C++", 'void foo() { int x = 42; }\nclass Bar {\n    int a, b;\n    int add() { return a + b; }\n};', "cpp"),
    ]

    for name, code, flang in medium_tests:
        print(f"\n  [{name}] ({code.count(chr(10))+1} lines)")
        s_t = bench_syntect_medium(name, code, iterations=10)
        print(f"    syntect-py:                   {s_t:.3f}ms")
        f_t = bench_fastpylight_medium(flang, code, iterations=10)
        print(f"    fastpylight (toks):           {f_t:.3f}ms ({s_t/f_t:.1f}x)")
        if HAS_PYGRAMENTS:
            p_t = bench_pygments_medium(flang, code, iterations=10)
            if p_t is not None:
                print(f"    Pygments:                     {p_t:.3f}ms ({s_t/p_t:.1f}x)")
        results[f"medium_{name}"] = {"syntect": s_t, "fastpylight": f_t}

    # ── Multi-language ──
    print("\n" + "-" * 70)
    print("  MULTI-LANGUAGE (14 languages)")
    print("-" * 70)
    multi_iter = max(3, iterations // 30)
    s_multi = bench_multi_syntect(multi_iter)
    f_multi = bench_multi_fastpylight(multi_iter)
    print(f"\n    syntect-py:                   {s_multi:.3f}ms")
    print(f"    fastpylight (toks):           {f_multi:.3f}ms ({s_multi/f_multi:.1f}x)")
    results["multi_language"] = {"syntect": s_multi, "fastpylight": f_multi}

    # ── Large files ──
    print("\n" + "-" * 70)
    print("  LARGE FILES (real files)")
    print("-" * 70)

    large_files = find_large_files(min_lines=2000, n=3)
    if large_files:
        for path, total_lines in large_files:
            code = read_file(path)
            size_kb = len(code) / 1024
            name = os.path.basename(path)
            ext = os.path.splitext(name)[1].lstrip('.')
            
            # Map extension to language
            lang_map = {
                'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript',
                'rs': 'Rust', 'go': 'Go', 'c': 'C', 'cpp': 'C++',
                'java': 'Java', 'html': 'HTML', 'css': 'CSS',
                'yaml': 'YAML', 'yml': 'YAML', 'json': 'JSON',
                'php': 'PHP', 'sh': 'Bash',
            }
            # fastpylight uses lowercase names
            fastpy_map = {
                'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                'rs': 'rust', 'go': 'go', 'c': 'c', 'cpp': 'cpp',
                'java': 'java', 'html': 'html', 'css': 'css',
                'yaml': 'yaml', 'yml': 'yaml', 'json': 'json',
                'php': 'php', 'sh': 'bash',
            }
            lang = lang_map.get(ext, ext.capitalize())
            flang = fastpy_map.get(ext, ext.lower())

            print(f"\n  [{name}] ({total_lines:,} lines, {size_kb:.0f} KB, {lang})")
            
            s_t = bench_large_file_syntect(code, lang, iterations=3)
            print(f"    syntect-py:                   {s_t:.1f}ms ({s_t/total_lines*1000:.4f}ms/100 lines)")
            
            f_t = bench_large_file_fastpylight(code, flang, iterations=3)
            print(f"    fastpylight (toks):           {f_t:.1f}ms ({f_t/total_lines*1000:.4f}ms/100 lines) ({s_t/f_t:.1f}x)")
            
            if HAS_PYGRAMENTS:
                p_t = bench_large_file_pygments(code, lang, iterations=3)
                if p_t is not None:
                    print(f"    Pygments:                     {p_t:.1f}ms ({p_t/total_lines*1000:.4f}ms/100 lines) ({s_t/p_t:.1f}x)")
            
            results[f"large_{name}"] = {"syntect": s_t, "fastpylight": f_t}
    else:
        print("\n  No large files found (>2000 lines) on this system.")

    # ── Output formats ──
    bench_output_formats()

    # ── Scaling ──
    bench_scaling()

    # ── Summary ──
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"\n  {'Benchmark':<35} {'syntect':>12} {'fastpylight':>12} {'Ratio':>8}")
    print(f"  {'-'*35} {'-'*12} {'-'*12} {'-'*8}")

    for name, data in results.items():
        s = data.get("syntect", 0)
        f = data.get("fastpylight", 0)
        ratio = s / f if f > 0 else float('inf')
        print(f"  {name:<35} {s:>10.3f}ms {f:>10.3f}ms {ratio:>7.1f}x")

    print(f"\n  {'=' * 70}")
    print(f"  Lower is better. Ratio > 1 means syntect is slower.")
    print(f"{'=' * 70}\n")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Comprehensive benchmark: syntect-py vs fastpylight")
    parser.add_argument("--iterations", type=int, default=100, help="Base iteration count")
    parser.add_argument("--files", action="store_true", help="Large-file mode only")
    parser.add_argument("--profile", action="store_true", help="Profile breakdown only")
    args = parser.parse_args()

    if args.profile:
        profile_breakdown()
        return

    if args.files:
        # Just run large-file benchmarks
        print("\n" + "=" * 70)
        print("  LARGE FILE BENCHMARK: syntect-py vs fastpylight")
        print("=" * 70)
        large_files = find_large_files(min_lines=2000, n=5)
        for path, total_lines in large_files:
            code = read_file(path)
            name = os.path.basename(path)
            ext = os.path.splitext(name)[1].lstrip('.')
            lang = lang_map.get(ext, ext.capitalize())
            flang = ext.lower()
            print(f"\n  [{name}] ({total_lines:,} lines)")
            s_t = bench_large_file_syntect(code, lang, iterations=3)
            f_t = bench_large_file_fastpylight(code, flang, iterations=3)
            print(f"    syntect-py:   {s_t:.1f}ms")
            print(f"    fastpylight:  {f_t:.1f}ms ({s_t/f_t:.1f}x)")
        return

    run_all_benchmarks(args.iterations)


if __name__ == "__main__":
    main()
