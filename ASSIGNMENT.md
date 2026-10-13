# Assignment: Build a 6-Agent Sequential Pipeline with Google ADK

**Module:** Agent Development Kit (ADK): Sequential Agents
**Type:** Individual / pairs (instructor's choice)
**Weight:** ____ % of final grade
**Released:** ____________ **Due:** ____________ (23:59)

---

## 1. Background

In class we built two sequential pipelines:

| Example | Pipeline |
|---|---|
| `version_2_sequential_website_agent` | requirements_writer → designer → code_writer → **HTML page** |
| `version_2_sequential_db_agent` | requirements_writer → designer → sql_writer → **SQLite DB** |

Both used three agents. In this assignment you will build a **longer pipeline with 6 agents**. Each agent does one job, saves its work to ADK **session state** through `output_key`, and the next agent reads that state.

---

## 2. Learning Objectives

By the end of this assignment you should be able to:

1. Design a multi-step workflow and split it into agents that each have **one responsibility**.
2. Wire agents together with `SequentialAgent(sub_agents=[...])`.
3. Pass data between agents with `output_key` and `{state_key}` placeholders in instructions.
4. Write clear, structured **instructions** (prompts) that produce predictable output.
5. Write **custom Python tools** and attach them to agents.
6. Run and debug a pipeline with `Runner` + `InMemorySessionService` and read the event stream.

---

## 3. The Default Project: "LaunchPad" (Product Launch Kit Generator)

The user types a one-line product idea, for example:

> *"A smart water bottle that tracks hydration for university students."*

Your pipeline turns that idea into a complete **launch kit**: research, personas, product strategy, marketing copy, a working landing page, and a QA review.

### Pipeline Blueprint

```
 User idea
    │
    ▼
┌──────────────────────┐   output_key: market_research_output
│ 1. market_researcher │──► output/<ts>_market_research.md
└──────────┬───────────┘
           ▼
┌──────────────────────┐   output_key: personas_output
│ 2. persona_builder   │──► output/<ts>_personas.md
└──────────┬───────────┘
           ▼
┌──────────────────────┐   output_key: product_strategy_output
│ 3. product_strategist│──► output/<ts>_product_strategy.md
└──────────┬───────────┘
           ▼
┌──────────────────────┐   output_key: marketing_copy_output
│ 4. copywriter        │──► output/<ts>_marketing_copy.md
└──────────┬───────────┘
           ▼
┌──────────────────────┐   output_key: landing_page_output
│ 5. landing_page_     │──► output/<ts>_landing_page.html
│    builder           │
└──────────┬───────────┘
           ▼
┌──────────────────────┐   output_key: qa_review_output
│ 6. qa_reviewer       │──► output/<ts>_qa_review.md
└──────────────────────┘
```

### Agent Contracts

Each agent **must** use the `name` and `output_key` below so grading scripts can check state.

| # | Agent `name` | Reads from state | `output_key` | Must produce | Tool(s) |
|---|---|---|---|---|---|
| 1 | `market_researcher_agent` | user message | `market_research_output` | Problem statement, target market, 3+ competitors (strengths/weaknesses), market gaps, risks | `write_text_file` |
| 2 | `persona_builder_agent` | `{market_research_output}` | `personas_output` | 3 personas: name, age, goals, pain points, buying triggers, a quote | `write_text_file` |
| 3 | `product_strategist_agent` | `{market_research_output}`, `{personas_output}` | `product_strategy_output` | Value proposition, MVP features (must-have / nice-to-have), pricing tiers, positioning statement, product name | `write_text_file` + **your custom tool** |
| 4 | `copywriter_agent` | `{personas_output}`, `{product_strategy_output}` | `marketing_copy_output` | Tagline, hero headline + sub-headline, 3 feature blurbs, 3 FAQs, CTA text, one social post per persona | `write_text_file` |
| 5 | `landing_page_builder_agent` | `{product_strategy_output}`, `{marketing_copy_output}` | `landing_page_output` | One self-contained HTML file (inline CSS, responsive) that uses the **exact** copy from agent 4 | `write_html_file` |
| 6 | `qa_reviewer_agent` | all of the above | `qa_review_output` | Score each artifact out of 10, list inconsistencies between agents (e.g. price differs between strategy and page), list fixes | `write_text_file` |

> **Important (we covered this in class):** ADK only substitutes `{key}` in instructions.
> Writing `state['personas_output']` in a prompt is just text and the model will **not** see the data.
> Always use `{personas_output}`.

---

## 4. Alternative Tracks (optional)

You may choose one of these instead of LaunchPad. Keep the **same rules**: 6 agents, `output_key` on each, at least 4 saved files, one custom tool, and a final reviewer agent.

| Track | Agents 1 → 6 |
|---|---|
| **Trip Planner** | destination_researcher → budget_planner → itinerary_builder → packing_list_writer → travel_guide_page_builder (HTML) → trip_reviewer |
| **Course Builder** | topic_analyst → syllabus_designer → lesson_writer → quiz_generator → course_page_builder (HTML) → pedagogy_reviewer |
| **Job Application Kit** | job_description_analyst → skills_matcher → resume_writer → cover_letter_writer → interview_prep_writer → application_reviewer |
| **Restaurant App DB** | requirements_writer → menu_designer → db_designer → sql_writer (SQLite) → sample_data_writer → schema_reviewer |
| **Your own idea** | Must be approved by the instructor by ____________ |

If you pick an alternative track, write your own contract table (like Section 3) at the top of your `README.md`.

---

## 5. Technical Requirements

### Must have (pass/fail)
- [ ] Exactly **6** `LlmAgent`s (5 is accepted only with instructor approval) wrapped in **one** `SequentialAgent` called `root_agent`.
- [ ] Every `LlmAgent` has a unique `name`, a `description.txt`, an `instructions.txt`, and an `output_key`.
- [ ] Prompts are loaded from files with `load_instructions_file(...)`. **No long prompts hard-coded in Python.**
- [ ] Agents 2–6 each read at least one earlier agent's output through `{state_key}`.
- [ ] At least **4 files** are written to `output/` in one run.
- [ ] At least **one custom tool that is not a file writer** (see 5.2).
- [ ] The pipeline runs end to end with `uv run agent_runner.py` **and** with `adk web`.

### 5.1 Instructions file structure
Every `instructions.txt` should follow this structure (see the `version_2_*` examples):

```
ROLE        – who the agent is (1–2 lines)
INPUTS      – which {state_keys} it reads, and what each contains
TASK        – numbered steps
OUTPUT FORMAT – exact markdown headings / HTML structure expected
RULES       – what it must NOT do (e.g. "do not invent new prices")
TOOL USAGE  – when and how to call the tool
```

### 5.2 Custom tool ideas (choose at least one)
| Tool | What it does | Used by |
|---|---|---|
| `calculate_pricing(cost: float, margin_percent: float) -> dict` | Returns price for 3 tiers | product_strategist |
| `count_words(text: str) -> dict` | Word/character count to enforce copy limits | copywriter |
| `check_html(html: str) -> dict` | Checks for `<title>`, `<meta viewport>`, closing tags | landing_page_builder / qa_reviewer |
| `get_today() -> dict` | Returns today's date for the launch timeline | product_strategist |
| `readability_score(text: str) -> dict` | Simple Flesch score | qa_reviewer |

Tools must have **type hints and a docstring**. ADK uses these to tell the model what the tool does.

---

## 6. Starter Code

The `starter/` folder has the same layout we used in class:

```
starter/
├── agent_runner.py                 # CLI runner (prints events + final state)
├── pyproject.toml
├── .env.example
├── agents/
│   ├── root_launch_pipeline/       # SequentialAgent  ← you add sub_agents
│   ├── market_researcher/          # ✅ COMPLETE worked example
│   ├── persona_builder/            # ✏️  TODO
│   ├── product_strategist/         # ✏️  TODO
│   ├── copywriter/                 # ✏️  TODO
│   ├── landing_page_builder/       # ✏️  TODO
│   └── qa_reviewer/                # ✏️  TODO
├── tools/file_writer_tool.py       # write_text_file ✅ , write_html_file ✏️ , custom tool ✏️
├── utils/                          # bedrock_llm.py + file_loader.py (same as class)
└── output/
```

Search the project for `TODO` to find every place you need to work.

### Run it
```bash
cd starter
cp .env.example .env        # add your AWS bearer token / region
uv sync
uv run agent_runner.py      # CLI
uv run adk web              # browser UI, pick "root_launch_pipeline"
```

**Tip:** Agent 1 is already wired into the root agent, so the project runs on day one. Add one agent at a time, run it, check the `output/` file and the state, then add the next one.

---

## 7. Deliverables

Submit **one zip** (or a GitHub link) containing:

1. Your completed `starter/` project (delete `.venv/` and `.env` first. **Never submit your keys.**)
2. `output/` from **two** full runs with two **different** product ideas.
3. `README.md` (1–2 pages) with:
   - your pipeline diagram and contract table
   - how to run it
   - a screenshot of `adk web` showing all 6 agents in the event trace
   - **Reflection** (about 300 words): Which agent was hardest to prompt and why? What inconsistency did the QA agent catch? What would you change if this were a `ParallelAgent` or `LoopAgent`?
4. A **2–3 minute screen recording** of one end-to-end run (optional, worth bonus marks).

---

## 8. Grading Rubric (100 points)

| Criteria | Excellent | Points |
|---|---|---|
| **Pipeline architecture** | 6 single-purpose agents, correct `SequentialAgent`, sensible order, no duplicated work | 15 |
| **State passing** | Every agent uses `output_key`; agents 2–6 correctly use `{state_key}`; outputs stay consistent across agents | 20 |
| **Instruction quality** | All prompts follow the ROLE/INPUTS/TASK/OUTPUT/RULES/TOOL structure; output is predictable across runs | 20 |
| **Tools** | File writers work; custom tool is useful, typed, documented, and actually called | 15 |
| **Final artifacts** | Landing page renders, is responsive, and uses the real copy; files are complete | 10 |
| **QA reviewer** | Gives real, specific critique and catches at least one cross-agent issue | 10 |
| **README & reflection** | Clear diagram, run steps, thoughtful reflection | 10 |
| **Bonus** (max +10) | Screen recording (+3) · `LoopAgent` that sends QA feedback back to the page builder until score ≥ 8 (+5) · `ParallelAgent` for agents 2 & 3 where valid (+2) | +10 |

**Deductions:** hard-coded prompts in Python (−5) · API keys in submission (−10) · pipeline does not run (graded on code only, max 50%).

---

## 9. Suggested Milestones

| Day | Milestone |
|---|---|
| 1 | Run the starter (agent 1 only). Read `market_researcher/` closely. |
| 2–3 | Agents 2 & 3 + custom tool. Check state in `adk web` → **State** tab. |
| 4 | Agent 4 (copy) & agent 5 (HTML). Open the HTML file in a browser. |
| 5 | Agent 6 (QA). Run two different ideas. Fix prompts based on QA feedback. |
| 6 | README, screenshots, reflection, submit. |

---

## 10. Hints & Common Pitfalls

- **Agent output is empty / agent skips work:** the model called the tool but returned no text. Tell it in RULES: *"After calling the tool, also return the full document as your final answer."* `output_key` stores the **final text response**, not the tool arguments.
- **Next agent "can't see" the previous output:** check spelling. `{personas_output}` must match the `output_key` exactly.
- **Missing state key error:** an earlier agent did not run or did not return text. Use `{key?}` only if the key is truly optional.
- **Nova Lite drifts or skips sections:** give it exact markdown headings to fill in. Small models follow templates much better than open-ended requests.
- **HTML gets cut off:** keep the page to 5–6 sections and inline CSS only. No external JS frameworks.
- Change `FINAL_AGENT_NAME` in `agent_runner.py` whenever you change which agent runs last.

---

## 11. Academic Integrity

You may use AI assistants to help you **debug**, but the prompts, tool code, and reflection must be your own work. You must be able to explain any line of your code if asked in a viva.
