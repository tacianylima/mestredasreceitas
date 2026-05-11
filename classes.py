import pygame
import os

# --- BANCO DE DADOS DE RECEITAS E ALIMENTOS ---
RECEITAS = {
    tuple(sorted(["Gordura", "Carne Moída"])): {"nome": "Carne de Hambúrguer", "cat": "Base"},
    tuple(sorted(["Água", "Trigo"])): {"nome": "Massa", "cat": "Base"},
    tuple(sorted(["Ovo", "Óleo"])): {"nome": "Maionese", "cat": "Base"},
    tuple(sorted(["Água", "Tomate"])): {"nome": "Molho", "cat": "Base"},
    tuple(sorted(["Laranja", "Água"])): {"nome": "Suco de Laranja", "cat": "Bebida"},
    tuple(sorted(["Levedura", "Trigo", "Água"])): {"nome": "Pão", "cat": "Principal"},
    tuple(sorted(["Levedura", "Malte", "Lúpulo", "Água"])): {"nome": "Cerveja", "cat": "Bebida"},
    tuple(sorted(["Pão", "Carne de Hambúrguer", "Maionese"])): {"nome": "X-Burger Gourmet", "cat": "Principal"},
    tuple(sorted(["Massa", "Molho", "Carne Moída"])): {"nome": "Espaguete Bolonhesa", "cat": "Principal"},
    tuple(sorted(["Laranja", "Trigo", "Ovo"])): {"nome": "Bolo de Laranja", "cat": "Sobremesa"},
    tuple(sorted(["Gordura", "Trigo", "Laranja"])): {"nome": "Torta de Laranja", "cat": "Sobremesa"},
}

ALIMENTOS_DATA = {
    "FASE_1": [("Água", 2, "agua.png"), ("Trigo", 5, "trigo.png"), ("Gordura", 4, "gordura.png"),
               ("Carne Moída", 12, "carne_moida.png"), ("Tomate", 6, "tomate.png")],
    "FASE_2": [("Laranja", 8, "laranja.png"), ("Ovo", 5, "ovo.png"), ("Óleo", 10, "oleo.png")],
    "FASE_3": [("Levedura", 15, "levedura.png"), ("Malte", 20, "malte.png"), ("Lúpulo", 25, "lupulo.png")]
}


# --- CLASSES VISUAIS ---
class Botao:
    def __init__(self, texto, x, y, largura, altura, cor, acao):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor
        self.acao = acao

    def desenhar(self, surface, fonte):
        pos_mouse = pygame.mouse.get_pos()
        # Efeito hover: clareia a cor quando o mouse passa por cima
        cor_f = (min(self.cor[0] + 30, 255), min(self.cor[1] + 30, 255),
                 min(self.cor[2] + 30, 255)) if self.rect.collidepoint(pos_mouse) else self.cor
        pygame.draw.rect(surface, cor_f, self.rect, border_radius=10)
        txt = fonte.render(self.texto, True, (255, 255, 255))
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def clicou(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos): return self.acao
        return None


class ItemDraggable:
    def __init__(self, nome, custo, x, y, img_nome):
        self.nome = nome
        self.custo = custo
        try:
            self.image = pygame.transform.scale(pygame.image.load(os.path.join("assets", img_nome)), (60, 60))
        except:
            self.image = pygame.Surface((60, 60))
            self.image.fill((218, 165, 32))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False

    def desenhar(self, surface, fonte):
        surface.blit(self.image, self.rect)
        txt = fonte.render(self.nome, True, (30, 30, 30))
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.bottom + 2))


# --- CLASSE DE CONTROLE DO JOGO ---
class Game:
    def __init__(self):
        self.estado = "MENU"
        self.dinheiro = 150
        self.receitas_descobertas = {}
        self.nivel = 1
        self.titulo = "Estagiário"

        self.fez_principal = False
        self.fez_sobremesa = False
        self.fez_bebida = False

        self.mensagens = "Bem-vindo! Compre itens na loja."
        self.itens_loja = []
        self.bancada = []
        self.item_selecionado = None
        self.atualizar_estoque_loja()

    def atualizar_estoque_loja(self):
        lista = []
        lista.extend(ALIMENTOS_DATA["FASE_1"])
        if self.nivel >= 2: lista.extend(ALIMENTOS_DATA["FASE_2"])
        if self.nivel >= 3: lista.extend(ALIMENTOS_DATA["FASE_3"])
        self.itens_loja = lista

    def verificar_evolucao(self):
        checklist_ok = self.fez_principal and self.fez_sobremesa and self.fez_bebida
        total = len(self.receitas_descobertas)

        if checklist_ok:
            if self.nivel == 1 and total >= 3:
                self.subir_nivel(2, "Ajudante de Cozinha")
            elif self.nivel == 2 and total >= 7:
                self.subir_nivel(3, "Sous-Chef")
            elif self.nivel == 3 and total >= 12:
                self.subir_nivel(4, "Chef Mestre de Receitas")

    def subir_nivel(self, novo_nv, novo_tit):
        self.nivel = novo_nv
        self.titulo = novo_tit
        self.fez_principal = self.fez_sobremesa = self.fez_bebida = False
        self.mensagens = f"PROMOÇÃO! Cargo atual: {novo_tit}"
        self.atualizar_estoque_loja()

    def acao_combinar(self):
        if len(self.bancada) < 2:
            self.mensagens = "Coloque pelo menos 2 ingredientes!"
            return

        nomes_na_mesa = [item.nome for item in self.bancada]
        chave = tuple(sorted(nomes_na_mesa))

        if chave in RECEITAS:
            dados = RECEITAS[chave]
            nome_r = dados["nome"]
            cat_r = dados["cat"]
            self.mensagens = f"SUCESSO: {nome_r}!"

            if cat_r == "Principal": self.fez_principal = True
            if cat_r == "Sobremesa": self.fez_sobremesa = True
            if cat_r == "Bebida": self.fez_bebida = True

            if nome_r not in self.receitas_descobertas:
                self.receitas_descobertas[nome_r] = ", ".join(nomes_na_mesa)
                self.dinheiro += 60
            self.verificar_evolucao()
        else:
            self.mensagens = "Essa mistura não deu em nada..."
            self.dinheiro -= 10

        self.bancada = []