import { describe, expect, expectTypeOf, it, vi } from 'vitest';

vi.mock('pdfjs-dist', () => ({
  GlobalWorkerOptions: { workerSrc: '' },
  PasswordResponses: { INCORRECT_PASSWORD: 2 },
  getDocument: vi.fn(),
}));

import * as publicApi from '../sdk';
import type {
  AttachmentMetadata,
  PdfDocumentSource,
  PdfReadyDetails,
  PdfSaveRequest,
  PdfSaveResult,
  PdfViewerAssetConfig,
  PdfViewerSDKProps,
  ViewerLifecycleCallbacks,
} from '../sdk';

describe('SDK public API', () => {
  it('exposes only the supported runtime component', () => {
    expect(Object.keys(publicApi).sort()).toEqual(['PdfViewerSDK']);
  });

  it('keeps host-facing contracts available from the public entry', () => {
    expectTypeOf<PdfViewerSDKProps>().toMatchTypeOf<ViewerLifecycleCallbacks>();
    expectTypeOf<PdfViewerSDKProps['source']>().toEqualTypeOf<PdfDocumentSource | null>();
    expectTypeOf<PdfViewerSDKProps['attachment']>().toEqualTypeOf<AttachmentMetadata | undefined>();
    expectTypeOf<PdfViewerSDKProps['assets']>().toEqualTypeOf<PdfViewerAssetConfig | undefined>();
    expectTypeOf<NonNullable<PdfViewerSDKProps['onReady']>>()
      .toEqualTypeOf<(details: PdfReadyDetails) => void>();
    expectTypeOf<NonNullable<PdfViewerSDKProps['onSave']>>()
      .toEqualTypeOf<(request: PdfSaveRequest) => Promise<PdfSaveResult>>();
  });
});
