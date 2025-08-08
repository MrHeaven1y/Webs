import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { openDB, type IDBPDatabase } from 'idb';
import { syncNotes } from '../services/api';

export type Note = {
  id: string;
  title: string;
  content: string;
  folderPath: string[]; // hierarchy of folders
  updatedAt: number;
  createdAt: number;
};

export type NotesGraphEdge = { from: string; to: string };

export type NotesContextValue = {
  notes: Note[];
  selectedNoteId: string | null;
  setSelectedNoteId: (id: string | null) => void;
  createNote: (title?: string, folderPath?: string[]) => Promise<Note>;
  updateNote: (id: string, updates: Partial<Pick<Note, 'title' | 'content' | 'folderPath'>>) => Promise<void>;
  deleteNote: (id: string) => Promise<void>;
  moveNote: (id: string, folderPath: string[]) => Promise<void>;
  search: (query: string) => Note[];
  getOutgoingLinks: (noteId: string) => string[]; // note ids referenced
  graphEdges: NotesGraphEdge[];
  refresh: () => Promise<void>;
};

const NotesContext = createContext<NotesContextValue | undefined>(undefined);

const DB_NAME = 'obsidian-lite';
const DB_VERSION = 1;
const NOTES_STORE = 'notes';

async function initDb(): Promise<IDBPDatabase> {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(NOTES_STORE)) {
        const store = db.createObjectStore(NOTES_STORE, { keyPath: 'id' });
        store.createIndex('title', 'title', { unique: false });
        store.createIndex('updatedAt', 'updatedAt', { unique: false });
      }
    },
  });
}

function extractWikiLinks(content: string): string[] {
  const matches = content.match(/\[\[([^\]]+)\]\]/g) || [];
  return matches
    .map(m => m.slice(2, -2).trim())
    .filter(Boolean);
}

function titleToId(title: string): string {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

export const NotesProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [db, setDb] = useState<IDBPDatabase | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);

  useEffect(() => {
    initDb().then(setDb);
  }, []);

  const refresh = useCallback(async () => {
    if (!db) throw new Error('DB not ready');
    const all = await db.getAll(NOTES_STORE);
    all.sort((a, b) => b.updatedAt - a.updatedAt);
    setNotes(all as Note[]);
  }, [db]);

  useEffect(() => {
    if (!db) return;
    refresh().catch(() => {});
  }, [db, refresh]);

  // Background sync with server
  useEffect(() => {
    if (!db) return;
    let cancelled = false;
    const database = db;
    async function doSync() {
      try {
        const local = (await database.getAll(NOTES_STORE)) as Note[];
        const remote = await syncNotes(local);
        // Merge by updatedAt and persist to local
        const byId = new Map<string, Note>();
        for (const n of local) byId.set(n.id, n);
        for (const n of remote) {
          const existing = byId.get(n.id);
          if (!existing || (n.updatedAt || 0) > (existing.updatedAt || 0)) byId.set(n.id, n);
        }
        const merged = Array.from(byId.values());
        for (const n of merged) await database.put(NOTES_STORE, n);
        if (!cancelled) await refresh();
      } catch (e) {
        // ignore network errors; remain offline
      }
    }
    doSync();
    const id = setInterval(doSync, 30000);
    return () => { cancelled = true; clearInterval(id); };
  }, [db, refresh]);

  const createNote = useCallback(async (title = 'Untitled', folderPath: string[] = []) => {
    if (!db) throw new Error('DB not ready');
    const id = titleToId(title) || crypto.randomUUID();
    const now = Date.now();
    const note: Note = { id, title, content: '', folderPath, createdAt: now, updatedAt: now };
    await db.put(NOTES_STORE, note);
    await refresh();
    setSelectedNoteId(id);
    return note;
  }, [db, refresh]);

  const updateNote = useCallback(async (id: string, updates: Partial<Pick<Note, 'title' | 'content' | 'folderPath'>>) => {
    if (!db) throw new Error('DB not ready');
    const existing = await db.get(NOTES_STORE, id) as Note | undefined;
    if (!existing) return;
    const updated: Note = { ...existing, ...updates, updatedAt: Date.now() };
    await db.put(NOTES_STORE, updated);
    await refresh();
  }, [db, refresh]);

  const deleteNote = useCallback(async (id: string) => {
    if (!db) throw new Error('DB not ready');
    await db.delete(NOTES_STORE, id);
    await refresh();
    if (selectedNoteId === id) setSelectedNoteId(null);
  }, [db, refresh, selectedNoteId]);

  const moveNote = useCallback(async (id: string, folderPath: string[]) => {
    await updateNote(id, { folderPath });
  }, [updateNote]);

  const search = useCallback((query: string) => {
    const q = query.trim().toLowerCase();
    if (!q) return notes;
    return notes.filter(n =>
      n.title.toLowerCase().includes(q) || n.content.toLowerCase().includes(q)
    );
  }, [notes]);

  const getOutgoingLinks = useCallback((noteId: string) => {
    const note = notes.find(n => n.id === noteId);
    if (!note) return [];
    const linkTitles = extractWikiLinks(note.content);
    const titleToNoteId = new Map(notes.map(n => [n.title, n.id] as const));
    return linkTitles.map(t => titleToNoteId.get(t) || titleToId(t));
  }, [notes]);

  const graphEdges: NotesGraphEdge[] = useMemo(() => {
    const edges: NotesGraphEdge[] = [];
    for (const n of notes) {
      const outgoing = extractWikiLinks(n.content);
      for (const t of outgoing) {
        const targetId = notes.find(x => x.title === t)?.id || titleToId(t);
        edges.push({ from: n.id, to: targetId });
      }
    }
    return edges;
  }, [notes]);

  const value: NotesContextValue = {
    notes,
    selectedNoteId,
    setSelectedNoteId,
    createNote,
    updateNote,
    deleteNote,
    moveNote,
    search,
    getOutgoingLinks,
    graphEdges,
    refresh,
  };

  return (
    <NotesContext.Provider value={value}>{children}</NotesContext.Provider>
  );
};

export function useNotes() {
  const ctx = useContext(NotesContext);
  if (!ctx) throw new Error('useNotes must be used within NotesProvider');
  return ctx;
}