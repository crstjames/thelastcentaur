# Contributing to The Last Centaur

Thank you for your interest in contributing to The Last Centaur! This document provides guidelines and instructions to help you get started.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Environment Setup](#development-environment-setup)
3. [API Development Guidelines](#api-development-guidelines)
4. [Frontend Development Guidelines](#frontend-development-guidelines)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Code Review Process](#code-review-process)

## Project Structure

The project is organized as follows:

```
thelastcentaur/
├── docs/                 # Documentation files
│   ├── api-reference.md  # API endpoint documentation
│   └── ...
├── frontend/             # Frontend React application
│   ├── app/              # Next.js app folder
│   ├── public/           # Static assets
│   └── ...
├── scripts/              # Utility scripts
│   ├── test_api_endpoints.py  # API testing script
│   └── ...
├── src/                  # Backend source code
│   ├── api/              # API routes
│   ├── auth/             # Authentication logic
│   ├── core/             # Core functionality
│   ├── db/               # Database models and session management
│   ├── game/             # Game logic and routes
│   └── main.py           # Application entry point
└── ...
```

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- PostgreSQL 14 or higher
- Docker and Docker Compose (optional, for containerized development)

### Setting Up the Backend

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/thelastcentaur.git
   cd thelastcentaur
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the backend:
   ```bash
   PYTHONPATH=. python -m src.main
   ```

### Setting Up the Frontend

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. Run the frontend:
   ```bash
   npm run dev
   ```

## API Development Guidelines

### Adding a New Endpoint

1. Define the endpoint in the appropriate router file in `src/game/router.py` or create a new router if needed.

2. Add the endpoint to the API reference documentation in `docs/api-reference.md`.

3. Create any necessary schemas in `src/game/schemas.py`.

4. Implement the endpoint logic.

5. Add tests for the endpoint in `scripts/test_api_endpoints.py`.

6. Update the frontend API client to include the new endpoint.

### API Best Practices

- Use consistent URL patterns as defined in `docs/code-review-template.md`.
- Always include authentication checks for protected endpoints.
- Properly validate all inputs using Pydantic models.
- Use appropriate HTTP status codes for responses.
- Add descriptive error messages to help clients understand issues.
- Document all endpoints in the API reference.

## Frontend Development Guidelines

### Adding a New Feature

1. Create any necessary API client methods in `frontend/app/services/api.ts`.

2. Use the constants from `frontend/app/constants/api-routes.ts` for API endpoints.

3. Implement the UI components.

4. Add error handling for API calls.

5. Ensure the UI is responsive and accessible.

### Frontend Best Practices

- Use TypeScript for all new code.
- Define interfaces for all data structures.
- Use React hooks and functional components.
- Follow the existing styling patterns.
- Include loading states for all asynchronous operations.
- Handle errors gracefully with user-friendly messages.
- Use the API client methods for all backend communication.

## Testing

### Running Backend Tests

1. Run the API endpoint tests:

   ```bash
   python scripts/test_api_endpoints.py
   ```

2. Run the authentication flow test:
   ```bash
   python scripts/test_auth_flow.py
   ```

### Running Frontend Tests

1. Run the frontend tests:
   ```bash
   cd frontend
   npm test
   ```

## Documentation

### API Documentation

- Keep the API reference in `docs/api-reference.md` up to date.
- Include all endpoints, request/response formats, and authentication requirements.

### Code Documentation

- Use docstrings for all Python functions and classes.
- Add comments for complex logic.
- Use JSDoc style comments for TypeScript/JavaScript functions.

## Pull Request Process

1. Fork the repository and create a new branch for your feature or bugfix.

2. Implement your changes, following the guidelines in this document.

3. Add or update tests as necessary.

4. Update documentation as needed.

5. Run the tests to ensure they pass.

6. Submit a pull request, using the template provided.

7. Address any feedback from code reviews.

## Code Review Process

All code changes go through a review process:

1. The PR will be reviewed using the checklist in `docs/code-review-template.md`.

2. Reviewers will provide feedback on the code.

3. Address the feedback and update the PR.

4. Once approved, the PR will be merged.

Thank you for contributing to The Last Centaur!
