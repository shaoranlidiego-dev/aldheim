# El Reino Olvidado: Aldheim

RPG táctico 2D por turnos, vista cenital y tablero cuadriculado. Pensado primero para Android.
Hecho con **Godot 4** y **GDScript**, sin complementos ni dependencias externas.

> Estado: base técnica (v0.2). Hay tablero, un personaje en pixel art (provisional) y movimiento por casillas.
> Todavía no hay combate, enemigos, personajes ni multijugador.

## Requisitos

- [Godot 4.3 o superior](https://godotengine.org/download) (versión estándar, no hace falta .NET).

## Abrir y ejecutar

1. Abrí Godot y en el Gestor de proyectos elegí **Importar**.
2. Seleccioná el archivo `project.godot` de esta carpeta y confirmá.
3. Abrí el proyecto y presioná **F5** (o el botón ▶). La escena principal es `scenes/main.tscn`.

## Cómo se juega

1. Tocá (o hacé clic en) el personaje: se marcan en azul las casillas alcanzables (4 pasos, sin atravesar obstáculos).
2. Tocá una casilla azul: la ficha camina hasta ahí.
3. Tocá cualquier otro lugar para cancelar la selección.

Los toques se tratan como clic izquierdo (`emulate_mouse_from_touch`), así el mismo código sirve en PC y en pantallas táctiles.

## Estructura

```
project.godot            Configuración (pantalla vertical 720x1280, escena principal)
scenes/main.tscn         Escena inicial: tablero, ficha e interfaz
scripts/board/board.gd        Tablero: dibujo de la grilla, terreno y conversión píxel <-> casilla
scripts/board/pathfinding.gd  Búsqueda de casillas alcanzables y caminos (BFS)
scripts/units/unit.gd         Unidad: casilla actual, dirección y movimiento animado (el sprite solo es visual)
assets/characters/hero_sheet.png        Hoja de sprites PROVISIONAL del héroe (16x16 por cuadro)
resources/characters/hero_frames.tres   SpriteFrames con las animaciones idle_/walk_ en 4 direcciones
tools/make_hero_sheet.py                Genera la hoja provisional (arte original, Pillow)
tools/build_hero_frames.gd              Regenera hero_frames.tres a partir de la hoja
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
- [ ] El personaje empieza en la casilla (1, 1).
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

## Probar en el editor: botón "Input" de la barra flotante

Desde Godot 4.4, al ejecutar con el juego incrustado o con el espacio de trabajo *Game* flotante, la barra
tiene modos de entrada. Solo el modo **Input** ("Allow game input") envía clics y toques al juego; los modos
de selección 2D/3D desactivan la entrada del juego para seleccionar nodos o mover la cámara del editor.
Si el modo activo no es *Input*, tocar la ficha no hace nada, pero eso es del editor, no del proyecto.

Para no depender de la barra:
- Dejá activado el modo **Input** durante la prueba; o
- Desactivá la incrustación (*Ajustes del editor > Run > Window Placement* o la opción *Embed Game* del espacio *Game*) para que el juego abra su propia ventana; o
- Exportá e instalá en el celular (*Despliegue con un clic*): ahí no interviene el editor.

## Generar un APK de depuración desde el propio Android (sin PC)

El repositorio incluye `export_presets.cfg` con el preset **Android (depuración)**: APK sin Gradle, solo
`arm64-v8a`, paquete `com.aldheim.reinoolvidado`. No contiene claves ni contraseñas.

1. Instalá el **editor oficial de Godot 4.7.2 para Android** (APK `Godot_v4.7.2-stable_android_editor.apk` en
   <https://github.com/godotengine/godot/releases/tag/4.7.2-stable>, o desde godotengine.org/download/android).
   Permití "instalar apps desconocidas" para el navegador o gestor de archivos que uses.
2. Descargá el proyecto como ZIP desde GitHub (rama `claude/aldheim-tactical-rpg-base-xavwgc`) y descomprimilo
   en una carpeta accesible (por ejemplo *Documentos/aldheim*).
3. En Godot: **Importar** y elegí `project.godot`. Abrilo.
4. Menú **Editor > Administrar plantillas de exportación > Descargar e instalar** (necesita internet, ~1 GB).
5. Menú **Proyecto > Exportar**. Debe aparecer *Android (depuración)*. Tocá **Exportar proyecto**, dejá
   marcada la opción de depuración, elegí una carpeta (por ejemplo *Descargas*) y guardá `aldheim-debug.apk`.
6. Abrí el APK desde el gestor de archivos, aceptá la instalación y abrí **Aldheim**.

Si la exportación pide un *keystore de depuración*, avisá con el texto exacto del mensaje: en Godot de escritorio se
genera con `keytool` y se indica en *Editor > Configuración del editor > Export > Android*.

Desde PC con Android SDK y JDK 17+ también sirve: `godot --headless --export-debug "Android (depuración)" build/aldheim-debug.apk`.

## Personaje (arte provisional)

La ficha circular fue reemplazada por un héroe de pixel art, vista cenital estilo RPG Maker, con un nodo
`AnimatedSprite2D` hijo de `Player` y un recurso `SpriteFrames`. **El dibujo es provisional**: lo generó
`tools/make_hero_sheet.py`, es arte original del proyecto (sin imágenes de terceros) y solo sirve para validar el
movimiento. No es el diseño final.

- La lógica táctica usa únicamente `Unit.cell`; el sprite sigue a `position` y queda centrado en la casilla
  (cuadro de 16 px escalado x4 = 64 px dentro de casillas de 80 px, filtro *nearest*).
- Al moverse se reproduce `walk_<dirección>` mirando hacia cada paso; al terminar, `idle_<dirección>`.
- El alcance (4 pasos), los obstáculos y el cálculo de caminos no cambiaron.

### Cómo sustituirlo por sprites definitivos

1. Dibujá una hoja PNG con cuadros del mismo tamaño y este orden: **3 columnas** (paso A, quieto, paso B) y
   **4 filas** (abajo, izquierda, derecha, arriba), como en RPG Maker. Guardala en
   `assets/characters/hero_sheet.png` (Godot la importa con filtro *nearest*).
2. Si el tamaño de cuadro no es 16x16, cambiá `FRAME_SIZE` en `tools/build_hero_frames.gd` y la escala del nodo
   `Sprite` en `scenes/main.tscn` para que mida cerca de 64 px.
3. Regenerá los cuadros: `godot --headless --script res://tools/build_hero_frames.gd` (después de abrir/importar
   el proyecto una vez). Alternativa: editar `hero_frames.tres` desde el panel *SpriteFrames* del editor.
4. Los nombres de animación deben mantenerse: `idle_down|left|right|up` y `walk_down|left|right|up`.

### Verificación del personaje

- [ ] El héroe aparece centrado en la casilla (1, 1) mirando hacia abajo, sin rastro de la ficha amarilla.
- [ ] Al caminar a la derecha, izquierda, arriba y abajo, el sprite mira hacia esa dirección y alterna cuadros.
- [ ] Al llegar queda quieto, mirando hacia donde caminó por última vez.
- [ ] En un camino con curvas cambia de dirección en cada giro.
- [ ] El héroe nunca pasa por las casillas oscuras y el alcance sigue siendo de 4 pasos.
- [ ] Los píxeles se ven nítidos (sin suavizado) en el celular.
