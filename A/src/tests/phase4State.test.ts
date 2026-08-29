import { describe, expect, it } from 'vitest';
import { DEFAULT_VIEW_STATE, clampEditorZoom, rotateViewDegrees } from '../lib/phase4State';

describe('Phase 4 view state', () => {
  it('opens a new source in single-page mode at 125%', () => {
    expect(DEFAULT_VIEW_STATE).toEqual({ viewMode: 'single', zoomMode: 'custom', scale: 1.25 });
  });

  it('normalizes temporary view rotation without mutating page data', () => {
    expect(rotateViewDegrees(0, -90)).toBe(270);
    expect(rotateViewDegrees(270, 90)).toBe(0);
  });

  it('keeps editor zoom inside practical independent limits', () => {
    expect(clampEditorZoom(0.1)).toBe(0.18);
    expect(clampEditorZoom(0.33)).toBe(0.33);
    expect(clampEditorZoom(0.9)).toBe(0.5);
  });
});
