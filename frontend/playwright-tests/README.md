# Playwright Tests for The Last Centaur

This directory contains end-to-end tests for The Last Centaur game using Playwright.

## Setup

1. Install dependencies:

```bash
cd frontend
npm install
npm install -D @playwright/test
```

2. Install Playwright browsers:

```bash
npx playwright install
```

## Running Tests

Run all tests:

```bash
npx playwright test
```

Run a specific test file:

```bash
npx playwright test game-paths.spec.ts
```

Run in UI mode (with visual debugging):

```bash
npx playwright test --ui
```

## Test Structure

- `auth.spec.ts` - Authentication tests (login, registration)
- `game-basic.spec.ts` - Basic game functionality tests (movement, inventory, etc.)
- `game-paths.spec.ts` - Complete game path tests (warrior, mystic, stealth)

## Test Development

To add a new test:

1. Create a new file in this directory with a `.spec.ts` suffix
2. Import the necessary Playwright components
3. Define your test scenarios
4. Run the test to verify it works

## Debugging Tests

When tests fail, Playwright provides useful diagnostic information, including:

- Screenshots of the failure state
- A trace file that can be viewed in the Playwright Trace Viewer
- Console logs from the browser

To generate trace files, run:

```bash
npx playwright test --trace on
```

Then view the trace file with:

```bash
npx playwright show-trace test-results/trace.zip
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Add the following to your GitHub Actions workflow:

```yaml
- name: Install dependencies
  run: npm ci

- name: Install Playwright browsers
  run: npx playwright install --with-deps

- name: Run Playwright tests
  run: npx playwright test
```
