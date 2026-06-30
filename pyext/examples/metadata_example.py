"""Example: Demonstrate metadata access from .tmPreferences files."""
import syntect

# Load syntax set (metadata is loaded with default syntaxes)
ss = syntect.SyntaxSet.load_defaults(True)

print("=== Metadata Access Demo ===\n")

# Access metadata on SyntaxSet
metadata = ss.metadata()
if metadata is None:
    print("No metadata loaded (use SyntaxSetBuilder with add_from_folder for .tmPreferences)")
else:
    print(f"Total metadata sets: {len(metadata.sets)}")
    print()

    # Show first few metadata sets
    shown = 0
    for mset in metadata.sets:
        if shown >= 10:
            print("...")
            break
        print(f"Selector: {mset.selector_string}")
        print(f"  line_comment: {mset.items.line_comment}")
        print(f"  block_comment: {mset.items.block_comment}")
        print(f"  indent_parens: {mset.items.indent_parens}")
        if mset.items.shell_variables:
            print(f"  shell_variables: {dict(mset.items.shell_variables)[:3]}")  # first 3
        print()
        shown += 1

print("=== SyntaxReference Metadata ===")
# Each syntax reference can have its own metadata
for syntax in ss.syntaxes()[:5]:
    print(f"{syntax.name}:")
    print(f"  scope: {syntax.scope}")
    print(f"  version: {syntax.version}")
    print(f"  first_line_match: {syntax.first_line_match}")
    print(f"  variables: {len(syntax.variables)} entries")
    print()

print("=== Done ===")
