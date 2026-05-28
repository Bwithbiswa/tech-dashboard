# Intel Tech Events Intelligence Dashboard

## Open Dashboard

### [Click here to open the Live Dashboard](https://bwithbiswa.github.io/tech-dashboard/)

> Opens directly in any browser — no download, no login required.
> Share this URL with your team or manager.

---

**Manager:** Chennagiri Sheshashai, Sowmya
**Team:** EPS COES GFX SRIOV Team

---

## What This Dashboard Does

A self-contained HTML dashboard that automatically tracks and displays technical conferences, paper submission deadlines, learning events, and talks relevant to the team. Covers two broad areas:

- **Core Tech Areas** — Virtualization, Graphics, AI, GenAI, AI Automation, Validation Automation, Display
- **Explore More Areas** — Cloud Computing, Cybersecurity, Robotics, Quantum, XR/AR/VR, DevOps, Semiconductor, IoT, Data Science

Events are organized into three geographic sections: **Bangalore/Nearby**, **India (Rest)**, and **Global/Outside India**.

---

## How It Is Built

A single HTML file with no backend server or database. Everything runs in the browser using JavaScript:

1. **Curated Event Data** — 60+ hand-picked events (name, date, location, area, link) as a reliable baseline.
2. **Live Event Fetch (browser)** — On every page load, the browser queries WikiCFP RSS feeds across 8 technical areas and merges live CFP/conference entries into the event board. Cached for 24 hours.
3. **Live News Feed** — On every page load, fetches fresh articles from Google News RSS using 10 targeted queries. Cached for 6 hours.
4. **Intel Theme** — Styled with Intel brand colors for a professional look.

---

## How Live Data Is Fetched

Because browsers block direct cross-origin requests, a **CORS proxy fallback chain** is used:

1. Tries a direct fetch (works if the remote allows CORS)
2. Falls back to `api.allorigins.win`
3. Falls back to `corsproxy.io`

This applies to both the Google News RSS feed and the WikiCFP RSS event feed.

---

## Cache & Refresh Schedule

| Data | Cache TTL |
|---|---|
| Live WikiCFP events | 24 hours |
| Core news feed | 6 hours |
| Explore news feed | 6 hours |

**Monday Auto-Refresh:** Every Monday all caches are cleared and everything re-fetches fresh automatically.

**Manual Refresh:** The **Refresh** button in the header clears all caches and re-fetches live.

---

## Event Urgency System

| Days Remaining | Label | Colour |
|---|---|---|
| <= 7 days | URGENT | Red |
| 8 - 14 days | NEARING | Orange |
| > 14 days | Scheduled | Green |
| Past | Past | Grey |

A **Paper Submissions table** separately tracks CFP deadlines with the same colour coding.

---

## Edit Mode

PIN-protected Edit Mode lets you add, edit, or delete events. Use the **Push to GitHub** button (visible in Edit Mode) to save changes permanently to the repo — they go live for everyone in ~60 seconds.

The Edit Mode PIN is stored separately and shared privately with authorised team members. Do not share it publicly.

---

## Auto-Update via GitHub Actions

A GitHub Actions workflow runs every Monday at 6:00 AM IST:

1. Queries WikiCFP across 15 technical areas via RSS
2. Parses event name, date, location, and submission deadline
3. Filters out past events — only future events kept
4. Injects results into `index.html` between special markers
5. Commits and pushes — GitHub Pages deploys in ~1 minute

Trigger manually any time from the [Actions tab](../../actions).

---

## File Structure

```
tech-dashboard/
|- index.html                  # Complete dashboard - single self-contained file
|- scripts/
|  `- fetch_events.py          # Fetches WikiCFP events weekly (GitHub Actions)
|- .github/
|  `- workflows/
|     `- update-events.yml     # GitHub Actions: runs every Monday 6 AM IST
`- README.md                   # This file
```
