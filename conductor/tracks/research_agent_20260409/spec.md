# Track Specification: Create a new 'Research-Agent' project

## Overview
This track aims to create a new agent project named `research_agent` using the FastLangFrame framework. This project will demonstrate multi-agent orchestration, where multiple specialized agents collaborate to perform research on a given topic.

## Objectives
- Use the `multi_agent` template to bootstrap the project.
- Implement at least two specialized agents:
    - **Search Agent**: Responsible for finding relevant information online.
    - **Summarizer Agent**: Responsible for synthesizing the found information into a coherent report.
- Configure the LangGraph state to pass information between agents.
- Provide a Streamlit UI for user interaction and real-time node tracing.

## Technical Requirements
- Programming Language: Python 3.12
- Framework: FastLangFrame (LangChain, LangGraph, FastAPI, Streamlit)
- Project Structure: Follow the standard FastLangFrame project layout.
- Environment: Use `.env` for API keys (OpenAI, etc.).

## User Stories
- As a user, I want to provide a research topic.
- As a user, I want to see the progress of the research as different agents perform their tasks.
- As a user, I want to receive a final summarized report of the research findings.