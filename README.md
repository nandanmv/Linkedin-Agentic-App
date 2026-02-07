# 🤖 LinkedIn Agentic App

An AI-powered content pipeline that automates the process of creating high-performance LinkedIn posts by learning from your past successes. This application integrates five specialized AI agents with Notion to evaluate ideas, generate content, and optimize drafts based on data-driven patterns.

## 🚀 Key Features

- **Data-Driven Analysis**: Automatically reverses-engineers your "Winning Formula" from your past successful posts.
- **Notion Integration**: Seamlessly connects to your Notion database to manage content ideas and drafts.
- **Multi-Agent Pipeline**:
  - **🧠 Resonance Agent**: The brain that identifies your unique style DNA.
  - **⚖️ Evaluator Agent**: Scores raw ideas based on viral potential.
  - **💡 Insight Agent**: Generates multiple strategic angles for each topic.
  - **✍️ Generator Agent**: Drafts posts using proven structural blueprints.
  - **🔍 Optimizer Agent**: Provides critical feedback and stress-tests drafts.

## 🛠️ Tech Stack

- **Language**: Python
- **CLI Framework**: Typer
- **UI/Terminal**: Rich
- **AI Models**: GPT-4o, Claude, etc. (Configurable)
- **Database**: Notion API
- **Content Analysis**: PyPDF

## ⚙️ Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nandanmv/Linkedin-Agentic-App.git
   cd Linkedin-Agentic-App
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file based on `.env.example` and fill in your API keys and configuration:
   - `NOTION_TOKEN`
   - `NOTION_DATABASE_ID`
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
   - Agent model configurations (e.g., `RESONANCE_MODEL=gpt-4o`)

## 📖 Usage

The application is controlled via a CLI:

- **Run the full pipeline**:
  ```bash
  python main.py all
  ```
- **Analyze past posts (Resonance)**:
  ```bash
  python main.py resonance
  ```
- **Evaluate new ideas**:
  ```bash
  python main.py evaluate
  ```
- **Generate insights/angles**:
  ```bash
  python main.py insight
  ```
- **Generate post drafts**:
  ```bash
  python main.py generate
  ```
- **Optimize drafts**:
  ```bash
  python main.py optimize
  ```

## 📂 Project Structure

- `src/agents/`: Logic for the AI agents.
- `prompts/`: Markdown templates for agent instructions.
- `My posts/`: Directory for your successful PDF posts (used by Resonance Agent).
- `MASTER_BLUEPRINT.md`: Data-driven structural rules for top-performing content.
- `AGENTS_GUIDE.md`: Detailed technical documentation of each agent's logic.

## 🧪 Utilities

Several helper scripts are included for maintenance:
- `inspect_notion.py`: Audit your Notion database schema.
- `archive_old_ideas.py`: Clean up old records in Notion.
- `check_notion_values.py`: Audit specific records and filters.

---
Built with ❤️ for LinkedIn content creators.
