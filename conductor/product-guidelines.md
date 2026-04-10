# Product Guidelines

## Core Principles
1. **Developer Experience (DX) First**: Every tool, template, and API should be intuitive for developers. Error messages should be helpful, and documentation should be clear.
2. **Modularity and Extensibility**: The framework must allow for easy replacement of LLM providers, database backends, and UI components.
3. **Simplicity Over Complexity**: Favor simple, readable code over clever abstractions. Avoid unnecessary dependencies.
4. **Reliability and Traceability**: Provide tools for tracing LLM execution (nodes, tools, state) to aid debugging and evaluation.

## Coding Style
- Follow PEP 8 for Python code.
- Use meaningful variable and function names.
- Type hints are mandatory for public APIs.
- Docstrings are required for core modules and functions.

## User Experience (UX)
- Streamlit UIs should be clean, responsive, and provide immediate feedback for agent actions.
- CLI output (`lapm`) should clearly indicate progress, success, and any errors.

## Testing Standards
- All core features and utility functions must have unit tests.
- Template-generated projects should include a basic test suite.
- Use `pytest` as the primary testing framework.