/// <reference lib="webworker" />

self.postMessage({ type: 'bootstrapping' });

void import('./scanConversion.worker').catch((error: unknown) => {
  self.postMessage({ type: 'error', error: error instanceof Error ? error.message : String(error) });
});
