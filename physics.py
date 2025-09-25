import math


class Projectile:
    def __init__(self, v0: float, angle_deg: float, g: float = 9.8):
        self.v0 = v0
        self.angle = math.radians(angle_deg)
        self.g = g
        self.t = 0
        self.position = (0, 0)
        self.vx = v0 * math.cos(self.angle)
        self.vy = v0 * math.sin(self.angle)

    def update(self, dt: float):
        self.t += dt
        x = self.vx * self.t
        y = self.vy * self.t - 0.5 * self.g * self.t**2
        if y < 0:
            y = 0
        self.position = (x * 10, y * 10)  