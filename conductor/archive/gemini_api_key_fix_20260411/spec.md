# Specification: Gemini API Key Not Valid in Streamlit Chat Test

## Overview
When running a `research_agent` project with the `gemini` provider, sending a message in the Streamlit chat test UI results in a `RuntimeError: API Key not valid`. The goal of this track is to analyze the root cause of this issue and fix the underlying code so it correctly retrieves the `GOOGLE_API_KEY` from the environment.

## Context & Reproduction
*   **Provider:** Gemini (`provider=gemini`)
*   **Project Type:** `research_agent`
*   **Environment Variable in `.env`:** `GOOGLE_API_KEY`
*   **Reproduction Steps:** Run the Streamlit chat app, send a message in the UI, and observe the error.
*   **Expected Behavior:** The agent should successfully read the API key from the environment and process the message.

## Functional Requirements
*   **Backend Fix Only:** The solution should fix the underlying code to ensure the `GOOGLE_API_KEY` is properly loaded and passed to the LangChain/LangGraph Gemini LLM integration.
*   **Fail Fast:** If the environment variable is missing or invalid at startup or invocation, the backend should fail fast with a clear exception, rather than failing silently or late in the execution.

## Non-Functional Requirements
*   No new UI components for API key input are required.

## Acceptance Criteria
*   The `research_agent` starts up successfully using `streamlit run`.
*   Sending a message in the chat UI returns a valid response from the Gemini model without throwing a `RuntimeError: API Key not valid`.
*   Unit tests pass successfully.

## Out of Scope
*   Adding API key input fields to the Streamlit UI sidebar.
*   Fixing API key issues for providers other than Gemini.