import random
import pygame
from physics import Projectile
from ui import InputBox, Button
import math  # added for any future math use

# Core settings
FPS = 120
SCALE = 10
GROUND_OFFSET = 50
CANNON_BASE_X = 50
# Fade animation timings
FADE_OUT_DURATION = 1 
FADE_IN_DURATION = 2  

# --- Pygame initialization ---------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Projectile Motion Simulator")
clock = pygame.time.Clock()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACTIVE_COLOR = (30, 144, 255)
SKY_TOP = (120, 180, 255)
SKY_BOTTOM = (220, 240, 255)
GRASS_TOP = (80, 200, 120)
GRASS_BOTTOM = (30, 120, 60)
SUN_COLOR = (255, 255, 120)
CLOUD_COLOR = (255, 255, 255, 180)
SHADOW_COLOR = (60, 60, 60, 90)
CANNON_BODY = (70, 70, 80)
CANNON_HIGHLIGHT = (140, 140, 150)
WHEEL_COLOR = (30, 30, 30)
FLASH_COLOR = (255, 200, 50)
LAUNCH_BTN_BG = (200, 30, 30)
LAUNCH_BTN_TEXT = (255, 255, 255)
RESET_BTN_BG = (0, 0, 0)
RESET_BTN_TEXT = (255, 255, 255)
# NEW: close button colors
CLOSE_BTN_BG = (140, 20, 20)
CLOSE_BTN_TEXT = (255, 255, 255)

# Fancy feature colors
PREDICT_COLOR = (255, 140, 0)
HUD_BG = (0, 0, 0, 120)
PARTICLE_BASE = (255, 230, 120)

# Cannonball size
BALL_RADIUS = 10
TARGET_RADIUS = 25

# Background drawing
def draw_gradient_rect(surf, rect, top_color, bottom_color):
    x, y, w, h = rect
    for i in range(h):
        ratio = i / h
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surf, (r, g, b), (x, y + i), (x + w, y + i))

def draw_sky_and_ground(screen, WIDTH, HEIGHT):
    # draw sky and sun, and ground band
    draw_gradient_rect(screen, (0, 0, WIDTH, HEIGHT - GROUND_OFFSET), SKY_TOP, SKY_BOTTOM)
    pygame.draw.circle(screen, SUN_COLOR, (WIDTH-120, 120), 60)
    # clouds now dynamic (removed static blits here)
    draw_gradient_rect(screen, (0, HEIGHT - GROUND_OFFSET, WIDTH, GROUND_OFFSET), GRASS_TOP, GRASS_BOTTOM)
    for gx in range(0, WIDTH, 18):
        pygame.draw.line(
            screen,
            (60, 180, 80),
            (gx, HEIGHT - 10),
            (gx + 2, HEIGHT - GROUND_OFFSET + random.randint(0, 10)),
            2
        )

