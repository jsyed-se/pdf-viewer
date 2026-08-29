import type { AttachmentMetadata, PdfSaveRequest, PdfSaveResult } from '../sdk';

export interface DemoRecord {
  id: string;
  title: string;
  description: string;
  attachments: Array<AttachmentMetadata & { mimeType: 'application/pdf'; size: number; updatedAt: string }>;
}

async function responseError(response: Response) {
  try {
    const value = await response.json() as { error?: string };
    return value.error || `The demo server returned HTTP ${response.status}.`;
  } catch {
    return `The demo server returned HTTP ${response.status}.`;
  }
}

export async function listDemoRecords(signal?: AbortSignal): Promise<DemoRecord[]> {
  const response = await fetch('/api/demo/records', { signal });
  if (!response.ok) throw new Error(await responseError(response));
  return response.json() as Promise<DemoRecord[]>;
}

export async function loadDemoAttachment(recordId: string, attachmentId: string, signal?: AbortSignal) {
  const response = await fetch(`/api/demo/records/${encodeURIComponent(recordId)}/attachments/${encodeURIComponent(attachmentId)}`, { signal });
  if (!response.ok) throw new Error(await responseError(response));
  return new Uint8Array(await response.arrayBuffer());
}

export async function persistDemoAttachment(request: PdfSaveRequest): Promise<PdfSaveResult> {
  const recordId = request.attachment?.recordId;
  const attachmentId = request.attachment?.id;
  if (!recordId || !attachmentId) throw new Error('Choose a persisted record attachment before uploading changes.');
  const response = await fetch(`/api/demo/records/${encodeURIComponent(recordId)}/attachments/${encodeURIComponent(attachmentId)}`, {
    method: 'PUT',
    headers: {
      'Content-Type': request.mimeType,
      'X-Filename': encodeURIComponent(request.filename),
    },
    body: Uint8Array.from(request.bytes).buffer,
    signal: request.signal,
  });
  if (!response.ok) throw new Error(await responseError(response));
  return response.json() as Promise<PdfSaveResult>;
}
