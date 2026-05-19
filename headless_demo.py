"""Headless demo — runs the simulation, prints state. No display needed.

Drops a ball + a few stacked boxes onto a floor and prints positions every
10 steps. Useful for CI / smoke testing the engine.
"""
from physengine import World, Body, Vec2, Circle, Box


def main() -> None:
    world = World(gravity=Vec2(0, 500))

    floor = world.add(Body(pos=Vec2(400, 580), shape=Box(400, 10)))
    floor.make_static()

    ball = world.add(Body(pos=Vec2(400, 100), shape=Circle(20),
                          mass=1.0, restitution=0.7))
    box1 = world.add(Body(pos=Vec2(420, 200), shape=Box(20, 20),
                          mass=1.0, restitution=0.3))
    box2 = world.add(Body(pos=Vec2(380, 300), shape=Box(20, 20),
                          mass=1.0, restitution=0.3))

    dt = 1 / 60
    for step in range(180):  # 3 seconds
        world.step(dt)
        if step % 30 == 0:
            print(f"t={step*dt:.2f}s  contacts={world.last_step_contacts}  "
                  f"ball={ball.pos.x:.1f},{ball.pos.y:.1f}  "
                  f"box1={box1.pos.x:.1f},{box1.pos.y:.1f}  "
                  f"box2={box2.pos.x:.1f},{box2.pos.y:.1f}")

    print("\nSimulation finished. Final positions:")
    print(f"  ball at ({ball.pos.x:.1f}, {ball.pos.y:.1f})")
    print(f"  box1 at ({box1.pos.x:.1f}, {box1.pos.y:.1f})")
    print(f"  box2 at ({box2.pos.x:.1f}, {box2.pos.y:.1f})")


if __name__ == "__main__":
    main()
