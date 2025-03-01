# Background Images for The Last Centaur

This directory contains background images used in The Last Centaur game.

## Required Images

### forest-background.jpg

This is the main background image used for the login and registration screens. It should be:

- A pixel art forest scene
- High resolution (at least 1920x1080)
- Vibrant colors that contrast well with the UI elements
- Similar to the Stein World game's background

## How to Add Your Own Background

1. Find a suitable pixel art forest background image. Some sources:

   - [OpenGameArt.org](https://opengameart.org/) - Free game assets
   - [itch.io](https://itch.io/game-assets/free/tag-pixel-art) - Many free and paid pixel art assets
   - [GameDev Market](https://www.gamedevmarket.net/category/2d/backgrounds/?type=free) - Free section
   - [Pixel Joint](http://pixeljoint.com/) - Pixel art community

2. Ensure you have the rights to use the image (free for commercial use or appropriate license)

3. Rename the image to `forest-background.jpg` (or update the references in the code)

4. Place the image in this directory

5. If the image is not in JPG format, convert it and update the references in:
   - `frontend/app/page.tsx`
   - `frontend/app/login/page.tsx`
   - `frontend/app/register/page.tsx`

## Placeholder Image

The current `forest-background.jpg` is a placeholder. Please replace it with a proper pixel art background before deploying the application.

## Example Background Style

Look for backgrounds similar to these games:

- Stein World
- Stardew Valley
- Terraria
- Eastward
