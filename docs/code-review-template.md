# Code Review Template for The Last Centaur

This template provides a standard set of criteria to review when making changes to The Last Centaur codebase.

## API Changes Review Checklist

When reviewing API changes, verify the following points:

- [ ] **URL Consistency**: Does the URL follow the pattern `/api/v1/[resource]/{id}` or `/api/v1/[resource]/{id}/[subresource]`?
- [ ] **Documentation**: Is the endpoint documented in `docs/api-reference.md`?
- [ ] **Frontend Integration**: Are the corresponding frontend API client methods updated?
- [ ] **Types**: Are all input/output types properly defined in schemas?
- [ ] **Auth Requirements**: Is authentication properly implemented and documented?
- [ ] **Error Handling**: Does the endpoint return appropriate error codes and messages?
- [ ] **Tests**: Are there tests covering this endpoint in `scripts/test_api_endpoints.py`?

## Frontend Code Review Checklist

When reviewing frontend code changes:

- [ ] **API Calls**: Are API calls using the correct endpoints from `api.ts`?
- [ ] **Error Handling**: Is there appropriate error handling for failed API calls?
- [ ] **Loading States**: Are loading states properly managed?
- [ ] **React Patterns**: Does the code follow modern React patterns?
- [ ] **TypeScript**: Are types properly defined and used?
- [ ] **Accessibility**: Does the UI follow accessibility best practices?
- [ ] **Responsiveness**: Is the UI responsive to different screen sizes?

## Backend Code Review Checklist

When reviewing backend code changes:

- [ ] **API Contract**: Does the implementation match the API documentation?
- [ ] **Database**: Are database operations properly handled with appropriate error handling?
- [ ] **Performance**: Are there any performance concerns with the implementation?
- [ ] **Validation**: Is input validation properly implemented?
- [ ] **Authentication**: Is authentication handled correctly?
- [ ] **Authorization**: Is authorization checked before accessing resources?
- [ ] **Error Handling**: Is error handling comprehensive and user-friendly?
- [ ] **Logging**: Are appropriate logging statements included?

## Pull Request Template

```
## Description
[Description of the changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## API Changes
- [ ] No API changes
- [ ] New API endpoint
- [ ] Modified existing endpoint
- [ ] Deleted endpoint

## Frontend Changes
- [ ] No frontend changes
- [ ] New UI component
- [ ] Modified existing component
- [ ] Updated API client

## Backend Changes
- [ ] No backend changes
- [ ] New route/endpoint
- [ ] Modified existing route/endpoint
- [ ] Database changes

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing performed

## Documentation
- [ ] API documentation updated
- [ ] Code comments added/updated
- [ ] README updated

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## API Naming Conventions

To ensure consistency in the API, follow these conventions:

### URL Paths

- Use lowercase, kebab-case for multi-word path segments
- Use plural nouns for resources (e.g., `/games`, not `/game`)
- Nest sub-resources under their parent resource (e.g., `/games/{id}/commands`)

### Request Parameters

- Use camelCase for parameter names in JSON payloads
- Use snake_case for query parameters in URLs

### Response Fields

- Use camelCase for all JSON response fields
- Use consistent naming patterns for similar concepts

## Error Response Format

All API error responses should follow this format:

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "field": "field_name" // Optional, for validation errors
}
```

## Code Style Guidelines

### Python

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Use async/await for asynchronous code
- Document classes and functions with docstrings

### TypeScript/JavaScript

- Use TypeScript for all new code
- Define interfaces for all data structures
- Use async/await for asynchronous code
- Use functional components with hooks for React components

## Common Issues to Watch For

- **Duplicated API paths**: Ensure that API paths in `router.py` match those in frontend `api.ts`
- **Missing authorization checks**: All game endpoints must verify the user owns the resource
- **Inconsistent error handling**: Follow the error handling patterns in the codebase
- **Incomplete validation**: Validate all input data before processing
- **Hardcoded values**: Avoid hardcoding values that should be configurable
- **Missing documentation**: All new endpoints must be documented
