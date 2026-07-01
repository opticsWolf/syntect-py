"""Large-file benchmark: syntect-py vs Pygments (fair comparison).

Key: Both must do full lex + format from scratch each iteration.
Pygments caches lexers, so we force fresh lexer creation each time.
"""
import timeit
import os
import syntect
from pygments import highlight as pygments_highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def find_largest_python_files(n=3):
    """Find the largest Python files on this system."""
    import pygments
    pygments_dir = os.path.dirname(pygments.__file__)

    files = []
    for root, dirs, fnames in os.walk(pygments_dir):
        for f in fnames:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    lines = sum(1 for _ in open(path))
                    if lines > 1000:
                        files.append((path, lines))
                except:
                    pass

    # Also check stdlib
    stdlib_dir = os.path.join(os.path.dirname(pygments.__file__), "..", "..", "..", "Lib")
    for root, dirs, fnames in os.walk(stdlib_dir):
        for f in fnames:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    lines = sum(1 for _ in open(path))
                    if lines > 1000:
                        files.append((path, lines))
                except:
                    pass

    files.sort(key=lambda x: x[1], reverse=True)
    return files[:n]


def main():
    print("=" * 80)
    print("  LARGE FILE BENCHMARK: syntect-py vs Pygments (FAIR)")
    print("  Both do full lex + format from scratch each iteration")
    print("=" * 80)
    print()

    files = find_largest_python_files(3)
    print(f"Testing with {len(files)} large Python file(s):")
    for path, lines in files:
        print(f"  {os.path.basename(path)}: {lines:,} lines")
    print()

    results = []

    for path, total_lines in files:
        code = read_file(path)
        size_kb = len(code) / 1024
        name = os.path.basename(path)

        print(f"{'=' * 80}")
        print(f"  File: {name}")
        print(f"  Lines: {total_lines:,} | Size: {size_kb:.0f} KB")
        print(f"{'=' * 80}")

        iterations = max(1, 5)

        # --- syntect-py: full lex + format each time ---
        ss = syntect.SyntaxSet.load_defaults(False)
        ts = syntect.ThemeSet.load_defaults()

        t_syntect = timeit.timeit(
            f"""
ss = syntect.SyntaxSet.load_defaults(False)
ts = syntect.ThemeSet.load_defaults()
code = r{repr(code)}
syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)
""",
            globals={"syntect": syntect},
            number=iterations,
        ) / iterations * 1000

        # --- Pygments: force FRESH lexer each time (no caching) ---
        t_pygments = timeit.timeit(
            f"""
code = r{repr(code)}
lexer = PythonLexer()          # Fresh lexer each time
formatter = HtmlFormatter()    # Fresh formatter each time
highlight(code, lexer, formatter)
""",
            globals={
                "highlight": pygments_highlight,
                "PythonLexer": PythonLexer,
                "HtmlFormatter": HtmlFormatter,
            },
            number=iterations,
        ) / iterations * 1000

        ratio = t_syntect / t_pygments if t_pygments > 0 else float("inf")

        print(f"    syntect-py:    {t_syntect:10.3f}ms  ({t_syntect/total_lines*1000:.4f}ms per 100 lines)")
        print(f"    Pygments:      {t_pygments:10.3f}ms  ({t_pygments/total_lines*1000:.4f}ms per 100 lines)")
        print(f"    syntect is     {ratio:6.1f}x {'slower' if ratio > 1 else 'faster'}")

        results.append(
            {
                "file": name,
                "lines": total_lines,
                "syntect": t_syntect,
                "pygments": t_pygments,
                "ratio": ratio,
            }
        )

    # Summary
    print(f"\n{'=' * 80}")
    print("  SUMMARY")
    print(f"{'=' * 80}")
    print()
    print(f"  {'File':<35} {'Lines':>8} {'syntect':>12} {'Pygments':>12} {'Ratio':>8}")
    print(f"  {'-'*35} {'-'*8} {'-'*12} {'-'*12} {'-'*8}")

    for r in results:
        print(
            f"  {r['file']:<35} {r['lines']:>8,} "
            f"{r['syntect']:>10.3f}ms {r['pygments']:>10.3f}ms {r['ratio']:>7.1f}x"
        )

    print()
    print(f"  {'=' * 80}")
    print(f"  Lower is better. Ratio > 1 means syntect is slower.")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
