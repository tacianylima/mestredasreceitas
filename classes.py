import pygame
import os

# --- BANCO DE DADOS DE RECEITAS ---
RECEITAS = {
    tuple(sorted(["Pó de Café", "Água"])): {"nome": "Café", "cat": "Bebida", "img": "cafe.png"},
    tuple(sorted(["Gordura", "Carne Moída"])): {"nome": "Carne de Hambúrguer", "cat": "Base",
                                                "img": "carne_hamburguer.png"},
    tuple(sorted(["Água", "Trigo"])): {"nome": "Massa", "cat": "Base", "img": "massa.png"},
    tuple(sorted(["Ovo", "Óleo"])): {"nome": "Maionese", "cat": "Base", "img": "maionese.png"},
    tuple(sorted(["Água", "Tomate"])): {"nome": "Molho", "cat": "Base", "img": "molho.png"},
    tuple(sorted(["Laranja", "Água"])): {"nome": "Suco de Laranja", "cat": "Bebida", "img": "suco.png"},
    tuple(sorted(["Levedura", "Trigo", "Água"])): {"nome": "Pão", "cat": "Principal", "img": "pao_pronto.png"},
    tuple(sorted(["Levedura", "Malte", "Lúpulo", "Água"])): {"nome": "Cerveja", "cat": "Bebida", "img": "cerveja.png"},
    tuple(sorted(["Pão", "Carne de Hambúrguer", "Maionese"])): {"nome": "X-Burger Gourmet", "cat": "Principal",
                                                                "img": "xburger.png"},
    tuple(sorted(["Massa", "Molho", "Carne Moída"])): {"nome": "Espaguete Bolonhesa", "cat": "Principal",
                                                       "img": "espaguete.png"},
    tuple(sorted(["Laranja", "Trigo", "Ovo"])): {"nome": "Bolo de Laranja", "cat": "Sobremesa", "img": "bolo.png"},
    tuple(sorted(["Gordura", "Trigo", "Laranja"])): {"nome": "Torta de Laranja", "cat": "Sobremesa",
                                                     "img": "torta.png"},
}

ALIMENTOS_DATA = {
    "FASE_1": [("Água", 2, "agua.png"), ("Trigo", 5, "trigo.png"), ("Gordura", 4, "gordura.png"),
               ("Carne Moída", 12, "carne_moida.png"), ("Tomate", 6, "tomate.png"),
               ("Laranja", 8, "laranja.png"), ("Pó de Café", 10, "po_cafe.png")],
    "FASE_2": [("Ovo", 5, "ovo.png"), ("Óleo", 10, "oleo.png")],
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
        cor_f = (min(self.cor[0] + 30, 255), min(self.cor[1] + 30, 255),
                 min(self.cor[2] + 30, 255)) if self.rect.collidepoint(pos_mouse) else self.cor
        pygame.draw.rect(surface, cor_f, self.rect, border_radius=12)
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
            self.image = pygame.transform.scale(pygame.image.load(os.path.join("assets", img_nome)).convert_alpha(),
                                                (65, 65))
        except:
            self.image = pygame.Surface((65, 65), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (218, 165, 32), (32, 32), 32)
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
        self.titulo = "Iniciante"
        self.fez_principal = self.fez_sobremesa = self.fez_bebida = False
        self.mensagens = "Bem-vinda(o) Chef! Arraste os itens para começar."

        self.itens_loja = []
        self.bancada = []
        self.item_selecionado = None
        self.itens_descobertos_loja = []  # Pratos que vão pra loja
        self.atualizar_estoque_loja()

        # Variáveis de Animação
        self.anim_img = None
        self.anim_nome = ""
        self.anim_alpha = 0
        self.anim_estado = None
        self.anim_timer = 0

    def atualizar_estoque_loja(self):
        lista = []
        lista.extend(ALIMENTOS_DATA["FASE_1"])
        if self.nivel >= 2: lista.extend(ALIMENTOS_DATA["FASE_2"])
        if self.nivel >= 3: lista.extend(ALIMENTOS_DATA["FASE_3"])

        # Adiciona as comidas prontas na loja para comprar
        lista.extend(self.itens_descobertos_loja)
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
        self.mensagens = f"PROMOÇÃO! Você agora é {novo_tit}!"
        self.atualizar_estoque_loja()

    def acao_combinar(self):
        if len(self.bancada) < 2:
            self.mensagens = "Coloque pelo menos 2 ingredientes!"
            return
        nomes_na_mesa = [item.nome for item in self.bancada]
        chave = tuple(sorted(nomes_na_mesa))

        if chave in RECEITAS:
            res = RECEITAS[chave]
            self.mensagens = f"SUCESSO: {res['nome']}!"

            # Ativa a Animação
            self.anim_nome = res['nome']
            nome_img = res.get("img", "")
            try:
                self.anim_img = pygame.transform.scale(
                    pygame.image.load(os.path.join("assets", nome_img)).convert_alpha(), (150, 150))
            except:
                self.anim_img = pygame.Surface((150, 150), pygame.SRCALPHA)
                pygame.draw.circle(self.anim_img, (255, 215, 0), (75, 75), 75)
            self.anim_estado = "FADE_IN"
            self.anim_alpha = 0
            self.anim_timer = 0

            # Lógica de Checklist e Loja
            if res['cat'] == "Principal": self.fez_principal = True
            if res['cat'] == "Sobremesa": self.fez_sobremesa = True
            if res['cat'] == "Bebida": self.fez_bebida = True

            if res['nome'] not in self.receitas_descobertas:
                self.receitas_descobertas[res['nome']] = ", ".join(nomes_na_mesa)
                self.dinheiro += 60

                # Adiciona o item pronto na loja custando um pouco a menos que os ingredientes
                custo_novo = sum(item.custo for item in self.bancada) - 1
                novo_ingrediente = (res['nome'], custo_novo, nome_img)
                self.itens_descobertos_loja.append(novo_ingrediente)
                self.atualizar_estoque_loja()

            self.verificar_evolucao()
        else:
            self.mensagens = "Não deu em nada..."
            self.dinheiro -= 10
        self.bancada = []

    def atualizar_animacao(self):
        if self.anim_estado == "FADE_IN":
            self.anim_alpha += 15
            if self.anim_alpha >= 255:
                self.anim_alpha = 255
                self.anim_estado = "WAIT"
        elif self.anim_estado == "WAIT":
            self.anim_timer += 1
            if self.anim_timer > 90:
                self.anim_estado = "FADE_OUT"
        elif self.anim_estado == "FADE_OUT":
            self.anim_alpha -= 15
            if self.anim_alpha <= 0:
                self.anim_alpha = 0
                self.anim_estado = None
                self.anim_img = None

    def desenhar_animacao(self, surface, fonte_animacao):
        if self.anim_estado and self.anim_img:
            img_animada = self.anim_img.copy()
            img_animada.set_alpha(self.anim_alpha)

            # Centraliza a animação na bancada
            rect = img_animada.get_rect(center=(415, 350))

            brilho = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(brilho, (255, 255, 200, min(100, self.anim_alpha)), (100, 100), 100)
            surface.blit(brilho, brilho.get_rect(center=rect.center))

            surface.blit(img_animada, rect)
            txt = fonte_animacao.render(self.anim_nome, True, (46, 139, 87))
            txt.set_alpha(self.anim_alpha)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.bottom + 10))