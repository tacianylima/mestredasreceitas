import pygame


class Botao:
    def __init__(self, texto, x, y, largura, altura, cor_base, cor_hover):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.fonte = pygame.font.SysFont("Arial", 30)

    def desenhar(self, tela):
        # Verifica se o mouse está em cima (efeito Hover)
        pos_mouse = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(pos_mouse) else self.cor_base

        pygame.draw.rect(tela, cor, self.rect, border_radius=10)
        # Desenha o texto centralizado
        texto_render = self.fonte.render(self.texto, True, (255, 255, 255))
        tela.blit(texto_render, (self.rect.centerx - texto_render.get_width() // 2,
                                 self.rect.centery - texto_render.get_height() // 2))

    def clicou(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False