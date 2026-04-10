# Specification: Streamlit UI FileNotFoundError Bugfix

## Overview
A `FileNotFoundError` occurs in the Streamlit UI backend (`streamlit/web/server/component_request_handler.py`) when submitting a simple query like "hi". The error is triggered while running the app from the project root.

## Bug Details
- **Triggering Action:** Submitting a text query (e.g., "hi") via the Streamlit chat UI.
- **Error Traceback:** `FileNotFoundError: [Errno 2] No such file or directory` at `streamlit/web/server/component_request_handler.py:55` during a file `open(abspath, "rb")` operation.
- **Execution Context:** `streamlit run ...` is executed from the project root directory.

## Functional Requirements
- Identify the resource or custom component (e.g., `st_chat_input_multimodal`) that Streamlit is attempting to load when a query is submitted.
- Ensure all paths to static assets or custom components used by the chat UI are resolved correctly or gracefully handle missing resources without crashing the request handler.

## Acceptance Criteria
- Submitting a basic query like "hi" through the Streamlit UI successfully processes and displays the response without throwing a `FileNotFoundError` in the console/logs.
- The UI maintains full functionality for chat interactions.

## Out of Scope
- Fixing issues unrelated to the chat input component or its direct resource dependencies.