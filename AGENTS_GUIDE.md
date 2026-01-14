# 🤖 LinkedIn Agentic App: Agents Guide

This guide provides a deep dive into the four AI agents that power the LinkedIn content pipeline. The system is designed to learn from your past successes and automate the process from raw idea to polished, high-performance post.

---

## 1. 🧠 Resonance Agent (The Brain)
**Module**: `src/agents/resonance.py` | **Prompt**: `prompts/resonance_agent.md`

### Core Function
The Resonance Agent analyzes your successful past content and reverse-engineers a "Winning Formula". Instead of matching your work against generic rules, it discovers your unique style DNA.

### Technical Logic
1. **File Hashing**: Calculates MD5 hashes of PDF files in the `My posts/` directory.
2. **Smart Caching**: Checks `.resonance_cache.json`. If hashes match, it returns the cached context instantly to save costs.
3. **Dynamic Discovery**: If files change, it reads the PDFs (using `pypdf`) and asks the LLM to identify **at least 7 Archetypes** and **7 Hook Strategies** specific to your data.
4. **Context Injection**: Provides the "Winning Formula" as a Markdown summary to all other agents.

---

## 2. ⚖️ Evaluator Agent (The Gatekeeper)
**Module**: `src/agents/evaluator.py` | **Prompt**: `prompts/evaluation_agent.md`

### Core Function
Scores raw ideas found in Notion based on their viral potential and alignment with your "Winning Formula".

### Technical Logic
1. **Fetch**: Queries Notion for pages with `Status = "New"`.
2. **Scoping**: Skips any record that already has a `Potential Score`.
3. **Extraction**: Reads the topic title, the "Notes" property, and the **entire Page Body** (blocks) to get full context.
4. **Context**: Pulls the latest Winning Formula from the Resonance Agent.
5. **Analyze**: The LLM evaluates the idea on a scale of 0-100, considering your historical archetypes and emotional drivers.
6. **Update**: Writes the numeric score back to the `Potential Score` property in Notion.

---

## 3. 💡 Insight Agent (The Growth Hacker)
**Module**: `src/agents/insight.py` | **Prompt**: `prompts/insight_agent.md`

### Core Function
Generates 3 high-performing angles from rough notes to help you decide how to approach a topic for maximum resonance.

### Technical Logic
1. **Fetch**: Queries Notion for pages with `Status = "Shortlisted"` and `Channel = "LinkedIn"`.
2. **Extraction**: Like the Evaluator, it pulls content from both properties and the Page Body.
3. **Dynamic Strategy**: Instead of fixed types, it chooses the best **Archetypes** and **Hook Strategies** from your "Winning Formula" specifically for that idea.
4. **Generation**: Creates 3 distinct angles, each with a specific hook and narrative arc.
5. **Update**: 
    - Writes the results to `Angle 1`, `Angle 2`, and `Angle 3`.
    - Moves the status to **`Insights`** once processed.

---

## 4. ✍️ Generator Agent (The Writer)
**Module**: `src/agents/generator.py` | **Prompt**: `prompts/generation_agent.md`

### Core Function
Transforms raw notes into a high-quality LinkedIn post draft that mimics your high-performance content style.

### Technical Logic
1. **Fetch**: Queries Notion for pages with `Status = "Shortlisted"`.
2. **Extraction**: Reads notes from both properties and the Page Body.
3. **Blueprinting**: Combines the `MASTER_BLUEPRINT.md` (structural rules) with the resonance "Winning Formula".
4. **Generation**: Drafts a post using proven hooks and archetypes.
5. **Update**: Saves the result to the `Post Draft` property and moves the status to `"Drafted"`.

---

## 5. 🔍 Optimizer Agent (The Editor)
**Module**: `src/agents/optimizer.py` | **Prompt**: `prompts/scoring_agent.md`

### Core Function
Provides a critical "stress test" for generated drafts, scoring them and offering actionable feedback.

### Technical Logic
1. **Fetch**: Queries Notion for pages with `Status = "Drafted"`.
2. **Benchmark**: Compares the draft against the resonance "Winning Formula".
3. **Feedback**: Generates a detailed critique and a machine-readable score.
4. **Update**: 
    - Writes score to `Engagement Score`.
    - Writes potential to `Viral Potential`.
    - Places the full critique into `Post Draft Feedback`.

---

## 🛠️ Utility Scripts
In addition to the core agents, several utilities are available for maintenance and debugging:

- **`archive_old_ideas.py`**: Fetches ideas created before Oct 31, 2025, and marks their status as "Old". Useful for cleaning up a long-standing database.
- **`inspect_notion.py`**: Prints the schema (properties and types) of your configured Notion database.
- **`probe_notion.py`**: A diagnostic tool to verify that the app has write access to key properties like `Status` and `Potential Score`.
- **`check_notion_values.py`**: A flexible query tool used to audit specific records and verify that filters (like Channel or Status) are matching the intended data.

---

## ⚙️ Global Configuration
Each agent's AI model can be independently configured in your `.env` file:
- `EVALUATOR_MODEL`
- `INSIGHT_MODEL`
- `GENERATOR_MODEL`
- `OPTIMIZER_MODEL`
- `RESONANCE_MODEL` (Recommended: `gpt-4o`)
