"""Collision detection + impulse-based resolution.

Supports three shape pairs: circle/circle, AABB/AABB, circle/AABB.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .body import Body
from .vec2 import Vec2
from .shapes import Box, Circle


@dataclass
class Manifold:
    a: Body
    b: Body
    normal: Vec2       # points from a to b
    penetration: float


def _detect_circle_circle(a: Body, b: Body) -> Optional[Manifold]:
    delta = b.pos - a.pos
    r = a.shape.radius + b.shape.radius
    dist_sq = delta.length_sq()
    if dist_sq >= r * r:
        return None
    if dist_sq > 1e-12:
        dist = dist_sq ** 0.5
        normal = delta * (1.0 / dist)
        return Manifold(a, b, normal, r - dist)
    return Manifold(a, b, Vec2(1.0, 0.0), r)


def _detect_box_box(a: Body, b: Body) -> Optional[Manifold]:
    dx = b.pos.x - a.pos.x
    px = (a.shape.half_width + b.shape.half_width) - abs(dx)
    if px <= 0:
        return None
    dy = b.pos.y - a.pos.y
    py = (a.shape.half_height + b.shape.half_height) - abs(dy)
    if py <= 0:
        return None
    if px < py:
        normal = Vec2(1.0 if dx > 0 else -1.0, 0.0)
        return Manifold(a, b, normal, px)
    normal = Vec2(0.0, 1.0 if dy > 0 else -1.0)
    return Manifold(a, b, normal, py)


def _detect_circle_box(circle_body: Body, box_body: Body) -> Optional[Manifold]:
    c: Circle = circle_body.shape  # type: ignore[assignment]
    bx: Box = box_body.shape  # type: ignore[assignment]
    delta = circle_body.pos - box_body.pos
    closest_x = max(-bx.half_width, min(bx.half_width, delta.x))
    closest_y = max(-bx.half_height, min(bx.half_height, delta.y))
    closest = Vec2(closest_x, closest_y)

    to_circle = delta - closest
    dist_sq = to_circle.length_sq()
    if dist_sq >= c.radius * c.radius:
        return None

    if dist_sq > 1e-12:
        dist = dist_sq ** 0.5
        normal_circle_to_box = -to_circle * (1.0 / dist)
        return Manifold(circle_body, box_body, normal_circle_to_box, c.radius - dist)
    overlap_x = bx.half_width - abs(delta.x)
    overlap_y = bx.half_height - abs(delta.y)
    if overlap_x < overlap_y:
        n = Vec2(1.0 if delta.x < 0 else -1.0, 0.0)
        return Manifold(circle_body, box_body, n, overlap_x + c.radius)
    n = Vec2(0.0, 1.0 if delta.y < 0 else -1.0)
    return Manifold(circle_body, box_body, n, overlap_y + c.radius)


def detect(a: Body, b: Body) -> Optional[Manifold]:
    ka, kb = a.shape.kind, b.shape.kind
    if ka == "circle" and kb == "circle":
        return _detect_circle_circle(a, b)
    if ka == "box" and kb == "box":
        return _detect_box_box(a, b)
    if ka == "circle" and kb == "box":
        return _detect_circle_box(a, b)
    if ka == "box" and kb == "circle":
        m = _detect_circle_box(b, a)
        if m is None:
            return None
        return Manifold(a, b, -m.normal, m.penetration)
    raise NotImplementedError(f"shape pair {ka}/{kb} not supported")


def resolve(m: Manifold) -> None:
    a, b = m.a, m.b
    rv = b.vel - a.vel
    vel_along_normal = rv.dot(m.normal)
    if vel_along_normal > 0:
        return  # already separating

    e = min(a.restitution, b.restitution)
    inv_mass_sum = a.inv_mass + b.inv_mass
    if inv_mass_sum <= 0:
        return

    j = -(1.0 + e) * vel_along_normal / inv_mass_sum
    impulse = m.normal * j
    a.apply_impulse(-impulse)
    b.apply_impulse(impulse)

    # Friction
    tangent = rv - m.normal * vel_along_normal
    t_len = tangent.length()
    if t_len > 1e-9:
        tangent = tangent * (1.0 / t_len)
        jt = -rv.dot(tangent) / inv_mass_sum
        mu = (a.friction + b.friction) * 0.5
        if abs(jt) > j * mu:
            jt = j * mu * (1 if jt > 0 else -1)
        friction_impulse = tangent * jt
        a.apply_impulse(-friction_impulse)
        b.apply_impulse(friction_impulse)

    # Positional correction (Baumgarte) — fixes sinking under sustained contact
    percent = 0.4
    slop = 0.01
    correction = m.normal * (max(m.penetration - slop, 0.0) / inv_mass_sum * percent)
    if a.inv_mass > 0:
        a.pos = a.pos - correction * a.inv_mass
    if b.inv_mass > 0:
        b.pos = b.pos + correction * b.inv_mass
