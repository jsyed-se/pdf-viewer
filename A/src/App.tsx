import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ArrowLeft, ChevronDown, Download, FileText, FileUp, Link2, Search } from 'lucide-react';
import { listDemoRecords, loadDemoAttachment, persistDemoAttachment, type DemoRecord } from './app/demoRepository';
import { PdfViewerSDK } from './sdk/PdfViewerSDK';
import type { AttachmentMetadata, PdfDocumentSource, PdfSaveRequest } from './sdk/types';

function metadataFor(source: PdfDocumentSource): AttachmentMetadata {
  const filename = source.kind === 'file' ? source.file.name : source.kind === 'bytes'
    ? source.filename : source.filename ?? source.url.split('/').pop() ?? 'remote-document.pdf';
  return { id: crypto.randomUUID(), filename, label: source.kind === 'url' ? 'Remote PDF' : 'Local workspace' };
}

function downloadBytes(bytes: Uint8Array, filename: string) {
  const url = URL.createObjectURL(new Blob([Uint8Array.from(bytes).buffer], { type: 'application/pdf' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1_000);
}

export default function App() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [source, setSource] = useState<PdfDocumentSource | null>(null);
  const [attachment, setAttachment] = useState<AttachmentMetadata>();
  const [records, setRecords] = useState<DemoRecord[]>([]);
  const [query, setQuery] = useState('');
  const [expandedRecords, setExpandedRecords] = useState<Set<string>>(new Set());
  const [url, setUrl] = useState('');
  const [dirty, setDirty] = useState(false);
  const [hostStatus, setHostStatus] = useState('Loading demonstration records…');
  const [hostError, setHostError] = useState<string | null>(null);
  const [hostBusy, setHostBusy] = useState(false);

  const refreshRecords = useCallback(async () => {
    try {
      const next = await listDemoRecords();
      setRecords(next);
      setExpandedRecords(new Set(next.map((record) => record.id)));
      setHostStatus(`${next.length} demonstration record${next.length === 1 ? '' : 's'} available`);
      return next;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setHostError(message);
      setHostStatus('The local demonstration server is unavailable.');
      return [];
    }
  }, []);

  useEffect(() => { void refreshRecords(); }, [refreshRecords]);

  const handleReady = useCallback(({ pageCount }: { pageCount: number }) => {
    setHostStatus(`${pageCount} page${pageCount === 1 ? '' : 's'} ready`);
  }, []);
  const handleError = useCallback((error: Error) => setHostStatus(error.message), []);

  const filteredRecords = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return records;
    return records.filter((record) => [record.id, record.title, record.description, ...record.attachments.map((item) => item.filename)]
      .some((value) => value.toLowerCase().includes(needle)));
  }, [query, records]);

  const handleCloseRequest = useCallback(() => {
    setSource(null);
    setAttachment(undefined);
    setDirty(false);
    setHostStatus('Returned to record attachments.');
  }, []);
  const canReplaceDocument = () => !dirty || window.confirm('This document has unsaved changes. Discard them and open another PDF?');
  const openSource = (next: PdfDocumentSource, nextAttachment = metadataFor(next)) => {
    if (!canReplaceDocument()) return;
    setSource(next);
    setAttachment(nextAttachment);
    setHostStatus(nextAttachment.recordId ? `Opening ${nextAttachment.filename}` : next.kind === 'url' ? 'Remote PDF' : 'Local workspace');
  };

  const openPersistedAttachment = async (record: DemoRecord, item: DemoRecord['attachments'][number]) => {
    if (!canReplaceDocument()) return;
    setHostBusy(true);
    setHostError(null);
    try {
      const bytes = await loadDemoAttachment(record.id, item.id);
      openSource({ kind: 'bytes', bytes, filename: item.filename }, {
        id: item.id, recordId: record.id, filename: item.filename, label: record.title, size: item.size, updatedAt: item.updatedAt,
      });
    } catch (error) {
      setHostError(error instanceof Error ? error.message : String(error));
    } finally { setHostBusy(false); }
  };

  const quickDownload = async (record: DemoRecord, item: DemoRecord['attachments'][number]) => {
    setHostBusy(true);
    setHostError(null);
    setHostStatus(`Downloading ${item.filename}…`);
    try {
      downloadBytes(await loadDemoAttachment(record.id, item.id), item.filename);
      setHostStatus(`${item.filename} downloaded from persisted storage.`);
    } catch (error) {
      setHostError(error instanceof Error ? error.message : String(error));
      setHostStatus('Quick Download failed.');
    } finally { setHostBusy(false); }
  };

  const handleSave = useCallback(async (request: PdfSaveRequest) => {
    const result = await persistDemoAttachment(request);
    setAttachment(result.attachment);
    await refreshRecords();
    setHostStatus(`${result.attachment.filename} persisted to ${result.attachment.recordId}.`);
    return result;
  }, [refreshRecords]);

  return (
    <main className={`app-shell${source ? ' viewer-active' : ''}`}>
      <h1 className="visually-hidden">Atlas PDF SDK demonstration</h1>
      <header className="host-header">
        {source ? <button type="button" className="back-button" onClick={() => canReplaceDocument() && handleCloseRequest()}><ArrowLeft /> Back to results</button>
          : <div className="host-brand"><span className="attachment-icon">A</span><span><strong>Atlas Records</strong><small>PDF SDK demonstration host</small></span></div>}
        <div className="attachment-summary"><FileText /><span><strong>{attachment?.filename ?? 'Record attachments'}</strong><small>{hostStatus}</small></span></div>
        {source && attachment?.recordId && <button type="button" className="quick-download-button" disabled={hostBusy} onClick={() => {
          const record = records.find((item) => item.id === attachment.recordId);
          const item = record?.attachments.find((candidate) => candidate.id === attachment.id);
          if (record && item) void quickDownload(record, item);
        }}><Download /> Quick Download</button>}
        <a className="source-offer-link" href="/SOURCE_OFFER.txt" target="_blank" rel="noreferrer">Source &amp; AGPL license</a>
      </header>

      {hostError && <div className="host-error" role="alert">{hostError}<button type="button" onClick={() => setHostError(null)}>Dismiss</button></div>}

      {!source ? <section className="records-screen" aria-label="Demonstration record search">
        <div className="records-heading">
          <div><p className="eyebrow">Demonstration host</p><h2>Records and attachments</h2><p>Search sample records, open an attachment, edit it in the SDK, and persist it back to this local server.</p></div>
          <label className="record-search"><Search /><span className="visually-hidden">Search records</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search ID, title, or filename" /></label>
        </div>
        <div className="record-list" aria-busy={hostBusy}>
          {filteredRecords.map((record) => {
            const expanded = expandedRecords.has(record.id);
            return <article className="record-card" key={record.id}>
              <button type="button" className="record-summary" aria-expanded={expanded} onClick={() => setExpandedRecords((current) => {
                const next = new Set(current); if (next.has(record.id)) next.delete(record.id); else next.add(record.id); return next;
              })}><span><strong>{record.title}</strong><small>{record.id} · {record.description}</small></span><ChevronDown className={expanded ? 'expanded' : ''} /></button>
              {expanded && <div className="attachment-table" role="table" aria-label={`Attachments for ${record.title}`}>
                <div className="attachment-row attachment-head" role="row"><span>Attachment</span><span>Updated</span><span>Size</span><span>Actions</span></div>
                {record.attachments.map((item) => <div className="attachment-row" role="row" key={item.id}>
                  <span><FileText /><span><strong>{item.filename}</strong><small>{item.id}</small></span></span>
                  <time dateTime={item.updatedAt}>{new Date(item.updatedAt).toLocaleString()}</time><span>{Math.max(1, Math.round(item.size / 1024))} KB</span>
                  <span className="attachment-actions"><button type="button" className="primary-button" disabled={hostBusy} onClick={() => void openPersistedAttachment(record, item)}>Open viewer</button><button type="button" className="secondary-button" disabled={hostBusy} onClick={() => void quickDownload(record, item)}><Download /> Quick Download</button></span>
                </div>)}
              </div>}
            </article>;
          })}
          {filteredRecords.length === 0 && <p className="empty-results">No demonstration records match “{query}”.</p>}
        </div>
        <details className="alternate-source-panel"><summary>Open a standalone PDF instead</summary>
          <form className="source-controls" onSubmit={(event) => {
            event.preventDefault(); const nextUrl = url.trim(); if (!nextUrl) return;
            try { const parsed = new URL(nextUrl); if (!/^https?:$/.test(parsed.protocol)) throw new Error(); openSource({ kind: 'url', url: parsed.toString() }); }
            catch { setHostStatus('Enter a complete http:// or https:// PDF URL.'); }
          }}><label><Link2 /><input aria-label="Remote PDF URL" type="url" value={url} placeholder="https://…/file.pdf" onChange={(event) => setUrl(event.target.value)} /></label>
            <button type="submit" className="secondary-button">Open URL</button><button type="button" className="open-button" onClick={() => fileInputRef.current?.click()}><FileUp /> Open PDF</button>
            <input ref={fileInputRef} hidden type="file" accept="application/pdf,.pdf" onChange={(event) => { const file = event.target.files?.[0]; if (file) openSource({ kind: 'file', file }); event.currentTarget.value = ''; }} />
          </form></details>
      </section> : <PdfViewerSDK source={source} attachment={attachment} onDirtyChange={setDirty}
        onReady={handleReady} onError={handleError}
        onSave={attachment?.recordId ? handleSave : undefined} onCloseRequest={handleCloseRequest} />}
    </main>
  );
}
