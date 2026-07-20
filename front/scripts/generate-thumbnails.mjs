import { deflateSync } from 'node:zlib'
import { writeFileSync } from 'node:fs'
import { join } from 'node:path'

const width = 720
const height = 480
const outDir = join(process.cwd(), 'src/static/images')

function rgba(hex) {
  const clean = hex.replace('#', '')
  return [
    parseInt(clean.slice(0, 2), 16),
    parseInt(clean.slice(2, 4), 16),
    parseInt(clean.slice(4, 6), 16),
    255
  ]
}

function makeCanvas(bg) {
  const data = new Uint8Array(width * height * 4)
  const color = rgba(bg)
  for (let index = 0; index < data.length; index += 4) {
    data[index] = color[0]
    data[index + 1] = color[1]
    data[index + 2] = color[2]
    data[index + 3] = color[3]
  }
  return data
}

function setPixel(data, x, y, color) {
  if (x < 0 || y < 0 || x >= width || y >= height) return
  const index = (Math.round(y) * width + Math.round(x)) * 4
  data[index] = color[0]
  data[index + 1] = color[1]
  data[index + 2] = color[2]
  data[index + 3] = color[3]
}

function rect(data, x, y, w, h, colorHex) {
  const color = rgba(colorHex)
  for (let yy = y; yy < y + h; yy += 1) {
    for (let xx = x; xx < x + w; xx += 1) setPixel(data, xx, yy, color)
  }
}

function ellipse(data, cx, cy, rx, ry, colorHex) {
  const color = rgba(colorHex)
  for (let y = Math.floor(cy - ry); y <= Math.ceil(cy + ry); y += 1) {
    for (let x = Math.floor(cx - rx); x <= Math.ceil(cx + rx); x += 1) {
      const dx = (x - cx) / rx
      const dy = (y - cy) / ry
      if (dx * dx + dy * dy <= 1) setPixel(data, x, y, color)
    }
  }
}

function line(data, x1, y1, x2, y2, size, colorHex) {
  const color = rgba(colorHex)
  const steps = Math.max(Math.abs(x2 - x1), Math.abs(y2 - y1))
  for (let i = 0; i <= steps; i += 1) {
    const x = x1 + ((x2 - x1) * i) / steps
    const y = y1 + ((y2 - y1) * i) / steps
    for (let yy = -size; yy <= size; yy += 1) {
      for (let xx = -size; xx <= size; xx += 1) {
        if (xx * xx + yy * yy <= size * size) setPixel(data, x + xx, y + yy, color)
      }
    }
  }
}

function chunk(type, data) {
  const typeBuffer = Buffer.from(type)
  const length = Buffer.alloc(4)
  length.writeUInt32BE(data.length)
  const crc = crc32(Buffer.concat([typeBuffer, data]))
  const crcBuffer = Buffer.alloc(4)
  crcBuffer.writeUInt32BE(crc)
  return Buffer.concat([length, typeBuffer, data, crcBuffer])
}

function crc32(buffer) {
  let crc = 0xffffffff
  for (const byte of buffer) {
    crc ^= byte
    for (let i = 0; i < 8; i += 1) {
      crc = crc & 1 ? 0xedb88320 ^ (crc >>> 1) : crc >>> 1
    }
  }
  return (crc ^ 0xffffffff) >>> 0
}

function savePng(name, pixels) {
  const raw = Buffer.alloc((width * 4 + 1) * height)
  for (let y = 0; y < height; y += 1) {
    const rawRow = y * (width * 4 + 1)
    raw[rawRow] = 0
    Buffer.from(pixels.buffer, y * width * 4, width * 4).copy(raw, rawRow + 1)
  }

  const header = Buffer.alloc(13)
  header.writeUInt32BE(width, 0)
  header.writeUInt32BE(height, 4)
  header[8] = 8
  header[9] = 6
  header[10] = 0
  header[11] = 0
  header[12] = 0

  writeFileSync(
    join(outDir, `${name}.png`),
    Buffer.concat([
      Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
      chunk('IHDR', header),
      chunk('IDAT', deflateSync(raw, { level: 9 })),
      chunk('IEND', Buffer.alloc(0))
    ])
  )
}

