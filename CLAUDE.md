# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **LinkedIn Agentic App** - a multi-agent AI pipeline that transforms raw ideas into polished LinkedIn posts. It learns from past successful content by extracting a "Winning Formula" and uses it to evaluate, enhance, and generate new posts.

## Commands

```bash
# Run individual agents
python main.py evaluate    # Score new ideas (Status="New")
python main.py insight     # Generate 3 angles (Status="Shortlisted" + Channel="LinkedIn")
python main.py generate    # Create post drafts (Status="Shortlisted")
python main.py optimize    # Score and critique drafts (Status="Drafted")
python main.py resonance   # Analyze past posts and update Winning Formula

# Run full pipeline (evaluate → generate → optimize)
python main.py all

# Using virtual environment explicitly
./venv/bin/python main.py <command>
```

## Architecture

### 5-Agent Pipeline

```
[Resonance Agent] → Extracts "Winning Formula" from PDFs in My posts/
        ↓ (provides context to all other agents)
[Evaluator Agent] → Scores ideas (0-100) based on viral potential
        ↓
[Insight Agent]   → Generates 3 distinct angles per idea
        ↓
[Generator Agent] → Creates full post drafts
        ↓
[Optimizer Agent] → Scores drafts and provides feedback
```

### Key Components

| Path | Purpose |
|------|---------|
| `main.py` | Typer CLI entry point |
| `src/agents/` | Agent implementations (resonance, evaluator, insight, generator, optimizer) |
| `src/utils/llm.py` | Multi-LLM router (OpenAI/Anthropic based on model prefix) |
| `src/utils/notion.py` | Notion API wrapper with pagination |
| `prompts/*.md` | System prompts for each agent |
| `MASTER_BLUEPRINT.md` | Data-driven content patterns (hooks, emotions, scoring rules) |
| `.resonance_cache.json` | Cached Winning Formula (auto-invalidates on PDF changes) |

### LLM Routing

Models are selected per-agent via `.env`. The router in `llm.py` uses a simple rule:
- Model names starting with `claude-` → Anthropic API
- Everything else → OpenAI API

### Notion Integration

The system uses Notion as its database. Ideas flow through statuses:
`New` → `Shortlisted` → `Insights` → `Drafted`

Key properties: `Status`, `Channel`, `Potential Score`, `Notes`, `Angle 1/2/3`, `Post Draft`, `Engagement Score`, `Viral Potential`, `Post Draft Feedback`

### Smart Caching

The Resonance Agent uses MD5 file hashes to detect changes in `My posts/*.pdf`. Analysis is only re-run when files change, avoiding unnecessary LLM calls.

## Configuration

Required environment variables (see `.env.example`):

```
NOTION_API_KEY=
NOTION_DATABASE_ID=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=      # Optional if only using OpenAI models

# Model selection per agent
EVALUATOR_MODEL=gpt-4o-mini
INSIGHT_MODEL=claude-sonnet-4-5
GENERATOR_MODEL=gpt-4o
OPTIMIZER_MODEL=gpt-4o-mini
RESONANCE_MODEL=gpt-4o
```

## Adding a New Agent

1. Create `src/agents/<name>.py` with a `run_<name>_agent()` function
2. Create `prompts/<name>_agent.md` with the system prompt
3. Add CLI command in `main.py` using `@app.command()`
4. Add model config variable to `.env` (e.g., `NEW_AGENT_MODEL=`)
5. Document in `AGENTS_GUIDE.md`
