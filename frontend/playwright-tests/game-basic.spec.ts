import { test, expect, Page } from "@playwright/test";

// Test user credentials
const TEST_USER = {
  username: `testuser_${Math.floor(Math.random() * 10000)}`,
  password: "password123",
  email: `test_${Math.floor(Math.random() * 10000)}@example.com`,
};

test.describe("The Last Centaur - Basic Game Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Set test timeout longer
    test.setTimeout(60000);

    // Enable console logging to diagnose API issues
    page.on("console", (msg) => console.log(`BROWSER LOG: ${msg.type()}: ${msg.text()}`));
    page.on("request", (request) => console.log(`Request: ${request.method()} ${request.url()}`));
    page.on("response", (response) => console.log(`Response: ${response.status()} ${response.url()}`));

    // Navigate to the homepage
    console.log("Navigating to homepage");
    await page.goto("http://localhost:3002");

    // If registration form is shown, register a new user
    console.log("Checking for registration form");
    if (await page.getByText("Register").isVisible()) {
      console.log("Registration form visible, registering new user");
      await page.getByRole("button", { name: "Register" }).click();

      // Fill in the registration form
      console.log("Filling registration form");
      await page.getByLabel("Username").fill(TEST_USER.username);
      await page.getByLabel("Email").fill(TEST_USER.email);
      await page.getByLabel("Password").fill(TEST_USER.password);
      await page.getByRole("button", { name: "Register", exact: true }).click();

      // Wait for registration to complete or return to login
      console.log("Waiting for registration to complete");
      await Promise.race([page.waitForURL("**/login"), page.waitForURL("**/dashboard")]);
    }

    // Login if we're on the login page
    console.log("Checking if on login page");
    if (page.url().includes("/login")) {
      console.log("On login page, logging in");
      await page.getByLabel("Username").fill(TEST_USER.username);
      await page.getByLabel("Password").fill(TEST_USER.password);
      await page.getByRole("button", { name: "Login" }).click();

      // Wait for login to complete
      console.log("Waiting for login to complete");
      await page.waitForURL("**/dashboard");
    }

    console.log("Authentication complete");
  });

  test("Create a new game and verify basic functionality", async ({ page }) => {
    try {
      // Try to create a new game
      console.log("Attempting to create new game");

      // Take screenshot of dashboard to debug
      await page.screenshot({ path: "dashboard_before_create.png" });

      // Check if New Game button exists
      const newGameButton = page.getByRole("button", { name: "New Game" });
      console.log("New Game button exists:", await newGameButton.isVisible());

      if (await newGameButton.isVisible()) {
        await newGameButton.click();

        // Take screenshot after clicking New Game
        await page.screenshot({ path: "new_game_dialog.png" });

        const createGameButton = page.getByRole("button", { name: "Create Game" });
        console.log("Create Game button exists:", await createGameButton.isVisible());

        if (await createGameButton.isVisible()) {
          await createGameButton.click();
        } else {
          console.log("Create Game button not found!");
          // Check what's visible on screen
          console.log("Visible elements:", await page.content());
        }
      } else {
        throw new Error("New Game button not found");
      }

      // Wait for game to load
      console.log("Waiting for game console to appear");
      await page.waitForSelector(".game-console", { timeout: 30000 });

      // Take screenshot of loaded game
      await page.screenshot({ path: "game_loaded.png" });
    } catch (error) {
      console.log("Error creating new game:", error);

      // Take error screenshot
      await page.screenshot({ path: "error_state.png" });

      // Check for any potential error messages on screen
      const errorText = await page.locator("text=error").allTextContents();
      console.log("Error messages on screen:", errorText);

      // Continue tests with existing game if possible
      console.log("Looking for existing games");
      const continueButtons = await page.getByText("Continue").all();
      console.log(`Found ${continueButtons.length} Continue buttons`);

      if (continueButtons.length > 0) {
        await continueButtons[0].click();
        await page.waitForSelector(".game-console", { timeout: 30000 });
      } else {
        console.log("No existing games found.");
        throw new Error("Cannot create or continue a game");
      }
    }

    // Basic game functionality tests
    console.log("Testing basic game functionality");

    // Check if game console is visible
    const gameConsole = page.locator(".game-console");
    expect(await gameConsole.isVisible()).toBeTruthy();

    // Execute 'look' command
    console.log("Executing look command");
    await page.getByPlaceholder("Enter command...").fill("look");
    await page.getByRole("button", { name: "Send" }).click();

    // Wait for response
    await page.waitForTimeout(2000);

    // Get game output
    const gameOutput = await page.locator(".game-output").textContent();
    console.log("Game output:", gameOutput);

    // Basic validation
    expect(gameOutput).toBeTruthy();
  });

  test("Check API health and connectivity", async ({ page, request }) => {
    // Test API connection directly
    console.log("Testing API health endpoint directly");
    const healthResponse = await request.get("http://localhost:8000/health");
    console.log("Health endpoint status:", healthResponse.status());
    console.log("Health endpoint body:", await healthResponse.text());

    // Test auth endpoint
    console.log("Testing auth endpoints");
    try {
      const loginResponse = await request.post("http://localhost:8000/api/v1/auth/login", {
        form: {
          username: TEST_USER.username,
          password: TEST_USER.password,
        },
      });
      console.log("Login response status:", loginResponse.status());
      const loginJson = await loginResponse.json();
      console.log("Login response:", JSON.stringify(loginJson, null, 2));

      if (loginJson.access_token) {
        // Test game endpoints with token
        console.log("Testing game endpoints with token");
        const gamesResponse = await request.get("http://localhost:8000/api/v1/game", {
          headers: {
            Authorization: `Bearer ${loginJson.access_token}`,
          },
        });
        console.log("Games list status:", gamesResponse.status());
        console.log("Games list:", await gamesResponse.text());
      }
    } catch (error) {
      console.log("API connectivity test error:", error);
    }
  });
});

