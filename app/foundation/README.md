# Foundation

## Purpose

The `foundation` folder contains essential, shared code that forms the base of our application. This includes utilities, configurations, and core functionalities used across multiple domains of the project.

## Guidelines for Usage

1. **Shared Functionality Only**: Only place code here that is genuinely used across multiple domains of the application.

2. **Keep It Clean**: Maintain high code quality standards. This code will be widely used, so it needs to be robust and well-tested.

3. **Document Thoroughly**: Provide clear documentation for functions, classes, and modules. Include usage examples where appropriate.

4. **Avoid Domain-Specific Logic**: If a piece of code is specific to a single domain (e.g., deals, integrations), it doesn't belong here.

5. **Minimize Dependencies**: Code in this folder should have minimal dependencies on other parts of the project.

6. **Versioning Consideration**: Changes here may affect multiple parts of the application. Consider versioning strategies for significant changes.

7. **Performance Matters**: Optimize code in this folder, as it's likely to be used frequently.

## What Belongs Here

- Configuration management
- Authentication and authorization utilities
- Logging setup and utilities
- Common data structures
- Shared API client setups (e.g., for external services)
- Generic error handling
- Shared middleware
- Common validation utilities

## What Doesn't Belong Here

- Business logic specific to a single domain
- Database models (unless they're truly cross-cutting concerns)
- API route definitions
- Large, complex functionalities that are only used in one or two places

## Folder Structure

```
foundation/
├── __init__.py
├── config.py
├── auth/
│   ├── __init__.py
│   └── firebase.py
├── storage/
│   ├── __init__.py
│   └── gcs.py
└── logging/
    ├── __init__.py
    └── logger.py
```

## Review Process

Changes to this folder should be reviewed carefully. Consider implementing a more stringent review process for PRs affecting this directory.

## Questions?

If you're unsure whether a piece of code belongs in the `foundation` folder, discuss it with the team. It's better to have a conversation than to misplace code.