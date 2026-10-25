#!/usr/bin/env python3
"""Prueba mínima: cuadro de 48x48 del Guerrero (vista frontal) a partir de la candidata docs/art/wip/sprite_ref4/candidate_down.png.

No redibuja: reduce la candidata con tres técnicas, mide cada una contra la referencia y guarda la mejor.
Salidas (solo en docs/art/wip/): warrior_<lado>_test.png, _guided.png, _compare.png y _variants.png.
Uso: python3 docs/art/wip/make_warrior_48_test.py [lado=48] [alto_figura=lado-4]   (requiere Pillow y numpy)
Ejemplo 64x64: python3 docs/art/wip/make_warrior_48_test.py 64 60
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

WIP = Path(__file__).resolve().parent
ROOT = WIP.parent.parent.parent
CAND = WIP / "sprite_ref4" / "candidate_down.png"
REF = ROOT / "docs" / "art" / "reference" / "warrior_reference_4views.jpg"
import sys
SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 48            # lado del lienzo
FIG_H = int(sys.argv[2]) if len(sys.argv) > 2 else SIZE - 4   # alto de la figura sin contorno (+1 px de contorno y 1 px de margen por lado)
TAG = f"warrior_{SIZE}_test"
OUTLINE = (18, 14, 29)


def load_candidate():
	im = Image.open(CAND).convert("RGBA")
	box = im.getchannel("A").getbbox()
	return im.crop(box)


def palette_of(img):
	a = np.asarray(img)
	return np.unique(a[a[:, :, 3] > 0][:, :3], axis=0).astype(np.float32)


def snap(rgb, pal):
	d = ((rgb[:, None, :] - pal[None]) ** 2).sum(2)
	return pal[d.argmin(1)]


def target_size(img):
	h = FIG_H
	return max(1, round(img.width * h / img.height)), h


def v_nearest(img):
	return img.resize(target_size(img), Image.NEAREST)


def v_lanczos(img, pal):
	w, h = target_size(img)
	a = np.asarray(img).astype(np.float32)
	pm = a.copy(); pm[:, :, :3] *= a[:, :, 3:4] / 255.0           # alfa premultiplicado para no ensuciar bordes
	r = np.asarray(Image.fromarray(pm.astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS)).astype(np.float32)
	alpha = r[:, :, 3]
	rgb = np.where(alpha[..., None] > 0, r[:, :, :3] * 255.0 / np.maximum(alpha[..., None], 1), 0)
	out = np.zeros((h, w, 4), np.uint8)
	m = alpha > 127
	out[m, :3] = snap(rgb[m], pal).astype(np.uint8); out[m, 3] = 255
	return Image.fromarray(out, "RGBA")


def v_detail(img, pal):
	"""Reducción que preserva detalle: por bloque usa el color medio, salvo que un rasgo muy oscuro (ojos, hebilla) o muy
	claro/dorado (brillos, ribetes) ocupe una parte apreciable del bloque; entonces gana ese rasgo."""
	w, h = target_size(img)
	a = np.asarray(img).astype(np.float32)
	sx, sy = a.shape[1] / w, a.shape[0] / h
	out = np.zeros((h, w, 4), np.uint8)
	lum = lambda c: 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]
	for y in range(h):
		for x in range(w):
			blk = a[int(y * sy):max(int(y * sy) + 1, int(np.ceil((y + 1) * sy))), int(x * sx):max(int(x * sx) + 1, int(np.ceil((x + 1) * sx)))]
			px = blk.reshape(-1, 4)
			op = px[px[:, 3] > 0]
			if len(op) * 2 <= len(px):
				continue
			mean = op[:, :3].mean(0)
			L = lum(op[:, :3]); lm = lum(mean)
			pick = mean
			dark = op[L < lm - 45]
			bright = op[L > lm + 45]
			if len(dark) >= 0.34 * len(op) and L.min() < 60:
				pick = dark[lum(dark[:, :3]).argmin(), :3]
			elif len(bright) >= 0.34 * len(op):
				pick = bright[lum(bright[:, :3]).argmax(), :3]
			out[y, x, :3] = snap(pick[None].astype(np.float32), pal)[0].astype(np.uint8); out[y, x, 3] = 255
	return Image.fromarray(out, "RGBA")


def v_phase(img, pal, ref):
	"""Vecino más cercano muestreando el centro de cada bloque con la fase (x, y) que mejor se parece a la referencia."""
	w, h = target_size(img)
	a = np.asarray(img)
	sx, sy = a.shape[1] / w, a.shape[0] / h
	best = None
	for fx in (0.25, 0.5, 0.75):
		for fy in (0.25, 0.5, 0.75):
			xs = np.minimum(((np.arange(w) + fx) * sx).astype(int), a.shape[1] - 1)
			ys = np.minimum(((np.arange(h) + fy) * sy).astype(int), a.shape[0] - 1)
			cand = Image.fromarray(a[np.ix_(ys, xs)], "RGBA")
			score = fidelity(cand, ref)[2]
			if best is None or score < best[0]:
				best = (score, cand, (fx, fy))
	print("  fase elegida", best[2])
	return best[1]


def v_guided(img, pal, ref):
	"""Silueta y paleta de la candidata; el color de cada píxel se toma de la referencia reducida a 44 px con nitidez."""
	from PIL import ImageFilter
	w, h = target_size(img)
	mask = v_lanczos(img, pal).getchannel("A")
	r = ref.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2.0, percent=90, threshold=2)).resize((w, h), Image.LANCZOS)
	r = r.filter(ImageFilter.UnsharpMask(radius=0.7, percent=70, threshold=1))
	rgb = np.asarray(r).astype(np.float32)
	m = np.asarray(mask) > 127
	out = np.zeros((h, w, 4), np.uint8)
	out[m, :3] = snap(rgb[m], pal).astype(np.uint8); out[m, 3] = 255
	return Image.fromarray(out, "RGBA")


def finish(fig):
	"""Añade el contorno de 1 px y centra en un lienzo de 48x48 apoyado abajo con 1 px de margen."""
	w, h = fig.size
	canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
	ox, oy = (SIZE - w) // 2, SIZE - h - 2
	canvas.alpha_composite(fig, (ox, oy))
	src = canvas.copy().load(); px = canvas.load()
	for y in range(SIZE):
		for x in range(SIZE):
			if src[x, y][3] == 0 and any(0 <= x + dx < SIZE and 0 <= y + dy < SIZE and src[x + dx, y + dy][3] > 0
			                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
				px[x, y] = OUTLINE + (255,)
	return canvas


def reference_figure():
	"""Figura de la vista frontal de la referencia, aislada del fondo (mismo método que tools/extract_warrior_sprites_ref.py)."""
	a = np.asarray(Image.open(REF).convert("RGB")).astype(int)[3:322]
	h, w, _ = a.shape
	bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
	bglike = np.abs(a - bg).sum(2) < 42
	seen = np.zeros((h, w), bool); dq = deque()
	for x in range(w):
		for y in (0, h - 1):
			if bglike[y, x] and not seen[y, x]: seen[y, x] = True; dq.append((y, x))
	for y in range(h):
		for x in (0, w - 1):
			if bglike[y, x] and not seen[y, x]: seen[y, x] = True; dq.append((y, x))
	while dq:
		y, x = dq.popleft()
		for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			ny, nx = y + dy, x + dx
			if 0 <= ny < h and 0 <= nx < w and bglike[ny, nx] and not seen[ny, nx]:
				seen[ny, nx] = True; dq.append((ny, nx))
	fg = ~seen
	ys, xs = np.where(fg)
	box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
	rgb = Image.fromarray(a.astype(np.uint8)).crop(box)
	m = Image.fromarray((fg * 255).astype(np.uint8)).crop(box)
	rgba = rgb.convert("RGBA"); rgba.putalpha(m)
	return rgba


def fidelity(img, ref):
	"""Compara `img` (sin contorno añadido) con la referencia en el espacio de la referencia (ampliación nearest)."""
	box = img.getchannel("A").getbbox()
	im = img.crop(box).resize(ref.size, Image.NEAREST)
	a, r = np.asarray(im).astype(np.float32), np.asarray(ref).astype(np.float32)
	ia, ra = a[:, :, 3] > 127, r[:, :, 3] > 127
	iou = (ia & ra).sum() / max(1, (ia | ra).sum())
	both = ia & ra
	mae = np.abs(a[both][:, :3] - r[both][:, :3]).mean()
	# error tras suavizar ambos (ignora la rejilla de píxeles, mide color y masa de cada zona)
	from PIL import ImageFilter
	sa = np.asarray(im.convert("RGB").filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
	sr = np.asarray(ref.convert("RGB").filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
	mae_s = np.abs(sa[both] - sr[both]).mean()
	return iou, mae, mae_s


def main():
	cand = load_candidate()
	pal = palette_of(cand)
	ref = reference_figure()
	variants = {"nearest": v_nearest(cand), "lanczos": v_lanczos(cand, pal), "detalle": v_detail(cand, pal), "fase": v_phase(cand, pal, ref)}
	guided = v_guided(cand, pal, ref)
	cand_full = Image.open(CAND).convert("RGBA")
	print(f"candidata original {cand_full.size}: figura {cand.size}, {len(pal)} colores | referencia (figura) {ref.size}")
	print(f"{'técnica':10s} {'IoU silueta':>12s} {'error color':>12s} {'error suav.':>12s} {'colores':>8s}")
	base = fidelity(cand, ref)
	print(f"{'candidata':10s} {base[0]:12.3f} {base[1]:12.1f} {base[2]:12.1f} {len(pal):8d}   (55x76, sin reducir)")
	scores = {}
	for k, v in variants.items():
		s = fidelity(v, ref)
		scores[k] = s
		n = len({tuple(p) for p in np.asarray(v).reshape(-1, 4)[np.asarray(v).reshape(-1, 4)[:, 3] > 0][:, :3]})
		print(f"{k:10s} {s[0]:12.3f} {s[1]:12.1f} {s[2]:12.1f} {n:8d}")
	g = fidelity(guided, ref)
	print(f"{'guiada':10s} {g[0]:12.3f} {g[1]:12.1f} {g[2]:12.1f} {'(color tomado de la referencia, paleta y silueta de la candidata)'}")
	best = min(scores, key=lambda k: scores[k][2] - 30 * scores[k][0])
	print("mejor técnica derivada SOLO de la candidata (error suavizado y silueta):", best)
	finish(guided).save(WIP / f"{TAG}_guided.png")
	final = finish(variants[best])
	final.save(WIP / f"{TAG}.png")
	# tableros
	Z = 8
	fin = {k: finish(v) for k, v in variants.items()}
	fin["guiada"] = finish(guided)
	vb = Image.new("RGB", (len(fin) * (SIZE * Z + 10) + 10, SIZE * Z + 20), (15, 24, 32))
	for i, (k, v) in enumerate(fin.items()):
		bg = Image.new("RGBA", v.size, (15, 24, 32, 255)); bg.alpha_composite(v)
		vb.paste(bg.convert("RGB").resize((SIZE * Z, SIZE * Z), Image.NEAREST), (10 + i * (SIZE * Z + 10), 10))
	vb.save(WIP / f"{TAG}_variants.png")
	H = SIZE * Z
	refv = Image.open(REF).convert("RGB").crop((0, 3, 247, 322))
	rf = ref.resize((round(ref.width * H / ref.height), H), Image.LANCZOS)
	rbg = Image.new("RGB", (SIZE * Z, H), (15, 24, 32)); rbg.paste(rf.convert("RGB"), ((SIZE * Z - rf.width) // 2, 0), rf.getchannel("A").resize(rf.size))
	cbg = Image.new("RGBA", cand_full.size, (15, 24, 32, 255)); cbg.alpha_composite(cand_full)
	cz = cbg.convert("RGB").resize((round(cand_full.width * H / cand_full.height), H), Image.NEAREST)
	nbg = Image.new("RGBA", final.size, (15, 24, 32, 255)); nbg.alpha_composite(final)
	nz = nbg.convert("RGB").resize((SIZE * Z, SIZE * Z), Image.NEAREST)
	gbg = Image.new("RGBA", (SIZE, SIZE), (15, 24, 32, 255)); gbg.alpha_composite(finish(guided))
	gz = gbg.convert("RGB").resize((SIZE * Z, SIZE * Z), Image.NEAREST)
	tiles = [rbg, cz, nz, gz]
	board = Image.new("RGB", (sum(t.width for t in tiles) + 40, H + 20), (15, 24, 32))
	x = 10
	for t in tiles:
		board.paste(t, (x, 10)); x += t.width + 10
	board.save(WIP / f"{TAG}_compare.png")
	print("Guardado en", WIP)


if __name__ == "__main__":
	main()
