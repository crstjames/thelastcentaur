import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

// Create a random test user
const testUser = {
  username: `test_user_${Math.floor(Math.random() * 10000)}`,
  password: "password123",
  email: `test${Math.floor(Math.random() * 10000)}@example.com`,
};

// Ensure log directory exists
const logDir = path.join(process.cwd(), "playwright-logs");
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// Log function to save detailed testing information
function logStep(step: string, details: unknown = "") {
  const timestamp = new Date().toISOString();
  const logMessage = `${timestamp} - ${step}`;
  console.log(logMessage);

  // Append to log file
  fs.appendFileSync(
    path.join(logDir, "game-test.log"),
    `${logMessage}${details ? ": " + JSON.stringify(details) : ""}\n`
  );
}

test.describe("The Last Centaur - Coordinate Game Diagnostic Tests", () => {
  test.beforeEach(async ({ page }) => {
    logStep("Starting test");

    // Navigate to homepage
    logStep("Navigating to homepage");
    await page.goto("http://localhost:3002/");

    // Take screenshot of the homepage
    await page.screenshot({ path: path.join(logDir, "homepage.png") });

    // Click on the start prompt to enter the dashboard
    const startPrompt = page.locator(".start-prompt");
    if (await startPrompt.isVisible()) {
      logStep("Clicking start prompt");
      await startPrompt.click();
      await page.waitForTimeout(500);
    }

    // Take screenshot of the dashboard
    await page.screenshot({ path: path.join(logDir, "dashboard.png") });

    // Handle login flow
    await handleLogin(page);
  });

  // Helper function to handle login
  async function handleLogin(page) {
    // Check if we're on the login page
    const loginForm = page.locator("form").filter({ hasText: "LOGIN" });

    if (await loginForm.isVisible()) {
      logStep("Login form visible, attempting to login");
      await page.screenshot({ path: path.join(logDir, "login-form.png") });

      // Log all form inputs on the page
      const inputs = await page.locator("input").all();
      for (const input of inputs) {
        const id = await input.getAttribute("id");
        const type = await input.getAttribute("type");
        const placeholder = await input.getAttribute("placeholder");
        logStep(`Found input field`, { id, type, placeholder });
      }

      // Fill login form
      try {
        await page.fill("#username", testUser.username);
        await page.fill("#password", testUser.password);

        // Find the login button within the form
        const loginButton = loginForm.locator('button:has-text("LOGIN")');
        if (await loginButton.isVisible()) {
          logStep("Clicking login button");
          await loginButton.click();
          await page.waitForTimeout(2000);
        } else {
          logStep("Login button not found");
        }
      } catch (error) {
        logStep("Error during login", { error: error.message });
        await page.screenshot({ path: path.join(logDir, "login-error.png") });
      }
    } else {
      logStep("Login form not visible, checking if we need to register");

      // Check for registration link
      const registerLink = page.getByText("REGISTER");
      if (await registerLink.isVisible()) {
        logStep("Clicking register link");
        await registerLink.click();
        await page.waitForTimeout(1000);

        // Fill registration form
        try {
          await page.fill("#username", testUser.username);
          await page.fill("#email", testUser.email);
          await page.fill("#password", testUser.password);

          const registerButton = page.locator('button:has-text("REGISTER")');
          if (await registerButton.isVisible()) {
            logStep("Clicking register button");
            await registerButton.click();
            await page.waitForTimeout(2000);

            // After registration we may need to login
            await handleLogin(page);
          } else {
            logStep("Register button not found");
          }
        } catch (error) {
          logStep("Error during registration", { error: error.message });
          await page.screenshot({ path: path.join(logDir, "registration-error.png") });
        }
      }
    }
  }

  test("Diagnose game creation and command processing issues", async ({ page }) => {
    // Take screenshot of dashboard after login
    await page.screenshot({ path: path.join(logDir, "after-login.png") });

    // Log the current URL
    const currentUrl = page.url();
    logStep("Current URL after login", currentUrl);

    // Log all visible elements to understand the UI state
    await logVisibleUI(page);

    // Test API connectivity
    logStep("Testing direct API connectivity");
    try {
      const healthResponse = await page.request.get("http://localhost:8000/health");
      logStep("Health check status", healthResponse.status());

      // Make a direct API call to create a game (bypassing UI)
      const createGameResponse = await page.request.post("http://localhost:8000/api/games/", {
        data: { name: `Test Game ${Math.floor(Math.random() * 1000)}` },
        headers: { "Content-Type": "application/json" },
      });
      logStep("Direct API create game response", {
        status: createGameResponse.status(),
        body: await createGameResponse.json().catch(() => "Failed to parse JSON"),
      });
    } catch (error) {
      logStep("API request failed", { error: error.message });
    }

    // Find and click the New Game button (if present)
    try {
      // Look for New Game button
      const newGameButton = page.getByRole("button", { name: /New Game/i });
      if (await newGameButton.isVisible()) {
        logStep("New Game button found, clicking");
        await newGameButton.click();
        await page.waitForTimeout(2000);

        // Take screenshot after clicking New Game
        await page.screenshot({ path: path.join(logDir, "after-new-game-click.png") });

        // Log the HTML content for debugging
        const content = await page.content();
        fs.writeFileSync(path.join(logDir, "after-new-game-click.html"), content);

        // Check if a game name input appears
        const gameNameInput = page.locator(
          "input[placeholder*='game name' i], input[placeholder*='name' i], input#name"
        );
        if ((await gameNameInput.count()) > 0) {
          logStep("Game name input found, filling");
          await gameNameInput.fill(`Test Game ${Math.floor(Math.random() * 1000)}`);

          // Look for create/submit button
          const createButton = page.getByRole("button", { name: /Create|Submit|Start/i });
          if (await createButton.isVisible()) {
            logStep("Create button found, clicking");
            await createButton.click();
            await page.waitForTimeout(2000);
          } else {
            logStep("Create button not found");
          }
        } else {
          logStep("Game name input not found");
        }
      } else {
        logStep("New Game button not found");
      }
    } catch (error) {
      logStep("Error during game creation UI flow", { error: error.message });
    }

    // Look for the game console after creating a game
    await page.screenshot({ path: path.join(logDir, "after-game-creation.png") });
    await logVisibleUI(page);

    // Look for any game console or command input
    const gameConsole = page.locator(".game-panel, .game-console, .terminal");
    const commandInput = page.locator("input[type='text'], textarea").filter({ visible: true });

    if ((await gameConsole.count()) > 0) {
      logStep("Game console found");

      if ((await commandInput.count()) > 0) {
        logStep("Command input found, testing commands");

        // Test basic commands
        const commands = ["look", "help", "inventory"];

        for (const command of commands) {
          try {
            await commandInput.fill(command);
            await page.keyboard.press("Enter");
            await page.waitForTimeout(1000);

            // Capture the console output
            const outputElement = page.locator(".game-output, .output, .console-output, .message");
            if ((await outputElement.count()) > 0) {
              const text = await outputElement.textContent();
              logStep(`Output for command "${command}"`, { text });

              // Check if the output contains the "Game not loaded" error
              if (text && text.includes("Game not loaded")) {
                logStep('!!! CRITICAL ERROR: "Game not loaded" message detected');

                // Capture the full state for debugging
                await page.screenshot({ path: path.join(logDir, `error-game-not-loaded-${command}.png`) });

                // Capture HTTP traffic for the last request
                const requestData = await page.evaluate(() => {
                  return JSON.stringify({
                    localStorage: { ...localStorage },
                    sessionStorage: { ...sessionStorage },
                  });
                });

                fs.writeFileSync(path.join(logDir, "storage-data.json"), requestData);
              }
            } else {
              logStep(`No output element found for command "${command}"`);
            }
          } catch (error) {
            logStep(`Error executing command "${command}"`, { error: error.message });
          }
        }
      } else {
        logStep("Command input not found");
      }
    } else {
      logStep("Game console not found");
    }

    // Capture the network requests
    try {
      // Examine localStorage and sessionStorage
      const storageData = await page.evaluate(() => {
        return {
          localStorage: Object.keys(localStorage).reduce((acc, key) => {
            acc[key] = localStorage.getItem(key);
            return acc;
          }, {}),
          sessionStorage: Object.keys(sessionStorage).reduce((acc, key) => {
            acc[key] = sessionStorage.getItem(key);
            return acc;
          }, {}),
        };
      });

      logStep("Browser storage data", storageData);
      fs.writeFileSync(path.join(logDir, "storage.json"), JSON.stringify(storageData, null, 2));
    } catch (error) {
      logStep("Error capturing browser storage", { error: error.message });
    }
  });

  // Helper function to log visible UI elements
  async function logVisibleUI(page) {
    logStep("Logging visible UI elements");

    // Log all buttons
    const buttons = await page.locator("button").all();
    for (const button of buttons) {
      const text = await button.textContent();
      const isVisible = await button.isVisible();
      if (isVisible) {
        logStep(`Button visible: ${text || "[No text]"}`);
      }
    }

    // Log all form inputs
    const inputs = await page.locator("input").all();
    for (const input of inputs) {
      const id = await input.getAttribute("id");
      const type = await input.getAttribute("type");
      const isVisible = await input.isVisible();
      if (isVisible) {
        logStep(`Input visible`, { id, type });
      }
    }

    // Log main UI containers
    const containers = [
      { name: "Game console", selector: ".game-panel, .game-console, .terminal" },
      { name: "Login form", selector: "form:has(input[type='password'])" },
      { name: "Dashboard", selector: ".dashboard, .navbar, header" },
    ];

    for (const container of containers) {
      const element = page.locator(container.selector);
      const count = await element.count();
      const isVisible = count > 0 && (await element.isVisible());
      logStep(`Container: ${container.name}`, { exists: count > 0, visible: isVisible });
    }
  }
});
