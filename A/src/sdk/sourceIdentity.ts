import type { PdfDocumentSource } from './publicTypes';

export type PdfDocumentSourceIdentity = string | File | Uint8Array | null;

/**
 * Identifies the document payload without depending on the caller's wrapper object.
 * This lets hosts use inline source objects without restarting an unchanged load.
 */
export function documentSourceIdentity(source: PdfDocumentSource | null): PdfDocumentSourceIdentity {
  if (!source) return null;
  if (source.kind === 'url') return source.url;
  if (source.kind === 'file') return source.file;
  return source.bytes;
}
