# Intel Tech Events Intelligence Dashboard

**Manager:** Chennagiri Sheshashai, Sowmya
**Team:** EPS COES GFX SRIOV Team

---

## What This Dashboard Does

This is a fully self-contained HTML dashboard that automatically tracks and displays technical conferences, paper submission deadlines, learning events, and technical talks relevant to the team. It covers two broad areas:

- **Core Tech Areas** - Virtualization, Graphics, AI, GenAI, AI Automation, Validation Automation, Display
- **Explore More Areas** - Cloud Computing, Cybersecurity, Robotics, Quantum, XR/AR/VR, DevOps, Semiconductor, IoT, Data Science

Events are organized into three geographic sections: **Bangalore/Nearby**, **India (Rest)**, and **Outside India (Global)**.

---

## How It Is Built

The dashboard is a single HTML file with no backend server or database. Everything runs inside the browser using JavaScript. It combines:

1. **Curated Event Data** - 50 hand-picked events (30 core + 20 explore) stored directly in the file as structured JavaScript objects, each with name, date, location, area, and link.
2. **Live News Feed** - On every page load, it fetches fresh articles from Google News RSS feeds and WikiCFP (call-for-papers site) using 19 targeted search queries across all technical areas.
3. **Intel Theme** - Styled with Intel brand colors (blue #0068b5, dark navy, light blue) for a professional look suitable for manager sharing.

---

## How It Fetches Live Data

Because browsers block direct cross-origin requests, the dashboard uses a **CORS proxy fallback chain** to fetch news:

1. Tries a direct fetch to Google News RSS (
ews.google.com/rss/search?q=...)
2. If blocked, falls back to pi.allorigins.win as a CORS proxy
3. If that fails, falls back to corsproxy.io

WikiCFP RSS is similarly fetched for paper submission deadlines (CFP = Call For Papers).

Each fetch returns XML which is parsed in-browser using DOMParser, extracting title, link, source, and date from each RSS item.

---

## How It Caches and Refreshes

To avoid fetching on every page load (which is slow and rate-limited), results are cached in the browser's localStorage:

| Cache | TTL |
|---|---|
| Core news cache | 6 hours |
| Explore news cache | 6 hours |

**Monday Auto-Refresh:** Every Monday, regardless of cache age, the dashboard automatically clears the cache and fetches fresh news. This ensures the team always starts the week with updated information.

**Manual Refresh:** A Refresh button in the header clears the cache immediately and re-fetches all news.

---

## How Events Are Displayed

Events go through a **urgency scoring system** based on how many days remain until the event date:

| Days Remaining | Label | Color |
|---|---|---|
| 7 days or fewer | URGENT | Red |
| 8 - 14 days | NEARING | Orange |
| 15 - 30 days | UPCOMING | Yellow |
| Beyond 30 days | Scheduled | Green |

An **Alert Bar** at the top shows pills for all urgent and nearing events at a glance. A **Paper Submissions table** separately tracks CFP deadlines with the same color coding.

---

## Edit Mode

The dashboard has a PIN-protected Edit Mode (intel2026) that allows authorized users to:
- Add new custom events (stored in localStorage)
- Delete existing events

All changes persist in the browser and do not affect what other users see.

---

## Auto-Update — How Events Stay Fresh Without Any Manual Work

A **GitHub Actions workflow** runs automatically every Monday at 6:00 AM IST. It:

1. Queries **WikiCFP** (a global call-for-papers database) across 15 technical areas using targeted RSS feeds
2. Parses each result to extract event name, date, location, and submission deadline
3. Filters out past events — only future events are kept
4. Injects the fetched events directly into `index.html` between special markers
5. Commits and pushes the updated file back to this repo
6. GitHub Pages automatically deploys the new version within ~1 minute

This means the dashboard updates itself every week — no one needs to touch the code or file manually.

The workflow can also be triggered manually at any time from the [Actions tab](../../actions).

---

## How It Fetches Live Data

Because browsers block direct cross-origin requests, the dashboard uses a **CORS proxy fallback chain** to fetch news on page load:

1. Tries a direct fetch to Google News RSS (`news.google.com/rss/search?q=...`)
2. If blocked, falls back to `api.allorigins.win` as a CORS proxy
3. If that fails, falls back to `corsproxy.io`

WikiCFP RSS is similarly fetched for paper submission deadlines (CFP = Call For Papers).

Each fetch returns XML which is parsed in-browser using `DOMParser`, extracting title, link, source, and date from each RSS item.

---

## File Structure in This Repo

```
tech-dashboard/
├── index.html                          # The complete dashboard (single self-contained file)
├── scripts/
│   └── fetch_events.py                 # Python script: fetches WikiCFP events, updates index.html
├── .github/
│   └── workflows/
│       └── update-events.yml           # GitHub Actions: runs fetch_events.py every Monday 6 AM IST
└── README.md                           # This file
```