# Shadow for projectile
def draw_projectile_shadow(screen, x, y, radius):
    shadow = pygame.Surface((radius*4, radius*2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, SHADOW_COLOR, (0, 0, radius*4, radius))
    screen.blit(shadow, (int(x-radius*2), int(y+radius*1.5)))

# Trail drawing
def draw_fancy_trail(screen, points, color=(255,0,0)):
    if len(points) < 2:
        return
    
    if len(points) > 2:
        pygame.draw.lines(screen, color, False, points, 2)
    
    for i in range(1, min(len(points), 20)):
        alpha = max(40, 180 - i*8)
        r, g, b = color
        trail = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(trail, (r, g, b, alpha), (4, 4), 4)
        screen.blit(trail, (points[-i][0]-4, points[-i][1]-4))

# Marker for max height
def draw_max_marker(screen, points, height_m=None, label_color=(20,20,20)):
    # draw marker at highest point
    if not points:
        return
    mx, my = min(points, key=lambda p: p[1])
    if height_m is None:
        height_m = (HEIGHT - GROUND_OFFSET - my) / SCALE
    MARKER_COLOR = (255, 215, 0)  # gold
    pygame.draw.circle(screen, MARKER_COLOR, (mx, my), 8)
    pygame.draw.circle(screen, (0, 0, 0), (mx, my), 8, 2)

# Cannon drawing
def draw_fancy_cannon(screen, base_x, base_y, angle_deg, fired=False):
    # draw cannon barrel, base and wheels
    dir_vec = pygame.math.Vector2(1, 0).rotate(-angle_deg)
    perp = dir_vec.rotate(90)
    barrel_length = 70
    barrel_width = 20

    end = pygame.math.Vector2(base_x, base_y) + dir_vec * barrel_length
    p1 = pygame.math.Vector2(base_x, base_y) + perp * (barrel_width/2)
    p2 = pygame.math.Vector2(base_x, base_y) - perp * (barrel_width/2)
    p3 = end - perp * (barrel_width*0.35)
    p4 = end + perp * (barrel_width*0.35)
    pygame.draw.polygon(screen, CANNON_BODY, [p1, p2, p3, p4])

    inset = 6
    p1h = pygame.math.Vector2(base_x, base_y) + perp * (barrel_width/2 - inset)
    p2h = pygame.math.Vector2(base_x, base_y) - perp * (barrel_width/2 - inset)
    p3h = end - perp * (barrel_width*0.35 - inset)
    p4h = end + perp * (barrel_width*0.35 - inset)
    pygame.draw.polygon(screen, CANNON_HIGHLIGHT, [p1h, p2h, p3h, p4h])
    
    pygame.draw.line(screen, (30,30,30), p3, p4, 2)
    
    base_rect = pygame.Rect(base_x - 38, base_y - 10, 76, 30)
    pygame.draw.ellipse(screen, CANNON_BODY, base_rect)  # shadowy base
    inner_rect = pygame.Rect(base_x - 30, base_y - 6, 60, 20)
    pygame.draw.ellipse(screen, CANNON_HIGHLIGHT, inner_rect)

    
    wheel_off = 26
    pygame.draw.circle(screen, WHEEL_COLOR, (base_x - wheel_off, base_y + 10), 12)
    pygame.draw.circle(screen, WHEEL_COLOR, (base_x + wheel_off, base_y + 10), 12)
    pygame.draw.circle(screen, (100,100,100), (base_x - wheel_off, base_y + 10), 6)
    pygame.draw.circle(screen, (100,100,100), (base_x + wheel_off, base_y + 10), 6)

    
    pygame.draw.circle(screen, (20,20,20), (int(end.x), int(end.y)), 6)
    pygame.draw.circle(screen, (200,200,200), (int(end.x + dir_vec.x*4), int(end.y + dir_vec.y*4)), 3)

   
    if fired:
        for i, alpha in enumerate((180, 120, 80)):
            radius = 12 + i*8
            surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*FLASH_COLOR, alpha), (radius, radius), radius)
            pos = (int(end.x - radius + dir_vec.x*6), int(end.y - radius + dir_vec.y*6))
            screen.blit(surf, pos)


# UI elements (inputs and buttons)
speed_input = InputBox(100, 40, 140, 32, text='20')
angle_input = InputBox(300, 40, 140, 32, text='45')
height_input = InputBox(500, 40, 140, 32, text='0')
launch_button = Button(660, 40, 100, 32, text='Launch')
reset_button = Button(780, 40, 100, 32, text='Reset')
# NEW: Pause/Play button
pause_button = Button(900, 40, 100, 32, text='Pause')
# NEW: close button (top-right)
close_button = Button(WIDTH - 70, 12, 56, 36, text='X')

font = pygame.font.Font(None, 28)

# Title font and Start button for the start screen
title_font = pygame.font.Font(None, 96)
start_button = Button(WIDTH // 2 - 120, HEIGHT // 2 + 40, 240, 60, text='Start')
on_start_screen = True
# Fade state
fading = False
fade_phase = None  # 'out' or 'in'
fade_start_ms = 0
# NEW: pause state
paused = False

# Added: button drawing helper (was referenced later but undefined)
def draw_custom_button(surface, btn, bg_color, text_color):
    # draw gradient button with border and centered text
    hover = btn.rect.collidepoint(pygame.mouse.get_pos())
    base = pygame.Color(*bg_color)
    shade = 1.15 if hover else 0.65
    top = base
    bottom = pygame.Color(
        min(255, int(base.r * shade)),
        min(255, int(base.g * shade)),
        min(255, int(base.b * shade)),
    )
    grad = pygame.Surface(btn.rect.size, pygame.SRCALPHA)
    for i in range(btn.rect.height):
        t = i / btn.rect.height
        r = int(top.r * (1 - t) + bottom.r * t)
        g = int(top.g * (1 - t) + bottom.g * t)
        b = int(top.b * (1 - t) + bottom.b * t)
        pygame.draw.line(grad, (r, g, b), (0, i), (btn.rect.width, i))
    surface.blit(grad, btn.rect.topleft)
    pygame.draw.rect(surface, (255, 255, 255), btn.rect, 2, border_radius=8)
    label = font.render(btn.text, True, text_color)
    surface.blit(label, label.get_rect(center=btn.rect.center))

# Helper: fullscreen fade overlay
def apply_fade_overlay(surface, alpha: int):
    if alpha <= 0:
        return
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(alpha)))
    surface.blit(overlay, (0, 0))

