import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as mupdf from 'mupdf';

const output = resolve(dirname(fileURLToPath(import.meta.url)), 'generated');
await mkdir(output, { recursive: true });

function scanImage(width, height, format) {
  const pixmap = new mupdf.Pixmap(mupdf.ColorSpace.DeviceRGB, [0, 0, width, height], false);
  pixmap.setResolution(96, 96);
  const pixels = pixmap.getPixels();
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 3;
      const border = x < 12 || y < 12 || x >= width - 12 || y >= height - 12;
      pixels[offset] = border ? 12 : Math.round(220 - 80 * x / width);
      pixels[offset + 1] = border ? 101 : Math.round(245 - 70 * y / height);
      pixels[offset + 2] = border ? 143 : 250;
    }
  }
  const bytes = format === 'png' ? pixmap.asPNG() : pixmap.asJPEG(88);
  pixmap.destroy();
  return bytes;
}

await writeFile(resolve(output, 'scan-landscape.png'), scanImage(640, 360, 'png'));
await writeFile(resolve(output, 'scan-portrait.jpg'), scanImage(360, 640, 'jpeg'));
await writeFile(resolve(output, 'scan-invalid.png'), 'not an image');
console.log(`Phase 4 scan fixtures generated in ${output}`);
