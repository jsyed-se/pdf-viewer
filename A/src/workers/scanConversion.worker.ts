/// <reference lib="webworker" />

import * as mupdf from 'mupdf';

interface ScanImageInput {
  name: string;
  mimeType: string;
  bytes: Uint8Array;
}

function pageSize(image: mupdf.Image): [number, number] {
  const dpiX = image.getXResolution() > 0 ? image.getXResolution() : 96;
  const dpiY = image.getYResolution() > 0 ? image.getYResolution() : 96;
  const width = Math.min(14_400, Math.max(36, image.getWidth() * 72 / dpiX));
  const height = Math.min(14_400, Math.max(36, image.getHeight() * 72 / dpiY));
  return [width, height];
}

self.onmessage = (event: MessageEvent<{ images: ScanImageInput[] }>) => {
  const document = new mupdf.PDFDocument();
  try {
    event.data.images.forEach((input, index) => {
      if (!/^image\/(png|jpeg)$/i.test(input.mimeType) && !/\.(png|jpe?g)$/i.test(input.name)) {
        throw new Error(`${input.name} is not a supported PNG or JPEG image.`);
      }
      const image = new mupdf.Image(input.bytes);
      const [width, height] = pageSize(image);
      const imageReference = document.addImage(image);
      const resources = document.newDictionary();
      const xObjects = document.newDictionary();
      xObjects.put('ScanImage', imageReference);
      resources.put('XObject', xObjects);
      const page = document.addPage(
        [0, 0, width, height],
        0,
        resources,
        `q ${width} 0 0 ${height} 0 0 cm /ScanImage Do Q`,
      );
      document.insertPage(-1, page);
      image.destroy();
      self.postMessage({ type: 'progress', completed: index + 1, total: event.data.images.length, filename: input.name });
    });
    const buffer = document.saveToBuffer('garbage=compact,compress=yes');
    const bytes = Uint8Array.from(buffer.asUint8Array());
    buffer.destroy();
    self.postMessage({ type: 'complete', bytes }, [bytes.buffer]);
  } catch (error) {
    self.postMessage({ type: 'error', error: error instanceof Error ? error.message : String(error) });
  } finally {
    document.destroy();
  }
};

self.postMessage({ type: 'ready' });
