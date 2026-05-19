# physengine — 2D Rigid-Body Physics Engine

A from-scratch 2D rigid-body physics engine in Python, with circle + AABB shapes, gravity, impulse-based collision response, friction, and positional correction for stable stacking. Comes with both a headless numerical demo (CI-friendly) and an interactive Pygame visualization.

## Quick start

```bash
pip install -r requirements.txt

# Headless — runs the sim, prints positions every 30 frames, no display needed
python headless_demo.py

# Visual — Pygame window, click to drop bodies, R to reset, ESC to quit
python demo.py
```

## What the engine does

| Feature | Implementation |
|---|---|
| 2D vectors | `Vec2` with dot, 2D cross, length, normalize, perp |
| Shapes | `Circle(radius)`, `Box(half_w, half_h)` (axis-aligned) |
| Rigid bodies | `Body(pos, vel, shape, mass, restitution, friction)` |
| Static bodies | `body.make_static()` — infinite mass, immovable |
| Integration | Semi-implicit Euler |
| Collision detection | circle-circle, AABB-AABB, circle-AABB; dispatched by shape kind |
| Collision response | Impulse along contact normal using combined restitution + inverse masses |
| Friction | Coulomb model, tangent impulse clamped to friction cone |
| Stacking | Baumgarte positional correction with slop tolerance |
| Iterative solver | Configurable iterations per step (default 8) |

## API at a glance

```python
from physengine import World, Body, Vec2, Circle, Box

world = World(gravity=Vec2(0, 800))

# Static floor
floor = world.add(Body(pos=Vec2(400, 580), shape=Box(400, 10)))
floor.make_static()

# A ball with bounce
ball = world.add(Body(pos=Vec2(400, 100), shape=Circle(20),
                      mass=1.0, restitution=0.7))

for _ in range(180):                    # 3 seconds at 60 FPS
    world.step(dt=1/60, iterations=10)
```

## Architecture

```
physengine/
├── vec2.py        # Vec2 — 2D vector primitive
├── shapes.py      # Circle, Box (+ moment-of-inertia formulas)
├── body.py        # Body — pos/vel/shape/mass/restitution/friction
├── collision.py   # detect() + resolve() — manifold-based impulse solver
└── world.py       # World — broad+narrow phase, iterative solver, integration
demo.py            # Pygame interactive demo
headless_demo.py   # Stdout-only smoke test
tests/             # 5 pytest cases (free fall, bouncing, elastic collision, ...)
```

The collision pipeline is the interesting part: `detect()` returns a `Manifold` with the contact normal and penetration depth, then `resolve()` applies the impulse using the standard `j = -(1+e) * v_n / (1/m_a + 1/m_b)` formula plus a friction tangent impulse clamped to Coulomb's cone, plus a Baumgarte correction to prevent objects from sinking under sustained contact.

## Verified behaviors (`pytest tests/`)

| Test | What it checks |
|---|---|
| `test_vec2_basic_ops` | Vector arithmetic, dot, length, normalize |
| `test_free_fall` | Distance under gravity matches `0.5 * g * t²` within 5% |
| `test_ball_hits_static_floor_and_doesnt_fall_through` | No tunneling; ball stays above the floor |
| `test_two_circles_collide_and_separate` | Equal-mass elastic head-on swap velocities |
| `test_static_box_immovable` | Static bodies don't move even under gravity |

All 5 pass.

## Tech stack
Python 3.10+ · NumPy-free (pure stdlib for the engine) · Pygame for the demo · pytest

## Roadmap
The engine is intentionally minimal — designed to read in one sitting. Honest next steps:
- Rotational dynamics (currently bodies track an angle but the solver ignores it)
- Oriented Bounding Boxes (OBB) via SAT
- Spatial hashing / quadtree to replace the O(n²) broad phase
- Continuous collision detection (CCD) for fast-moving bodies

## License
MIT — see [LICENSE](LICENSE).
