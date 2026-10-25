#!/usr/bin/env python3
"""PRUEBA DE VIABILIDAD (no integrada en el juego): sprites candidatos desde la referencia de cuatro vistas.

Fuente: docs/art/reference/warrior_reference_4views.jpg (una pose por dirección: abajo, izquierda, derecha, arriba).
Pasos: aislar cada figura del fondo oscuro (relleno desde los bordes + componente mayor) -> reducir todas las vistas a la misma
escala (70 px de alto) con realce de nitidez -> paleta COMPARTIDA de 48 colores (k-means++ conserva brillos raros) -> alfa duro,
sin tramado -> contorno oscuro de 1 px. Salida: docs/art/wip/sprite_ref4/candidate_<dirección>.png (55x76).

Limitación clave: la referencia trae SOLO UNA pose por dirección; de aquí no salen cuadros de caminata.
Uso: python3 tools/extract_warrior_sprites_ref.py   (requiere Pillow y numpy)
"""
import sys
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs' / 'art' / 'reference' / 'warrior_reference_4views.jpg'
OUT = ROOT / 'docs' / 'art' / 'wip' / 'sprite_ref4'
PANELS={'down':(3,322),'left':(328,661),'right':(667,1000),'up':(1006,1340)}
TARGET_H = 70
COLORS = 48
im=Image.open(SRC).convert('RGB'); a=np.asarray(im).astype(int)
def isolate(y0,y1):
    sub=a[y0:y1]; h,w,_=sub.shape
    border=np.concatenate([sub[0],sub[-1],sub[:,0],sub[:,-1]]); bg=np.median(border,axis=0)
    dist=np.abs(sub-bg).sum(axis=2)
    bglike=dist<42
    seen=np.zeros((h,w),bool); dq=deque()
    for x in range(w):
        for y in (0,h-1):
            if bglike[y,x] and not seen[y,x]: seen[y,x]=True; dq.append((y,x))
    for y in range(h):
        for x in (0,w-1):
            if bglike[y,x] and not seen[y,x]: seen[y,x]=True; dq.append((y,x))
    while dq:
        y,x=dq.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<h and 0<=nx<w and bglike[ny,nx] and not seen[ny,nx]:
                seen[ny,nx]=True; dq.append((ny,nx))
    fg=~seen
    # quitar motas pequeñas: conservar la componente mayor
    lab=-np.ones((h,w),int); best=(0,-1); n=0
    for y in range(h):
        for x in range(w):
            if fg[y,x] and lab[y,x]<0:
                q=[(y,x)]; lab[y,x]=n; cnt=0
                while q:
                    cy,cx=q.pop(); cnt+=1
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<h and 0<=nx<w and fg[ny,nx] and lab[ny,nx]<0: lab[ny,nx]=n; q.append((ny,nx))
                if cnt>best[0]: best=(cnt,n)
                n+=1
    fg=lab==best[1]
    return sub,fg
out={}
for name,(y0,y1) in PANELS.items():
    sub,fg=isolate(y0,y1)
    ys,xs=np.where(fg); box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    rgb=Image.fromarray(sub.astype(np.uint8)).crop(box)
    mask=Image.fromarray((fg*255).astype(np.uint8)).crop(box)
    out[name]=(rgb,mask)
    print(name,'figura',rgb.size)

OUT.mkdir(parents=True, exist_ok=True)
H = max(r.size[1] for r, _ in out.values()); sc = TARGET_H / H
small={}
for name,(rgb,mask) in out.items():
    w=max(1,round(rgb.size[0]*sc)); h=max(1,round(rgb.size[1]*sc))
    # pre-realce de contraste local antes de reducir
    r=rgb.filter(ImageFilter.UnsharpMask(radius=2.0,percent=90,threshold=2))
    r=r.resize((w,h),Image.LANCZOS)
    r=r.filter(ImageFilter.UnsharpMask(radius=0.7,percent=70,threshold=1))
    m=mask.resize((w,h),Image.LANCZOS).point(lambda v:255 if v>140 else 0)
    small[name]=(np.asarray(r).astype(float),np.asarray(m)>0)
# paleta compartida (k-means++ con muestreo D^2 -> conserva colores raros como los brillos)
pix=np.concatenate([s[m] for s,m in small.values()]); rng=np.random.default_rng(7)
K=48
cent=[pix[rng.integers(len(pix))]]
d2=((pix-cent[0])**2).sum(1)
for _ in range(K-1):
    p=d2/d2.sum(); cent.append(pix[rng.choice(len(pix),p=p)]); d2=np.minimum(d2,((pix-cent[-1])**2).sum(1))
cent=np.array(cent)
for _ in range(12):
    lab=((pix[:,None,:]-cent[None])**2).sum(2).argmin(1)
    for k in range(K):
        sel=pix[lab==k]
        if len(sel): cent[k]=sel.mean(0)
pal=np.clip(cent,0,255).astype(np.uint8)
W=max(s.shape[1] for s,_ in small.values())+6; Hh=max(s.shape[0] for s,_ in small.values())+6
for name,(s,m) in small.items():
    lab=((s[:,:,None,:]-pal[None,None].astype(float))**2).sum(3).argmin(2)
    rgba=np.zeros((s.shape[0],s.shape[1],4),np.uint8); rgba[...,:3]=pal[lab]; rgba[...,3]=np.where(m,255,0)
    img=Image.fromarray(rgba,'RGBA')
    canvas=Image.new('RGBA',(W,Hh),(0,0,0,0)); canvas.alpha_composite(img,((W-img.size[0])//2,Hh-img.size[1]-3))
    # limpiar píxeles huérfanos de alfa
    a=np.asarray(canvas)[:,:,3]>0
    px=canvas.load()
    for y in range(1,Hh-1):
        for x in range(1,W-1):
            n=a[y-1,x]+a[y+1,x]+a[y,x-1]+a[y,x+1]
            if a[y,x] and n==0: px[x,y]=(0,0,0,0)
    src=canvas.copy().load()
    for y in range(Hh):
        for x in range(W):
            if src[x,y][3]==0 and any(0<=x+dx<W and 0<=y+dy<Hh and src[x+dx,y+dy][3]>0 for dx,dy in((1,0),(-1,0),(0,1),(0,-1))): px[x,y]=(18,14,29,255)
    canvas.save(OUT / f'candidate_{name}.png')
    print(name,canvas.size,'colores',len({tuple(p) for p in np.asarray(canvas).reshape(-1,4)[:,:3][np.asarray(canvas).reshape(-1,4)[:,3]>0]}))
