# Add Research Agent Template Plan

## Objective
Add a new `research_agent` template to the `FastLangFrame/templates` directory. This template will provide a pre-configured architecture for a research-focused agent, specializing in query expansion, multi-source search (Web/Doc), data synthesis, and report generation.

## Key Files & Context
- **Base Template:** `multi_agent` template will be used as the structural foundation.
- **Target Directory:** `research_agent`
- **Files to Modify within `research_agent`:**
  - `copier.yml`: Update project defaults and descriptions.
  - `<%project_name%>/graph/state.py`: Define research-specific state variables (queries, results, report).
  - `<%project_name%>/graph/nodes.py`: Implement `ResearchPlannerNode`, `SearchNode`, and `SynthesisNode`.
  - `<%project_name%>/graph/builder.py`: Configure the LangGraph flow (Plan -> Search -> Synthesize).
  - `<%project_name%>/graph/prompts/default/`: Add prompt templates for the new nodes.
  - `<%project_name%>/graph/tools/research/`: Add mock tools for web search and retrieval.

## Implementation Steps
1. **Directory Duplication:** Copy the contents of the `multi_agent` template to a new `research_agent` directory using `cp -r`.
2. **Template Configuration:** Update `copier.yml` to reflect the "Research Agent" branding.
3. **Graph State Update:** Modify `state.py` to handle a collection of search results and the final research report.
4. **Node Implementation:**
   - Implement `ResearchPlannerNode`: Analyzes user query and generates a list of search tasks.
   - Implement `SearchNode`: Executes search tasks (mocking the search process).
   - Implement `SynthesisNode`: Aggregates all search results into a structured Markdown report.
5. **Prompt Management:** Create corresponding prompt files in `graph/prompts/default/` for each new node.
6. **Workflow Builder:** Update `builder.py` to wire these nodes into a cohesive graph.
7. **Cleanup:** Remove any leftover nodes or tools from `multi_agent` that do not serve the research purpose.

## Verification & Testing
1. **Template Scaffolding:** Use `copier` (if available) or a manual copy to create a test project from the new `research_agent` template.
2. **Execution Test:** Run the generated project's `main.py` and provide a research-oriented query (e.g., "Research the latest trends in LLM agents").
3. **Validation:** Confirm that the output is a structured report and that all graph nodes execute in the expected order.
