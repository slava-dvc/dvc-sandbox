# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Build Docker: `make build-app`
- Deploy: `make deploy-app`
- Full deployment: `make all`
- Run tests: `python -m pytest tests`
- Run single test: `python -m pytest tests/test_file.py::test_function`
- Run backend dev: `python3 -m app.backend --port 8000`

## Code Style Guidelines
- Python 3.12 with type hints in function signatures
- Imports organized: stdlib → third-party → local modules
- Use snake_case for functions/variables, PascalCase for classes, camelCase for json and database fields
- 4-space indentation throughout
- Domain-driven structure with common code in `foundation/`
- Use provided design patterns: `singleton.py`, `class_factory.py` 
- Exception handling with proper HTTP status codes
- Use `__all__` to define public API in modules
- Follow instructions and Keep it as simple as possible. Avoid overengineering 
- Avoid `else`. Use plain flow as much as possible.