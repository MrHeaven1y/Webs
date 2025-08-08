import React, { useCallback, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useNotes } from '../context/NotesContext';

function parseWikiLinks(text: string) {
  const parts: Array<{ type: 'text' | 'link'; value: string }> = [];
  const regex = /(\[\[[^\]]+\]\])/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(text))) {
    if (match.index > last) parts.push({ type: 'text', value: text.slice(last, match.index) });
    parts.push({ type: 'link', value: match[0].slice(2, -2) });
    last = match.index + match[0].length;
  }
  if (last < text.length) parts.push({ type: 'text', value: text.slice(last) });
  return parts;
}

export const NotePreview: React.FC = () => {
  const { notes, selectedNoteId, setSelectedNoteId, createNote } = useNotes();
  const selected = useMemo(() => notes.find(n => n.id === selectedNoteId) || null, [notes, selectedNoteId]);

  const openOrCreate = useCallback(async (title: string) => {
    const existing = notes.find(n => n.title === title);
    if (existing) {
      setSelectedNoteId(existing.id);
    } else {
      const n = await createNote(title);
      setSelectedNoteId(n.id);
    }
  }, [notes, setSelectedNoteId, createNote]);

  if (!selected) return <div className="p-4 text-sm opacity-70">No note selected</div>;

  const components = {
    p({ node, children, ...props }: any) {
      const text = String(children);
      const items = parseWikiLinks(text);
      if (items.some(i => i.type === 'link')) {
        return (
          <p {...props}>
            {items.map((it, idx) => it.type === 'text' ? it.value : (
              <button key={idx} className="text-accent underline" onClick={() => openOrCreate(it.value)}>
                [[{it.value}]]
              </button>
            ))}
          </p>
        );
      }
      return <p {...props}>{children}</p>;
    }
  } as any;

  return (
    <div className="p-3 prose prose-invert max-w-none">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {selected.content || ''}
      </ReactMarkdown>
    </div>
  );
};