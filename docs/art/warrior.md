# Guerrero — documento de arte

Referencia aprobada: [`reference/warrior_reference.png`](reference/warrior_reference.png).
Es una lámina conceptual: **no se usa como spritesheet** ni se importa en el juego (`docs/` lleva `.gdignore` y
se excluye del APK). Los sprites jugables se redibujan píxel a píxel con `tools/make_warrior_sheet.py`
(arte original del proyecto, sin imágenes de terceros).

## Rasgos del personaje
Rol: tanque / daño físico. Espada y armadura pesada. Cabeza grande (estilo chibi), pelo castaño desordenado,
bufanda y capa azules con emblema dorado en la espalda, armadura de acero oscuro con hombreras y bordes dorados,
pantalón pizarra y botas marrones.

## Paleta (tomada de la lámina)
| Uso | Color |
|---|---|
| Piel / sombra | `#fdc9a1` / `#efac7f` |
| Rojo (gema) | `#ae252a` |
| Azul capa / sombras | `#4b86cb` / `#2f5ca0` / `#1f3e75` |
| Acero | `#4d5667` (base), `#8a96ab`, `#cfd6e2` |
| Pizarra (pantalón) | `#494764`, `#2e2d42` |
| Dorado | `#e3ad5e` |
| Contorno | `#14161f` |

## Contrato de la hoja jugable
`assets/characters/warrior/sprites/warrior_sheet.png`: cuadros de **32×32**, fondo transparente, contorno de 1 px,
ocupa ~28 px de alto centrado en el cuadro (se escala x2 = 64 px en casillas de 80 px, filtro *nearest*).

| | Col 0 | Col 1 | Col 2 | Col 3 |
|---|---|---|---|---|
| Uso | quieto A | quieto B (respiración) | paso A | paso B |

Filas (orden RPG Maker): 0 abajo, 1 izquierda, 2 derecha (espejo de izquierda), 3 arriba.
Animaciones en `resources/characters/warrior/warrior_frames.tres` (generado por `tools/build_warrior_frames.gd`):
`idle_<dir>` (2 cuadros, 2 fps) y `walk_<dir>` (paso A, quieto, paso B, quieto; 8 fps).

## Estado por etapas
| Etapa | Contenido | Estado |
|---|---|---|
| 1 | Quieto y caminar en 4 direcciones | **Implementado** (v0.3) |
| 2 | Correr, quieto/espera extendido | Previsto |
| 3 | Ataque 1 (espada horizontal), Ataque 2 (golpe ascendente) | Previsto |
| 4 | Defensa (guardia), recibir daño, derrotado | Previsto |
| 5 | Habilidad especial (aura de fuerza), celebrar, señalar, hablar | Previsto |
| 6 | Retratos de diálogo | Previsto |

Cada etapa nueva = filas/hojas nuevas en `assets/characters/warrior/sprites/` + una entrada en la tabla `ANIMATIONS`
de `tools/build_warrior_frames.gd`. El código de `Unit` reproduce `<estado>_<dirección>` sin cambios.

## Retratos (separados del sprite jugable)
Viven en `assets/characters/warrior/portraits/`, un PNG por expresión, fuera de la hoja del sprite.
Previstos: neutral, sonriente, decidido, enojado, triste, sorprendido, dolorido, concentrado, hablando.
**Todavía no existen**: no se generaron para no entregar un arte que no se pueda verificar a este nivel.