# --- Added: helpers to draw velocity vectors (Vx, Vy, V) ---
def draw_arrow(surface, start, vec, color, width=3):
    # Draw a simple arrow from start by vec (in pixels)
    sx, sy = start
    ex, ey = sx + vec[0], sy + vec[1]
    pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
    ang = math.atan2(vec[1], vec[0]) if (vec[0] or vec[1]) else 0.0
    head_len = 10
    head_ang = math.radians(22)
    left = (ex - head_len * math.cos(ang - head_ang), ey - head_len * math.sin(ang - head_ang))
    right = (ex - head_len * math.cos(ang + head_ang), ey - head_len * math.sin(ang + head_ang))
    pygame.draw.polygon(surface, color, [(ex, ey), left, right])

def draw_velocity_vectors(surface, px, py, vx, vy):
    # Scale m/s to pixels and invert y for screen coords
    scale = 3
    vx_vec = (vx * scale, 0)
    vy_vec = (0, -vy * scale)
    v_vec  = (vx * scale, -vy * scale)
    # Colors (local, avoids changing global palette)
    vx_col = (0, 120, 255)
    vy_col = (0, 200, 120)
    v_col  = (255, 120, 40)
    # Draw arrows
    draw_arrow(surface, (px, py), vx_vec, vx_col, 3)
    draw_arrow(surface, (px, py), vy_vec, vy_col, 3)
    draw_arrow(surface, (px, py), v_vec,  v_col,  2)
    # Labels
    v_mag = math.hypot(vx, vy)
    surface.blit(font.render(f"Vx={vx:.1f} m/s", True, vx_col), (px + 8, py - 20))
    surface.blit(font.render(f"Vy={vy:.1f} m/s", True, vy_col), (px - 8 - font.size(f"Vy={vy:.1f} m/s")[0], py - 36))
    surface.blit(font.render(f"V={v_mag:.1f} m/s", True, v_col), (px + 8, py + 8))

# NEW: formula-accurate metrics based on angle and height
def compute_launch_metrics(v0: float, angle_deg: float, h0: float, g: float, proj: Projectile):
    """
    Returns (T, R, H_display)
    H_display:
      - If h0≈0: H = (v0^2 sin^2θ)/(2g)  (above launch)
      - If θ≈0 and h0>0: H = 1/2 g T^2  (drop distance; equals h0)
      - Else: H = h0 + (v0^2 sin^2θ)/(2g) (apex above ground)
    """
    eps = 1e-6
    angle_rad = math.radians(angle_deg)
    s = math.sin(angle_rad)
    c = math.cos(angle_rad)

    # Level ground (h0 ~ 0)
    if abs(h0) < eps:
        T = (2 * v0 * s) / g if g > 0 else 0.0
        R = v0 * c * T  # numerically stable and equivalent to (v0^2 sin 2θ)/g
        H = (v0 * v0 * s * s) / (2 * g) if g > 0 else 0.0
        return max(0.0, T), max(0.0, R), max(0.0, H)

    # Horizontal from height (θ ~ 0 and h0 > 0)
    if abs(s) < eps:
        T = math.sqrt(2 * h0 / g) if g > 0 else 0.0
        R = v0 * T
        H = 0.5 * g * (T * T)  # equals h0
        return max(0.0, T), max(0.0, R), max(0.0, H)

    # General case (h0 > 0, θ > 0)
    T = proj.flight_time()
    R = v0 * c * T
    H = h0 + (v0 * v0 * s * s) / (2 * g) if g > 0 else h0
    return max(0.0, T), max(0.0, R), max(0.0, H)

