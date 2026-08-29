import type { ViewMode, ZoomMode } from '../sdk/types';

export const DEFAULT_VIEW_STATE: { viewMode: ViewMode; zoomMode: ZoomMode; scale: number } = {
  viewMode: 'single',
  zoomMode: 'custom',
  scale: 1.25,
};

export function rotateViewDegrees(current: number, degrees: -90 | 90) {
  return (((current + degrees) % 360) + 360) % 360;
}

export function clampEditorZoom(value: number) {
  return Math.max(0.18, Math.min(0.5, value));
}
