import pygame


def get_font():
    if not hasattr(get_font, "_font"):
        get_font._font = pygame.font.Font(None, 32)
    return get_font._font


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0, 0, 0)
        self.text = text
        self.txt_surface = get_font().render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
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
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Button:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = get_font().render(text, True, (0, 0, 0))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))