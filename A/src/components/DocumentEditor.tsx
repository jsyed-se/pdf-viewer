import { useLayoutEffect, useRef, useState } from 'react';
import {
  Clipboard,
  ClipboardPaste,
  Copy,
  Download,
  FilePlus2,
  Images,
  Redo2,
  RotateCcw,
  RotateCw,
  Save,
  Scissors,
  Trash2,
  Undo2,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import type { PDFDocumentProxy } from 'pdfjs-dist';
import type { EngineSnapshot } from '../sdk/types';
import { clampEditorZoom } from '../lib/phase4State';
import { PdfPageCanvas } from './PdfPageCanvas';

interface DocumentEditorProps {
  document: PDFDocumentProxy;
  snapshot: EngineSnapshot;
  selected: Set<number>;
  busy: boolean;
  busyLabel?: string;
  onSelectedChange: (selected: Set<number>) => void;
  onCommand: (command: string, payload?: unknown) => void;
  onImport: (file: File) => void;
  onScan: (files: File[]) => void;
  onCancelScan: () => void;
  scanProgress?: { completed: number; total: number; filename: string };
  onCancel: () => void;
  onSave: () => void;
  onExport: () => void;
}

function EditorButton({
  label,
  disabled,
  onClick,
  children,
}: {
  label: string;
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button className="tool-button" type="button" disabled={disabled} onClick={onClick} aria-label={label}>
      {children}
      <span>{label}</span>
    </button>
  );
}

export function DocumentEditor({
  document,
  snapshot,
  selected,
  busy,
  busyLabel,
  onSelectedChange,
  onCommand,
  onImport,
  onScan,
  onCancelScan,
  scanProgress,
  onCancel,
  onSave,
  onExport,
}: DocumentEditorProps) {
  const importRef = useRef<HTMLInputElement>(null);
  const scanRef = useRef<HTMLInputElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);
  const pendingScrollRatio = useRef<{ x: number; y: number } | null>(null);
  const [editorZoom, setEditorZoom] = useState(0.28);
  const selectedPages = [...selected].sort((a, b) => a - b);
  const noneSelected = selected.size === 0;
  const allSelected = selected.size === snapshot.pageCount;
  const maxSelected = noneSelected ? snapshot.pageCount - 1 : Math.max(...selectedPages);

  const changeEditorZoom = (next: number) => {
    const grid = gridRef.current;
    if (grid) pendingScrollRatio.current = {
      x: grid.scrollWidth > grid.clientWidth ? grid.scrollLeft / (grid.scrollWidth - grid.clientWidth) : 0,
      y: grid.scrollHeight > grid.clientHeight ? grid.scrollTop / (grid.scrollHeight - grid.clientHeight) : 0,
    };
    setEditorZoom(clampEditorZoom(next));
  };

  useLayoutEffect(() => {
    const grid = gridRef.current;
    const ratio = pendingScrollRatio.current;
    if (!grid || !ratio) return;
    pendingScrollRatio.current = null;
    grid.scrollLeft = ratio.x * Math.max(0, grid.scrollWidth - grid.clientWidth);
    grid.scrollTop = ratio.y * Math.max(0, grid.scrollHeight - grid.clientHeight);
  }, [editorZoom]);

  const togglePage = (pageIndex: number) => {
    const next = new Set(selected);
    if (next.has(pageIndex)) next.delete(pageIndex);
    else next.add(pageIndex);
    onSelectedChange(next);
  };

  return (
    <section className="document-editor" aria-label="Document editor">
      <header className="editor-toolbar">
        <div className="editor-title"><span className="editor-mark">✎</span> Document editor</div>
        <div className="editor-actions" role="toolbar" aria-label="Document editor toolbar">
          <EditorButton label="Scan images" disabled={busy} onClick={() => scanRef.current?.click()}><Images /></EditorButton>
          <EditorButton label="Import" disabled={busy} onClick={() => importRef.current?.click()}><FilePlus2 /></EditorButton>
          <EditorButton label="Delete" disabled={busy || noneSelected || allSelected} onClick={() => onCommand('delete')}><Trash2 /></EditorButton>
          <EditorButton label="Rotate left" disabled={busy || noneSelected} onClick={() => onCommand('rotate', -90)}><RotateCcw /></EditorButton>
          <EditorButton label="Rotate right" disabled={busy || noneSelected} onClick={() => onCommand('rotate', 90)}><RotateCw /></EditorButton>
          <EditorButton label="Extract" disabled={busy || noneSelected} onClick={() => onCommand('extract')}><Scissors /></EditorButton>
          <EditorButton label="Undo" disabled={busy || !snapshot.canUndo} onClick={() => onCommand('undo')}><Undo2 /></EditorButton>
          <EditorButton label="Redo" disabled={busy || !snapshot.canRedo} onClick={() => onCommand('redo')}><Redo2 /></EditorButton>
          <EditorButton label="Editor zoom out" disabled={busy || editorZoom <= 0.18} onClick={() => changeEditorZoom(editorZoom - 0.05)}><ZoomOut /></EditorButton>
          <span className="editor-zoom-value" aria-label={`Editor zoom ${Math.round(editorZoom * 100)} percent`}>{Math.round(editorZoom * 100)}%</span>
          <EditorButton label="Editor zoom in" disabled={busy || editorZoom >= 0.5} onClick={() => changeEditorZoom(editorZoom + 0.05)}><ZoomIn /></EditorButton>
          <button
            type="button"
            className="text-action"
            disabled={busy}
            onClick={() => onSelectedChange(allSelected ? new Set() : new Set(snapshot.pages.map((page) => page.index)))}
          >
            {allSelected ? 'Select none' : 'Select all'}
          </button>
          <EditorButton label="Keep selected" disabled={busy || noneSelected || allSelected} onClick={() => onCommand('keep')}><Clipboard /></EditorButton>
          <EditorButton label="Copy" disabled={busy || noneSelected} onClick={() => onCommand('copy')}><Copy /></EditorButton>
          <EditorButton label="Paste" disabled={busy || !snapshot.hasClipboard} onClick={() => onCommand('paste', maxSelected)}><ClipboardPaste /></EditorButton>
        </div>
        <input
          name="editor-import-pdf"
          ref={importRef}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onImport(file);
            event.currentTarget.value = '';
          }}
        />
        <input
          name="editor-scan-images"
          ref={scanRef}
          type="file"
          accept="image/png,image/jpeg,.png,.jpg,.jpeg"
          multiple
          hidden
          onChange={(event) => {
            const files = Array.from(event.target.files ?? []);
            if (files.length) onScan(files);
            event.currentTarget.value = '';
          }}
        />
      </header>
      {scanProgress && <div className="scan-progress" role="status" aria-live="polite">
        <span className="spinner" />
        <span><strong>Converting scan images</strong><small>{scanProgress.filename || 'Preparing images'} · {scanProgress.completed} of {scanProgress.total}</small></span>
        <progress value={scanProgress.completed} max={scanProgress.total}>{scanProgress.completed} of {scanProgress.total}</progress>
        <button type="button" className="secondary-button" onClick={onCancelScan}>Cancel scanning</button>
      </div>}
      {busy && !scanProgress && <div className="scan-progress operation-progress" role="status" aria-live="polite">
        <span className="spinner" />
        <span><strong>{busyLabel ?? 'Updating PDF with MuPDF WebAssembly…'}</strong><small>Please keep this document open.</small></span>
      </div>}
      <div ref={gridRef} className="editor-grid" aria-busy={busy} style={{ gridTemplateColumns: `repeat(auto-fill, minmax(${Math.round(750 * editorZoom)}px, 1fr))` }}>
        {snapshot.pages.map((page) => {
          const isSelected = selected.has(page.index);
          return (
            <article
              className={`editor-page-card${isSelected ? ' selected' : ''}`}
              key={`${page.index}-${page.rotation}`}
              draggable={!busy}
              onDragStart={(event) => event.dataTransfer.setData('text/page-index', String(page.index))}
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                const from = Number(event.dataTransfer.getData('text/page-index'));
                if (Number.isInteger(from) && from !== page.index) onCommand('move', { from, to: page.index });
              }}
            >
              <button
                className="page-select-button"
                type="button"
                aria-pressed={isSelected}
                onClick={() => togglePage(page.index)}
              >
                <span className="page-index-dot">{isSelected ? '✓' : page.index + 1}</span>
                <PdfPageCanvas document={document} pageNumber={page.index + 1} scale={editorZoom} compact />
              </button>
              <div className="reorder-row">
                <button
                  type="button"
                  aria-label={`Move page ${page.index + 1} left`}
                  disabled={busy || page.index === 0}
                  onClick={() => onCommand('move', { from: page.index, to: page.index - 1 })}
                >←</button>
                <span>Page {page.index + 1}{page.rotation ? ` · ${page.rotation}°` : ''}</span>
                <button
                  type="button"
                  aria-label={`Move page ${page.index + 1} right`}
                  disabled={busy || page.index === snapshot.pageCount - 1}
                  onClick={() => onCommand('move', { from: page.index, to: page.index + 1 })}
                >→</button>
              </div>
            </article>
          );
        })}
      </div>
      <footer className="editor-commit-actions">
        <button type="button" className="secondary-button" disabled={busy} onClick={onExport}><Download /> Export</button>
        <button type="button" className="secondary-button" disabled={busy} onClick={onCancel}><X /> Cancel</button>
        <button type="button" className="primary-button" disabled={busy} onClick={onSave}><Save /> Save changes</button>
      </footer>
    </section>
  );
}
