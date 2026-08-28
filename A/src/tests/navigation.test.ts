import { describe, expect, it } from 'vitest';
import { decideVisiblePage } from '../lib/navigation';

describe('decideVisiblePage', () => {
  it('accepts ordinary scroll tracking when no navigation is pending', () => {
    expect(decideVisiblePage(null, 3)).toEqual({ accept: true, clearPendingNavigation: false });
  });

  it('ignores an old visible page while programmatic navigation is pending', () => {
    expect(decideVisiblePage(8, 2)).toEqual({ accept: false, clearPendingNavigation: false });
  });

  it('accepts the requested page and releases the navigation lock', () => {
    expect(decideVisiblePage(8, 8)).toEqual({ accept: true, clearPendingNavigation: true });
  });
});
