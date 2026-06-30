"""Example: Highlight code to a full HTML file."""
import syntect
import sys


def highlight_to_html(code, syntax_name, theme_name, output_path, syntax_set, theme_set):
    """Highlight code and save to a complete HTML file."""
    # Get syntax and theme
    syntax_ref = syntax_set.find_syntax_by_name(syntax_name)
    theme = theme_set.get_theme(theme_name)

    if syntax_ref is None:
        print(f"Unknown syntax: {syntax_name}", file=sys.stderr)
        return

    if theme is None:
        print(f"Unknown theme: {theme_name}", file=sys.stderr)
        return

    # Create full HTML with line numbers
    html = syntect.highlighted_html_at_line_and_column_number(
        code, syntax_ref, theme, syntax_set, theme_set, start_line=1
    )

    # Wrap in full HTML document with CSS
    css = syntect.css_for_theme(theme, "spaced")
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
{css}
</style>
</head>
<body>
<pre>{html}</pre>
</body>
</html>"""

    # Write to file
    with open(output_path, "w") as f:
        f.write(full_html)

    print(f"Written {len(full_html)} bytes to {output_path}")


if __name__ == "__main__":
    ss = syntect.SyntaxSet.load_defaults(True)
    ts = syntect.ThemeSet.load_defaults()

    # Example: highlight Rust code
    code = """fn main() {
    let x = 42;
    println!("Hello, World!");
}"""

    highlight_to_html(
        code,
        "Rust",
        "base16-ocean.dark",
        "output.html",
        ss,
        ts,
    )
