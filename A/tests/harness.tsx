/* eslint-disable react-refresh/only-export-components */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { PdfViewerSDK } from '../src/sdk/PdfViewerSDK';
import type { PdfDocumentSource } from '../src/sdk/types';
import '../src/styles.css';
import './harness.css';

type HarnessSource = PdfDocumentSource & { kind: 'bytes' };

async function fixtureSource(name: string): Promise<HarnessSource> {
  const response = await fetch(`/tests/fixtures/generated/${name}`);
  if (!response.ok) throw new Error(`Fixture request failed: ${response.status}`);
  return { kind: 'bytes', bytes: new Uint8Array(await response.arrayBuffer()), filename: name };
}

function Harness() {
  const dual = new URLSearchParams(window.location.search).get('dual') === '1';
  const [primary, setPrimary] = useState<HarnessSource | null>(null);
  const [secondary, setSecondary] = useState<HarnessSource | null>(null);
  const [events, setEvents] = useState<string[]>([]);
  const record = useCallback((event: string) => setEvents((current) => [...current, event]), []);

  useEffect(() => {
    void Promise.all([
      fixtureSource('normal.pdf').then(setPrimary),
      dual ? fixtureSource('merge-beta.pdf').then(setSecondary) : Promise.resolve(),
    ]).catch((error) => record(`harness:error:${String(error)}`));
  }, [dual, record]);

  const callbacks = useCallback((name: string, close: () => void) => ({
    onReady: ({ pageCount, filename }: { pageCount: number; filename: string }) => record(`${name}:ready:${filename}:${pageCount}`),
    onProgress: (loaded: number, total?: number) => record(`${name}:progress:${loaded}/${total ?? '?'}`),
    onPageChange: (page: number) => record(`${name}:page:${page}`),
    onDirtyChange: (dirty: boolean) => record(`${name}:dirty:${dirty}`),
    onSave: (_bytes: Uint8Array, filename: string) => record(`${name}:save:${filename}`),
    onError: (error: Error) => record(`${name}:error:${error.message}`),
    onPasswordRequest: (reason: 'required' | 'incorrect') => {
      record(`${name}:password:${reason}`);
      return Promise.resolve(null);
    },
    onCloseRequest: () => {
      record(`${name}:close`);
      close();
    },
  }), [record]);
  const primaryCallbacks = useMemo(() => callbacks('primary', () => setPrimary(null)), [callbacks]);
  const secondaryCallbacks = useMemo(() => callbacks('secondary', () => setSecondary(null)), [callbacks]);

  return (
    <main className="harness-shell">
      <header>
        <h1>PDF SDK validation harness</h1>
        <p>Raw-byte input and isolated-instance evidence only; this is not the product demo.</p>
        <button type="button" onClick={() => void fixtureSource('multi-page-text.pdf').then(setPrimary)}>Replace primary bytes</button>
        <button type="button" onClick={() => void fixtureSource('normal.pdf').then(setPrimary)}>Restore primary bytes</button>
      </header>
      <section className="harness-log" aria-label="SDK event log">
        <h2>SDK event log</h2>
        <output>{events.join('\n')}</output>
      </section>
      <section className="sdk-host" aria-label="Primary SDK instance">
        <PdfViewerSDK source={primary} {...primaryCallbacks} />
      </section>
      {dual && (
        <section className="sdk-host" aria-label="Secondary SDK instance">
          <PdfViewerSDK source={secondary} {...secondaryCallbacks} />
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<Harness />);
