export type PdfDocumentSource =
  | { kind: 'file'; file: File }
  | { kind: 'url'; url: string; filename?: string }
  | { kind: 'bytes'; bytes: Uint8Array; filename: string };

export interface AttachmentMetadata {
  id: string;
  filename: string;
  label?: string;
  recordId?: string;
  size?: number;
  updatedAt?: string;
}

export interface PdfReadyDetails {
  pageCount: number;
  filename: string;
}

export type PdfPasswordReason = 'required' | 'incorrect';
export type PdfProgressCallback = (loaded: number, total?: number) => void;
export type PdfErrorCallback = (error: Error) => void;

export interface PdfViewerAssetConfig {
  /** URL containing the package's copied `dist-sdk/assets` directory. */
  baseUrl: string;
}

export interface PdfSaveRequest {
  bytes: Uint8Array;
  filename: string;
  mimeType: 'application/pdf';
  attachment?: AttachmentMetadata;
  signal: AbortSignal;
}

export interface PdfSaveResult {
  attachment: AttachmentMetadata;
  savedAt: string;
}

export interface ViewerLifecycleCallbacks {
  onReady?: (details: PdfReadyDetails) => void;
  onProgress?: PdfProgressCallback;
  onError?: PdfErrorCallback;
  onPageChange?: (page: number) => void;
  onDirtyChange?: (dirty: boolean) => void;
  onSave?: (request: PdfSaveRequest) => Promise<PdfSaveResult>;
  onCloseRequest?: () => void;
  onPasswordRequest?: (reason: PdfPasswordReason) => Promise<string | null>;
}

export interface PdfViewerSDKProps extends ViewerLifecycleCallbacks {
  source: PdfDocumentSource | null;
  attachment?: AttachmentMetadata;
  assets?: PdfViewerAssetConfig;
  /** Opt in to the SDK's generic post-save dialog. Host applications own confirmation by default. */
  showSaveConfirmation?: boolean;
  className?: string;
}
