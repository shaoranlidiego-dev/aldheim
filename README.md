# El Reino Olvidado: Aldheim

RPG táctico 2D por turnos, vista cenital y tablero cuadriculado. Pensado primero para Android.
Hecho con **Godot 4** y **GDScript**, sin complementos ni dependencias externas.

> Estado: base técnica (v0.1). Hay tablero, una ficha y movimiento por casillas.
> Todavía no hay combate, enemigos, personajes ni multijugador.

## Requisitos

- [Godot 4.3 o superior](https://godotengine.org/download) (versión estándar, no hace falta .NET).

## Abrir y ejecutar

1. Abrí Godot y en el Gestor de proyectos elegí **Importar**.
2. Seleccioná el archivo `project.godot` de esta carpeta y confirmá.
3. Abrí el proyecto y presioná **F5** (o el botón ▶). La escena principal es `scenes/main.tscn`.

## Cómo se juega

1. Tocá (o hacé clic en) la ficha amarilla: se marcan en azul las casillas alcanzables (4 pasos, sin atravesar obstáculos).
2. Tocá una casilla azul: la ficha camina hasta ahí.
3. Tocá cualquier otro lugar para cancelar la selección.

Los toques se tratan como clic izquierdo (`emulate_mouse_from_touch`), así el mismo código sirve en PC y en pantallas táctiles.

## Estructura

```
project.godot            Configuración (pantalla vertical 720x1280, escena principal)
scenes/main.tscn         Escena inicial: tablero, ficha e interfaz
scripts/board/board.gd        Tablero: dibujo de la grilla, terreno y conversión píxel <-> casilla
scripts/board/pathfinding.gd  Búsqueda de casillas alcanzables y caminos (BFS)
scripts/units/unit.gd         Ficha: casilla actual y movimiento animado
scripts/game/game.gd          Controlador: entrada táctil y flujo de selección/movimiento
```

Cada pieza tiene una sola responsabilidad: el tablero no conoce unidades y la unidad no lee la entrada,
para poder sumar luego turnos, combate, enemigos y red sin reescribir lo existente.

## Android (pendiente de verificar)

El proyecto está configurado para pantalla vertical y renderizador *Mobile*, pero **no se probó en un dispositivo**. Para exportar:

1. En Godot: *Editor > Administrar plantillas de exportación* e instalá las de tu versión.
2. Instalá el JDK 17 y el Android SDK, y configurá sus rutas en *Editor > Configuración del editor > Export > Android*.
3. *Proyecto > Exportar > Añadir… > Android*, con un keystore de depuración propio (no lo subas al repositorio).
4. Conectá el dispositivo con depuración USB y usá *Despliegue con un clic*.

Guía oficial: <https://docs.godotengine.org/es/stable/tutorials/export/exporting_for_android.html>

## Lista de verificación

Marcá cada punto al probar en el editor (F5) y luego en un dispositivo Android.

**Primer arranque**
- [ ] Al importar el proyecto por primera vez no aparecen errores en el panel *Salida* ni en *Depurador*.
- [ ] La ventana es vertical (720x1280) y se ve todo el tablero y el texto superior.

**Tablero**
- [ ] Se ve una grilla de 8 columnas x 12 filas con casillas alternadas en dos tonos.
- [ ] Hay 6 casillas oscuras (obstáculos) en (3,4), (4,4), (3,5), (1,7), (6,7) y (5,8).
- [ ] La grilla no se corta ni se superpone con el texto en la parte superior.

**Movimiento**
- [ ] La ficha amarilla empieza en la casilla (1, 1).
- [ ] Tocar la ficha marca en azul las casillas alcanzables (máximo 4 pasos, 23 desde el inicio).
- [ ] Tocar la ficha otra vez, o tocar fuera de lo azul, quita la selección.
- [ ] Tocar una casilla azul mueve la ficha paso a paso, rodeando los obstáculos.
- [ ] Durante la animación los toques se ignoran y al terminar el texto muestra la nueva casilla.
- [ ] Tocar un obstáculo o una casilla lejana no mueve la ficha.

**Controles táctiles (Android)**
- [ ] Un toque con el dedo equivale a un clic: selecciona y mueve igual que en el editor.
- [ ] Las casillas son lo bastante grandes para tocarlas con precisión.
- [ ] Los toques funcionan en todo el tablero, incluidas las esquinas.
- [ ] Al rotar o en pantallas de otra proporción, el juego se escala con bandas y no se deforma.
- [ ] Al volver a la app desde segundo plano, el estado sigue correcto.

**Nota para ejecución por línea de comandos**: la primera vez, abrí el proyecto en el editor (o ejecutá `godot --headless --import`) para generar la caché de `class_name`; sin ella, scripts como `Board` o `Unit` no se resuelven.
