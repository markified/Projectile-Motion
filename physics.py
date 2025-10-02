import math


class Projectile:
    def __init__(self, v0: float, angle_deg: float, g: float = 9.8, h0: float = 0.0):
        self.v0 = v0
        self.angle = math.radians(angle_deg)
        self.g = g
        self.h0 = float(h0)
        self.t = 0.0
        # components
        self.vx = v0 * math.cos(self.angle)
        self.vy0 = v0 * math.sin(self.angle)
        self.landed = False
        # position stored in pixels for compatibility (meters * 10)
        self.position = (0, int(self.h0 * 10))

    def update(self, dt: float):
        if self.landed:
            return
        self.t += dt
        # position in meters
        x_m = self.vx * self.t
        y_m = self.h0 + self.vy0 * self.t - 0.5 * self.g * self.t**2

        # if we've dropped to or below ground, compute exact landing time and clamp
        if y_m <= 0:
            t_land = self.flight_time()
            if t_land > 0 and t_land <= self.t + 1e-9:
                # clamp to exact landing time
                self.t = t_land
                x_m = self.vx * self.t
                y_m = 0.0
                self.landed = True
            else:
                # fallback if flight_time couldn't be computed
                y_m = max(0.0, y_m)
                if y_m == 0.0:
                    self.landed = True

        # store position in pixels (scale factor 10)
        self.position = (x_m * 10, y_m * 10)

    def flight_time(self) -> float:
        # Solve 0 = h0 + vy0 * t - 0.5 * g * t^2  -> 0.5*g*t^2 - vy0*t - h0 = 0
        eps = 1e-12
        if abs(self.g) < eps:
            # no gravity: if vy0 < 0 then land in t = -h0/vy0, else infinite / zero
            if abs(self.vy0) < eps:
                return 0.0
            t = -self.h0 / self.vy0
            return t if t > 0 else 0.0

        discr = self.vy0 ** 2 + 2 * self.g * self.h0
        if discr < 0:
            return 0.0
        # positive root (vy0 + sqrt(discr)) / g
        t = (self.vy0 + math.sqrt(discr)) / self.g
        return t if t > 0 else 0.0

    def range(self) -> float:
        return self.vx * self.flight_time()

    def max_height(self) -> float:
        # If initial vertical speed is zero or downward, max height is initial height h0
        eps = 1e-12
        if self.vy0 <= eps:
            return self.h0
        # otherwise h0 + vy0^2 / (2*g)
        return self.h0 + (self.vy0 ** 2) / (2 * self.g)