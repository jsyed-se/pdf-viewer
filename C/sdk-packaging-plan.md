# SDK Packaging Correction Plan

## Baseline and scope

- Branch: `feature/sdk`
- Main baseline: `fa07068d9da4e9d9180438858628b2bd490a6650`
- Goal: turn the existing SDK-shaped React component into a locally distributable package without changing PDF behavior or the host/SDK ownership boundary.
- Preserve: PDF.js viewing, MuPDF worker processing, scan conversion, transactional save, the demo host, existing tests, screenshots, transcript, licenses, and the `A/`, `B/`, `C/` layout.
- Exclude: new PDF features, UI redesign, npm publication, production-support claims, demo persistence code, internal engine APIs, evidence, transcripts, screenshots, fixtures, and temporary validation artifacts.

The baseline has no package entry point, declaration build, peer dependencies, or package allowlist. The demo imports SDK source directly. PDF.js, MuPDF, and scan workers use Vite source transforms that must be proven from an installed tarball rather than assumed from the monorepo build.

## Implementation sequence

1. **Define the public contract.** Add one explicit SDK entry that exports `PdfViewerSDK` and host-facing source, attachment, lifecycle, save, progress, error, and result types. Separate those declarations from worker commands, engine snapshots, clients, and UI internals. Make the demo consume the public entry.
2. **Separate SDK presentation from host presentation.** Publish scoped viewer/editor styles through an explicit stylesheet export while keeping records, attachment, and page-shell rules demo-only.
3. **Add an independent library build.** Produce ESM, bundled runtime chunks/assets, source maps, and generated declarations in a dedicated output. Externalize React, React DOM, and the JSX runtime; declare React packages as peers while retaining local development copies.
4. **Constrain the package.** Add accurate ESM entry, type, export, file, peer, license, and local-package metadata. Include the package README, AGPL license, MuPDF notice, and source offer. Allow only the consumer runtime and legal files into `npm pack`.
5. **Prove automatic asset resolution.** Inspect the built package for the PDF.js worker, MuPDF worker/WASM, and scan worker. Use package-relative emitted URLs if the packed consumer resolves every asset in development and production. Add a typed asset-base option only if automatic resolution fails.
6. **Add an independent consumer.** Keep a small React example outside the SDK workspace. It imports only the package name and documented stylesheet, opens a controlled PDF, reports dirty state, and implements successful and rejected host saves. Validation installs the generated tarball into a clean temporary copy.
7. **Add focused packaging tests.** Check the exact public export surface, metadata and peer dependencies, generated declarations, tarball allowlist, absence of demo/internal files, consumer TypeScript compilation, worker asset output, and the existing callback/source lifecycle regression.
8. **Validate the artifact.** From a lockfile install, run type checking, linting, all tests, the demo build, SDK build, and `npm pack`. Install the tarball in a temporary consumer; type-check and build it; then exercise development and production browser flows. Require PDF rendering, navigation, one MuPDF mutation, successful host save, failed-save dirty preservation, and zero worker/WASM 404s.
9. **Update only material documentation.** Document public APIs, build/pack/install commands, the package/consumer architecture boundary, transactional saves, automatic assets, exact validation evidence, browser limits, and AGPL/commercial-license risk. Preserve historical records and do not fabricate AI artifacts.

## Completion gate

Completion requires a clean packed-consumer proof, not merely a successful source build. The tarball must expose usable ESM and declarations, keep React external, contain only intended runtime/legal files, and work in a production consumer with PDF.js and MuPDF/scan assets loaded successfully. Existing functionality and quality gates must remain green. Only after every acceptance item passes will the correction be committed and pushed.
