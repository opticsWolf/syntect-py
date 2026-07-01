"""Large-file benchmark: syntect-py vs fastpylight vs Pygments (fair comparison).

Both libraries do full lex + format from scratch each iteration.
"""
import timeit
import os
import syntect

try:
    from fastpylight import highlight as fastpylight_highlight
    HAS_FASTPYLIGHT = True
except ImportError:
    HAS_FASTPYLIGHT = False

try:
    from pygments import highlight as pygments_highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    HAS_PYGRAMENTS = True
except ImportError:
    HAS_PYGRAMENTS = False


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def find_large_files(ext=".py", min_lines=500, n=5):
    """Find the largest files on this system."""
    candidates = []
    
    # Check common Python locations
    for base in ["/usr", "/opt"]:
        if not os.path.isdir(base):
            continue
        for root, dirs, fnames in os.walk(base):
            if "node_modules" in root or "__pycache__" in root:
                continue
            for f in fnames:
                if f.endswith(ext):
                    path = os.path.join(root, f)
                    try:
                        lines = sum(1 for _ in open(path))
                        if lines > min_lines:
                            candidates.append((path, lines))
                    except:
                        pass
    
    # Check standard library
    import sysconfig
    stdlib = sysconfig.get_path('stdlib')
    if stdlib:
        for root, dirs, fnames in os.walk(stdlib):
            for f in fnames:
                if f.endswith(ext):
                    path = os.path.join(root, f)
                    try:
                        lines = sum(1 for _ in open(path))
                        if lines > min_lines:
                            candidates.append((path, lines))
                    except:
                        pass
    
    # Check pip packages
    for base in [os.path.dirname(__import__("pip").__file__), 
                 os.path.dirname(__import__("setuptools").__file__)]:
        if base and os.path.isdir(base):
            for root, dirs, fnames in os.walk(base):
                for f in fnames:
                    if f.endswith(ext):
                        path = os.path.join(root, f)
                        try:
                            lines = sum(1 for _ in open(path))
                            if lines > min_lines:
                                candidates.append((path, lines))
                        except:
                            pass
    
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:n]


# Language mapping for file extensions
LANG_MAP = {
    'py': 'Python', 'js': 'JavaScript', 'ts': 'TypeScript', 'jsx': 'JavaScript',
    'rs': 'Rust', 'go': 'Go', 'c': 'C', 'cpp': 'C++', 'h': 'C', 'hpp': 'C++',
    'java': 'Java', 'html': 'HTML', 'htm': 'HTML', 'css': 'CSS',
    'yaml': 'YAML', 'yml': 'YAML', 'json': 'JSON', 'md': 'Markdown',
    'toml': 'TOML', 'rb': 'Ruby', 'php': 'PHP', 'sh': 'Bash',
    'vue': 'HTML', 'svelte': 'HTML', 'sql': 'SQL',
}

FASTPY_LANG_MAP = {
    'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'jsx': 'jsx',
    'rs': 'rust', 'go': 'go', 'c': 'c', 'cpp': 'cpp', 'h': 'c', 'hpp': 'cpp',
    'java': 'java', 'html': 'html', 'htm': 'html', 'css': 'css',
    'yaml': 'yaml', 'yml': 'yaml', 'json': 'json', 'md': 'markdown',
    'toml': 'toml', 'rb': 'ruby', 'php': 'php', 'sh': 'bash',
    'vue': 'html', 'svelte': 'html', 'sql': 'sql',
}


