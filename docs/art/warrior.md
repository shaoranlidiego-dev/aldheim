# Guerrero — documento de arte

Referencias aprobadas: [`reference/warrior_reference.png`](reference/warrior_reference.png) (lámina inicial) y
[`reference/warrior_reference_2.png`](reference/warrior_reference_2.png) (tablero + diálogo + retratos). Son láminas
conceptuales: **no se importan en el juego** (`docs/` lleva `.gdignore` y se excluye del APK) ni se usan como
spritesheet. Todo el arte jugable se genera con código propio (`tools/make_warrior_art.py`) para los **sprites**, sin copiar píxeles de las referencias. Los **retratos** sí se derivan de la
referencia (ver más abajo).

## Rasgos
Rol: tanque / daño físico. Pelo castaño desordenado con reflejos cobrizos, bufanda y capa azules, armadura oscura
con acero y cobre, emblema dorado (flor de lis) en la capa, botas de cuero.

## Paleta cerrada
Definida en `tools/warrior_art/palette.py` (piel, pelo, azules, aceros, cobre, dorado, cuero, contorno `#12141d`).
Todo el arte usa solo esos colores: sin degradados ni semitransparencias (el alfa es 0 o 255).

## Cómo se genera
Sprites: formas a 8x → reducción por moda de color a píxeles nítidos → contorno de 1 px.
Luz arriba-izquierda: borde claro arriba-izq., borde oscuro abajo-der. y sombras recortadas dentro de cada pieza.
La caminata sale de una pose parametrizada (balanceo de piernas y brazos, rebote del cuerpo, vaivén de capa y pelo).

```
tools/make_warrior_art.py        punto de entrada de los sprites (y de los retratos procedurales antiguos)
tools/warrior_art/raster.py      motor de dibujo y reducción a píxeles
tools/warrior_art/palette.py     paleta
tools/warrior_art/pose.py        poses de quieto y caminar (6 cuadros)
tools/warrior_art/sprite_*.py    vistas frontal, trasera y lateral
tools/warrior_art/sheet.py       ensambla la hoja
tools/warrior_art/portrait.py    retratos procedurales ANTIGUOS (archivados; ya no se usan en el juego)
tools/extract_warrior_portraits.py  retratos actuales, extraídos de la referencia
```

## Sprites jugables (separados de los retratos)
`assets/characters/warrior/sprites/warrior_sheet.png`: **352×176**, cuadros de **44×44** (40 px de dibujo + 2 px de
margen transparente por lado, así ningún contorno toca el borde), 8 columnas × 4 filas.
Columnas: 0-1 quieto (respiración), 2-7 caminar (6 cuadros). Filas: abajo, izquierda, derecha (espejo), arriba.
Se muestran a escala x2 (88 px de cuadro; el personaje mide ~80 px de alto, igual que la casilla), filtro *nearest*.
Animaciones en `resources/characters/warrior/warrior_frames.tres`: `idle_<dir>` (2 fps) y `walk_<dir>` (12 fps).

## Retratos (separados de los sprites)
`assets/characters/warrior/portraits/warrior_<expresión>.png`: **128×128**, RGB opaco (fondo azul de la referencia),
**64 colores** por imagen, sin tramado. Expresiones: neutral, sonriente, determinado, enojado, triste, sorprendido,
herido y agotado. Aún **no se muestran en el juego** (no hay sistema de diálogos); están importados como `Texture2D`.

**Procedencia:** se extraen de los ocho recuadros de la lámina aprobada `reference/warrior_reference_2.png` con
`python3 tools/extract_warrior_portraits.py` (recorte de 146×146 px dentro del marco dorado, sin marco, sombra del marco ni
etiqueta → reducción Lanczos a 128×128 → cuantización a 64 colores sin tramado). El script valida cada recorte (sin línea
dorada de marco, sin fila oscura inferior, exactamente 64 colores) y `--install` copia el resultado a `assets/` archivando
antes los anteriores en `archive/portraits_procedural_v1/`. La carpeta de trabajo es `wip/portraits_ref/`.

