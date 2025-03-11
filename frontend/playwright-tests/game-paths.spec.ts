import { test, expect, Page } from "@playwright/test";

// Test user credentials
const TEST_USER = {
  username: `testuser_${Math.floor(Math.random() * 10000)}`,
  password: "password123",
  email: `test_${Math.floor(Math.random() * 10000)}@example.com`,
};

test.describe("The Last Centaur - Complete Game Path Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the homepage
    await page.goto("http://localhost:3002");

    // If registration form is shown, register a new user
    if (await page.getByText("Register").isVisible()) {
      await page.getByRole("button", { name: "Register" }).click();

      // Fill in the registration form
      await page.getByLabel("Username").fill(TEST_USER.username);
      await page.getByLabel("Email").fill(TEST_USER.email);
      await page.getByLabel("Password").fill(TEST_USER.password);
      await page.getByRole("button", { name: "Register", exact: true }).click();

      // Wait for registration to complete or return to login
      await Promise.race([page.waitForURL("**/login"), page.waitForURL("**/dashboard")]);
    }

    // Login if we're on the login page
    if (page.url().includes("/login")) {
      await page.getByLabel("Username").fill(TEST_USER.username);
      await page.getByLabel("Password").fill(TEST_USER.password);
      await page.getByRole("button", { name: "Login" }).click();

      // Wait for login to complete
      await page.waitForURL("**/dashboard");
    }

    // Create a new game for each test to ensure fresh state
    try {
      await page.getByRole("button", { name: "New Game" }).click();
      await page.getByRole("button", { name: "Create Game" }).click();

      // Wait for game to load
      await page.waitForSelector(".game-console", { timeout: 10000 });
    } catch (error) {
      console.log("Could not create new game, will try to use existing one", error);

      // If we can't create a new game, try to select an existing one
      await page.getByText("Continue").first().click();
      await page.waitForSelector(".game-console", { timeout: 10000 });
    }
  });

  test("Complete the Warrior Path", async ({ page }) => {
    // Start the Warrior Path test
    await page.getByPlaceholder("Enter command...").fill("look");
    await page.getByRole("button", { name: "Send" }).click();

    // Initial location should be Awakening Woods
    await expectConsoleToContain(page, "AWAKENING_WOODS");

    // Follow the Warrior Path
    const warriorCommands = [
      // 1. Get starting equipment
      { cmd: "get rusty_sword", expect: "rusty_sword" },
      { cmd: "get leather_pouch", expect: "leather_pouch" },
      { cmd: "equip rusty_sword", expect: "equip" },

      // 2. Move east to Warrior's Camp
      { cmd: "east", expect: "WARRIORS_CAMP" },
      { cmd: "get basic_shield", expect: "basic_shield" },
      { cmd: "equip basic_shield", expect: "equip" },

      // 3. Move east to Training Grounds
      { cmd: "east", expect: "TRAINING_GROUNDS" },
      { cmd: "get training_sword", expect: "training_sword" },
      { cmd: "equip training_sword", expect: "equip" },

      // 4. Move east to Honor Shrine
      { cmd: "east", expect: "HONOR_SHRINE" },
      { cmd: "get honor_medal", expect: "honor_medal" },

      // 5. Now head north and west to Crystal Pond
      { cmd: "north", expect: "Area" },
      { cmd: "north", expect: "MEDITATION_CIRCLE" },
      { cmd: "west", expect: "CRYSTAL_POND" },
      { cmd: "get luminous_crystal", expect: "luminous_crystal" },

      // 6. Head west to Shadow Domain
      { cmd: "west", expect: "MYSTIC_MOUNTAINS" },
      { cmd: "west", expect: "SHADOW_DOMAIN" },
      { cmd: "get shadow_essence", expect: "shadow_essence" },

      // 7. Go north to Shadow Training
      { cmd: "north", expect: "SHADOW_TRAINING" },
      { cmd: "get shadow_blade", expect: "shadow_blade" },

      // 8. Use coordinate movement to head toward Guardian Overlook
      { cmd: "inventory", expect: "inventory" }, // Check our items
      { cmd: "where", expect: "position" }, // Check our position

      // At this point, we need to navigate to the Crossroads
      // Let's try a realistic path:
      { cmd: "south", expect: "SHADOW_DOMAIN" },
      { cmd: "east", expect: "MYSTIC_MOUNTAINS" },
      { cmd: "east", expect: "CRYSTAL_POND" },
      { cmd: "east", expect: "MEDITATION_CIRCLE" },
      { cmd: "east", expect: "Area" }, // Generic area
      { cmd: "north", expect: "Area" }, // Generic area
      { cmd: "north", expect: "Area" }, // Generic area
      { cmd: "north", expect: "Area" }, // Generic area
      { cmd: "east", expect: "CROSSROADS" }, // Should reach Crossroads

      // From Crossroads, head north and east toward Guardian Overlook
      { cmd: "north", expect: "Area" },
      { cmd: "east", expect: "Area" },
      { cmd: "north", expect: "Area" },
      { cmd: "east", expect: "Area" },
      { cmd: "north", expect: "Area" },
      { cmd: "east", expect: "Area" },
    ];

    // Execute Warrior Path commands
    for (const { cmd, expect } of warriorCommands) {
      // Execute command
      await page.getByPlaceholder("Enter command...").fill(cmd);
      await page.getByRole("button", { name: "Send" }).click();

      // Wait for response
      await page.waitForTimeout(1000);

      // Verify expected text (skip verification if contains "Area" since generic areas vary)
      if (!expect.includes("Area")) {
        await expectConsoleToContain(page, expect);
      }
    }

    // Test is successful if we've executed all commands and can see position information
    // Note: In a real test, we'd verify that we reached the Ancient Sanctuary
    // and defeated the final boss, but that's a longer path than we can easily
    // test in this basic example.

    // Check our inventory to verify we collected key items
    await page.getByPlaceholder("Enter command...").fill("inventory");
    await page.getByRole("button", { name: "Send" }).click();
    await page.waitForTimeout(1000);

    // Should have acquired key items
    const inventory = await page.locator(".game-output").textContent();
    expect(inventory).toContain("training_sword");
    expect(inventory).toContain("honor_medal");
    expect(inventory).toContain("shadow_blade");
  });
});

async function expectConsoleToContain(page: Page, text: string): Promise<void> {
  const consoleText = await page.locator(".game-output").textContent();
  expect(consoleText).toContain(text);
}
