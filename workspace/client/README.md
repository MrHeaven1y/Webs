# Obsidian-Lite (React + Vite + Tailwind + IndexedDB)

A minimal Obsidian-like note-taking app with Markdown editing, wiki-links ([[Note Title]]), folder sidebar with drag-and-drop, search, and a graph view of note connections. Offline-first via IndexedDB with optional sync to a Node.js Express server.

## Features
- Dark theme styled similar to Obsidian (TailwindCSS)
- Markdown editor with live preview (react-markdown + remark-gfm)
- Wiki-links: type [[Note Title]] to create/link notes
- Sidebar folder tree with drag-and-drop move
- Search across titles and content
- Graph view (vis-network) of note connections
- IndexedDB storage for offline-first use
- Simple Express API for syncing
- Modular architecture ready for plugins

## Getting Started

### Prerequisites
- Node.js 18+

### Install

- Client
  ```bash
  cd workspace/client
  npm install
  ```

- Server
  ```bash
  cd server
  npm install
  ```

### Development
- Start server
  ```bash
  cd server
  npm run dev
  ```
- Start client
  ```bash
  cd workspace/client
  npm run dev
  ```
- Open the client at the URL shown by Vite (usually `http://localhost:5173`).

If your server runs on a different host/port, set an env in the client:
```bash
# in workspace/client/.env.local
VITE_API_URL=http://localhost:4000
```

### Build
```bash
cd workspace/client
npm run build
```
Output will be in `dist/`.

## Project Structure
- `src/context/NotesContext.tsx`: Notes state, IndexedDB, search, wiki-link parsing, graph edges
- `src/components/*`: UI components (editor, preview, sidebar, search, graph)
- `src/services/api.ts`: Simple fetch-based sync API
- `server/index.js`: Express API with local JSON persistence

## Notes on Plugins
The app is designed around a central `NotesContext` and small UI components, so plugins can subscribe to notes changes, extend the editor preview, or add panes without invasive changes.

## License
MIT
