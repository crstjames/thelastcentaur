# The Last Centaur - Frontend

This is the frontend for The Last Centaur, a text-based RPG accessible via web browsers and chat interfaces.

## Getting Started

First, install the dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Important Notes

### Background Image

The landing page requires a background image. Please add a pixel art forest background image to:

```
public/images/forest-background.jpg
```

If no image is provided, a fallback gradient will be used, but for the best experience, please add a proper pixel art background image.

You can find free pixel art backgrounds at:

- [OpenGameArt.org](https://opengameart.org/)
- [itch.io](https://itch.io/game-assets/free/tag-pixel-art)
- [GameDev Market](https://www.gamedevmarket.net/category/2d/backgrounds/?type=free)

### Design Reference

The design is inspired by Stein World, a pixel art MMORPG. The key elements include:

- Pixel art forest background
- Large centered game title
- Flashing "Click to Start" button
- Social media icons and language selector in the top right

## Project Structure

- `app/` - The main application code
  - `page.tsx` - The landing page
  - `layout.tsx` - The root layout
  - `globals.css` - Global styles
  - `context/` - Context providers
  - `services/` - API services
  - `login/` - Login page
  - `register/` - Registration page
  - `games/` - Games listing page
  - `play/` - Game play page

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
