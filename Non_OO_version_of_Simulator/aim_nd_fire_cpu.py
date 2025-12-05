"""
pro_fire_sim.py

Single-file advanced projectile + flame simulation using Tkinter.

Run:
    python pro_fire_sim.py

 version python:   Python 3.12.6 (C:\Python312\python.exe)
 python -m pip install moderngl moderngl-window pyrr
"""

import tkinter as tk
import random
import math
import time
import sys

# Optional: detect moderngl (GPU) presence and inform user
try:
    import moderngl  # noqa: F401

    HAS_MODERNG = True
except Exception:
    HAS_MODERNG = False

if HAS_MODERNG:
    print(
        "moderngl detected: GPU shader mode is possible. This script currently uses Tkinter rendering by default."
    )
    print(
        "If you want a GPU shader implementation, tell me and I'll provide a separate moderngl-based renderer."
    )
else:
    print("moderngl not found — running Tkinter renderer (no extra deps required).")

# -------------------------
# Config
# -------------------------
WIDTH, HEIGHT = 1000, 700
TARGET_FPS = 60  # target frames per second
GRAVITY = 700.0  # px/s^2
AIR_DRAG = 0.995  # per frame multiplicative (approx)
PROJECTILE_SPEED = 1200.0  # base px/s
AUTO_FIRE_RATE = 10.0  # shots per second when holding fire
WIND = 0.0  # horizontal wind (px/s) positive -> right
GROUND_Y = HEIGHT - 40
MAX_PROJECTILES = 40
MAX_PARTICLES = 800


# -------------------------
# Utility
# -------------------------
def clamp(v, a, b):
    return max(a, min(b, v))


def gauss_like(n=8):
    return sum(random.random() for _ in range(n)) / n


# -------------------------
# Fractal-ish fast flame generator
# (two-level midpoint displacement optimized for realtime)
# -------------------------
def build_wiggly_points(A, B, std, levels=2):
    """
    Return list of points approximating a wiggly curve from A to B.
    This is a cheap midpoint displacement with few subdivisions.
    """
    pts = [A, B]
    for level in range(levels):
        new_pts = []
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            mx = (x1 + x2) * 0.5
            my = (y1 + y2) * 0.5
            # perpendicular
            px = -(y2 - y1)
            py = x2 - x1
            mag = math.hypot(px, py) + 1e-6
            px /= mag
            py /= mag
            factor = std * (0.6**level)
            t = (gauss_like(6) - 0.5) * 2 * factor
            mx += px * t
            my += py * t
            new_pts.append((x1, y1))
            new_pts.append((mx, my))
        new_pts.append(pts[-1])
        pts = new_pts
    return pts


# -------------------------
# Particle / Projectile classes
# -------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "col")

    def __init__(self, x, y, vx, vy, life, size, col):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.col = col

    def step(self, dt):
        self.vy += GRAVITY * dt * 0.1  # very light gravity on particles
        self.vx += WIND * dt * 0.3  # particles affected a bit by wind
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0


class Projectile:
    __slots__ = ("x", "y", "vx", "vy", "alive", "age", "radius", "owner")

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.age = 0.0
        self.radius = 5.0
        self.owner = None

    def step(self, dt):
        # Apply wind and gravity; drag multiplicative
        self.vx += WIND * dt
        self.vy += GRAVITY * dt
        # simple drag
        self.vx *= 1.0 - (1.0 - AIR_DRAG) * dt * 60.0
        self.vy *= 1.0 - (1.0 - AIR_DRAG) * dt * 60.0
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt


