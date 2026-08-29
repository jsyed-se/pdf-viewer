import { afterEach, describe, expect, it, vi } from 'vitest';
import { PdfEngineClient } from '../sdk/engineClient';

class WorkerMock {
  static instances: WorkerMock[] = [];

  readonly postMessage = vi.fn();
  readonly terminate = vi.fn();
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: ErrorEvent) => void) | null = null;
  private readonly messageListeners = new Set<(event: MessageEvent) => void>();

  constructor(readonly url: string | URL, readonly options?: WorkerOptions) {
    WorkerMock.instances.push(this);
  }

  addEventListener(type: string, listener: EventListenerOrEventListenerObject) {
    if (type === 'message' && typeof listener === 'function') {
      this.messageListeners.add(listener as (event: MessageEvent) => void);
    }
  }

  removeEventListener(type: string, listener: EventListenerOrEventListenerObject) {
    if (type === 'message' && typeof listener === 'function') {
      this.messageListeners.delete(listener as (event: MessageEvent) => void);
    }
  }

  emitMessage(data: unknown) {
    const event = { data } as MessageEvent;
    for (const listener of this.messageListeners) listener(event);
    this.onmessage?.(event);
  }
}

describe('packaged document-worker request lifecycle', () => {
  afterEach(() => {
    WorkerMock.instances = [];
    vi.unstubAllGlobals();
  });

  it('waits for the hosted bootstrap handshake and correlates the worker response', async () => {
    vi.stubGlobal('document', { baseURI: 'https://consumer.example/app/' });
    vi.stubGlobal('window', { setTimeout, clearTimeout });
    vi.stubGlobal('Worker', WorkerMock as unknown as typeof Worker);

    const client = new PdfEngineClient('/atlas-pdf-assets/');
    const response = client.call({ type: 'reset' });
    const worker = WorkerMock.instances[0];

    expect(worker.url).toBe('https://consumer.example/atlas-pdf-assets/pdfEngine.bootstrap.worker.js');
    expect(worker.options).toEqual({ type: 'module', name: 'atlas-mupdf-engine' });
    expect(worker.postMessage).not.toHaveBeenCalled();

    worker.emitMessage({ type: 'ready' });
    await Promise.resolve();
    expect(worker.postMessage).toHaveBeenCalledWith({ id: 1, command: { type: 'reset' } });

    worker.emitMessage({ id: 1, result: { wasm: true } });
    await expect(response).resolves.toEqual({ wasm: true });

    client.destroy();
    expect(worker.terminate).toHaveBeenCalledOnce();
  });
});
