import { useEffect, useState } from 'react';
import './index.css';
import { NoteEditor } from './components/NoteEditor';
import { NotePreview } from './components/NotePreview';
import { Sidebar } from './components/Sidebar';
import { SearchBar } from './components/SearchBar';
import { GraphView } from './components/GraphView';
import { NotesProvider } from './context/NotesContext';

function App() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) root.classList.add('dark');
    else root.classList.remove('dark');
  }, [isDark]);

  return (
    <NotesProvider>
      <div className="h-screen w-screen overflow-hidden">
        <div className="flex h-full">
          <Sidebar className="w-64 border-r border-border" />
          <main className="flex-1 flex flex-col">
            <header className="flex items-center gap-2 border-b border-border px-3 py-2 bg-neutral-900">
              <SearchBar className="flex-1" />
              <button className="px-3 py-1 border border-border rounded hover:bg-background" onClick={() => setIsDark(d => !d)}>
                {isDark ? 'Light' : 'Dark'}
              </button>
            </header>
            <section className="grid grid-cols-2 gap-0 flex-1 min-h-0">
              <div className="min-h-0 overflow-auto border-r border-border bg-neutral-950">
                <NoteEditor />
              </div>
              <div className="min-h-0 overflow-auto bg-neutral-900">
                <NotePreview />
              </div>
            </section>
            <footer className="h-64 border-t border-border bg-neutral-900 min-h-0 overflow-hidden">
              <GraphView />
            </footer>
          </main>
        </div>
      </div>
    </NotesProvider>
  );
}

export default App;
