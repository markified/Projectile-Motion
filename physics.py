import math


class Projectile:
    def __init__(self, v0: float, angle_deg: float, g: float = 9.8, h0: float = 0.0):
        # input parameters
        self.v0 = v0
        self.angle = math.radians(angle_deg)
        self.g = g
        self.h0 = float(h0)

        # time state
        self.t = 0.0
        self.landed = False

        # velocity components
        self.vx = v0 * math.cos(self.angle)
        self.vy0 = v0 * math.sin(self.angle)

        # position stored in pixels (scale: 10 px per meter)
        self.position = (0, int(self.h0 * 10))

    def update(self, dt: float):
        # stop if already landed
        if self.landed:
            return

        # advance time
        self.t += dt

        # position in meters
        x_m = self.vx * self.t
        y_m = self.h0 + self.vy0 * self.t - 0.5 * self.g * self.t**2

        # handle ground contact
        if y_m <= 0:
            t_land = self.flight_time()
            if 0 < t_land <= self.t + 1e-9:
                # snap to exact landing
                self.t = t_land
                x_m = self.vx * self.t
                y_m = 0.0
                self.landed = True
            else:
                y_m = max(0.0, y_m)
                if y_m == 0.0:
                    self.landed = True

        # store pixel position
        self.position = (x_m * 10, y_m * 10)

    def flight_time(self) -> float:
        # solve vertical motion until y = 0
        eps = 1e-12
        if abs(self.g) < eps:
            # no gravity case
            if abs(self.vy0) < eps:
                return 0.0
            t = -self.h0 / self.vy0
            return t if t > 0 else 0.0

        discr = self.vy0**2 + 2 * self.g * self.h0
        if discr < 0:
            return 0.0
        t = (self.vy0 + math.sqrt(discr)) / self.g
        return t if t > 0 else 0.0

    def range(self) -> float:
        # horizontal distance at landing
        return self.vx * self.flight_time()

    def max_height(self) -> float:
        # peak height relative to ground
        eps = 1e-12
        if self.vy0 <= eps:
            return self.h0
        return self.h0 + (self.vy0**2) / (2 * self.g)