"""World: container of bodies, runs the simulation step."""
from __future__ import annotations
from typing import List

from .body import Body
from .vec2 import Vec2
from . import collision


class World:
    def __init__(self, gravity: Vec2 = Vec2(0.0, 500.0)) -> None:
        self.gravity: Vec2 = gravity
        self.bodies: List[Body] = []
        self.contacts: List[collision.Manifold] = []
        self.last_step_contacts = 0

    def add(self, body: Body) -> Body:
        self.bodies.append(body)
        return body

    def step(self, dt: float, iterations: int = 8) -> None:
        # 1. Broad+narrow phase (naive O(n^2))
        self.contacts.clear()
        n = len(self.bodies)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.bodies[i], self.bodies[j]
                if a.is_static and b.is_static:
                    continue
                m = collision.detect(a, b)
                if m is not None:
                    self.contacts.append(m)
        self.last_step_contacts = len(self.contacts)

        # 2. Iterative impulse solver
        for _ in range(iterations):
            for m in self.contacts:
                collision.resolve(m)

        # 3. Integrate
        for body in self.bodies:
            body.integrate(dt, self.gravity)