clouds = [
    {
        'x': random.randint(0, WIDTH),
        'y': random.randint(40, 180),
        'r': random.randint(30, 55),
        'speed': random.uniform(10, 35)
    } for _ in range(6)
]

particles = []         
last_launch_time = None 

def get_cannon_muzzle(base_x, base_y, angle_deg):
    """Return muzzle (x,y) and direction vector of cannon barrel."""
    barrel_length = 70
    dir_vec = pygame.math.Vector2(1, 0).rotate(-angle_deg)
    muzzle = pygame.math.Vector2(base_x, base_y) + dir_vec * barrel_length
    return int(muzzle.x), int(muzzle.y), dir_vec

def spawn_particles(mx, my, dir_vec):
    """Create simple fading particles at muzzle."""
    for _ in range(25):
        spread = dir_vec.rotate(random.uniform(-35, 35))
        speed = random.uniform(90, 240)
        particles.append({
            'pos': [mx, my],
            'vel': [spread.x * speed, spread.y * speed],
            'life': random.uniform(0.25, 0.6),
            'max': 0.6
        })

def update_particles(dt):
    """Advance and prune particles."""
    gravity = 300
    for p in particles:
        p['life'] -= dt
        p['vel'][1] += gravity * dt
        p['pos'][0] += p['vel'][0] * dt
        p['pos'][1] += p['vel'][1] * dt
    particles[:] = [p for p in particles if p['life'] > 0]


projectile = None
landed = False
total_time = 0
total_distance = 0
max_height = 0

# Traces
all_traces = []        
current_trace = None    

recent_records = []  
MAX_RECORDS = 5
# Add target variables 
target_x = None  
target_y = None
TARGET_RADIUS = 25
target_hit = False

# initialize target position (use constants)
target_x = WIDTH - 200
target_y = HEIGHT - GROUND_OFFSET

