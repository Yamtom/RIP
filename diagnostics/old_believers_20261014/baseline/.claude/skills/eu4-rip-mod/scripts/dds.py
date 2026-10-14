import struct

HDR = 128

def read_dds(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'DDS ', path
    _flags, h, w, _pitch, _depth, _mips = struct.unpack('<6I', d[8:32])
    bits = struct.unpack('<I', d[88:92])[0]
    assert bits == 32, (path, bits)
    px = d[HDR:HDR + w * h * 4]
    assert len(px) == w * h * 4, (len(px), w, h)
    return w, h, bytearray(px), bytearray(d[:HDR])

def write_dds(path, w, h, px, header):
    hdr = bytearray(header)
    struct.pack_into('<I', hdr, 12, h)
    struct.pack_into('<I', hdr, 16, w)
    struct.pack_into('<I', hdr, 20, w * 4)      # pitch
    open(path, 'wb').write(bytes(hdr) + bytes(px))

def crop(w, h, px, x0, cw):
    out = bytearray()
    for y in range(h):
        s = (y * w + x0) * 4
        out += px[s:s + cw * 4]
    return out

def paste(w, h, px, x0, cw, src):
    for y in range(h):
        d = (y * w + x0) * 4
        s = y * cw * 4
        px[d:d + cw * 4] = src[s:s + cw * 4]

def to_png(path, w, h, px):
    from PIL import Image
    img = Image.frombytes('RGBA', (w, h), bytes(px))
    b, g, r, a = img.split()
    Image.merge('RGBA', (r, g, b, a)).save(path)
