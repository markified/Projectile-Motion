import pygame
from physics import Projectile
from ui import InputBox, Button


FPS = 60

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Projectile Motion Simulator")
clock = pygame.time.Clock()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACTIVE_COLOR = (30, 144, 255)

# CANNONBALL SIZE
BALL_RADIUS = 10

# CANNON
CANNON_BODY = (70, 70, 80)
CANNON_HIGHLIGHT = (140, 140, 150)
WHEEL_COLOR = (30, 30, 30)
FLASH_COLOR = (255, 200, 50)

def draw_fancy_cannon(screen, base_x, base_y, angle_deg, fired=False):
    
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


# UI elements
speed_input = InputBox(100, 40, 140, 32, text='20')
angle_input = InputBox(300, 40, 140, 32, text='45')
launch_button = Button(500, 40, 100, 32, text='Launch')  
reset_button = Button(650, 40, 100, 32, text='Reset')

# Add font for labels
font = pygame.font.Font(None, 28)

projectile = None
landed = False
total_time = 0
total_distance = 0
max_height = 0
trace_points = []

recent_records = []  # Store tuples: (speed, angle, total_time, total_distance, max_height)
MAX_RECORDS = 5

running = True
while running:
    dt = clock.tick(FPS) / 1000  # seconds per frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        speed_input.handle_event(event)
        angle_input.handle_event(event)
        if launch_button.handle_event(event):
            try:
                v0 = float(speed_input.text)
                angle = float(angle_input.text)
                g = 9.8  
                projectile = Projectile(v0, angle, g)
                landed = False
                total_time = 0
                total_distance = 0
                max_height = 0
                # trace_points = []  # Do NOT reset trace on new launch
            except ValueError:
                print("Invalid input")
        if reset_button.handle_event(event):
            projectile = None
            landed = False
            total_time = 0
            total_distance = 0
            max_height = 0
            trace_points = []
            recent_records = []

    if projectile and not landed:
        prev_y = projectile.position[1]
        projectile.update(dt)
        x, y = projectile.position
        
        if y / 10 > max_height:
            max_height = y / 10
    
        screen_x = x + 50
        screen_y = HEIGHT - 50 - y
        trace_points.append((int(screen_x), int(screen_y)))
        if y == 0 and prev_y > 0:
            landed = True
            total_time = projectile.t
            total_distance = x / 10  
            # Add to recent records, but only if inputs are valid numbers
            try:
                v0_val = float(speed_input.text)
                angle_val = float(angle_input.text)
                recent_records.insert(0, (
                    v0_val,
                    angle_val,
                    total_time,
                    total_distance,
                    max_height
                ))
                if len(recent_records) > MAX_RECORDS:
                    recent_records.pop()
            except ValueError:
                pass  # Ignore if input boxes are empty or invalid

    screen.fill(WHITE)
    pygame.draw.line(screen, BLACK, (0, HEIGHT-50), (WIDTH, HEIGHT-50), 2)

    
    cannon_base_x = 50
    cannon_base_y = HEIGHT - 50
    
    # Ensure angle_deg is defined (fallback to 45 if input invalid)
    try:
        angle_deg = float(angle_input.text)
    except Exception:
        angle_deg = 45

    # Determine if a recent launch just occurred (show flash briefly)
    fired = False
    if projectile:
        try:
            fired = projectile.t is not None and projectile.t < 0.12
        except Exception:
            fired = False

    draw_fancy_cannon(screen, cannon_base_x, cannon_base_y, angle_deg, fired=fired)

    
    if projectile:
        x, y = projectile.position
        screen_x = x + 50
        screen_y = HEIGHT - 50 - y
        pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), BALL_RADIUS)


    if len(trace_points) > 1:
        pygame.draw.lines(screen, (255, 0, 0), False, trace_points, 2)

   
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

    speed_input.draw(screen)
    angle_input.draw(screen)
    launch_button.draw(screen)
    reset_button.draw(screen)

    
    speed_input.color = orig_speed_color
    angle_input.color = orig_angle_color

   
    if landed:
        time_label = font.render(f"Total Time: {total_time:.2f} s", True, BLACK)
        dist_label = font.render(f"Total Range: {total_distance:.2f} m", True, BLACK)
        maxh_label = font.render(f"Max Height: {max_height:.2f} m", True, BLACK)
        screen.blit(time_label, (100, 90))
        screen.blit(dist_label, (100, 120))
        screen.blit(maxh_label, (100, 150))

    # Show recent record launches (left side)
    records_to_show = recent_records[:MAX_RECORDS]
    if records_to_show:
        start_x = 500  # left column
        start_y = 150  # vertical start (adjust if needed)
        record_title = font.render("Recent Launches:", True, BLACK)
        screen.blit(record_title, (start_x, start_y - 40))
        for i, rec in enumerate(records_to_show):
            rec_text = font.render(
                f"{i+1}. v0={rec[0]:.1f} m/s, θ={rec[1]:.1f}°, t={rec[2]:.2f}s, R={rec[3]:.2f}m, H={rec[4]:.2f}m",
                True, BLACK
            )
            screen.blit(rec_text, (start_x, start_y + i * 30))

    pygame.display.flip()

pygame.quit()