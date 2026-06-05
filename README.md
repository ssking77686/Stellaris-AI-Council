# Stellaris AI Council · 群星AI智囊团

一个《群星》游戏辅助工具。六位 AI 大臣读取你的游戏存档，分析帝国现状，提出战略建议。AI 只建议，不替你操作——所有决策由你审批。另，大臣们讲中文。

**快速开始：** Python 3.10+、Node.js 20+、DeepSeek API key 三样准备好，然后 `cd backend && pip install -r requirements.txt && cp .env.example .env`（编辑 .env 填 key），再 `cd ../stellaris-command-center && pnpm install`，最后回项目根目录 `python start.py`。浏览器打开 `http://localhost:5173` 就能用了。

A companion tool for Paradox's [Stellaris](https://www.paradoxinteractive.com/games/stellaris/about). Six AI ministers — finance, military, science, foreign affairs, interior, and construction — read your save files and offer strategic advice. They propose, you decide. Nothing is automated without your approval.

> **Note:** The UI and agent personalities are currently in Chinese. That said, the code, APIs, and save parser are language-agnostic, and you can swap the system prompts to English in `backend/app/agents/base.py`. If there's demand for English localization, open an issue or ping me — happy to prioritize it.

---

## What it does

- **Save file parsing** — Upload a `.sav` file (or point it at your save directory for automatic monitoring). The parser extracts your empire's resources, planets, fleets, technologies, and all known AI empires.
- **AI minister chat** — Each of the six ministers has a distinct personality and domain. They see your actual game state every time you talk to them.
- **Proposal system** — Ministers generate structured proposals (build this, research that, declare war on them). They land in an approval panel where you can accept or reject.
- **Imperial court sessions** — All six ministers debate an agenda topic in a multi-round discussion, streamed in real time via WebSocket.
- **Chronicle** — A timeline of all events, proposals, coordination tasks, and court sessions.

The core loop: you play Stellaris → the tool picks up your save → ministers analyze it → they make suggestions → you decide.

---

## Current state

The project is **functional and I use it regularly**, but it's not polished. Here's the honest breakdown:

**Working well:**
- Save upload and directory monitoring (watchdog + 2s debounce)
- The streaming Clausewitz tokenizer handles 100MB+ save files without loading them entirely into memory
- Empire dashboard with live resource bars, minister cards, and alert notifications
- All six agent personalities with game-state injection on every message
- Proposal approval workflow (accept / reject / modify)
- Court sessions with multi-turn discussion
- WebSocket push for save updates, court speeches, and new proposals
- Neighbor empire extraction (military power, economy, tech, government type, personality)

**Partial / rough:**
- Technology and leader extraction works but analysis is shallow
- Diplomacy beyond war status and neighbor summaries is not yet implemented
- The UI is functional but could use a design pass
- English localization — the agents speak Chinese, the frontend is Chinese

**Not yet done:**
- Hyperlane network / strategic chokepoint analysis (the full galaxy graph is in the save, just not parsed)
- Automated tests
- macOS / Linux testing (it should work, but I only run it on Windows 11)

---

## Quick start

You need Python 3.10+, Node.js 20+, and a [DeepSeek API key](https://platform.deepseek.com/).

```bash
git clone <repo-url>
cd <repo-name>

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env    # edit .env, add your DeepSeek key

# Frontend
cd ../stellaris-command-center
pnpm install

# Launch (from project root)
cd ..
python start.py
```

Open `http://localhost:5173` for the dashboard, `http://localhost:8001/docs` for the API reference.

To switch the AI model, edit `backend/.env` — the project uses the OpenAI-compatible API format, so any provider with that interface should work (Claude via Anthropic, GPT via OpenAI, local models via Ollama, etc.), though only DeepSeek has been tested.

---

## How the save parser works

Stellaris saves are zip files containing a `gamestate` in Paradox's Clausewitz text format — hundreds of megabytes of nested `key=value` and `key={...}` blocks. Loading it all into memory at once isn't practical.

The parser (`clausewitz_tokenizer.py`) does a two-pass stream:
1. First pass locates the player's country index from the `player` block near the top of the file
2. Second pass scans every top-level key, extracts only the sections we care about (country, planets, fleets, technology, species, leaders, wars), and skips everything else with depth-aware block skipping

This keeps memory usage bounded to the size of the largest single extracted block (typically a few MB) rather than the entire gamestate.

---

## Tech stack

| Layer | What | Why |
|-------|------|-----|
| Frontend | React 19 + TypeScript + Vite + Tailwind + shadcn/ui | Dark sci-fi theme, component library |
| Backend | Python + FastAPI + Uvicorn | Async, WebSocket-native, auto-docs |
| AI | DeepSeek API (OpenAI-compatible) | Strong Chinese, good value, standard SDK |
| Database | SQLite + SQLAlchemy 2.0 (async) + aiosqlite | Zero setup, JSON columns for flexible save format |
| Save parsing | Custom streaming Clausewitz tokenizer | 100MB+ files, extract-only-what-you-need |
| Save watching | watchdog | Cross-platform FS events, debounced |
| Scheduling | APScheduler | Periodic reports, auto court sessions |

---

## Project layout

```
├── start.py / start.bat
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── agents/base.py          # Minister definitions + prompt templates
│       ├── api/                    # REST + WebSocket endpoints
│       ├── core/
│       │   ├── clausewitz_tokenizer.py
│       │   ├── save_parser.py
│       │   ├── save_watcher.py
│       │   ├── agent_engine.py
│       │   ├── agent_coordinator.py
│       │   ├── court_orchestrator.py
│       │   └── scheduler.py
│       └── models/
├── stellaris-command-center/       # React frontend
│   └── src/
│       ├── pages/                  # Dashboard, AgentChat, CourtHall, etc.
│       ├── components/             # UI components + shadcn/ui
│       └── api/                    # API client + WebSocket hook
└── prototype/                      # Early HTML mockups
```

---

## Known limitations

- **Single-user local tool** — not SaaS, no auth, no multi-tenancy; runs on your machine
- **Save format compatibility** — major Stellaris patches can change field names; if your save fails to parse, open an issue
- **Large saves** — late-game 100MB+ saves take 3-8 seconds to parse depending on your hardware
- **Chinese-only UI for now** — to make it English-friendly, you'd need to swap the agent prompts in `agents/base.py` and translate the frontend strings; the architecture supports it, it just hasn't been done

---

## Contributing

Issues and PRs welcome. Areas where help would be especially valuable:

- **Save compatibility testing** — try it with your save and report breakage
- **English (or other language) localization** — swap the prompts, translate the UI strings
- **Tests** — there are currently none
- **Hyperlane / geography analysis** — the galaxy graph data is all there in the save

---

## License

MIT

---

*Stellaris is a registered trademark of Paradox Interactive. This is a fan-made, non-commercial tool.*
