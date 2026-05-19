"""Shape primitives: Circle and axis-aligned Box."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Circle:
    radius: float

    @property
    def kind(self) -> str:
        return "circle"

    def moment_of_inertia(self, mass: float) -> float:
        # Solid disk about its center: 0.5 * m * r^2
        return 0.5 * mass * self.radius * self.radius


@dataclass
class Box:
    half_width: float
    half_height: float

    @property
    def kind(self) -> str:
        return "box"

    def moment_of_inertia(self, mass: float) -> float:
        # Solid rectangle about its center: (1/12) * m * (w^2 + h^2)
        w = 2 * self.half_width
        h = 2 * self.half_height
        return (mass * (w * w + h * h)) / 12.0
