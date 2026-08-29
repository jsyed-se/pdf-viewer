interface ScanProgress {
  completed: number;
  total: number;
  filename: string;
}

interface ScanInput {
  name: string;
  mimeType: string;
  bytes: Uint8Array;
}

export async function convertScanImages(
  files: File[],
  signal: AbortSignal,
  onProgress: (progress: ScanProgress) => void,
): Promise<Uint8Array> {
  if (files.length === 0) throw new Error('Choose one or more PNG or JPEG images.');
  const inputs: ScanInput[] = [];
  for (const [index, file] of files.entries()) {
    if (signal.aborted) throw new DOMException('Scan import cancelled.', 'AbortError');
    if (!/^image\/(png|jpeg)$/i.test(file.type) && !/\.(png|jpe?g)$/i.test(file.name)) {
      throw new Error(`${file.name} is not a supported PNG or JPEG image.`);
    }
    inputs.push({ name: file.name, mimeType: file.type, bytes: new Uint8Array(await file.arrayBuffer()) });
    onProgress({ completed: index + 1, total: files.length * 2, filename: `Read ${file.name}` });
  }
  if (signal.aborted) throw new DOMException('Scan import cancelled.', 'AbortError');

  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL('../workers/scanConversion.bootstrap.worker.ts', import.meta.url), { type: 'module', name: 'atlas-scan-converter' });
    const abort = () => {
      worker.terminate();
      reject(new DOMException('Scan import cancelled.', 'AbortError'));
    };
    signal.addEventListener('abort', abort, { once: true });
    worker.onmessage = (event: MessageEvent<{ type: string; completed?: number; total?: number; filename?: string; bytes?: Uint8Array; error?: string }>) => {
      if (event.data.type === 'ready') {
        const transfer = inputs.map((input) => input.bytes.buffer);
        worker.postMessage({ images: inputs }, transfer);
      } else if (event.data.type === 'progress' && event.data.completed != null && event.data.total != null) {
        onProgress({ completed: files.length + event.data.completed, total: files.length * 2, filename: `Converted ${event.data.filename ?? 'image'}` });
      } else if (event.data.type === 'complete' && event.data.bytes) {
        signal.removeEventListener('abort', abort);
        worker.terminate();
        resolve(event.data.bytes);
      } else if (event.data.type === 'error') {
        signal.removeEventListener('abort', abort);
        worker.terminate();
        reject(new Error(event.data.error || 'Image conversion failed.'));
      }
    };
    worker.onerror = (event) => {
      signal.removeEventListener('abort', abort);
      worker.terminate();
      reject(new Error(event.message || 'Image conversion worker failed.'));
    };
  });
}