# -------------------------
# Simulator / Renderer
# -------------------------
class Simulator:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        self.projectiles = []
        self.particles = []
        self.target = {"x": WIDTH - 160, "y": GROUND_Y - 120, "r": 36}
        self.origin = (80, GROUND_Y)
        self.mouse = (self.origin[0] + 120, self.origin[1] - 120)
        self.aim_angle = -math.pi / 4
        self.holding_fire = False
        self.last_auto_fire = 0.0
        self.last_time = time.time()
        self.show_debug = False

        # controls
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_click)
        root.bind("<KeyPress>", self.on_key_down)
        root.bind("<KeyRelease>", self.on_key_up)

        # UI text
        self.hint_text = self.canvas.create_text(
            12,
            12,
            anchor="nw",
            fill="white",
            font=("Helvetica", 12),
            text=self.hint_string(),
        )

        # start loop
        self.running = True
        self.loop()

    def hint_string(self):
        return (
            "Aim with mouse or arrow keys. Click or Space to fire. Hold Space = rapid fire. "
            "Wind [ / ]  Toggle debug: D. FPS target: %d" % TARGET_FPS
        )

    def on_mouse_move(self, e):
        self.mouse = (e.x, e.y)
        ox, oy = self.origin
        self.aim_angle = math.atan2(e.y - oy, e.x - ox)

    def on_click(self, e):
        self.fire(e.x, e.y)

    def on_key_down(self, e):
        if e.keysym == "space":
            self.holding_fire = True
        elif e.keysym == "Left":
            self.aim_angle -= 0.06
        elif e.keysym == "Right":
            self.aim_angle += 0.06
        elif e.keysym == "Up":
            self.aim_angle -= 0.06
        elif e.keysym == "Down":
            self.aim_angle += 0.06
        elif e.keysym == "d" or e.keysym == "D":
            self.show_debug = not self.show_debug
        elif e.keysym == "bracketleft":
            global WIND
            WIND -= 10
        elif e.keysym == "bracketright":
            WIND += 10

    def on_key_up(self, e):
        if e.keysym == "space":
            self.holding_fire = False

    def fire(self, tx, ty):
        # compute direction
        ox, oy = self.origin
        dx = tx - ox
        dy = ty - oy
        d = math.hypot(dx, dy)
        if d < 1:
            return
        vx = dx / d * PROJECTILE_SPEED
        vy = dy / d * PROJECTILE_SPEED
        if len(self.projectiles) < MAX_PROJECTILES:
            p = Projectile(ox, oy, vx, vy)
            self.projectiles.append(p)

    def spawn_explosion(self, x, y, power=1.0, color_range=None, num=60):
        # spawn particles in a burst
        for i in range(int(num * power)):
            ang = random.random() * math.pi * 2
            speed = random.random() * 300 * math.sqrt(power)
            vx = math.cos(ang) * speed + WIND * 0.2
            vy = math.sin(ang) * speed * 0.6 - 150 * power
            life = 0.4 + random.random() * 0.8
            size = 2 + random.random() * 4
            # color orange->red->yellow
            r = int(clamp(200 + random.randint(0, 55), 0, 255))
            g = int(clamp(random.randint(50, 180), 0, 255))
            b = 20
            col = "#%02x%02x%02x" % (r, g, b)
            if len(self.particles) < MAX_PARTICLES:
                self.particles.append(Particle(x, y, vx, vy, life, size, col))

    def step_sim(self, dt):
        # auto-fire
        if self.holding_fire:
            now = time.time()
            if now - self.last_auto_fire >= 1.0 / AUTO_FIRE_RATE:
                # fire along the current aim angle
                ox, oy = self.origin
                vx = math.cos(self.aim_angle) * PROJECTILE_SPEED
                vy = math.sin(self.aim_angle) * PROJECTILE_SPEED
                if len(self.projectiles) < MAX_PROJECTILES:
                    p = Projectile(ox, oy, vx, vy)
                    self.projectiles.append(p)
                self.last_auto_fire = now

        # step projectiles
        to_remove = []
        for p in self.projectiles:
            p.step(dt)
            # map collisions
            # ground collision
            if p.y >= GROUND_Y:
                p.y = GROUND_Y
                # bounce or explode — small bounce with energy loss
                if abs(p.vy) > 180:
                    # bounce
                    p.vy = -p.vy * 0.35
                    p.vx *= 0.6
                    # spawn ricochet spark
                    self.spawn_explosion(p.x, p.y - 6, power=0.4, num=12)
                else:
                    # low-speed -> settle and explode
                    to_remove.append(p)
                    self.spawn_explosion(p.x, p.y, power=1.0, num=40)
                continue
            # target collision
            dx = p.x - self.target["x"]
            dy = p.y - self.target["y"]
            if dx * dx + dy * dy <= self.target["r"] ** 2:
                to_remove.append(p)
                self.spawn_explosion(p.x, p.y, power=1.8, num=120)
                # small target push (move target a bit)
                self.target["x"] += random.uniform(-12, 12)
                self.target["y"] += random.uniform(-8, 8)
                continue
            # off-screen
            if p.x < -200 or p.x > WIDTH + 200 or p.y < -500 or p.y > HEIGHT + 500:
                to_remove.append(p)
        # remove
        for p in to_remove:
            if p in self.projectiles:
                self.projectiles.remove(p)

        # particles
        new_particles = []
        for q in self.particles:
            q.step(dt)
            if q.life > 0 and 0 <= q.x <= WIDTH * 2 and -500 <= q.y <= HEIGHT + 500:
                new_particles.append(q)
        self.particles = new_particles

    def render(self):
        c = self.canvas
        c.delete("all")
        # background
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", outline="")

        # ground
        c.create_rectangle(0, GROUND_Y, WIDTH, HEIGHT, fill="#1b1b1b", outline="")

        # target
        tx, ty, tr = self.target["x"], self.target["y"], self.target["r"]
        c.create_oval(
            tx - tr, ty - tr, tx + tr, ty + tr, fill="#7a0f0f", outline="red", width=2
        )
        c.create_text(tx, ty, text="TARGET", fill="#ffd7d7", font=("Helvetica", 10))

        # draw particles (back to front)
        for q in self.particles:
            alpha = clamp(q.life / q.max_life, 0.0, 1.0)
            size = q.size * (0.5 + 0.5 * alpha)
            # fade color by mixing with black
            c.create_oval(
                q.x - size, q.y - size, q.x + size, q.y + size, fill=q.col, outline=""
            )

        # draw projectiles and flames
        for p in self.projectiles:
            # flame/backtrail is based on speed
            speed = math.hypot(p.vx, p.vy)
            # flame length scales with speed (clamped)
            flame_len = clamp(10 + speed * 0.03, 12, 120)
            # flame std depends on speed (faster -> more turbulent)
            flame_std = clamp(6 + speed * 0.03, 6, 48)

            # back-point (behind projectile relative to velocity)
            vmag = math.hypot(p.vx, p.vy) + 1e-6
            bx = p.x - (p.vx / vmag) * flame_len
            by = p.y - (p.vy / vmag) * flame_len

            # Adaptive multi-layer flame: inner bright thin, outer wider and redder
            # layers: inner (yellow), mid (orange), outer (red)
            layers = [
                (0.3, 2.0, "#FFF8B0"),  # inner: multiplier std, width, color
                (1.0, 3.5, "#FFB347"),  # mid
                (1.6, 5.5, "#D93F1A"),  # outer
            ]
            for mult, w, col in layers:
                std = flame_std * mult
                pts = build_wiggly_points((p.x, p.y), (bx, by), std=std, levels=2)
                # draw polyline
                if len(pts) >= 2:
                    flat = []
                    for xx, yy in pts:
                        flat.extend((xx, yy))
                    c.create_line(*flat, fill=col, width=w, smooth=True, splinesteps=6)

            # projectile core
            c.create_oval(p.x - 4, p.y - 4, p.x + 4, p.y + 4, fill="white", outline="")
            c.create_oval(
                p.x - 8, p.y - 8, p.x + 8, p.y + 8, outline="", fill="#FF6F3C"
            )

        # draw origin / cannon
        ox, oy = self.origin
        # barrel end
        angle = self.aim_angle
        bx = ox + math.cos(angle) * 60
        by = oy + math.sin(angle) * 60
        c.create_line(ox, oy, bx, by, fill="#666666", width=10, capstyle="round")
        c.create_oval(ox - 10, oy - 10, ox + 10, oy + 10, fill="#444444", outline="")

        # wind arrow
        wind_label = f"WIND: {WIND:.1f} px/s"
        c.create_text(12, HEIGHT - 24, anchor="w", fill="white", text=wind_label)

        # hint text
        c.create_text(
            12,
            12,
            anchor="nw",
            fill="white",
            text=self.hint_string(),
            font=("Helvetica", 11),
        )

        # debug overlay (optional)
        if self.show_debug:
            fps_text = "PROJECTILES: %d    PARTICLES: %d" % (
                len(self.projectiles),
                len(self.particles),
            )
            c.create_text(WIDTH - 12, 12, anchor="ne", fill="lightgreen", text=fps_text)

    def loop(self):
        now = time.time()
        dt = now - self.last_time
        # clamp dt to avoid big jumps if OS paused
        dt = clamp(dt, 0.0, 1.0 / 15.0)
        self.last_time = now

        # simulation step
        self.step_sim(dt)

        # render
        self.render()

        # schedule next frame
        delay = int(1000.0 / TARGET_FPS)
        self.root.after(delay, self.loop)


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pro Fire Simulator — Tkinter (no external deps required)")
    sim = Simulator(root)
    root.mainloop()
