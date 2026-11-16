"""Utilitas untuk menampilkan data dalam bentuk tabel ASCII di terminal."""

import shutil
import textwrap


def render_table(headers, rows, title=None, note=None, max_total=None):
    """Membuat tabel ASCII dengan word-wrap otomatis sesuai lebar terminal."""
    if max_total is None:
        max_total = max(shutil.get_terminal_size((110, 24)).columns - 1, 60)

    headers = [str(h) for h in headers]
    rows = [[str(c) for c in r] for r in rows]
    n = len(headers)

    def longest(text):
        return max((len(line) for line in text.split("\n")), default=0)

    widths = [max([longest(headers[i])] + [longest(r[i]) for r in rows])
              for i in range(n)]

    # Kecilkan kolom terlebar sampai tabel muat di terminal.
    overhead = 3 * n + 1
    while sum(widths) + overhead > max_total and max(widths) > 8:
        widths[widths.index(max(widths))] -= 1

    def wrap_cell(text, width):
        lines = []
        for segment in text.split("\n"):
            lines.extend(textwrap.wrap(segment, width, break_long_words=True) or [""])
        return lines

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt_row(cells):
        wrapped = [wrap_cell(c, w) for c, w in zip(cells, widths)]
        height = max(len(c) for c in wrapped)
        return [
            "| " + " | ".join(
                (c[i] if i < len(c) else "").ljust(w)
                for c, w in zip(wrapped, widths)
            ) + " |"
            for i in range(height)
        ]

    lines = []
    if title:
        lines.append(title)
    lines += [sep] + fmt_row(headers) + [sep]
    for r in rows:
        lines += fmt_row(r)
    lines.append(sep)
    if note:
        lines += textwrap.wrap(note, max_total)
    return "\n".join(lines)


def tabel_detail(pairs, title, note=None):
    """Tabel vertikal dua kolom: Atribut | Keterangan."""
    return render_table(["Atribut", "Keterangan"], pairs, title=title, note=note)
