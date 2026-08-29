import { act, create, type ReactTestRenderer } from 'react-test-renderer';
import { useState } from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { getDocumentMock, hostRenderMock, readyMock } = vi.hoisted(() => ({
  getDocumentMock: vi.fn(),
  hostRenderMock: vi.fn(),
  readyMock: vi.fn(),
}));

vi.mock('pdfjs-dist', () => ({
  GlobalWorkerOptions: { workerSrc: '' },
  PasswordResponses: { INCORRECT_PASSWORD: 2 },
  getDocument: getDocumentMock,
}));

vi.mock('../sdk/engineClient', () => ({
  PdfEngineClient: class {
    resetIfStarted = vi.fn().mockResolvedValue(undefined);
    destroy = vi.fn();
    call = vi.fn();
  },
}));

vi.mock('../components/PdfPageCanvas', () => ({ PdfPageCanvas: () => null }));
vi.mock('../components/DocumentEditor', () => ({ DocumentEditor: () => null }));

import { PdfViewerSDK } from '../sdk/PdfViewerSDK';

function createLoadingTask() {
  const document = {
    numPages: 1,
    cleanup: vi.fn().mockResolvedValue(undefined),
    getPage: vi.fn().mockResolvedValue({
      getViewport: () => ({ width: 612, height: 792 }),
    }),
  };
  let resolveDocument!: (value: typeof document) => void;
  const promise = new Promise<typeof document>((resolve) => { resolveDocument = resolve; });
  const task = {
    promise,
    destroy: vi.fn().mockResolvedValue(undefined),
    onProgress: undefined as undefined | ((progress: { loaded: number; total: number }) => void),
    onPassword: undefined as unknown,
  };
  queueMicrotask(() => {
    task.onProgress?.({ loaded: 50, total: 100 });
    resolveDocument(document);
  });
  return task;
}

function InlineHost({ url }: { url: string }) {
  const [, setLoaded] = useState(0);
  hostRenderMock();
  return (
    <PdfViewerSDK
      source={{ kind: 'url', url }}
      onProgress={(loaded) => setLoaded(loaded)}
      onReady={(details) => readyMock(details)}
      onError={() => setLoaded(-1)}
      onPasswordRequest={async () => null}
    />
  );
}

describe('PdfViewerSDK lifecycle identity', () => {
  beforeEach(() => {
    getDocumentMock.mockReset();
    hostRenderMock.mockReset();
    readyMock.mockReset();
    getDocumentMock.mockImplementation(createLoadingTask);
    vi.stubGlobal('window', {
      setTimeout,
      clearTimeout,
      prompt: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      confirm: vi.fn(() => true),
    });
    Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  });

  it('does not reload when inline callbacks rerender an equivalent source', async () => {
    let renderer!: ReactTestRenderer;
    await act(async () => {
      renderer = create(<InlineHost url="/same.pdf" />);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(getDocumentMock).toHaveBeenCalledTimes(1);
    expect(readyMock).toHaveBeenCalledTimes(1);
    expect(hostRenderMock.mock.calls.length).toBeGreaterThan(1);

    await act(async () => {
      renderer.update(<InlineHost url="/same.pdf" />);
      await Promise.resolve();
    });

    expect(getDocumentMock).toHaveBeenCalledTimes(1);
    expect(readyMock).toHaveBeenCalledTimes(1);

    await act(async () => {
      renderer.update(<InlineHost url="/different.pdf" />);
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(getDocumentMock).toHaveBeenCalledTimes(2);
    expect(readyMock).toHaveBeenCalledTimes(2);

    await act(async () => renderer.unmount());
  });
});
