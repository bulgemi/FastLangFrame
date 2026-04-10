# Track Specification: FastAPI Swagger Schema Improvement

## Overview
This track aims to improve the FastAPI Swagger UI experience for the Agent API. Currently, the Swagger UI provides a generic schema that might be difficult to use immediately. This improvement will include more descriptive schemas and sample user queries (e.g., "hi") to allow users to quickly test the API directly from the Swagger interface.

## Objectives
- Enhance Pydantic models used in FastAPI endpoints with better descriptions and examples.
- Provide sample user queries for common interactions.
- Ensure the Swagger UI reflects these improvements correctly.

## Technical Requirements
- Programming Language: Python 3.12
- Framework: FastLangFrame (FastAPI, Pydantic)
- Location: `src/core/api_models.py` and potentially other endpoint definitions.

## User Stories
- As a developer, I want to see clear descriptions of the API request and response fields in the Swagger UI.
- As a developer, I want to be able to click "Try it out" and have a sample query pre-filled so I can quickly test the API.
- As a developer, I want to see representative examples for all data types in the API schema.