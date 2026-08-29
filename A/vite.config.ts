import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';

const recordId = 'CASE-2026-0042';
const attachmentId = 'ATT-0001';
const runtimeDirectory = resolve(import.meta.dirname, '.runtime-data');
const runtimePdf = resolve(runtimeDirectory, `${attachmentId}.pdf`);
const runtimeManifest = resolve(runtimeDirectory, 'records.json');
const seedPdf = resolve(import.meta.dirname, '..', 'C', 'evidence', 'generated-pdfs', 'combined-working-copy.pdf');

interface DemoAttachment {
  id: string;
  recordId: string;
  filename: string;
  mimeType: 'application/pdf';
  size: number;
  updatedAt: string;
}

interface DemoRecord {
  id: string;
  title: string;
  description: string;
  attachments: DemoAttachment[];
}

async function ensureDemoRecords(): Promise<DemoRecord[]> {
  await mkdir(runtimeDirectory, { recursive: true });
  try {
    return JSON.parse(await readFile(runtimeManifest, 'utf8')) as DemoRecord[];
  } catch {
    const bytes = await readFile(seedPdf);
    await writeFile(runtimePdf, bytes);
    const records: DemoRecord[] = [{
      id: recordId,
      title: 'Northwind permit review',
      description: 'Safe local demonstration record',
      attachments: [{
        id: attachmentId,
        recordId,
        filename: 'permit-review.pdf',
        mimeType: 'application/pdf',
        size: bytes.byteLength,
        updatedAt: new Date().toISOString(),
      }],
    }];
    await writeFile(runtimeManifest, JSON.stringify(records, null, 2));
    return records;
  }
}

function sendJson(response: ServerResponse, status: number, value: unknown) {
  response.statusCode = status;
  response.setHeader('Content-Type', 'application/json');
  response.end(JSON.stringify(value));
}

async function readRequestBody(request: IncomingMessage, limit = 25 * 1024 * 1024) {
  const chunks: Buffer[] = [];
  let length = 0;
  for await (const chunk of request) {
    const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    length += bytes.length;
    if (length > limit) throw new Error('The edited PDF exceeds the 25 MB demo limit.');
    chunks.push(bytes);
  }
  return Buffer.concat(chunks);
}

async function demoApiMiddleware(request: IncomingMessage, response: ServerResponse, next: () => void) {
        if (!request.url?.startsWith('/api/demo/')) return next();
        try {
          const url = new URL(request.url, 'http://localhost');
          const match = url.pathname.match(/^\/api\/demo\/records\/([^/]+)\/attachments\/([^/]+)$/);
          if (request.method === 'GET' && url.pathname === '/api/demo/records') {
            return sendJson(response, 200, await ensureDemoRecords());
          }
          if (!match) return sendJson(response, 404, { error: 'Demo resource not found.' });
          const [, requestedRecordId, requestedAttachmentId] = match;
          const records = await ensureDemoRecords();
          const record = records.find((item) => item.id === requestedRecordId);
          const attachment = record?.attachments.find((item) => item.id === requestedAttachmentId);
          if (!record || !attachment) return sendJson(response, 404, { error: 'Attachment not found.' });
          if (request.method === 'GET') {
            const bytes = await readFile(runtimePdf);
            response.statusCode = 200;
            response.setHeader('Content-Type', 'application/pdf');
            response.setHeader('Content-Length', bytes.byteLength);
            response.setHeader('Content-Disposition', `attachment; filename="${attachment.filename.replace(/["\r\n]/g, '')}"`);
            return response.end(bytes);
          }
          if (request.method === 'PUT') {
            if (!/^application\/pdf(?:;|$)/i.test(String(request.headers['content-type'] ?? ''))) {
              return sendJson(response, 415, { error: 'Only application/pdf uploads are accepted.' });
            }
            const bytes = await readRequestBody(request);
            if (!bytes.subarray(0, 5).equals(Buffer.from('%PDF-'))) {
              return sendJson(response, 400, { error: 'The upload is not a valid PDF payload.' });
            }
            const requestedFilename = decodeURIComponent(String(request.headers['x-filename'] ?? attachment.filename));
            const safeFilename = requestedFilename.replace(/[^a-z0-9._-]+/gi, '-').replace(/^-+|-+$/g, '') || attachment.filename;
            attachment.filename = safeFilename.toLowerCase().endsWith('.pdf') ? safeFilename : `${safeFilename}.pdf`;
            attachment.size = bytes.byteLength;
            attachment.updatedAt = new Date().toISOString();
            await writeFile(runtimePdf, bytes);
            await writeFile(runtimeManifest, JSON.stringify(records, null, 2));
            return sendJson(response, 200, { attachment, savedAt: attachment.updatedAt });
          }
          return sendJson(response, 405, { error: 'Method not allowed.' });
        } catch (error) {
          return sendJson(response, 500, { error: error instanceof Error ? error.message : String(error) });
        }
}

function demoPersistencePlugin(): Plugin {
  return {
    name: 'atlas-demo-persistence',
    configureServer(server) {
      server.middlewares.use(demoApiMiddleware);
    },
    configurePreviewServer(server) {
      server.middlewares.use(demoApiMiddleware);
    },
  };
}

export default defineConfig({
  plugins: [react(), demoPersistencePlugin()],
  worker: { format: 'es' },
  build: { target: 'es2022' },
});
