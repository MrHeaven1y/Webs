import React, { useCallback, useMemo, useState } from 'react';
import { useNotes, type Note } from '../context/NotesContext';

function buildFolderTree(notes: Note[]) {
  const root: any = { name: '', folders: new Map<string, any>(), notes: [] as Note[] };
  for (const n of notes) {
    let node = root;
    for (const part of n.folderPath) {
      if (!node.folders.has(part)) node.folders.set(part, { name: part, folders: new Map(), notes: [] });
      node = node.folders.get(part);
    }
    node.notes.push(n);
  }
  return root;
}

export const Sidebar: React.FC<{ className?: string }> = ({ className }) => {
  const { notes, selectedNoteId, setSelectedNoteId, moveNote, createNote } = useNotes();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const tree = useMemo(() => buildFolderTree(notes), [notes]);

  const toggle = useCallback((path: string) => {
    setExpanded(e => ({ ...e, [path]: !e[path] }));
  }, []);

  const onDrop = useCallback((e: React.DragEvent, folderPath: string[]) => {
    const noteId = e.dataTransfer.getData('text/plain');
    if (noteId) {
      moveNote(noteId, folderPath);
    }
  }, [moveNote]);

  const onDragStart = useCallback((e: React.DragEvent, noteId: string) => {
    e.dataTransfer.setData('text/plain', noteId);
  }, []);

  const renderNode = (node: any, path: string[] = []) => {
    const entries = Array.from(node.folders.entries()) as [string, any][];
    return (
      <ul className="space-y-1">
        {entries.map(([name, child]) => {
          const childPath = [...path, name];
          const key = childPath.join('/');
          const isOpen = expanded[key] ?? true;
          return (
            <li key={key}>
              <div
                className="flex items-center gap-2 px-2 py-1 hover:bg-neutral-800 cursor-pointer"
                onClick={() => toggle(key)}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => onDrop(e, childPath)}
              >
                <span>{isOpen ? '▼' : '▶'}</span>
                <span className="font-medium">{name}</span>
              </div>
              {isOpen && (
                <div className="ml-4">
                  {renderNode(child, childPath)}
                </div>
              )}
            </li>
          );
        })}
        {node.notes.map((n: Note) => (
          <li key={n.id}
              draggable
              onDragStart={(e) => onDragStart(e, n.id)}
              className={`px-2 py-1 rounded cursor-pointer hover:bg-neutral-800 ${selectedNoteId === n.id ? 'bg-neutral-800 border border-border' : ''}`}
              onClick={() => setSelectedNoteId(n.id)}>
            <div className="truncate">{n.title}</div>
          </li>
        ))}
      </ul>
    );
  };

  const onNewNote = useCallback(async () => {
    const n = await createNote();
    setSelectedNoteId(n.id);
  }, [createNote, setSelectedNoteId]);

  return (
    <aside className={"h-full p-2 overflow-auto " + (className || '')}
           onDragOver={(e) => e.preventDefault()}
           onDrop={(e) => onDrop(e, [])}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="font-semibold">Notes</div>
        <button className="px-2 py-1 border border-border rounded" onClick={onNewNote}>+</button>
      </div>
      {renderNode(tree)}
    </aside>
  );
};