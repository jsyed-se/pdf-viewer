import { describe, expect, it } from 'vitest';
import { documentSourceIdentity } from '../sdk/sourceIdentity';

describe('document source identity', () => {
  it('ignores new wrapper objects for the same URL', () => {
    expect(documentSourceIdentity({ kind: 'url', url: '/document.pdf' }))
      .toBe(documentSourceIdentity({ kind: 'url', url: '/document.pdf' }));
  });

  it('uses the underlying file or byte-array reference', () => {
    const file = new File(['%PDF-'], 'document.pdf', { type: 'application/pdf' });
    const bytes = new Uint8Array([37, 80, 68, 70, 45]);

    expect(documentSourceIdentity({ kind: 'file', file }))
      .toBe(documentSourceIdentity({ kind: 'file', file }));
    expect(documentSourceIdentity({ kind: 'bytes', bytes, filename: 'first.pdf' }))
      .toBe(documentSourceIdentity({ kind: 'bytes', bytes, filename: 'renamed.pdf' }));
  });

  it('changes when the document payload changes', () => {
    expect(documentSourceIdentity({ kind: 'url', url: '/first.pdf' }))
      .not.toBe(documentSourceIdentity({ kind: 'url', url: '/second.pdf' }));
    expect(documentSourceIdentity({ kind: 'bytes', bytes: new Uint8Array([1]), filename: 'document.pdf' }))
      .not.toBe(documentSourceIdentity({ kind: 'bytes', bytes: new Uint8Array([1]), filename: 'document.pdf' }));
  });
});
