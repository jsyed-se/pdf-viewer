import { useEffect, useRef, useState } from 'react';
import { TextLayer, type PDFDocumentProxy, type PDFPageProxy } from 'pdfjs-dist';
import type { AnnotationTool } from '../sdk/types';

type PdfQuad = [number, number, number, number, number, number, number, number];
type RegionAnnotationTool = 'text' | 'highlight' | 'redact';

interface PdfPageCanvasProps {
  document: PDFDocumentProxy;
  pageNumber: number;
  scale: number;
  compact?: boolean;
  active?: boolean;
  annotationTool?: AnnotationTool;
  selectedAnnotationRect?: [number, number, number, number];
  onVisible?: (pageNumber: number) => void;
  onAnnotate?: (
    pageNumber: number,
    tool: RegionAnnotationTool,
    pdfRect: [number, number, number, number],
  ) => void;
  onTextAnnotate?: (pageNumber: number, tool: 'highlight-text' | 'redact-text', pdfQuads: PdfQuad[]) => void;
}

interface Point {
  x: number;
  y: number;
}

export function PdfPageCanvas({
  document,
  pageNumber,
  scale,
  compact = false,
  active = false,
  annotationTool = 'none',
  selectedAnnotationRect,
  onVisible,
  onAnnotate,
  onTextAnnotate,
}: PdfPageCanvasProps) {
  const frameRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const textLayerRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<ReturnType<PDFPageProxy['getViewport']> | null>(null);
  const [nearViewport, setNearViewport] = useState(false);
  const [dimensions, setDimensions] = useState({
    width: compact ? 140 : 612 * scale,
    height: compact ? 180 : 792 * scale,
  });
  const [drawingStart, setDrawingStart] = useState<Point | null>(null);
  const [drawingEnd, setDrawingEnd] = useState<Point | null>(null);
  const [selectedAnnotationStyle, setSelectedAnnotationStyle] = useState<React.CSSProperties | undefined>();
  const [renderError, setRenderError] = useState<string | null>(null);
  const onVisibleRef = useRef(onVisible);

  useEffect(() => {
    onVisibleRef.current = onVisible;
  }, [onVisible]);

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;
    const root = compact ? frame.closest('.thumbnail-rail') : frame.closest('.page-workspace');
    const preloadObserver = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setNearViewport(true);
      },
      { root, rootMargin: compact ? '400px 0px' : '700px 0px', threshold: 0 },
    );
    preloadObserver.observe(frame);
    const visibilityObserver = compact || !onVisibleRef.current
      ? null
      : new IntersectionObserver(
        ([entry]) => {
          if (entry.intersectionRatio >= 0.45) onVisibleRef.current?.(pageNumber);
        },
        { root, rootMargin: '0px', threshold: [0, 0.45] },
      );
    visibilityObserver?.observe(frame);
    return () => {
      preloadObserver.disconnect();
      visibilityObserver?.disconnect();
    };
  }, [compact, pageNumber]);

  useEffect(() => {
    if (!nearViewport) return;
    setRenderError(null);
    let cancelled = false;
    let activeTask: ReturnType<PDFPageProxy['render']> | null = null;
    void document.getPage(pageNumber)
      .then(async (page) => {
        if (cancelled || !canvasRef.current) return;
        const viewport = page.getViewport({ scale });
        viewportRef.current = viewport;
        setDimensions({ width: viewport.width, height: viewport.height });
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d', { alpha: false });
        if (!context) throw new Error('Canvas rendering is unavailable in this browser.');
        const outputScale = Math.min(window.devicePixelRatio || 1, compact ? 1.5 : 2.5);
        canvas.width = Math.max(1, Math.floor(viewport.width * outputScale));
        canvas.height = Math.max(1, Math.floor(viewport.height * outputScale));
        canvas.style.width = `${viewport.width}px`;
        canvas.style.height = `${viewport.height}px`;
        activeTask = page.render({
          canvas,
          canvasContext: context,
          viewport,
          transform: outputScale === 1 ? undefined : [outputScale, 0, 0, outputScale, 0, 0],
        });
        await activeTask.promise;
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        if (error instanceof Error && (error.name === 'RenderingCancelledException' || /Loading aborted|sendWithPromise/.test(error.message))) return;
        setRenderError(error instanceof Error ? error.message : 'This page could not be rendered.');
      });
    return () => {
      cancelled = true;
      activeTask?.cancel();
    };
  }, [compact, document, nearViewport, pageNumber, scale]);

  useEffect(() => {
    if (!selectedAnnotationRect) {
      setSelectedAnnotationStyle(undefined);
      return;
    }
    let cancelled = false;
    void document.getPage(pageNumber).then((page) => {
      if (cancelled) return;
      const viewport = page.getViewport({ scale });
      const first = viewport.convertToViewportPoint(selectedAnnotationRect[0], selectedAnnotationRect[1]);
      const second = viewport.convertToViewportPoint(selectedAnnotationRect[2], selectedAnnotationRect[3]);
      setSelectedAnnotationStyle({
        left: Math.min(first[0], second[0]),
        top: Math.min(first[1], second[1]),
        width: Math.abs(second[0] - first[0]),
        height: Math.abs(second[1] - first[1]),
      });
    }).catch(() => setSelectedAnnotationStyle(undefined));
    return () => { cancelled = true; };
  }, [document, pageNumber, scale, selectedAnnotationRect]);

  useEffect(() => {
    if (compact || !nearViewport || !textLayerRef.current) return;
    const container = textLayerRef.current;
    let cancelled = false;
    let textLayer: TextLayer | null = null;
    container.replaceChildren();
    void document.getPage(pageNumber)
      .then(async (page) => {
        if (cancelled) return;
        const viewport = page.getViewport({ scale });
        textLayer = new TextLayer({
          textContentSource: page.streamTextContent(),
          container,
          viewport,
        });
        await textLayer.render();
      })
      .catch((error: unknown) => {
        if (cancelled || (error instanceof Error && /cancel/i.test(error.message))) return;
        setRenderError(error instanceof Error ? error.message : 'The selectable text layer could not be rendered.');
      });
    return () => {
      cancelled = true;
      textLayer?.cancel();
      container.replaceChildren();
    };
  }, [compact, document, nearViewport, pageNumber, scale]);

  const pointFromEvent = (event: React.PointerEvent<HTMLDivElement>): Point => {
    const rect = event.currentTarget.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
  };

  const finishAnnotation = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!drawingStart || !viewportRef.current || (annotationTool !== 'text' && annotationTool !== 'highlight' && annotationTool !== 'redact')) return;
    const end = pointFromEvent(event);
    const startPdf = viewportRef.current.convertToPdfPoint(drawingStart.x, drawingStart.y);
    const endPdf = viewportRef.current.convertToPdfPoint(end.x, end.y);
    const minimum = annotationTool === 'text' ? 24 : 8;
    const cssWidth = Math.abs(end.x - drawingStart.x);
    const cssHeight = Math.abs(end.y - drawingStart.y);
    const adjustedEnd =
      cssWidth < minimum && cssHeight < minimum
        ? viewportRef.current.convertToPdfPoint(drawingStart.x + minimum, drawingStart.y + minimum)
        : endPdf;
    onAnnotate?.(pageNumber, annotationTool, [startPdf[0], startPdf[1], adjustedEnd[0], adjustedEnd[1]]);
    setDrawingStart(null);
    setDrawingEnd(null);
    event.currentTarget.releasePointerCapture(event.pointerId);
  };

  const selectionStyle = drawingStart && drawingEnd
    ? {
        left: Math.min(drawingStart.x, drawingEnd.x),
        top: Math.min(drawingStart.y, drawingEnd.y),
        width: Math.abs(drawingEnd.x - drawingStart.x),
        height: Math.abs(drawingEnd.y - drawingStart.y),
      }
    : undefined;

  const finishTextSelection = (event: React.PointerEvent<HTMLDivElement>) => {
    if ((annotationTool !== 'highlight-text' && annotationTool !== 'redact-text') || !viewportRef.current || !frameRef.current) return;
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return;
    const range = selection.getRangeAt(0);
    const layer = event.currentTarget;
    if (!layer.contains(range.startContainer) && !layer.contains(range.endContainer)) return;
    const frameRect = frameRef.current.getBoundingClientRect();
    const quads = Array.from(range.getClientRects()).flatMap<PdfQuad>((rect) => {
      const left = Math.max(rect.left, frameRect.left);
      const right = Math.min(rect.right, frameRect.right);
      const top = Math.max(rect.top, frameRect.top);
      const bottom = Math.min(rect.bottom, frameRect.bottom);
      if (right - left < 1 || bottom - top < 1) return [];
      const upperLeft = viewportRef.current!.convertToPdfPoint(left - frameRect.left, top - frameRect.top);
      const upperRight = viewportRef.current!.convertToPdfPoint(right - frameRect.left, top - frameRect.top);
      const lowerLeft = viewportRef.current!.convertToPdfPoint(left - frameRect.left, bottom - frameRect.top);
      const lowerRight = viewportRef.current!.convertToPdfPoint(right - frameRect.left, bottom - frameRect.top);
      return [[...upperLeft, ...upperRight, ...lowerLeft, ...lowerRight] as PdfQuad];
    });
    if (quads.length === 0) return;
    onTextAnnotate?.(pageNumber, annotationTool, quads);
    selection.removeAllRanges();
  };

  return (
    <div
      ref={frameRef}
      className={`pdf-page-frame${compact ? ' compact' : ''}${active ? ' active' : ''}`}
      style={{ width: dimensions.width, minHeight: dimensions.height }}
      data-page-number={pageNumber}
      role="group"
      aria-label={`PDF page ${pageNumber}`}
    >
      <canvas ref={canvasRef} aria-hidden="true" />
      {!compact && (
        <div
          ref={textLayerRef}
          className={`text-layer${annotationTool === 'highlight-text' || annotationTool === 'redact-text' ? ' selecting' : ''}`}
          role="group"
          aria-label={`Selectable text for page ${pageNumber}`}
          onPointerUp={finishTextSelection}
        />
      )}
      {!nearViewport && <div className="page-skeleton" role="img" aria-label={`Page ${pageNumber} waiting to render`} />}
      {renderError && <div className="page-render-error" role="alert">Page {pageNumber} could not be rendered: {renderError}</div>}
      {!compact && annotationTool !== 'none' && annotationTool !== 'highlight-text' && annotationTool !== 'redact-text' && (
        <div
          className={`annotation-draw-layer tool-${annotationTool}`}
          role="application"
          aria-label={`Draw ${annotationTool} annotation on page ${pageNumber}`}
          onPointerDown={(event) => {
            event.currentTarget.setPointerCapture(event.pointerId);
            const point = pointFromEvent(event);
            setDrawingStart(point);
            setDrawingEnd(point);
          }}
          onPointerMove={(event) => drawingStart && setDrawingEnd(pointFromEvent(event))}
          onPointerUp={finishAnnotation}
          onPointerCancel={() => {
            setDrawingStart(null);
            setDrawingEnd(null);
          }}
        >
          {selectionStyle && <span className="annotation-selection" style={selectionStyle} />}
        </div>
      )}
      {selectedAnnotationStyle && <span className="selected-annotation-region" style={selectedAnnotationStyle} aria-hidden="true" />}
      <span className="page-number-badge" aria-hidden="true">{pageNumber}</span>
    </div>
  );
}
