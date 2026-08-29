import type { EngineCommand, EngineResult } from './types';
import { PDF_ENGINE_WORKER_FILE, runtimeWorkerUrl } from './runtimeAssets';

interface PendingCall {
  resolve: (value: EngineResult) => void;
  reject: (reason: Error) => void;
}

export class PdfEngineClient {
  private worker: Worker | null = null;
  private ready: Promise<void> | null = null;
  private rejectReady: ((reason: Error) => void) | null = null;
  private nextId = 1;
  private pending = new Map<number, PendingCall>();

  constructor(private readonly assetBaseUrl?: string) {}

  private getWorker() {
    if (this.worker) return this.worker;
    const workerUrl = runtimeWorkerUrl(
      this.assetBaseUrl,
      PDF_ENGINE_WORKER_FILE,
      new URL('../workers/pdfEngine.bootstrap.worker.ts', import.meta.url),
    );
    const worker = new Worker(
      workerUrl,
      { type: 'module', name: 'atlas-mupdf-engine' },
    );
    let readyTimer: number | undefined;
    this.ready = new Promise<void>((resolve, reject) => {
      this.rejectReady = reject;
      readyTimer = window.setTimeout(() => reject(new Error('The MuPDF WebAssembly worker did not become ready.')), 20_000);
      const handleReady = (event: MessageEvent<{ type?: string; error?: string }>) => {
        if (event.data.type === 'bootstrap-error') {
          window.clearTimeout(readyTimer);
          worker.removeEventListener('message', handleReady);
          reject(new Error(event.data.error || 'The MuPDF WebAssembly worker failed to load.'));
          return;
        }
        if (event.data.type !== 'ready') return;
        window.clearTimeout(readyTimer);
        worker.removeEventListener('message', handleReady);
        this.rejectReady = null;
        resolve();
      };
      worker.addEventListener('message', handleReady);
    });
    worker.onmessage = (event: MessageEvent<{ type?: string; id?: number; result?: EngineResult; error?: string }>) => {
      if (event.data.type === 'ready' || event.data.id == null) return;
      const call = this.pending.get(event.data.id);
      if (!call) return;
      this.pending.delete(event.data.id);
      if (event.data.error) call.reject(new Error(event.data.error));
      else call.resolve(event.data.result ?? {});
    };
    worker.onerror = (event) => {
      const error = new Error(event.message || 'The PDF processing worker failed.');
      window.clearTimeout(readyTimer);
      this.rejectReady?.(error);
      this.rejectReady = null;
      for (const call of this.pending.values()) call.reject(error);
      this.pending.clear();
    };
    this.worker = worker;
    return worker;
  }

  call(command: EngineCommand): Promise<EngineResult> {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      const worker = this.getWorker();
      void this.ready?.then(() => worker.postMessage({ id, command })).catch((error: unknown) => {
        this.pending.delete(id);
        reject(error instanceof Error ? error : new Error(String(error)));
      });
    });
  }

  resetIfStarted(): Promise<EngineResult> {
    if (!this.worker) return Promise.resolve({});
    return this.call({ type: 'reset' });
  }

  destroy() {
    this.worker?.terminate();
    this.worker = null;
    this.rejectReady?.(new Error('PDF engine was closed.'));
    this.rejectReady = null;
    this.ready = null;
    const error = new Error('PDF engine was closed.');
    for (const call of this.pending.values()) call.reject(error);
    this.pending.clear();
  }
}
