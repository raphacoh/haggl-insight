"""Build the Jeff Horing edition from the built Insight deck.

Usage: python3 -I source/build_jeff.py index.html jeff/index.html
The Grok film and poster stay next to the Insight deck, so the Jeff deck links them with ../.
"""
import base64
import re
import sys
from pathlib import Path

here = Path(__file__).parent
src, out = Path(sys.argv[1]), Path(sys.argv[2])
html = src.read_text(encoding='utf-8')
SECTION = r'(<section class="slide[^"]*" id="([^"]+)".*?</section>)\n'


def replace_once(text, old, new):
    assert text.count(old) == 1, f'expected one match for {old[:70]!r}'
    return text.replace(old, new)


def pick(pattern, text):
    m = re.search(pattern, text, re.S)
    assert m, pattern
    return m.group(0)


sections = {m.group(2): m.group(1) for m in re.finditer(SECTION, html, re.S)}

# Pieces reused from the Insight deck: the install film, the agents' logos and Stripe's replies.
film = re.search(r'<div class="film-frame">(<video id="haggl-demo".*?</button>)</div>', sections['category'], re.S).group(1)
lockups = ''.join(pick(rf'<div class="agent-lockup" data-brand="{brand}"[^>]*>.*?</div>', sections['product'])
                  for brand in ['grok', 'claude', 'muse', 'dots', 'openclaw'])
replies = pick(r'<div class="email-replies">(?:<button.*?</button>)+</div>', sections['partner-emails'])
icon = ('<svg viewBox="10 20 240 200" aria-hidden="true"><path fill="#FF4A1C" '
        'd="M90 20L10 100L90 180L125 145L80 100L125 55Z M170 60L250 140L170 220L135 185L180 140L135 95Z"/></svg>')
RIVALS = [('profound', 'Profound'), ('peec', 'Peec AI'), ('athena', 'AthenaHQ'), ('scrunch', 'Scrunch'), ('limy', 'Limy')]
rivals = ''.join(f'<span class="rival"><img src="data:image/png;base64,{base64.b64encode((here / "logos" / f"{key}.png").read_bytes()).decode()}" alt=""><span>{name}</span></span>'
                 for key, name in RIVALS)

new = (here / 'jeff.html').read_text(encoding='utf-8')
for key, value in {'{{INSTALL_FILM}}': film, '{{AGENT_LOCKUPS}}': lockups, '{{STRIPE_REPLIES}}': replies,
                   '{{HAGGL_ICON}}': icon, '{{RIVALS}}': rivals}.items():
    assert key in new, key
    new = new.replace(key, value)
sections.update({m.group(2): m.group(1) for m in re.finditer(SECTION, new, re.S)})

s = sections['vision-2022']
s = replace_once(s, '<p>Slide 3 of the 2022 Moojo pitch.</p>',
                 '<p>Before Moojo I led product at Waze and was a director of product at Google. I started Moojo in 2022 to give every shopper personalized cashback on every purchase, priced by what that customer is worth to the merchant. This is slide 3 of that first pitch.</p>')
sections['vision-2022'] = s

s = sections['attention-2024']
s = replace_once(s, '<p>Slide 4 of the September 2024 Moojo thesis.</p>',
                 '<p>In September 2024 I wrote that agents would end the attention economy, and that brands would have to ask how much each customer is worth to them. This is that slide.</p>')
sections['attention-2024'] = s

s = sections['grok-demo']
s = replace_once(s, 'poster="grok-poster.jpg" src="grok-demo.mp4"', 'poster="../grok-poster.jpg" src="../grok-demo.mp4"')
s = replace_once(s, '<img src="grok-poster.jpg" alt="">', '<img src="../grok-poster.jpg" alt="">')
s = replace_once(s, '<p>a Lisbon hotel, once the agent showed one booking email from my Gmail</p>',
                 '<p>a Lisbon hotel booked direct, less than the 15–25% hotels pay Booking</p>')
sections['grok-demo'] = s

s = sections['performance']
s = replace_once(s, '<p class="arr-range" data-edit-key="performance-primary-range">24.9% → 65.0%</p>',
                 '<p class="arr-range arr-explain" data-edit-key="performance-primary-range">The share of shopping agents that recommend your store for the same shopping task, from 24.9% without haggl.ai to 65.0% with it</p>')
sections['performance'] = s

s = sections['candidates']
s = replace_once(s, 'data-title="What a few million buys"', 'data-title="The acquisition"')
s = replace_once(s, '<h2>A few million dollars buys long‑term merchant relationships</h2>',
                 '<h2>We buy a coupon site so the network starts with merchants on day one</h2>')
s = replace_once(s, '<template class="notes"><p>Other coupon',
                 '<template class="notes"><p>Coupon sites fight over the same static codes and affiliate fees. We open the one we buy to agents only, and every code becomes a single-use offer priced for one shopper and paid from the merchant’s acquisition budget.</p><p>Other coupon')
sections['candidates'] = s

ORDER = ['mission', 'vision-2022', 'attention-2024', 'what-is-haggl', 'grok-demo', 'performance', 'price-not-content',
         'install', 'consent', 'stripe', 'programmatic-offers', 'candidates', 'own-the-category']
main = re.search(r'(<main id="presentation"[^>]*>\n)(.*?)(\n</main>)', html, re.S)
html = html[:main.start(2)] + '\n'.join(sections[k] for k in ORDER) + html[main.end(2):]

# The flywheel slide isn't in this edition, so the deck script must not assume its elements exist.
html = replace_once(html, "function syncLoop(){const which=", "function syncLoop(){if(!document.querySelector('#loop-explanation'))return;const which=")
html = replace_once(html, "clone.querySelector('#loop-explanation').textContent=explanations.all;clone.querySelector('#loop-explanation').dataset.editKey='flywheel-explanation:all';",
                    "const loopNote=clone.querySelector('#loop-explanation');if(loopNote){loopNote.textContent=explanations.all;loopNote.dataset.editKey='flywheel-explanation:all';}")
html = replace_once(html, "clone.querySelector('.flywheel-diagram').classList.remove('filtered');", "clone.querySelector('.flywheel-diagram')?.classList.remove('filtered');")

css = (here / 'jeff.css').read_text(encoding='utf-8')
html = replace_once(html, '</style>\n</head>', css.strip() + '\n</style>\n</head>')
html = replace_once(html, '<span class="edition">Raphael Cohen / October 2026</span>', '<span class="edition">Raphael Cohen / November 2026</span>')
html = replace_once(html, 'HAGGL · OCTOBER 2026', 'HAGGL · NOVEMBER 2026')
html = replace_once(html, '<span class="page-number" id="page-number">01 / 13</span>', f'<span class="page-number" id="page-number">01 / {len(ORDER)}</span>')
html = replace_once(html, 'aria-label="Haggl category plan and the use of funds"', 'aria-label="haggl.ai for Insight Partners"')
total = html.count('<section class="slide')
labels = iter(range(1, total + 1))
html, n = re.subn(r'aria-label="\d+ of \d+:', lambda m: f'aria-label="{next(labels)} of {total}:', html)
assert n == total == len(ORDER), (n, total)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding='utf-8')
print(f'{out}: {total} slides, {len(html):,} bytes')
