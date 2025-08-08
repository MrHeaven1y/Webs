import React, { useEffect, useMemo, useState } from 'react';
import { useNotes } from '../context/NotesContext';

export const SearchBar: React.FC<{ className?: string }> = ({ className }) => {
  const { search, setSelectedNoteId } = useNotes();
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);

  const results = useMemo(() => search(query).slice(0, 8), [search, query]);

  useEffect(() => {
    setOpen(query.length > 0);
  }, [query]);

  return (
    <div className={`relative ${className || ''}`}>
      <input
        className="w-full bg-neutral-900 border border-border rounded px-3 py-1 outline-none"
        placeholder="Search notes..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {open && (
        <div className="absolute z-10 mt-1 w-full bg-neutral-900 border border-border rounded shadow">
          {results.length === 0 && <div className="px-3 py-2 text-sm opacity-70">No results</div>}
          {results.map(n => (
            <button
              key={n.id}
              className="w-full text-left px-3 py-2 hover:bg-neutral-800"
              onClick={() => { setSelectedNoteId(n.id); setOpen(false); setQuery(''); }}
            >
              <div className="font-medium truncate">{n.title}</div>
              <div className="text-xs opacity-60 truncate">{n.content.replace(/\n/g, ' ')}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};