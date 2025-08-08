import React, { useEffect, useMemo, useRef } from 'react';
import { DataSet, Network, type Node as VisNode, type Edge as VisEdge } from 'vis-network/standalone';
import { useNotes } from '../context/NotesContext';

export const GraphView: React.FC = () => {
  const { notes, graphEdges, setSelectedNoteId } = useNotes();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const networkRef = useRef<Network | null>(null);

  const data = useMemo(() => {
    const nodes: VisNode[] = notes.map(n => ({ id: n.id, label: n.title, shape: 'dot', size: 10 }));
    const edges: VisEdge[] = graphEdges.map(e => ({ from: e.from, to: e.to, arrows: 'to' }));
    return { nodes: new DataSet(nodes), edges: new DataSet(edges) };
  }, [notes, graphEdges]);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!networkRef.current) {
      networkRef.current = new Network(containerRef.current, data, {
        autoResize: true,
        physics: { stabilization: true },
        interaction: { hover: true },
        nodes: { color: { background: '#252526', border: '#3c3c3c', highlight: { background: '#5c9cf5', border: '#5c9cf5' } }, font: { color: '#d4d4d4' } },
        edges: { color: { color: '#3c3c3c', highlight: '#5c9cf5' } },
      });
      networkRef.current.on('click', (params) => {
        const id = params?.nodes?.[0];
        if (id) setSelectedNoteId(id);
      });
    } else {
      networkRef.current.setData(data);
    }
  }, [data, setSelectedNoteId]);

  return <div ref={containerRef} className="w-full h-full" />;
};