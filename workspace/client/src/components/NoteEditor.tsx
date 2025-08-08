import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNotes } from '../context/NotesContext';

export const NoteEditor: React.FC = () => {
  const { notes, selectedNoteId, setSelectedNoteId, updateNote, createNote } = useNotes();
  const selected = useMemo(() => notes.find(n => n.id === selectedNoteId) || null, [notes, selectedNoteId]);
  const [localTitle, setLocalTitle] = useState<string>(selected?.title || '');
  const [localContent, setLocalContent] = useState<string>(selected?.content || '');

  useEffect(() => {
    setLocalTitle(selected?.title || '');
    setLocalContent(selected?.content || '');
  }, [selectedNoteId]);

  // Autosave
  useEffect(() => {
    const handle = setTimeout(() => {
      if (selected) {
        updateNote(selected.id, { title: localTitle, content: localContent });
      }
    }, 400);
    return () => clearTimeout(handle);
  }, [localTitle, localContent, selected, updateNote]);

  const onNewNote = useCallback(async () => {
    const n = await createNote('Untitled');
    setSelectedNoteId(n.id);
  }, [createNote, setSelectedNoteId]);

  if (!selected) {
    return (
      <div className="h-full p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">No note selected</h2>
          <button className="px-3 py-1 rounded border border-border" onClick={onNewNote}>New Note</button>
        </div>
        <p className="text-sm opacity-70">Select or create a note to start editing.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-border flex items-center gap-2">
        <input
          className="w-full bg-transparent outline-none text-xl font-semibold"
          value={localTitle}
          onChange={(e) => setLocalTitle(e.target.value)}
          placeholder="Note title"
        />
      </div>
      <textarea
        className="flex-1 p-3 bg-transparent outline-none resize-none"
        value={localContent}
        onChange={(e) => setLocalContent(e.target.value)}
        placeholder="Write in Markdown... Use [[Note Title]] to link."
      />
    </div>
  );
};