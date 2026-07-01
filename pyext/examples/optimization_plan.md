# Optimization Plan for syntect-py

> Date: 2026-06-30
> Baseline: 148.1ms/100 lines (2.29x vs Pygments)

---

## Optimizations (in priority order)

### 1. Pre-allocate token vectors (LOW effort, MEDIUM impact)
- `highlight_string()`: `all_tokens` grows dynamically → pre-allocate
- `highlight_lines()`: `all_tokens` and per-line vectors → pre-allocate
- `split_lines_with_endings()`: returned Vec → pre-allocate based on newline count

### 2. Generate output directly from syntect types (MEDIUM effort, HIGH impact)
- `highlight_string()` currently creates `PyStyle` for every token, then iterates
  `Vec<(PyStyle, String)>` again for HTML/terminal generation
- New approach: generate HTML and terminal output directly from syntect's
  `(Style, &str)` tuples during the lexing loop — no intermediate `PyStyle` needed
- This eliminates one full pass over all tokens and avoids `PyStyle` allocation
  for output generation

### 3. Optimize HTML generation (LOW effort, MEDIUM impact)
- `generate_html_from_tokens()` uses many `push_str` + `format!` calls
- Replace with `write!` into a pre-sized `String` buffer
- Reduce string allocations in `escape_html()`

### 4. Optimize terminal escape generation (LOW effort, LOW impact)
- `as_terminal_escaped_impl()` uses `format!` per token — expensive
- Replace with manual buffer writes

### 5. Lazy terminal output in `PyHighlightResult` (MEDIUM effort, MEDIUM impact)
- `terminal_escaped` is generated eagerly in `highlight_string()` even if never used
- Change to `Option<String>` with lazy computation on first access
- Benchmark shows terminal gen is ~1/3 of output overhead

### 6. Batch style conversion (HIGH effort, MEDIUM impact)
- `syntect_style_to_py()` creates `PyStyle` with nested `PyColor` and `PyFontStyle`
- For bulk operations, convert multiple styles in one pass
- Flatter representation: encode `(fg_r, fg_g, fg_b, fg_a, bg_r, bg_g, bg_b, bg_a, font_bits)` as a single struct

---

## Implementation Order

1. Pre-allocation (quick win, no risk)
2. Direct output generation from syntect types (biggest impact)
3. HTML generation optimization
4. Terminal escape optimization
5. Lazy terminal output
6. Batch style conversion (if time permits)
