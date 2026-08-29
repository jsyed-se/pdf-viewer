# SDK Consumer Example

This application validates the installed package boundary. It imports the viewer and its public types from `@atlas-pdf/react-sdk` and imports presentation rules from `@atlas-pdf/react-sdk/styles.css`. It has no source aliases or repository-internal imports.

Build the SDK and create the local package from the repository root, then install the generated tarball here:

```sh
npm run build:sdk
npm run pack:sdk
cd examples/sdk-consumer
npm install
npm install ../../A/atlas-pdf-react-sdk-1.0.0.tgz
npm run typecheck
npm run build
npm run dev
```

For clean-consumer validation, copy this directory to a temporary location and install the tarball by absolute path. The `predev` and `prebuild` hooks copy the installed package's complete `dist-sdk/assets` directory to `public/atlas-pdf-assets`; the viewer receives that served location through `assets.baseUrl`. The example opens `public/sample.pdf`, reports SDK lifecycle and dirty-state callbacks, and lets the host save callback intentionally succeed or fail. Generated tarballs, `node_modules`, and build output are validation artifacts and must not be committed.
