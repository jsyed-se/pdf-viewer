import { useCallback, useState } from 'react';
import {
  PdfViewerSDK,
  type AttachmentMetadata,
  type PdfDocumentSource,
  type PdfSaveRequest,
  type PdfSaveResult,
  type PdfViewerSDKProps,
} from '@atlas-pdf/react-sdk';

const sampleSource: PdfDocumentSource = {
  kind: 'url',
  url: '/sample.pdf',
  filename: 'sample.pdf',
};

const initialAttachment: AttachmentMetadata = {
  id: 'consumer-sample',
  filename: 'sample.pdf',
  label: 'Independent consumer fixture',
};

export default function App() {
  const [source, setSource] = useState<PdfDocumentSource | null>(sampleSource);
  const [attachment, setAttachment] = useState<AttachmentMetadata>(initialAttachment);
  const [failSaves, setFailSaves] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [status, setStatus] = useState('Opening /sample.pdf…');

  const handleSave = useCallback(async (request: PdfSaveRequest): Promise<PdfSaveResult> => {
    setStatus(`Host received ${request.bytes.byteLength} bytes for ${request.filename}.`);
    await new Promise((resolve) => window.setTimeout(resolve, 250));
    if (failSaves) {
      setStatus('Host rejected the save. Dirty edits should remain available.');
      throw new Error('Intentional consumer save failure. Retry with “Save succeeds” selected.');
    }

    const savedAt = new Date().toISOString();
    const savedAttachment: AttachmentMetadata = {
      ...(request.attachment ?? initialAttachment),
      filename: request.filename,
      size: request.bytes.byteLength,
      updatedAt: savedAt,
    };
    setAttachment(savedAttachment);
    setStatus(`Host accepted ${request.filename} at ${savedAt}.`);
    return { attachment: savedAttachment, savedAt };
  }, [failSaves]);

  const handleReady: NonNullable<PdfViewerSDKProps['onReady']> = useCallback(({ filename, pageCount }) => {
    setStatus(`${filename} is ready with ${pageCount} page${pageCount === 1 ? '' : 's'}.`);
  }, []);

  return (
    <main className="consumer-shell">
      <header className="consumer-header">
        <div>
          <p className="eyebrow">Independent package consumer</p>
          <h1>Atlas PDF SDK</h1>
        </div>
        <div className="consumer-controls">
          {!source && <button type="button" onClick={() => setSource(sampleSource)}>Open /sample.pdf</button>}
          <label>
            Save behavior
            <select value={failSaves ? 'failure' : 'success'} onChange={(event) => setFailSaves(event.target.value === 'failure')}>
              <option value="success">Save succeeds</option>
              <option value="failure">Save fails</option>
            </select>
          </label>
        </div>
        <dl className="consumer-output" aria-live="polite">
          <div><dt>Dirty</dt><dd data-testid="dirty-state">{dirty ? 'yes' : 'no'}</dd></div>
          <div><dt>Status</dt><dd data-testid="host-status">{status}</dd></div>
        </dl>
      </header>

      <section className="viewer-host" aria-label="Packaged PDF viewer">
        {source ? (
          <PdfViewerSDK
            source={source}
            attachment={attachment}
            assets={{ baseUrl: '/atlas-pdf-assets/' }}
            onReady={handleReady}
            onProgress={(loaded, total) => setStatus(`Loading ${loaded}${total ? ` of ${total}` : ''} bytes…`)}
            onPageChange={(page) => setStatus(`Viewing page ${page}.`)}
            onDirtyChange={setDirty}
            onSave={handleSave}
            onError={(error) => setStatus(`SDK error: ${error.message}`)}
            onPasswordRequest={async () => null}
            onCloseRequest={() => {
              setSource(null);
              setStatus('Viewer closed.');
            }}
          />
        ) : (
          <div className="closed-state">
            <p>The viewer is closed.</p>
            <button type="button" onClick={() => setSource(sampleSource)}>Open /sample.pdf</button>
          </div>
        )}
      </section>
    </main>
  );
}
