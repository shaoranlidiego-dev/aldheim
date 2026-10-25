"""Pose de un cuadro de animación y ciclo de caminata de 6 cuadros."""
import math
from dataclasses import dataclass

WALK_FRAMES = 6


@dataclass
class Pose:
	bob: float = 0.0       # el cuerpo baja `bob` px (cuando las piernas están abiertas)
	swing_l: float = 0.0   # avance de la pierna izquierda de pantalla (-1 atrás .. 1 adelante)
	swing_r: float = 0.0
	lift_l: float = 0.0    # elevación del pie (0 apoyado .. 1 levantado)
	lift_r: float = 0.0
	arm_l: float = 0.0     # avance del brazo izquierdo de pantalla
	arm_r: float = 0.0
	sway: float = 0.0      # vaivén de capa, bufanda y mechones (-1..1)
	breath: float = 0.0    # respiración (0..1)


def walk_pose(frame: int) -> Pose:
	phi = 2 * math.pi * frame / WALK_FRAMES
	cos_l, sin_l = math.cos(phi), math.sin(phi)
	return Pose(
		bob=0.9 * abs(cos_l),
		swing_l=cos_l, swing_r=-cos_l,
		lift_l=max(0.0, -sin_l), lift_r=max(0.0, sin_l),
		arm_l=-cos_l, arm_r=cos_l,
		sway=sin_l,
	)


def idle_pose(frame: int) -> Pose:
	return Pose(breath=float(frame), bob=0.5 * frame, sway=0.0 if frame == 0 else 0.4)