const thumbnails = {
  'tomato-egg': (data) => {
    ellipse(data, 220, 240, 120, 92, '#d9412e')
    ellipse(data, 302, 190, 84, 76, '#ec5c3b')
    ellipse(data, 430, 245, 106, 86, '#ffd15a')
    ellipse(data, 515, 205, 66, 58, '#ffe08a')
    line(data, 118, 338, 605, 338, 18, '#59452f')
    line(data, 188, 130, 268, 108, 11, '#4b8a42')
    line(data, 500, 312, 598, 312, 10, '#4b8a42')
  },
  'mapo-tofu': (data) => {
    ellipse(data, 360, 265, 250, 132, '#b73428')
    rect(data, 196, 176, 96, 72, '#f6dfb4')
    rect(data, 332, 152, 92, 74, '#f8e7c3')
    rect(data, 438, 246, 104, 76, '#f1d9a8')
    rect(data, 266, 272, 98, 72, '#fae9c8')
    ellipse(data, 500, 178, 15, 15, '#5c2c24')
    ellipse(data, 226, 310, 13, 13, '#5c2c24')
    line(data, 132, 360, 588, 360, 20, '#5b3328')
  },
  'steamed-egg': (data) => {
    ellipse(data, 360, 276, 220, 128, '#f3bf54')
    ellipse(data, 360, 256, 184, 95, '#ffe097')
    line(data, 172, 324, 548, 324, 20, '#7a9fba')
    line(data, 278, 178, 294, 98, 8, '#d4d4d4')
    line(data, 360, 168, 382, 84, 8, '#d4d4d4')
    line(data, 438, 181, 456, 104, 8, '#d4d4d4')
  },
  'chicken-pot': (data) => {
    rect(data, 218, 176, 284, 214, '#6b5142')
    ellipse(data, 360, 176, 196, 58, '#8a6a55')
    ellipse(data, 360, 169, 158, 36, '#f0c86f')
    ellipse(data, 282, 166, 30, 30, '#f8e7bd')
    ellipse(data, 376, 176, 24, 24, '#f8e7bd')
    line(data, 435, 148, 536, 166, 12, '#5e9d63')
    line(data, 222, 238, 498, 238, 12, '#533f35')
  },
  cucumber: (data) => {
    ellipse(data, 292, 248, 92, 128, '#559a5a')
    ellipse(data, 424, 238, 84, 124, '#6fb66a')
    ellipse(data, 286, 230, 34, 34, '#d9f1a7')
    ellipse(data, 438, 264, 32, 32, '#d9f1a7')
    line(data, 152, 342, 584, 342, 17, '#48643c')
    ellipse(data, 520, 172, 12, 12, '#d8422c')
    ellipse(data, 552, 204, 10, 10, '#d8422c')
  },
  'fried-rice': (data) => {
    ellipse(data, 360, 270, 225, 118, '#f1c45b')
    ellipse(data, 265, 238, 24, 24, '#f6e7b6')
    ellipse(data, 332, 300, 20, 20, '#f6e7b6')
    ellipse(data, 468, 247, 22, 22, '#f6e7b6')
    rect(data, 420, 292, 44, 28, '#db5a49')
    rect(data, 250, 292, 42, 28, '#df6b4e')
    ellipse(data, 394, 218, 13, 13, '#579f5b')
    ellipse(data, 505, 285, 12, 12, '#579f5b')
    line(data, 136, 342, 584, 342, 20, '#5c7f97')
  }
}

const backgrounds = {
  'tomato-egg': '#fff0dc',
  'mapo-tofu': '#f4eadc',
  'steamed-egg': '#edf3ed',
  'chicken-pot': '#eef0e8',
  cucumber: '#eaf2e3',
  'fried-rice': '#f7eee2'
}

for (const [name, draw] of Object.entries(thumbnails)) {
  const canvas = makeCanvas(backgrounds[name])
  draw(canvas)
  savePng(name, canvas)
}
