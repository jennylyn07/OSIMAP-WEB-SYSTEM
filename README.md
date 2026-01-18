# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)


Documentation

# OSIMAP: Crime Mapping & Analytics

A full‑stack platform for visualizing and analyzing crime data. It combines an authenticated, map‑first UI with background analytics and exportable insights for reporting and decision support.

## What it does
- Map exploration with heatmaps, marker clustering, filters, and print‑ready views.
- Secure, role‑based access with session management and protected routes.
- File uploads with background cleaning and HDBSCAN clustering.
- Dashboards, profiles, admin tools, and a separate download portal.

## Architecture at a glance
- Frontend: React (CRA), React Router, React Leaflet, Chart.js, Lucide.
- Services:
  - Root Node/Express: support email + healthcheck.
  - Backend Node/Express: upload orchestration and processing.
  - Python pipeline: cleaning, clustering (HDBSCAN), GeoJSON export.
- Data: Supabase JS client for auth/storage.
- Additional: Next.js download page (sub‑app: `osimap-download-page/`).

Monorepo layout:
- `src/` React app (protected routes, contexts, map, dashboards)
- `server.js` Root Express service (support email, health)
- `backend/` Node service + Python scripts (analytics pipeline)
- `osimap-download-page/` Next.js download portal

## Tech highlights
- React 19, React Router 7 with Suspense code‑splitting.
- Leaflet ecosystem: heat, fullscreen, marker clusters.
- Supabase integration for auth and data access.
- Python HDBSCAN for robust density‑based clustering.

## Quickstart (dev)
- Requirements: Node 18+, npm, Python 3.10+
- Env (examples):
  - `EMAIL_USER`, `EMAIL_PASS` (SMTP/Gmail for support)
  - `REACT_APP_SUPABASE_URL`, `REACT_APP_SUPABASE_ANON_KEY`
- Install: `npm install`
- Run all services: `npm run dev`

## Demo targets
- Auth‑gated dashboard and interactive map with advanced filters.
- Upload flow with progress and background processing.
- Printable reports and admin functionality.
- Download page for sharing curated datasets/artifacts.
