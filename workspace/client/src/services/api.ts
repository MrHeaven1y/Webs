import type { Note } from '../context/NotesContext';

const BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:4000';

export async function fetchNotes(): Promise<Note[]> {
  const res = await fetch(`${BASE_URL}/api/notes`);
  return res.json();
}

export async function upsertNote(note: Note): Promise<Note> {
  const res = await fetch(`${BASE_URL}/api/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(note),
  });
  return res.json();
}

export async function deleteNoteRemote(id: string): Promise<void> {
  await fetch(`${BASE_URL}/api/notes/${id}`, { method: 'DELETE' });
}

export async function syncNotes(notes: Note[]): Promise<Note[]> {
  const res = await fetch(`${BASE_URL}/api/notes/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes }),
  });
  const data = await res.json();
  return data.notes || [];
}