async function testBasicCommands(page) {
  // List of basic commands to test
  const commands = [
    { cmd: "look", expectation: /You are in/ },
    { cmd: "inventory", expectation: /inventory|Inventory/ },
    { cmd: "help", expectation: /commands|Commands/ },
    { cmd: "map", expectation: /map|Map/ },
  ];

  // Execute each command and verify the output
  for (const { cmd, expectation } of commands) {
    // Type command
    await page.getByPlaceholder("Enter command...").fill(cmd);
    await page.getByRole("button", { name: "Send" }).click();

    // Wait for response
    await page.waitForTimeout(1000);

    // Verify response includes expected text
    const outputText = await page.locator(".game-output").textContent();
    expect(outputText).toMatch(expectation);
  }
}

async function testMovement(page) {
  // Get the initial position
  await page.getByPlaceholder("Enter command...").fill("look");
  await page.getByRole("button", { name: "Send" }).click();
  await page.waitForTimeout(1000);

  // Try each movement direction
  const directions = ["north", "east", "south", "west"];

  for (const direction of directions) {
    // Execute the movement command
    await page.getByPlaceholder("Enter command...").fill(direction);
    await page.getByRole("button", { name: "Send" }).click();

    // Wait for response
    await page.waitForTimeout(1000);

    // Check the output - should either show a new area or say you can't go that way
    const responseText = await page.locator(".game-output").textContent();

    if (responseText.includes("You are in") || !responseText.includes("can't go")) {
      console.log(`Successfully moved ${direction}`);
    } else {
      console.log(`Movement ${direction} was blocked - this may be expected`);
    }

    // Look around to see where we are
    await page.getByPlaceholder("Enter command...").fill("look");
    await page.getByRole("button", { name: "Send" }).click();
    await page.waitForTimeout(1000);
  }
}