running = True
while running:
    dt = clock.tick(FPS) / 1000  # seconds per frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # NEW: toggle pause via Space key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused

        speed_input.handle_event(event)
        angle_input.handle_event(event)
        height_input.handle_event(event)

        # NEW: close button handling
        if close_button.handle_event(event):
            running = False
        # NEW: pause button handling
        if pause_button.handle_event(event):
            paused = not paused

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            ui_clicked = (speed_input.rect.collidepoint(event.pos)
                          or angle_input.rect.collidepoint(event.pos)
                          or height_input.rect.collidepoint(event.pos)   
                          or launch_button.rect.collidepoint(event.pos)
                          or reset_button.rect.collidepoint(event.pos))
            if not ui_clicked:
                target_x = mx
                target_y = HEIGHT - GROUND_OFFSET
                target_hit = False
        if launch_button.handle_event(event):
            try:
                v0 = float(speed_input.text)
                angle = float(angle_input.text)
                h0 = float(height_input.text)  
                g = 9.8
                projectile = Projectile(v0, angle, g, h0)
                # spawn muzzle particles
                mx, my, dvec = get_cannon_muzzle(CANNON_BASE_X, HEIGHT - GROUND_OFFSET - int(h0 * SCALE), angle)
                spawn_particles(mx, my, dvec)
                last_launch_time = pygame.time.get_ticks() / 1000.0
                landed = False
                total_time = 0
                total_distance = 0
                max_height = 0
                # start a new trace for this launch and keep previous traces
                trace_color = (random.randint(120,255), random.randint(60,220), random.randint(40,200))
                trace = {'points': [], 'color': trace_color, 'max_height': projectile.max_height()}
                all_traces.append(trace)
                current_trace = trace
            except ValueError:
                print("Invalid input")
        if reset_button.handle_event(event):
            projectile = None
            landed = False
            total_time = 0
            total_distance = 0
            max_height = 0
            all_traces = []      
            current_trace = None
            recent_records = []
            target_hit = False

        # Start screen: handle Start button click -> begin fade out
        if on_start_screen and start_button.handle_event(event):
            fading = True
            fade_phase = 'out'
            fade_start_ms = pygame.time.get_ticks()

    # Start screen rendering (skip simulation until started)
    if on_start_screen:
        # update clouds for animated background
        for c in clouds:
            c['x'] += c['speed'] * dt
            if c['x'] - c['r']*3 > WIDTH:
                c['x'] = -c['r']*3
                c['y'] = random.randint(40, 180)
                c['speed'] = random.uniform(10, 35)

        screen.fill(WHITE)
        draw_sky_and_ground(screen, WIDTH, HEIGHT)

        # draw dynamic clouds
        for c in clouds:
            cloud = pygame.Surface((c['r']*3, c['r']*2), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud, CLOUD_COLOR, (0, c['r']//2, c['r']*3, c['r']))
            pygame.draw.ellipse(cloud, CLOUD_COLOR, (c['r'], 0, c['r']*2, c['r']))
            screen.blit(cloud, (int(c['x']), int(c['y'])))

        # title
        title_text = title_font.render("Projectile Motion Simulator", True, ACTIVE_COLOR)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

        # Start button (same theme using custom drawer)
        draw_custom_button(screen, start_button, LAUNCH_BTN_BG, LAUNCH_BTN_TEXT)

        # NEW: draw close button on start screen
        draw_custom_button(screen, close_button, CLOSE_BTN_BG, CLOSE_BTN_TEXT)

        # Fade-out overlay while transitioning to game
        if fading and fade_phase == 'out':
            now = pygame.time.get_ticks()
            t = (now - fade_start_ms) / (FADE_OUT_DURATION * 1000.0)
            t = max(0.0, min(1.0, t))
            apply_fade_overlay(screen, int(255 * t))
            if t >= 1.0:
                # switch to game and start fade-in
                on_start_screen = False
                fade_phase = 'in'
                fade_start_ms = now

        pygame.display.flip()
        continue

    # Physics update only if not paused
    if projectile and not landed:
        prev_y = projectile.position[1]
        if not paused:
            projectile.update(dt)
            # meters -> pixels for plotting
            x_m, y_m = projectile.position
            x_px = x_m * SCALE
            y_px = y_m * SCALE
            # update max height and trace while running
            if current_trace is not None:
                current_trace['max_height'] = max(current_trace.get('max_height', 0.0), projectile.max_height())
                current_trace['points'].append(
                    (int(x_px + CANNON_BASE_X), int(HEIGHT - GROUND_OFFSET - y_px))
                )
            # handle landing using formulas
            if projectile.landed:
                landed = True
                try:
                    v0_val = float(speed_input.text)
                    angle_val = float(angle_input.text)
                    h0_val = float(height_input.text)
                except ValueError:
                    v0_val, angle_val, h0_val = 0.0, 0.0, 0.0
                g_val = 9.8
                total_time, total_distance, h_display = compute_launch_metrics(v0_val, angle_val, h0_val, g_val, projectile)
                if target_x is not None:
                    target_distance_m = (target_x - CANNON_BASE_X) / SCALE
                    tolerance_m = (TARGET_RADIUS + BALL_RADIUS) / SCALE
                    target_hit = abs(total_distance - target_distance_m) <= tolerance_m
                else:
                    target_hit = False
                max_height = h_display
                if current_trace is not None:
                    current_trace['max_height'] = max(current_trace.get('max_height', 0.0), h_display)
                try:
                    recent_records.insert(0, (v0_val, angle_val, total_time, total_distance, h_display))
                    if len(recent_records) > MAX_RECORDS:
                        recent_records.pop()
                except Exception:
                    pass

    # Update moving clouds (only when not paused)
    if not paused:
        for c in clouds:
            c['x'] += c['speed'] * dt
            if c['x'] - c['r']*3 > WIDTH:
                c['x'] = -c['r']*3
                c['y'] = random.randint(40, 180)
                c['speed'] = random.uniform(10, 35)

        update_particles(dt)

    # ...existing code before drawing sky...

    screen.fill(WHITE)
    draw_sky_and_ground(screen, WIDTH, HEIGHT)
    # draw dynamic clouds
    for c in clouds:
        cloud = pygame.Surface((c['r']*3, c['r']*2), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud, CLOUD_COLOR, (0, c['r']//2, c['r']*3, c['r']))
        pygame.draw.ellipse(cloud, CLOUD_COLOR, (c['r'], 0, c['r']*2, c['r']))
        screen.blit(cloud, (int(c['x']), int(c['y'])))
    pygame.draw.line(screen, BLACK, (0, HEIGHT - GROUND_OFFSET), (WIDTH, HEIGHT - GROUND_OFFSET), 2)
    # compute cannon base position
    try:
        h0_draw = float(height_input.text)
    except Exception:
        h0_draw = 0.0
    cannon_base_x = CANNON_BASE_X
    cannon_base_y = HEIGHT - GROUND_OFFSET - int(h0_draw * SCALE)  

    # base/platform from cannon_base_y down to ground ---
    # platform dimensions
    platform_width = 80
    platform_x = cannon_base_x - platform_width // 2
    platform_top = cannon_base_y
    platform_bottom = HEIGHT - GROUND_OFFSET
    platform_height = max(4, platform_bottom - platform_top)
    platform_rect = pygame.Rect(platform_x, platform_top, platform_width, platform_height)
    # platform colors
    PLATFORM_COLOR = (120, 80, 40)       # brown
    PLATFORM_HIGHLIGHT = (160, 110, 60)  # lighter top
    pygame.draw.rect(screen, PLATFORM_COLOR, platform_rect)
  
    highlight_rect = pygame.Rect(platform_x, platform_top, platform_width, 6)
    pygame.draw.rect(screen, PLATFORM_HIGHLIGHT, highlight_rect)
    
    slat_color = (100, 60, 30)
    for sx in range(platform_x + 6, platform_x + platform_width - 6, 10):
        pygame.draw.line(screen, slat_color, (sx, platform_top + 8), (sx, platform_bottom - 6), 2)

    # --- Ensure angle_deg is defined (fallback to 45 if input invalid) ---
    try:
        angle_deg = float(angle_input.text)
    except Exception:
        angle_deg = 45

    fired = False
    if projectile:
        try:
            fired = projectile.t is not None and projectile.t < 0.12
        except Exception:
            fired = False
    draw_fancy_cannon(screen, cannon_base_x, cannon_base_y, angle_deg, fired=fired)

    # projectile drawing (screen coords)
    if projectile:
        x_m, y_m = projectile.position
        screen_x = x_m * SCALE + CANNON_BASE_X
        screen_y = HEIGHT - GROUND_OFFSET - y_m * SCALE
        pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), BALL_RADIUS)
        draw_projectile_shadow(screen, screen_x, HEIGHT - GROUND_OFFSET, BALL_RADIUS)

        # --- Added: draw Vx, Vy, and resultant V after launch ---
        if not landed:
            vx = projectile.vx
            vy = projectile.vy0 - projectile.g * projectile.t
            draw_velocity_vectors(screen, int(screen_x), int(screen_y), vx, vy)

    # draw all stored traces (persistent)
    for trace in all_traces:
        pts = trace['points']
        if len(pts) > 0:
            draw_fancy_trail(screen, pts, trace.get('color', (0,0,255)))

    # highlight max height of current trace (if any), else last trace
    target_trace = None
    if current_trace and current_trace.get('points'):
        target_trace = current_trace
    else:
        for tr in reversed(all_traces):
            if tr.get('points'):
                target_trace = tr
                break
    if target_trace:
        draw_max_marker(screen, target_trace['points'], height_m=target_trace.get('max_height'))

   
    speed_label_color = ACTIVE_COLOR if speed_input.active else BLACK
    angle_label_color = ACTIVE_COLOR if angle_input.active else BLACK
    speed_label = font.render("Speed (m/s):", True, speed_label_color)
    angle_label = font.render("Angle (deg):", True, angle_label_color)
    screen.blit(speed_label, (100, 20))
    screen.blit(angle_label, (300, 20))

    
    orig_speed_color = speed_input.color
    orig_angle_color = angle_input.color
    speed_input.color = ACTIVE_COLOR if speed_input.active else BLACK
    angle_input.color = ACTIVE_COLOR if angle_input.active else BLACK

    # draw UI controls
    speed_input.draw(screen)
    angle_input.draw(screen)
    draw_custom_button(screen, launch_button, LAUNCH_BTN_BG, LAUNCH_BTN_TEXT)
    draw_custom_button(screen, reset_button, RESET_BTN_BG, RESET_BTN_TEXT)
    # close button on main screen (top-right)
    draw_custom_button(screen, close_button, CLOSE_BTN_BG, CLOSE_BTN_TEXT)
    # NEW: draw Pause/Play button and keep label in sync
    pause_button.text = 'Play' if paused else 'Pause'
    draw_custom_button(screen, pause_button, RESET_BTN_BG, RESET_BTN_TEXT)

    # restore original color state
    speed_input.color = orig_speed_color
    angle_input.color = orig_angle_color

    # Draw UI labels including height label and active color change
    height_label_color = ACTIVE_COLOR if height_input.active else BLACK
    height_label = font.render("Cannon Height (m):", True, height_label_color)
    screen.blit(height_label, (480, 20))

    # ensure the height input is drawn with active highlight (existing pattern)
    orig_height_color = height_input.color
    height_input.color = ACTIVE_COLOR if height_input.active else BLACK

    height_input.draw(screen)

    # restore original color state
    height_input.color = orig_height_color

   
    if landed:
        time_label = font.render(f"Total Time: {total_time:.2f} s", True, BLACK)
        dist_label = font.render(f"Total Range: {total_distance:.2f} m", True, BLACK)
        maxh_label = font.render(f"Max Height: {max_height:.2f} m", True, BLACK)
        screen.blit(time_label, (100, 90))
        screen.blit(dist_label, (100, 120))
        screen.blit(maxh_label, (100, 150))

    # Show recent record launches 
    records_to_show = recent_records[:MAX_RECORDS]
    if records_to_show:
        start_x = 750
        start_y = 130
        record_title = font.render("Recent Launches:", True, BLACK)
        screen.blit(record_title, (start_x, start_y - 40))

        line_h = font.get_linesize()
        spacing_between_records = 10  # blank space between records

        y = start_y
        for i, rec in enumerate(records_to_show):
            # index on its own line
            idx_text = font.render(f"{i+1}.", True, BLACK)
            screen.blit(idx_text, (start_x, y))

            # details rendered on separate lines, indented
            info_x = start_x + 30
            labels = [
                f"V = {rec[0]:.1f} m/s",
                f"θ  = {rec[1]:.1f}°",
                f"T  = {rec[2]:.2f} s",
                f"R  = {rec[3]:.2f} m",
                f"H  = {rec[4]:.2f} m",
            ]
            for j, lbl in enumerate(labels):
                txt = font.render(lbl, True, BLACK)
                screen.blit(txt, (info_x, y + j * line_h))

            # advance y to next record (adds an extra blank line)
            y += len(labels) * line_h + spacing_between_records
# Draw target dummy (bullseye + pole)
    if target_x is None:
        target_x = WIDTH - 200
    if target_y is None:
        target_y = HEIGHT - GROUND_OFFSET

    # choose colors depending on hit state
    outer_color = (80, 200, 80) if target_hit else (150, 0, 0)
    middle_color = (255, 255, 255) if not target_hit else (220, 255, 220)
    inner_color = (0, 100, 200) if not target_hit else (0, 120, 0)

    pygame.draw.circle(screen, outer_color, (int(target_x), int(target_y)), TARGET_RADIUS)
    pygame.draw.circle(screen, middle_color, (int(target_x), int(target_y)), int(TARGET_RADIUS * 0.66))
    pygame.draw.circle(screen, inner_color, (int(target_x), int(target_y)), int(TARGET_RADIUS * 0.33))
    
    pygame.draw.rect(screen, (100, 60, 20), (int(target_x) - 3, target_y - 2, 6, 40))
   
    target_dist_label = font.render(
        f"Target: {(target_x - CANNON_BASE_X) / SCALE:.2f} m",
        True,
        BLACK
    )
    # adjusted vertical labels with GROUND_OFFSET where applicable
    screen.blit(target_dist_label, (int(target_x) - TARGET_RADIUS, target_y - 110))

    # show HIT/MISS if landed
    if landed:
        hit_text = font.render(
            "HIT!" if target_hit else "MISS",
            True,
            (0,150,0) if target_hit else (180,30,30)
        )
        screen.blit(hit_text, (int(target_x) - TARGET_RADIUS, target_y - 80))

    # handle fade-in after start
    if fading and fade_phase == 'in':
        now = pygame.time.get_ticks()
        t = (now - fade_start_ms) / (FADE_IN_DURATION * 1000.0)
        t = max(0.0, min(1.0, t))
        apply_fade_overlay(screen, int(255 * (1.0 - t)))
        if t >= 1.0:
            fading = False
            fade_phase = None

    # NEW: pause overlay and label
    if paused:
        apply_fade_overlay(screen, 100)
        paused_text = title_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(paused_text, paused_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

pygame.quit()