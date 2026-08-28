/// <reference lib="webworker" />

self.postMessage({ type: 'bootstrapping' });

void import('./pdfEngine.worker').catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  self.postMessage({ type: 'bootstrap-error', error: message });
});
