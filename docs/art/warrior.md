# Guerrero — documento de arte

Referencias aprobadas: [`reference/warrior_reference.png`](reference/warrior_reference.png) (lámina inicial) y
[`reference/warrior_reference_2.png`](reference/warrior_reference_2.png) (tablero + diálogo + retratos). Son láminas
conceptuales: **no se importan en el juego** (`docs/` lleva `.gdignore` y se excluye del APK) ni se usan como
spritesheet. Todo el arte jugable se genera con código propio (`tools/make_warrior_art.py`), sin imágenes de terceros
y sin copiar píxeles de las referencias.

## Rasgos
Rol: tanque / daño físico. Pelo castaño desordenado con reflejos cobrizos, bufanda y capa azules, armadura oscura
con acero y cobre, emblema dorado (flor de lis) en la capa, botas de cuero.

## Paleta cerrada
Definida en `tools/warrior_art/palette.py` (piel, pelo, azules, aceros, cobre, dorado, cuero, contorno `#12141d`).
Todo el arte usa solo esos colores: sin degradados ni semitransparencias (el alfa es 0 o 255).

## Cómo se genera
Formas a 8x (sprites) o 4x (retratos) → reducción por moda de color a píxeles nítidos → contorno de 1 px.
Luz arriba-izquierda: borde claro arriba-izq., borde oscuro abajo-der. y sombras recortadas dentro de cada pieza.
La caminata sale de una pose parametrizada (balanceo de piernas y brazos, rebote del cuerpo, vaivén de capa y pelo).

```
tools/make_warrior_art.py        punto de entrada (sprites y retratos)
tools/warrior_art/raster.py      motor de dibujo y reducción a píxeles
tools/warrior_art/palette.py     paleta
tools/warrior_art/pose.py        poses de quieto y caminar (6 cuadros)
tools/warrior_art/sprite_*.py    vistas frontal, trasera y lateral
tools/warrior_art/sheet.py       ensambla la hoja
tools/warrior_art/portrait.py    retratos y expresiones
```

## Sprites jugables (separados de los retratos)
`assets/characters/warrior/sprites/warrior_sheet.png`: **352×176**, cuadros de **44×44** (40 px de dibujo + 2 px de
margen transparente por lado, así ningún contorno toca el borde), 8 columnas × 4 filas.
Columnas: 0-1 quieto (respiración), 2-7 caminar (6 cuadros). Filas: abajo, izquierda, derecha (espejo), arriba.
Se muestran a escala x2 (88 px de cuadro; el personaje mide ~80 px de alto, igual que la casilla), filtro *nearest*.
Animaciones en `resources/characters/warrior/warrior_frames.tres`: `idle_<dir>` (2 fps) y `walk_<dir>` (12 fps).

## Retratos (separados de los sprites)
`assets/characters/warrior/portraits/warrior_<expresión>.png`, **128×128**, fondo transparente, un archivo por
expresión: neutral, sonriente, determinado, enojado, triste, sorprendido, herido, agotado. Aún **no se usan en el
juego** (no hay sistema de diálogos); están listos para importarse como `Texture2D`.

## Estado por etapas
| Etapa | Contenido | Estado |
|---|---|---|
| 1 | Quieto y caminar en 4 direcciones (6 cuadros) | **Implementado** |
| 2 | Retratos con 8 expresiones | **Arte listo**, sin uso en el juego |
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
