# Obsidian-Lite Monorepo

This workspace contains a React client and an Express server.

## Structure
- `workspace/client`: Vite React TypeScript app (Tailwind, IndexedDB, vis-network)
- `server`: Node.js Express API

## Setup

1) Install dependencies
```bash
# Client
auth $(whoami) >/dev/null 2>&1 || true
cd /workspace/workspace/client
npm install

# Server
cd /workspace/server
npm install
```

2) Run in development
```bash
# Server
cd /workspace/server
npm run dev

# Client (in a new terminal)
cd /workspace/workspace/client
npm run dev
```

3) Optional: configure client to point to a different API
Create `/workspace/workspace/client/.env.local`:
```ini
VITE_API_URL=http://localhost:4000
```

## Notes
- Data is stored offline in browser IndexedDB. Server persists data to `server/data.json`.
- Wiki-links use the syntax `[[Note Title]]`. Clicking a link opens existing note or creates it.
- Drag a note item in the sidebar into a folder header to move it.
- Graph pane shows connections; click a node to open that note.

## License
MIT
