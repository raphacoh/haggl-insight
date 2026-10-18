"""Build the Insight edition: the approved Aleph deck plus the "What to do with the money" section.

Usage: python3 -I source/build.py <aleph index.html> <out index.html>
The Aleph deck is https://github.com/raphacoh/haggl-presentation (index.html, unchanged here).
"""
import re
import sys
from pathlib import Path

here = Path(__file__).parent
src, out = Path(sys.argv[1]), Path(sys.argv[2])
html = src.read_text(encoding='utf-8')

css = (here / 'money.css').read_text(encoding='utf-8')
slides = (here / 'money.html').read_text(encoding='utf-8')
targets = (here / 'targets.html').read_text(encoding='utf-8')
rows, notes = targets.split('<!-- NOTES -->')
slides = slides.replace('<!-- TARGET ROWS -->', rows.strip()).replace('<!-- TARGET NOTES -->', notes.strip())


def replace_once(text, old, new):
    assert text.count(old) == 1, f'expected one match for {old[:60]!r}'
    return text.replace(old, new)


html = replace_once(html, '</style>\n</head>', css.strip() + '\n</style>\n</head>')
html = replace_once(html, '</section>\n</main>', '</section>\n' + slides.strip() + '\n</main>')
html = replace_once(html, '<meta name="theme-color" content="#111111">',
                    '<meta name="theme-color" content="#111111">\n<meta name="robots" content="noindex, nofollow">')
# Aleph's decision slide (decide this week or close the company) stays out of the Insight edition.
html, n = re.subn(r'<section class="slide dark decision" id="decision".*?</section>\n', '', html, flags=re.S)
assert n == 1, n
total = html.count('<section class="slide')
labels = iter(range(1, total + 1))
html, n = re.subn(r'aria-label="\d+ of \d+:', lambda m: f'aria-label="{next(labels)} of {total}:', html)
assert n == total, n
html = replace_once(html, 'aria-label="Haggl category plan"', 'aria-label="Haggl category plan and the use of funds"')
out.write_text(html, encoding='utf-8')
print(f'{out}: {total} slides, {len(html):,} bytes')
