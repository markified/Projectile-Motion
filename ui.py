import pygame


def get_font():
    # return a cached font instance
    if not hasattr(get_font, "_font"):
        get_font._font = pygame.font.Font(None, 32)
    return get_font._font


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        # rectangle, colors and initial text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0, 0, 0)
        self.text = text
        self.txt_surface = get_font().render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        # mouse toggles active; keys edit text
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = get_font().render(self.text, True, self.color)

    def draw(self, screen):
        # render text and border
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Button:
    def __init__(self, x, y, w, h, text=''):
        # rectangle and label
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = get_font().render(text, True, (0, 0, 0))

    def handle_event(self, event):
        # return True when clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen, bg_color=(200, 200, 200), text_color=(0, 0, 0), border_radius=8):
        # draw themed button
        draw_custom_button(screen, self, bg_color, text_color, border_radius)


def draw_custom_button(surface, btn, bg_color, text_color, border_radius=8):
    """
    Draw a button with vertical gradient, border and centered text.
    """
    # draw gradient, border and centered label
    hover = btn.rect.collidepoint(pygame.mouse.get_pos())
    base = pygame.Color(*bg_color)
    # Slightly lighter when hovered, darker otherwise
    shade = 1.15 if hover else 0.65
    top = base
    bottom = pygame.Color(
        min(255, int(base.r * shade)),
        min(255, int(base.g * shade)),
        min(255, int(base.b * shade)),
    )

    grad = pygame.Surface(btn.rect.size, pygame.SRCALPHA)
    h = btn.rect.height if btn.rect.height > 0 else 1
    for i in range(h):
        t = i / h
        r = int(top.r * (1 - t) + bottom.r * t)
        g = int(top.g * (1 - t) + bottom.g * t)
        b = int(top.b * (1 - t) + bottom.b * t)
        pygame.draw.line(grad, (r, g, b), (0, i), (btn.rect.width, i))
    surface.blit(grad, btn.rect.topleft)

    pygame.draw.rect(surface, (255, 255, 255), btn.rect, 2, border_radius=border_radius)

    # Render text centered
    label = get_font().render(getattr(btn, 'text', ''), True, text_color)
    surface.blit(label, label.get_rect(center=btn.rect.center))