import pygame
import sys
import os

# --- CONFIGURAÇÕES INICIAIS ---
pygame.init()
LARGURA, ALTURA = 900, 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mestre das Receitas - Edição Gourmet")
relogio = pygame.time.Clock()

# Cores
BRANCO = (255, 255, 255)
PRETO = (30, 30, 30)
VERDE_SUCCESS = (46, 139, 87)
AZUL_UI = (70, 130, 180)
COR_BOTAO = (100, 100, 100)
COR_HOVER = (150, 150, 150)
OURO = (218, 165, 32)

# Fontes
fonte_titulo = pygame.font.SysFont("Arial", 50, bold=True)
fonte_texto = pygame.font.SysFont("Arial", 24)
fonte_hud = pygame.font.SysFont("Arial", 20, bold=True)


# --- CLASSES (Aula 02) ---

class Botao:
    def __init__(self, texto, x, y, largura, altura, cor, acao):
        self.texto = texto
        self.rect = pygame.Rect(x, y, largura, altura)
        self.cor = cor
        self.acao = acao

    def desenhar(self, surface):
        pos_mouse = pygame.mouse.get_pos()
        cor_final = COR_HOVER if self.rect.collidepoint(pos_mouse) else self.cor

        pygame.draw.rect(surface, cor_final, self.rect, border_radius=12)
        txt = fonte_texto.render(self.texto, True, BRANCO)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def clicou(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return self.acao
        return None


class Alimento:
    def __init__(self, nome, custo, x, y, img_nome):
        self.nome = nome
        self.custo = custo
        # Caminho relativo
        caminho_img = os.path.join("assets", img_nome)
        try:
            self.image = pygame.image.load(caminho_img)
            self.image = pygame.transform.scale(self.image, (80, 80))
        except:
            # Fallback se a imagem não existir
            self.image = pygame.Surface((80, 80))
            self.image.fill((200, 100, 100))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.pos_inicial = (x, y)

    def desenhar(self, surface):
        surface.blit(self.image, self.rect)
        # Mostrar preço abaixo do item
        txt_preco = fonte_hud.render(f"R${self.custo}", True, PRETO)
        surface.blit(txt_preco, (self.rect.centerx - txt_preco.get_width() // 2, self.rect.bottom + 5))


# --- LÓGICA DO JOGO ---

# Banco de dados de combinações
# Usar nomes em ordem alfabética na tupla para evitar erro de ordem
RECEITAS = {
    tuple(sorted(["Pão", "Carne"])): "Hambúrguer",
    tuple(sorted(["Leite", "Trigo"])): "Massa",
    tuple(sorted(["Massa", "Tomate"])): "Pizza",
    tuple(sorted(["Batata", "Óleo"])): "Batata Frita",
    tuple(sorted(["Hambúrguer", "Queijo"])): "X-Cheeseburger"
}


class Jogo:
    def __init__(self):
        self.estado = "MENU"
        self.dinheiro = 150
        self.receitas_descobertas = []
        self.titulo_profissional = "Estagiário"
        self.mensagens = "Bem-vindo, Chef!"

        # Ingredientes básicos que o jogador pode "comprar" arrastando
        self.estoque = [
            Alimento("Pão", 5, 50, 550, "pao.png"),
            Alimento("Carne", 15, 150, 550, "carne.png"),
            Alimento("Leite", 8, 250, 550, "leite.png"),
            Alimento("Trigo", 5, 350, 550, "trigo.png"),
            Alimento("Tomate", 10, 450, 550, "tomate.png"),
            Alimento("Batata", 7, 550, 550, "batata.png"),
            Alimento("Óleo", 12, 650, 550, "oleo.png"),
            Alimento("Queijo", 10, 750, 550, "queijo.png")
        ]

        self.itens_na_bancada = []
        self.item_selecionado = None

    def atualizar_titulo(self):
        qtd = len(self.receitas_descobertas)
        if qtd >= 10:
            self.titulo_profissional = "Mestre das Receitas (VITÓRIA!)"
        elif qtd >= 6:
            self.titulo_profissional = "Chef"
        elif qtd >= 3:
            self.titulo_profissional = "Ajudante de Cozinha"

    def combinar_itens(self, item1, item2):
        if self.dinheiro < (item1.custo + item2.custo):
            self.mensagens = "Sem dinheiro para os ingredientes!"
            return

        self.dinheiro -= (item1.custo + item2.custo)
        par = tuple(sorted([item1.nome, item2.nome]))

        if par in RECEITAS:
            resultado = RECEITAS[par]
            self.mensagens = f"Sucesso! Criou: {resultado}"
            if resultado not in self.receitas_descobertas:
                self.receitas_descobertas.append(resultado)
                self.dinheiro += 20  # Bónus por descoberta
        else:
            self.mensagens = "Essa mistura não deu em nada..."

        self.atualizar_titulo()

    def desenhar_hud(self):
        pygame.draw.rect(tela, AZUL_UI, (0, 0, LARGURA, 100))
        txt_money = fonte_titulo.render(f"R$ {self.dinheiro}", True, OURO)
        txt_rank = fonte_hud.render(f"Cargo: {self.titulo_profissional}", True, BRANCO)
        txt_msg = fonte_hud.render(self.mensagens, True, BRANCO)

        tela.blit(txt_money, (20, 20))
        tela.blit(txt_rank, (LARGURA - 300, 20))
        tela.blit(txt_msg, (LARGURA // 2 - txt_msg.get_width() // 2, 70))

        # Área de compras (estoque)
        pygame.draw.rect(tela, (220, 220, 220), (0, 530, LARGURA, 170))
        txt_instrucao = fonte_hud.render("Arraste itens do estoque para a bancada para combinar!", True, PRETO)
        tela.blit(txt_instrucao, (LARGURA // 2 - txt_instrucao.get_width() // 2, 535))


# --- LOOP PRINCIPAL ---

jogo = Jogo()

# Botões do Menu
botoes_menu = [
    Botao("Iniciar Jogo", 350, 250, 200, 50, VERDE_SUCCESS, "JOGANDO"),
    Botao("Instruções", 350, 320, 200, 50, AZUL_UI, "INSTRUCOES"),
    Botao("Créditos", 350, 390, 200, 50, COR_BOTAO, "CREDITOS"),
    Botao("Sair", 350, 460, 200, 50, (180, 50, 50), "SAIR")
]

while True:
    tela.fill(BRANCO)
    eventos = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Tratamento de cliques por Estado
        if jogo.estado == "MENU":
            for btn in botoes_menu:
                nova_acao = btn.clicou(evento)
                if nova_acao:
                    if nova_acao == "SAIR": pygame.quit(); sys.exit()
                    jogo.estado = nova_acao

        elif jogo.estado in ["INSTRUCOES", "CREDITOS", "LIVRO"]:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                jogo.estado = "MENU"

        elif jogo.estado == "JOGANDO":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                jogo.estado = "MENU"

            # Lógica de Arrastar (Aula 04)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Tenta pegar do estoque para criar um novo item na bancada
                for ali in jogo.estoque:
                    if ali.rect.collidepoint(evento.pos):
                        novo = Alimento(ali.nome, ali.custo, ali.rect.x, ali.rect.y, "")  # Simplificado
                        novo.image = ali.image  # Copia imagem
                        novo.dragging = True
                        jogo.itens_na_bancada.append(novo)
                        jogo.item_selecionado = novo
                        break

                # Se não pegou no estoque, tenta mover o que já está na bancada
                if not jogo.item_selecionado:
                    for item in jogo.itens_na_bancada:
                        if item.rect.collidepoint(evento.pos):
                            item.dragging = True
                            jogo.item_selecionado = item
                            break

            if evento.type == pygame.MOUSEBUTTONUP:
                if jogo.item_selecionado:
                    jogo.item_selecionado.dragging = False
                    # Verifica se soltou em cima de outro para combinar
                    for outro in jogo.itens_na_bancada:
                        if outro != jogo.item_selecionado and jogo.item_selecionado.rect.colliderect(outro.rect):
                            jogo.combinar_itens(jogo.item_selecionado, outro)
                            jogo.itens_na_bancada.remove(jogo.item_selecionado)
                            jogo.itens_na_bancada.remove(outro)
                            break
                    jogo.item_selecionado = None

            if evento.type == pygame.MOUSEMOTION:
                if jogo.item_selecionado:
                    jogo.item_selecionado.rect.center = evento.pos

    # --- DESENHO DAS TELAS ---

    if jogo.estado == "MENU":
        txt_tit = fonte_titulo.render("MESTRE DAS RECEITAS", True, VERDE_SUCCESS)
        tela.blit(txt_tit, (LARGURA // 2 - txt_tit.get_width() // 2, 100))
        # Comandos obrigatórios no menu
        txt_cmds = fonte_hud.render("Comandos: Use o Mouse para Arrastar os ingredientes | ESC para Menu", True, PRETO)
        tela.blit(txt_cmds, (LARGURA // 2 - txt_cmds.get_width() // 2, 600))
        for btn in botoes_menu: btn.desenhar(tela)

    elif jogo.estado == "INSTRUCOES":
        tela.fill((240, 240, 240))
        instr = [
            "1. Arraste ingredientes do estoque (lateral) para a bancada.",
            "2. Solte um ingrediente sobre o outro para tentar uma receita.",
            "3. Cada tentativa consome dinheiro do seu orçamento.",
            "4. Descubra receitas novas para subir de cargo e ganhar bônus.",
            "5. Derrota: Se não puder mais comprar ingredientes ou R$ 0.",
            "6. Vitória: Tornar-se um Mestre (10 receitas descobertas).",
            "", "Pressione ESC para voltar"
        ]
        for i, linha in enumerate(instr):
            t = fonte_texto.render(linha, True, PRETO)
            tela.blit(t, (50, 100 + i * 40))

    elif jogo.estado == "CREDITOS":
        tela.fill(PRETO)
        cred = ["Desenvolvido por: Taciany Campos de Lima", "Disciplina: Linguagem de Programação Aplicada",
                "Professor: Jadson de Araujo Almeida", "Assets: Flaticon / OpenGameArt / Magnific em https://www.magnific.com/", "", "ESC para voltar"]
        for i, linha in enumerate(cred):
            t = fonte_texto.render(linha, True, BRANCO)
            tela.blit(t, (LARGURA // 2 - t.get_width() // 2, 200 + i * 50))

    elif jogo.estado == "JOGANDO":
        jogo.desenhar_hud()
        for ali in jogo.estoque: ali.desenhar(tela)
        for item in jogo.itens_na_bancada: item.desenhar(tela)

        # Condição de Derrota
        if jogo.dinheiro <= 0 and len(jogo.itens_na_bancada) < 2:
            txt_lose = fonte_titulo.render("FALÊNCIA! O CHEF TÁ POBRE.", True, (200, 0, 0))
            tela.blit(txt_lose, (LARGURA // 2 - txt_lose.get_width() // 2, ALTURA // 2))

    pygame.display.flip()
    relogio.tick(60)