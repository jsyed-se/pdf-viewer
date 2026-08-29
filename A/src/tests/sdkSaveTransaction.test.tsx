import { act, create, type ReactTestInstance, type ReactTestRenderer } from 'react-test-renderer';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const { engineCallMock, getDocumentMock } = vi.hoisted(() => ({
  engineCallMock: vi.fn(),
  getDocumentMock: vi.fn(),
}));

vi.mock('pdfjs-dist', () => ({
  GlobalWorkerOptions: { workerSrc: '' },
  PasswordResponses: { INCORRECT_PASSWORD: 2 },
  getDocument: getDocumentMock,
}));

vi.mock('../sdk/engineClient', () => ({
  PdfEngineClient: class {
    call = engineCallMock;
    resetIfStarted = vi.fn().mockResolvedValue(undefined);
    destroy = vi.fn();
  },
}));

vi.mock('../components/PdfPageCanvas', () => ({ PdfPageCanvas: () => null }));
vi.mock('../components/DocumentEditor', () => ({
  DocumentEditor: ({ onSave }: { onSave: () => void }) => (
    <button type="button" aria-label="Save transaction" onClick={onSave}>Save transaction</button>
  ),
}));

import { PdfViewerSDK } from '../sdk/PdfViewerSDK';
import type { PdfSaveRequest, PdfSaveResult } from '../sdk/publicTypes';

const dirtySnapshot = {
  pageCount: 1,
  pages: [{ index: 0, width: 612, height: 792, rotation: 0, annotationCount: 0, widgetCount: 0 }],
  annotations: [],
  widgets: [],
  bookmarks: [],
  canUndo: true,
  canRedo: false,
  hasClipboard: false,
  dirty: true,
  wasm: true,
  capabilities: {
    nativeAnnotations: true,
    appliedRedaction: true,
    bookmarkEditing: true,
    signatureWidgetCreation: false,
  },
} as const;

function loadingTask() {
  const document = {
    numPages: 1,
    cleanup: vi.fn().mockResolvedValue(undefined),
    getData: vi.fn().mockResolvedValue(new Uint8Array([37, 80, 68, 70, 45])),
    getPage: vi.fn().mockResolvedValue({ getViewport: () => ({ width: 612, height: 792 }) }),
  };
  return {
    promise: Promise.resolve(document),
    destroy: vi.fn().mockResolvedValue(undefined),
    onProgress: undefined,
    onPassword: undefined,
  };
}

async function settle() {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
}

function button(renderer: ReactTestRenderer, label: string): ReactTestInstance {
  return renderer.root.find((node) => node.type === 'button' && node.props['aria-label'] === label);
}

async function openEditor(renderer: ReactTestRenderer) {
  await act(async () => {
    button(renderer, 'Edit document').props.onClick();
    await settle();
  });
}

describe('transactional host save', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    getDocumentMock.mockReset();
    getDocumentMock.mockImplementation(loadingTask);
    engineCallMock.mockReset();
    engineCallMock.mockImplementation(async (command: { type: string }) => {
      if (command.type === 'open') return { snapshot: dirtySnapshot };
      if (command.type === 'serialize') return { snapshot: dirtySnapshot, bytes: new Uint8Array([37, 80, 68, 70, 45, 49]) };
      if (command.type === 'commit') return { snapshot: { ...dirtySnapshot, dirty: false } };
      return { snapshot: dirtySnapshot };
    });
    vi.stubGlobal('window', {
      setTimeout,
      clearTimeout,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      confirm: vi.fn(() => true),
      prompt: vi.fn(),
    });
    Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  });

  it('commits only after the host save promise resolves', async () => {
    let resolveSave!: (result: PdfSaveResult) => void;
    const onSave = vi.fn((request: PdfSaveRequest) => {
      void request;
      return new Promise<PdfSaveResult>((resolve) => { resolveSave = resolve; });
    });
    const onDirtyChange = vi.fn();
    let renderer!: ReactTestRenderer;

    await act(async () => {
      renderer = create(<PdfViewerSDK source={{ kind: 'url', url: '/sample.pdf', filename: 'sample.pdf' }} onSave={onSave} onDirtyChange={onDirtyChange} />);
      await settle();
    });
    await openEditor(renderer);

    await act(async () => {
      button(renderer, 'Save transaction').props.onClick();
      await settle();
    });

    expect(onSave).toHaveBeenCalledOnce();
    expect(onSave.mock.calls[0][0]).toMatchObject({ filename: 'sample.pdf', mimeType: 'application/pdf' });
    expect(onSave.mock.calls[0][0].bytes).toBeInstanceOf(Uint8Array);
    expect(engineCallMock.mock.calls.map(([command]) => command.type)).not.toContain('commit');
    expect(onDirtyChange).toHaveBeenLastCalledWith(true);

    resolveSave({ attachment: { id: 'saved', filename: 'sample.pdf' }, savedAt: '2026-08-29T00:00:00.000Z' });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(3_000);
      await settle();
    });

    expect(engineCallMock.mock.calls.map(([command]) => command.type)).toContain('commit');
    expect(onDirtyChange).toHaveBeenLastCalledWith(false);
    await act(async () => renderer.unmount());
    vi.useRealTimers();
  });

  it('keeps dirty edits and skips commit when the host rejects', async () => {
    const failure = new Error('Host persistence failed.');
    const onSave = vi.fn().mockRejectedValue(failure);
    const onError = vi.fn();
    const onDirtyChange = vi.fn();
    let renderer!: ReactTestRenderer;

    await act(async () => {
      renderer = create(<PdfViewerSDK source={{ kind: 'url', url: '/sample.pdf', filename: 'sample.pdf' }} onSave={onSave} onError={onError} onDirtyChange={onDirtyChange} />);
      await settle();
    });
    await openEditor(renderer);

    await act(async () => {
      button(renderer, 'Save transaction').props.onClick();
      await settle();
    });

    expect(engineCallMock.mock.calls.map(([command]) => command.type)).not.toContain('commit');
    expect(onDirtyChange).toHaveBeenLastCalledWith(true);
    expect(onError).toHaveBeenCalledWith(failure);
    expect(renderer.root.findAll((node) => node.props.role === 'alertdialog')).toHaveLength(1);
    expect(button(renderer, 'Save transaction')).toBeTruthy();

    await act(async () => {
      await vi.runAllTimersAsync();
      renderer.unmount();
    });
    vi.useRealTimers();
  });
});
