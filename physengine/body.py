"""Rigid body: position, velocity, mass, shape. Static = infinite mass."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union

from .vec2 import Vec2
from .shapes import Box, Circle


@dataclass
class Body:
    pos: Vec2 = field(default_factory=Vec2.zero)
    vel: Vec2 = field(default_factory=Vec2.zero)
    shape: Union[Circle, Box] = field(default_factory=lambda: Circle(10.0))
    mass: float = 1.0
    restitution: float = 0.5
    friction: float = 0.2

    inv_mass: float = field(init=False, default=0.0)
    inv_inertia: float = field(init=False, default=0.0)
    angle: float = 0.0
    angular_vel: float = 0.0

    def __post_init__(self) -> None:
        self._refresh_mass()

    def _refresh_mass(self) -> None:
        if self.mass <= 0 or self.mass == float("inf"):
            self.inv_mass = 0.0
            self.inv_inertia = 0.0
            self.mass = float("inf")
        else:
            self.inv_mass = 1.0 / self.mass
            I = self.shape.moment_of_inertia(self.mass)
            self.inv_inertia = 1.0 / I if I > 0 else 0.0

    def make_static(self) -> None:
        self.mass = float("inf")
        self.inv_mass = 0.0
        self.inv_inertia = 0.0
        self.vel = Vec2.zero()
        self.angular_vel = 0.0

    @property
    def is_static(self) -> bool:
        return self.inv_mass == 0.0

    def apply_impulse(self, impulse: Vec2) -> None:
        if self.is_static:
            return
        self.vel = self.vel + impulse * self.inv_mass

    def integrate(self, dt: float, gravity: Vec2) -> None:
        if self.is_static:
            return
        self.vel = self.vel + gravity * dt
        self.pos = self.pos + self.vel * dt
        self.angle = self.angle + self.angular_vel * dt
