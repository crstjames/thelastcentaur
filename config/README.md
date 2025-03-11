# The Last Centaur - Configuration Files

This directory contains configuration files used by The Last Centaur game engine and testing tools.

## Authentication Files

### auth.json

Contains default test user credentials used for automated testing:

```json
{
  "username": "testuser2",
  "password": "password123"
}
```

### login.json

Contains alternative test user credentials:

```json
{
  "username": "testuser",
  "password": "testpassword"
}
```

### auth_secret.json

Contains secret keys used for authentication in tests.

## Usage

These configuration files are primarily used for testing and development purposes. They should not contain real user credentials or production API keys.

In production environments, sensitive information should be stored in environment variables or secure secret management systems, not in plain-text JSON files.