**Qué se pierde:** reducción 146→128 px (error medio ≈2,4/255) y cuantización a 64 colores (error medio ≈3,9/255, ≈3 % de
píxeles con diferencia visible): los degradados de piel y fondo pasan a escalones de tono y los brillos finos del pelo y el
medallón se simplifican. La fuente no es una grilla de píxeles real: el resultado es una *ilustración pixelada*, no pixel art
de píxeles contados a mano.

**Derechos:** la lámina de referencia parece generada por IA y la titularidad de ese tipo de imágenes es incierta. Los retratos
son una derivación directa de ella; conviene revisar su origen y licencia antes de publicar el juego.

**Retratos procedurales anteriores:** archivados en `archive/portraits_procedural_v1/` (se pueden regenerar con
`python3 tools/make_warrior_art.py portraits`, que ya no escribe en `assets/`). El retrato piloto de tres cuartos pintado
con código (`wip/warrior_portrait_pilot*.png`) queda como estudio y no se usa.

## Estado por etapas
| Etapa | Contenido | Estado |
|---|---|---|
| 1 | Quieto y caminar en 4 direcciones (6 cuadros) | **Implementado** |
| 2 | Retratos con 8 expresiones (extraídos de la referencia) | **Implementado en assets**, sin uso en el juego |
| 3 | Correr, ataques (espada horizontal y ascendente) | Previsto |
| 4 | Defensa, recibir daño, derrotado | Previsto |
| 5 | Habilidad especial, celebrar, señalar, hablar | Previsto |

Cada etapa nueva = más filas/hojas en `assets/characters/warrior/sprites/` y una entrada en la tabla `ANIMATIONS`
de `tools/build_warrior_frames.gd`. `Unit` reproduce `<estado>_<dirección>` sin cambios.

## Limitaciones conocidas
- Es arte procedural: reproduce el diseño, la paleta y el espíritu de la referencia, pero **no iguala su nivel de
  detalle** (texturas, brillos de armadura, expresividad del rostro). Un artista de pixel art podría reemplazar la
  hoja y los retratos respetando las dimensiones y nombres de este documento.
- Las espadas, escudos y efectos de las referencias no están dibujados todavía.

## Retrato piloto v2 (trabajo en curso, no integrado)
`docs/art/wip/warrior_portrait_pilot.png` (128×128, tres cuartos, 49 colores, alfa 0/255) se genera con
`python3 tools/make_warrior_pilot.py`. Usa el motor de pintura `tools/warrior_art/painter.py` (relieve + luz cálida
arriba-izquierda + rampas por material + hebras de pelo + rasgos del rostro dibujados a mano en plantillas).
Los sprites y retratos del juego (`assets/`) **no** se reemplazaron: siguen siendo la versión anterior hasta que el
piloto sea aprobado.

## Prueba de sprites desde la referencia de cuatro vistas (no integrada)
Referencia obligatoria del personaje jugable: `reference/warrior_reference_4views.jpg` (una pose por dirección). Prueba de
viabilidad en `wip/sprite_ref4/` (script `tools/extract_warrior_sprites_ref.py`): `candidate_<dirección>.png`, 55×76 px,
paleta compartida de 48 colores, alfa duro. Evidencia: `candidates_vs_reference.png` y `board_test_candidates_vs_current.png`
(las candidatas sobre el tablero real a 720×1280, junto al sprite actual).

**Resultado:** silueta, volumen del pelo con reflejos cobrizos, bufanda, capa con flor de lis, hombreras de acero, ribetes y botas
doradas se reconocen claramente y se acercan mucho más a la referencia que el sprite chibi actual. Son una reducción automática
del render, no pixel art dibujado: tienen algo de ruido (brillos sueltos), los ojos son pequeños y los matices de acero se
simplifican.

**Por qué no se integró:** la referencia contiene una sola pose por dirección. Integrarla en `idle_*`/`walk_*` sería reemplazar
las animaciones por imágenes estáticas o inventar cuadros de caminata. Hacen falta cuadros reales de caminata (6 por dirección
y 2 de reposo) en el mismo estilo para sustituir la hoja actual.
