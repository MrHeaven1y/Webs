const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

const DATA_FILE = path.join(__dirname, 'data.json');

/**
 * Load and persist notes
 */
let notes = [];
try {
  if (fs.existsSync(DATA_FILE)) {
    const raw = fs.readFileSync(DATA_FILE, 'utf-8');
    notes = JSON.parse(raw);
  }
} catch (e) {
  console.error('Failed to load data file', e);
  notes = [];
}

function persist() {
  try {
    fs.writeFileSync(DATA_FILE, JSON.stringify(notes, null, 2));
  } catch (e) {
    console.error('Failed to persist data', e);
  }
}

// health
app.get('/api/health', (_req, res) => res.json({ ok: true }));

// list notes
app.get('/api/notes', (req, res) => {
  res.json(notes);
});

// upsert note
app.post('/api/notes', (req, res) => {
  const note = req.body;
  if (!note.id) note.id = uuidv4();
  const idx = notes.findIndex(n => n.id === note.id);
  if (idx >= 0) notes[idx] = note; else notes.push(note);
  persist();
  res.json(note);
});

// bulk sync
app.post('/api/notes/sync', (req, res) => {
  const incoming = req.body.notes || [];
  const byId = new Map(notes.map(n => [n.id, n]));
  for (const n of incoming) {
    const existing = byId.get(n.id);
    if (!existing || (n.updatedAt || 0) > (existing.updatedAt || 0)) {
      byId.set(n.id, n);
    }
  }
  notes = Array.from(byId.values());
  persist();
  res.json({ notes });
});

// delete
app.delete('/api/notes/:id', (req, res) => {
  const { id } = req.params;
  notes = notes.filter(n => n.id !== id);
  persist();
  res.json({ ok: true });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log('Server listening on port', PORT);
});