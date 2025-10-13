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

        # position in meters (decoupled from screen pixels)
        self.position = (0.0, float(self.h0))

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

        # store position in meters
        self.position = (x_m, y_m)

    # Instantaneous velocity components (m/s)
    def velocity(self) -> tuple[float, float]:
        # vx is constant; vy decreases by g*t
        return self.vx, (self.vy0 - self.g * self.t)

    # Instantaneous speed magnitude (m/s)
    def speed(self) -> float:
        vx, vy = self.velocity()
        return math.hypot(vx, vy)

    def flight_time(self) -> float:
        # time until y = 0 (general h0 handled)
        eps = 1e-12
        if abs(self.g) < eps:
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
        # horizontal distance at landing (meters)
        t = self.flight_time()
        return max(0.0, self.vx * t)

    def max_height(self) -> float:
        # peak height above ground (meters)
        eps = 1e-12
        if self.vy0 <= eps:
            return self.h0
        return self.h0 + (self.vy0**2) / (2 * self.g)

    # ----------------- Angled launch formulas (relative to horizontal) -----------------
    def x_t(self, t: float) -> float:
        # x = v0 cos(θ) t
        return self.v0 * math.cos(self.angle) * t

    def y_t(self, t: float) -> float:
        # y = h + v0 sin(θ) t - 1/2 g t^2
        return self.h0 + self.v0 * math.sin(self.angle) * t - 0.5 * self.g * t * t

    def range_level(self) -> float:
        # R = (v0^2 sin(2θ)) / g   (h0 = 0)
        return (self.v0 * self.v0 * math.sin(2 * self.angle)) / self.g

    def max_height_relative(self) -> float:
        # H = (v0^2 sin^2(θ)) / (2g)   (above launch level)
        s = math.sin(self.angle)
        return (self.v0 * self.v0 * s * s) / (2 * self.g)

    def time_of_flight_level(self) -> float:
        # T = (2 v0 sin(θ)) / g   (h0 = 0)
        return (2 * self.v0 * math.sin(self.angle)) / self.g

    # ------------- Horizontal launch (no initial vertical angle) from height h0 --------
    def vx_horizontal(self) -> float:
        # Vx = v0 (constant)
        return self.v0

    def vy_horizontal(self, t: float) -> float:
        # Vy (signed) = - g t (downward)
        return -self.g * t

    def vy_horizontal_mag(self, t: float) -> float:
        # |Vy| = g t
        return self.g * t

    def speed_horizontal(self, t: float) -> float:
        # V = sqrt(v0^2 + (g t)^2)
        return math.hypot(self.v0, self.g * t)

    def theta_horizontal(self, t: float) -> float:
        # θ = atan2(Vy, Vx) in degrees (negative = below horizontal)
        vx = self.v0
        vy = -self.g * t
        return math.degrees(math.atan2(vy, vx))

    def theta_horizontal_textbook(self, t: float) -> float:
        # θ = tan⁻¹(Vx / Vy) in degrees (as listed; undefined at t=0 -> return 90°)
        vy_mag = self.g * t
        if vy_mag <= 1e-12:
            return 90.0
        return math.degrees(math.atan(self.v0 / vy_mag))

    def drop_height(self, t: float) -> float:
        # H = 1/2 g t^2 (distance fallen from launch level)
        return 0.5 * self.g * t * t

    def range_horizontal(self, t: float) -> float:
        # R = Vx t
        return self.v0 * t

    def time_of_flight_horizontal_from_height(self) -> float:
        # T = sqrt(2 H / g) with H = h0
        return math.sqrt(2 * max(0.0, self.h0) / self.g) if self.g > 0 else 0.0

    @staticmethod
    def time_from_height(height: float, g: float = 9.8) -> float:
        # T = sqrt(2 H / g)
        if g <= 0 or height < 0:
            return 0.0
        return math.sqrt(2 * height / g)