"""
fetch_events.py
Runs in GitHub Actions every Monday.
Fetches live technical conference/CFP data from WikiCFP RSS feeds,
parses event details, and injects them into index.html between markers.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import json
import time
from datetime import date, datetime

# ── Queries: (search term, area tag used in dashboard) ──────────────────────
QUERIES = [
    ('virtualization hypervisor',       'virtualization'),
    ('GPU graphics rendering',          'graphics'),
    ('artificial intelligence',         'ai'),
    ('machine learning deep learning',  'ai'),
    ('large language model generative', 'genai'),
    ('display OLED AMOLED screen',      'display'),
    ('test automation validation',      'automation'),
    ('cloud computing kubernetes',      'cloud'),
    ('cybersecurity information security', 'security'),
    ('robotics autonomous systems',     'robotics'),
    ('quantum computing',               'quantum'),
    ('semiconductor VLSI chip design',  'semi'),
    ('internet of things embedded',     'iot'),
    ('data science analytics',          'data'),
    ('augmented reality virtual reality XR', 'xr'),
]

# Keywords that indicate an India-based event location
INDIA_KEYWORDS = [
    'india', 'bengaluru', 'bangalore', 'mumbai', 'delhi', 'hyderabad',
    'chennai', 'pune', 'kolkata', 'noida', 'gurgaon', 'gurugram',
    'ahmedabad', 'jaipur', 'kochi', 'trivandrum', 'bhubaneswar',
]

BLR_KEYWORDS = ['bengaluru', 'bangalore']


def fetch_wikicfp_rss(query: str) -> str | None:
    url = 'http://www.wikicfp.com/cfp/rss?q=' + urllib.parse.quote(query)
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; tech-dashboard-bot/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'  [WARN] fetch failed for "{query}": {e}')
        return None


def parse_date_str(s: str) -> date | None:
    """Parse strings like 'Jun 19, 2026' or 'January 12, 2026'."""
    s = s.strip().rstrip('.')
    for fmt in ('%b %d, %Y', '%B %d, %Y', '%b. %d, %Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_description(desc: str):
    """Extract (event_date, location, deadline) from a WikiCFP RSS description."""
    event_date = location = deadline = None

    m = re.search(r'When\s*:\s*(.+?)(?:\n|<)', desc)
    if m:
        raw = m.group(1).strip()
        start_part = raw.split(' - ')[0].strip()
        event_date = parse_date_str(start_part)

    m = re.search(r'Where\s*:\s*(.+?)(?:\n|<)', desc)
    if m:
        location = m.group(1).strip()

    m = re.search(r'(?:Deadline|Submission Deadline)\s*:\s*(.+?)(?:\n|<)', desc)
    if m:
        deadline = parse_date_str(m.group(1).strip())

    return event_date, location, deadline


def location_tag(loc: str | None) -> str:
    """Return 'blr', 'india', or 'global' based on location string."""
    if not loc:
        return 'global'
    low = loc.lower()
    if any(k in low for k in BLR_KEYWORDS):
        return 'blr'
    if any(k in low for k in INDIA_KEYWORDS):
        return 'india'
    return 'global'


def is_future(d: date | None) -> bool:
    return d is not None and d >= date.today()


def fmt(d: date | None) -> str:
    return d.strftime('%Y-%m-%d') if d else ''


# ── Fetch and parse events ───────────────────────────────────────────────────
events = []
seen_titles: set[str] = set()
event_id = 5000

for query, area in QUERIES:
    print(f'Fetching: {query}')
    xml_text = fetch_wikicfp_rss(query)
    if not xml_text:
        continue

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f'  [WARN] XML parse error: {e}')
        continue

    count = 0
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        link  = (item.findtext('link')  or '').strip()
        desc  = (item.findtext('description') or '').strip()

        if not title or title in seen_titles:
            continue

        event_date, location, deadline = parse_description(desc)

        # Skip if both event date and deadline are in the past or missing
        if not is_future(event_date) and not is_future(deadline):
            continue

        seen_titles.add(title)
        loc_str = location or 'Online / TBD'
        geo     = location_tag(location)

        events.append({
            'id':       event_id,
            'name':     title,
            'date':     fmt(event_date) if event_date else fmt(deadline),
            'loc':      loc_str,
            'area':     area,
            'link':     link,
            'type':     'paper' if deadline and not event_date else 'conference',
            'desc':     f'Submission deadline: {fmt(deadline)}' if deadline else '',
            'geo':      geo,
            'auto':     True,
        })
        event_id += 1
        count += 1
        if count >= 8:          # max 8 events per query
            break

    print(f'  → {count} events added')
    time.sleep(0.8)             # be polite to WikiCFP

print(f'\nTotal auto-fetched events: {len(events)}')

# ── Inject into index.html ───────────────────────────────────────────────────
START = '// === AUTO_EVENTS_START ==='
END   = '// === AUTO_EVENTS_END ==='

with open('index.html', encoding='utf-8') as f:
    html = f.read()

if START not in html or END not in html:
    print('ERROR: Markers not found in index.html')
    exit(1)

js_block = (
    f'{START}\n'
    '// Auto-fetched events from WikiCFP (updated weekly by GitHub Actions)\n'
    f'const AUTO_EVENTS = {json.dumps(events, indent=2)};\n'
    f'{END}'
)

html = re.sub(
    re.escape(START) + r'.*?' + re.escape(END),
    js_block,
    html,
    flags=re.DOTALL
)

# Update "Last refreshed" date so the static HTML reflects when data was fetched
today = date.today()
today_str = f'{today.day} {today.strftime("%b")} {today.year}'  # e.g. "29 May 2026"
html = re.sub(
    r'Last refreshed: \d{1,2} \w+ \d{4}',
    f'Last refreshed: {today_str}',
    html
)

with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

print(f'index.html updated with {len(events)} auto events (Last refreshed: {today_str}).')