def main():
    print("=" * 80)
    print("  LARGE FILE BENCHMARK: syntect-py vs fastpylight vs Pygments")
    print("  Both do full lex + format from scratch each iteration")
    print("=" * 80)
    print()

    # Test with multiple file types
    file_types = [('.py', 'Python'), ('.js', 'JavaScript'), ('.rs', 'Rust'), ('.go', 'Go')]
    
    all_results = []

    for ext, lang in file_types:
        files = find_large_files(ext, min_lines=1000, n=2)
        if not files:
            print(f"  No {lang} files > 1000 lines found, skipping.")
            continue

        for path, total_lines in files:
            code = read_file(path)
            size_kb = len(code) / 1024
            name = os.path.basename(path)
            
            fastpy_lang = FASTPY_LANG_MAP.get(ext.lstrip('.'), ext.lstrip('.'))
            
            print(f"\n{'=' * 80}")
            print(f"  File: {name}")
            print(f"  Lines: {total_lines:,} | Size: {size_kb:.0f} KB | Language: {lang}")
            print(f"{'=' * 80}")

            iterations = max(1, 3)

            # --- syntect-py ---
            ss = syntect.SyntaxSet.load_defaults(False)
            ts = syntect.ThemeSet.load_defaults()
            t_syntect = timeit.timeit(
                f"""
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = r{repr(code)}
syntect.highlight_string(code, "{lang}", "base16-ocean.dark", ss, ts)
""",
                globals={"syntect": syntect},
                number=iterations,
            ) / iterations * 1000

            # --- fastpylight ---
            if HAS_FASTPYLIGHT:
                t_fastpy = timeit.timeit(
                    f"""
code = r{repr(code)}
from fastpylight import highlight
highlight(code, "{fastpy_lang}")
""",
                    globals={},
                    number=iterations,
                ) / iterations * 1000
            else:
                t_fastpy = None

            # --- Pygments ---
            if HAS_PYGRAMENTS:
                t_pygments = timeit.timeit(
                    f"""
code = r{repr(code)}
lexer = PythonLexer()
formatter = HtmlFormatter()
pygments_highlight(code, lexer, formatter)
""",
                    globals={
                        "pygments_highlight": pygments_highlight,
                        "PythonLexer": PythonLexer,
                        "HtmlFormatter": HtmlFormatter,
                    },
                    number=iterations,
                ) / iterations * 1000
            else:
                t_pygments = None

            print(f"    syntect-py:       {t_syntect:10.3f}ms  ({t_syntect/total_lines*1000:.4f}ms per 100 lines)")
            if t_fastpy is not None:
                print(f"    fastpylight:      {t_fastpy:10.3f}ms  ({t_fastpy/total_lines*1000:.4f}ms per 100 lines)  ({t_syntect/t_fastpy:.1f}x)")
            if t_pygments is not None:
                print(f"    Pygments:         {t_pygments:10.3f}ms  ({t_pygments/total_lines*1000:.4f}ms per 100 lines)  ({t_syntect/t_pygments:.1f}x)")

            all_results.append({
                "file": name,
                "lang": lang,
                "lines": total_lines,
                "syntect": t_syntect,
                "fastpylight": t_fastpy,
                "pygments": t_pygments,
            })

    # Summary
    print(f"\n{'=' * 80}")
    print("  SUMMARY")
    print(f"{'=' * 80}")
    print()
    print(f"  {'File':<30} {'Lang':<10} {'Lines':>8} {'syntect':>12} {'fastpy':>12} {'Pygments':>12}")
    print(f"  {'-'*30} {'-'*10} {'-'*8} {'-'*12} {'-'*12} {'-'*12}")

    for r in all_results:
        synt_str = f"{r['syntect']:>10.3f}ms"
        fast_str = f"{r['fastpylight']:>10.3f}ms" if r['fastpylight'] is not None else "         N/A"
        pyg_str = f"{r['pygments']:>10.3f}ms" if r['pygments'] is not None else "         N/A"
        print(f"  {r['file']:<30} {r['lang']:<10} {r['lines']:>8,} {synt_str} {fast_str} {pyg_str}")

    print()
    print(f"  {'=' * 80}")
    print(f"  Lower is better. Ratio > 1 means syntect is slower.")
    if HAS_FASTPYLIGHT:
        print(f"  Syntect vs fastpylight: {sum(r['syntect'] for r in all_results) / sum(r['fastpylight'] for r in all_results if r['fastpylight']):.1f}x avg")
    if HAS_PYGRAMENTS:
        print(f"  Syntect vs Pygments:    {sum(r['syntect'] for r in all_results) / sum(r['pygments'] for r in all_results if r['pygments']):.1f}x avg")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
