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

# Plain notes: the Aleph notes carry hedges and method caveats that don't belong in a pitch.
NOTE_EDITS = [
    ('<p>This is a literal screenshot of slide 3 from the archived 2022 “[external] Moojo pitch.” The original wording, colors, proportions and Feedback label are preserved.</p>',
     '<p>Slide 3 of the 2022 Moojo pitch.</p>'),
    ('<p>This is a literal screenshot of slide 4 from the frozen “Moojo Thesis” source, created September 2024 and last modified October 2024. The original 2025+ forecast and historical architecture remain historical claims.</p>',
     '<p>Slide 4 of the September 2024 Moojo thesis.</p>'),
    (' Hermes was publicly released before Q3 and is shown as part of the ecosystem available in that quarter, with a September release verified. Logos identify products and do not claim a Haggl partnership or tested integration.',
     ' Hermes shipped a September release.'),
    (' Stripe did not state a regional split or absolute purchase count. This is an external adoption signal, not Haggl transaction growth, and is retained alongside the US Muse estimate at the founder’s request.', ''),
    (' The US-only value is derived as 5.8M × 95.5% = approximately 5.54M, shown rounded to ~5.5M. Both source inputs are estimates, so this is a derived estimate rather than a separately measured exact count. Downloads represent app uptake, not shopping transactions or Haggl execution.',
     ' The US figure is 5.8M × 95.5%, about 5.5M.'),
    ('<p>My working assumption is that the buyer is', '<p>The buyer is'),
    ('<p>We still need to learn where customers will actually place us in their budgets. Loyalty budgets may also fund', '<p>Loyalty budgets can also fund'),
    ('The founder-supplied 83.9-second film is embedded unchanged and plays offline. It shows an installation-to-campaign product demonstration; the film is not independent evidence of a paid purchase or production conversion lift.',
     'The film shows haggl.ai from installation to a live campaign.'),
    (' Stripe’s public MCP is authenticated account-level API access; it does not establish automatic third-party Haggl tooling at every POS.', ''),
    (' No evidence establishes that either partner is buying Haggl as a customer; merchants remain the proposed campaign buyers.', ''),
    (' Existing supported identity claims and separately permitted financial insights are distinct from these requested spend-claim additions.', ''),
    (' Default rollout and spend-claim delivery are goals to agree, not completed commitments.', ''),
    (' This measures underlying account coverage, not Link users, shopping adoption or Haggl customers. Consumers choose which accounts to connect and can revoke access. No US-only Link user count is asserted.', ''),
    (' The visible ~425K rounds that crawler-detected store count. It is not Wix-certified active commerce or committed rollout eligibility; consumer and merchant populations are different units and must not be added.', ''),
    (' A joint announcement is part of the distribution thesis, not a signed announcement commitment.', ''),
    (' The distribution checkmark means a credible path to scale, not signed default placement or a completed deployment. Agents becoming a primary buyer is the business thesis; Link-channel growth and app downloads do not supply a market-wide shopping share.', ''),
    (' This is a hypothesis about recurring routes and reputation, not a claim that usage automatically trains every consumer model.', ''),
    (' This is an illustrative scenario, not a stated airline/Hilton partnership.', ''),
    (' I don’t know whether this will become defensible, and I don’t want us to obsess about it; we need to keep growing as fast as possible. The identity mechanism depends on permission to use customer context across the relevant merchants.', ''),
    (' We should be clear about which flows we can measure, especially where we do not have a reliable market-wide denominator.', ''),
    (' A quote or recommendation does not tell us that, and a synthetic test cannot establish paid conversion in production.', ''),
]


def replace_once(text, old, new):
    assert text.count(old) == 1, f'expected one match for {old[:70]!r}'
    return text.replace(old, new)


for old, new in NOTE_EDITS:
    html = replace_once(html, old, new)
html, n = re.subn(r'<p data-edit-key="product-logo-notes-frame">.*?</p>\n  ', '', html, flags=re.S)
assert n == 1, n
html, n = re.subn(r'(<section class="slide performance performance-simple" id="performance".*?<template class="notes">).*?(</template>)',
                  r'\1<p>ARR, the Agentic Recommendation Rate, is the share of shopping agents that recommend the store. Across 15 retail and hospitality categories it goes from 24.9% without haggl.ai to 65.0% with it.</p>\2',
                  html, flags=re.S)
assert n == 1, n

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
