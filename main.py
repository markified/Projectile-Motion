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


# UI elements
speed_input = InputBox(100, 20, 140, 32, text='20')
angle_input = InputBox(300, 20, 140, 32, text='45')
launch_button = Button(500, 20, 100, 32, text='Launch')  

# Add font for labels
font = pygame.font.Font(None, 28)


projectile = None
landed = False
total_time = 0
total_distance = 0

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
            except ValueError:
                print("Invalid input")

    if projectile and not landed:
        prev_y = projectile.position[1]
        projectile.update(dt)
        x, y = projectile.position
        
        if y == 0 and prev_y > 0:
            landed = True
            total_time = projectile.t
            total_distance = x / 10  

    screen.fill(WHITE)
    
    pygame.draw.line(screen, BLACK, (0, HEIGHT-50), (WIDTH, HEIGHT-50), 2)

    
    cannon_base_x = 50
    cannon_base_y = HEIGHT - 50
    
    pygame.draw.circle(screen, (80, 80, 80), (cannon_base_x, cannon_base_y), 20)
    
    try:
        angle_deg = float(angle_input.text)
    except ValueError:
        angle_deg = 45
    angle_rad = -angle_deg * 3.14159265 / 180  
    barrel_length = 40
    barrel_width = 12
    
    end_x = cannon_base_x + barrel_length * pygame.math.Vector2(1, 0).rotate_rad(angle_rad).x
    end_y = cannon_base_y + barrel_length * pygame.math.Vector2(1, 0).rotate_rad(angle_rad).y
    
    pygame.draw.line(screen, (60, 60, 60), (cannon_base_x, cannon_base_y), (end_x, end_y), barrel_width)

    
    if projectile:
        x, y = projectile.position
        screen_x = x + 50
        screen_y = HEIGHT - 50 - y
        pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5)

   
    speed_label_color = ACTIVE_COLOR if speed_input.active else BLACK
    angle_label_color = ACTIVE_COLOR if angle_input.active else BLACK
    speed_label = font.render("Speed (m/s):", True, speed_label_color)
    angle_label = font.render("Angle (deg):", True, angle_label_color)
    screen.blit(speed_label, (100, 0))
    screen.blit(angle_label, (300, 0))

    
    orig_speed_color = speed_input.color
    orig_angle_color = angle_input.color
    speed_input.color = ACTIVE_COLOR if speed_input.active else BLACK
    angle_input.color = ACTIVE_COLOR if angle_input.active else BLACK

    speed_input.draw(screen)
    angle_input.draw(screen)
    launch_button.draw(screen)

    
    speed_input.color = orig_speed_color
    angle_input.color = orig_angle_color

   
    if landed:
        time_label = font.render(f"Total Time: {total_time:.2f} s", True, BLACK)
        dist_label = font.render(f"Total Distance: {total_distance:.2f} m", True, BLACK)
        screen.blit(time_label, (100, 70))
        screen.blit(dist_label, (100, 100))

    pygame.display.flip()

pygame.quit()