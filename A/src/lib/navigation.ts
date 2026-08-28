export interface VisibilityDecision {
  accept: boolean;
  clearPendingNavigation: boolean;
}

export function decideVisiblePage(
  pendingNavigationPage: number | null,
  visiblePage: number,
): VisibilityDecision {
  if (pendingNavigationPage == null) {
    return { accept: true, clearPendingNavigation: false };
  }
  const reachedTarget = pendingNavigationPage === visiblePage;
  return { accept: reachedTarget, clearPendingNavigation: reachedTarget };
}
