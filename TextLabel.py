import pygame

class TextLabel():
    def __init__(self, x, y, text, size, tag, font):
        self.font = font
        self.size = size
        self.text_raw = text
        self.tag = tag
        self.x = x
        self.y = y
        self.fontRender = pygame.font.SysFont(font, int(size))
        self._generate_text()

    def _generate_text(self):
        self.text = self.fontRender.render(self.text_raw, True, (255, 255, 255))
        self.rect = self.text.get_rect(center=(self.x, self.y))

    def setText(self, text):
        self.text_raw = text
        self._generate_text()

    def draw(self, surface):
        # Draw outline
        for dx, dy in [(-2, -2), (-2, 0), (-2, 2),
                       (0, -2),          (0, 2),
                       (2, -2), (2, 0), (2, 2)]:
            outline = self.fontRender.render(self.text_raw, True, (0, 0, 0))
            surface.blit(outline, self.rect.move(dx, dy).topleft)

        # Draw main text
        surface.blit(self.text, self.rect.topleft)
        return True
