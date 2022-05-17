import pygame

class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, label, pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.label = label
        self.change_text(label, bg)
 
    def change_text(self, text, bg="black"):
        """Change the text whe you click"""
        self.text = self.font.render(text, 1, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def draw(self,screen):
        screen.blit(self.surface, (self.x, self.y))
 
    def check_click(self, x, y) -> bool:
        if self.rect.collidepoint(x, y):
            self.change_text(self.feedback, bg="red")
            return True
        return False