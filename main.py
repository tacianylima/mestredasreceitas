import pygame
import sys
import os
from classes import Botao, ItemDraggable, Game

# --- CONFIGURAÇÕES INICIAIS ---
pygame.init()
LARGURA, ALTURA = 1000, 750
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mestre das Receitas")
relogio = pygame.time.Clock()

# --- CORES ---
BRANCO, PRETO = (255, 255, 255), (30, 30, 30)
VERDE_SUCCESS, AZUL_UI = (46, 139, 87), (70, 130, 180)
COR_BOTAO, OURO, VERMELHO = (100, 100, 100), (218, 165, 32), (200, 50, 50)


# --- SISTEMA DE FONTES CUSTOMIZADAS ---
def carregar_fonte(nome_arquivo, tamanho, fallback):
    caminho = os.path.join("assets", nome_arquivo)
    try:
        return pygame.font.Font(caminho, tamanho)
    except:
        print(f"Aviso: A fonte {nome_arquivo} não foi encontrada. Usando {fallback}.")
        return pygame.font.SysFont(fallback, tamanho)


# Carregando as fontes com tamanhos adequados
fonte_titulo = carregar_fonte("BungeeSpice-Regular.ttf", 50, "Arial")
fonte_livro = carregar_fonte("Sacramento-Regular.ttf", 38, "Verdana")  # Maior pq é cursiva
fonte_texto = carregar_fonte("EBGaramond-Regular.ttf", 26, "Arial")
fonte_hud = carregar_fonte("EBGaramond-Regular.ttf", 22, "Arial")

# --- INSTÂNCIAS ---
game = Game()
btn_combinar = Botao("COMBINAR", 420, 520, 150, 50, VERDE_SUCCESS, "COMBINAR")
botoes_menu = [
    Botao("INICIAR", 400, 300, 200, 50, AZUL_UI, "JOGANDO"),
    Botao("LIVRO DE RECEITAS", 400, 370, 200, 50, OURO, "LIVRO"),
    Botao("INSTRUÇÕES", 400, 440, 200, 50, COR_BOTAO, "INSTRUCOES"),
    Botao("CRÉDITOS", 400, 510, 200, 50, COR_BOTAO, "CREDITOS"),
    Botao("SAIR", 400, 580, 200, 50, VERMELHO, "SAIR")
]

# --- LOOP PRINCIPAL ---
while True:
    tela.fill(BRANCO)
    eventos = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT: pygame.quit(); sys.exit()

        if game.estado == "MENU":
            for b in botoes_menu:
                a = b.clicou(evento)
                if a == "SAIR": pygame.quit(); sys.exit()
                if a: game.estado = a

        elif game.estado in ["INSTRUCOES", "CREDITOS", "LIVRO"]:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                game.estado = "MENU"

        elif game.estado == "JOGANDO":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: game.estado = "MENU"
            if btn_combinar.clicou(evento) == "COMBINAR": game.acao_combinar()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Compras na loja
                for i, (nome, custo, img) in enumerate(game.itens_loja):
                    if pygame.Rect(820, 110 + i * 70, 170, 60).collidepoint(evento.pos):
                        if game.dinheiro >= custo:
                            game.dinheiro -= custo
                            novo = ItemDraggable(nome, custo, evento.pos[0] - 30, evento.pos[1] - 30, img)
                            novo.dragging = True
                            game.bancada.append(novo)
                            game.item_selecionado = novo
                        else:
                            game.mensagens = "Saldo insuficiente!"

                # Arrastar itens da bancada
                for it in game.bancada:
                    if it.rect.collidepoint(evento.pos):
                        it.dragging = True
                        game.item_selecionado = it

            if evento.type == pygame.MOUSEBUTTONUP:
                if game.item_selecionado:
                    game.item_selecionado.dragging = False
                    game.item_selecionado = None

            if evento.type == pygame.MOUSEMOTION and game.item_selecionado:
                game.item_selecionado.rect.center = evento.pos

    # --- DESENHO DAS TELAS ---
    if game.estado == "MENU":
        try:
            fundo = pygame.transform.scale(pygame.image.load(os.path.join("assets", "fundo_menu.png")),
                                           (LARGURA, ALTURA))
            tela.blit(fundo, (0, 0))
        except:
            tela.fill((220, 240, 220))  # Cor de fundo verde clara caso falte a imagem

        # Desenha o Título usando BungeeSpice
        t_tit = fonte_titulo.render("MESTRE DAS RECEITAS", True, PRETO)
        tela.blit(t_tit, (LARGURA // 2 - t_tit.get_width() // 2, 100))

        # Desenha os botões usando EBGaramond
        for b in botoes_menu: b.desenhar(tela, fonte_hud)

    elif game.estado == "LIVRO":
        try:
            f_livro = pygame.transform.scale(pygame.image.load(os.path.join("assets", "fundo_livro.png")),
                                             (LARGURA, ALTURA))
            tela.blit(f_livro, (0, 0))
        except:
            tela.fill((245, 222, 179))

        # Título do livro usando BungeeSpice
        tela.blit(fonte_titulo.render("SUAS DESCOBERTAS", True, (60, 30, 0)), (50, 40))

        # Desenhando as receitas com a fonte Sacramento (cursiva)
        for i, (nome, ing) in enumerate(game.receitas_descobertas.items()):
            txt = fonte_livro.render(f"{nome}: feito com {ing}", True, (80, 40, 10))
            tela.blit(txt, (70, 130 + i * 35))

        tela.blit(fonte_texto.render("ESC para voltar ao menu", True, PRETO), (50, ALTURA - 50))

    elif game.estado == "INSTRUCOES":
        tela.fill(BRANCO)
        tela.blit(fonte_titulo.render("COMO JOGAR", True, PRETO), (100, 50))
        inst = ["1. Compre itens na LOJA (Direita) usando seu orçamento.",
                "2. Arraste-os para o centro e clique COMBINAR.",
                "3. Para evoluir de fase, faça 1 Principal, 1 Sobremesa e 1 Bebida.",
                "4. Se o dinheiro acabar, você vai à falência!",
                "", "Pressione ESC para voltar."]
        for i, l in enumerate(inst): tela.blit(fonte_texto.render(l, True, PRETO), (100, 150 + i * 40))

    elif game.estado == "CREDITOS":
        tela.fill(BRANCO)
        tela.blit(fonte_titulo.render("CRÉDITOS", True, PRETO), (LARGURA // 2 - 100, 80))
        cred = ["DESENVOLVIDO POR: Taciany Campos de Lima",
                "DISCIPLINA: Linguagem de Programação Aplicada",
                "PROFESSOR: Jadson de Araujo Almeida",
                "FONTES: Bungee Spice, Sacramento, EB Garamond",
                "", "Pressione ESC para voltar."]
        for i, l in enumerate(cred):
            txt_cred = fonte_texto.render(l, True, PRETO)
            tela.blit(txt_cred, (LARGURA // 2 - txt_cred.get_width() // 2, 180 + i * 50))

    elif game.estado == "JOGANDO":
        # Barra de Status Superior
        pygame.draw.rect(tela, AZUL_UI, (0, 0, LARGURA, 100))
        tela.blit(fonte_titulo.render(f"R$ {game.dinheiro}", True, OURO), (20, 15))
        tela.blit(fonte_hud.render(f"Cargo: {game.titulo}", True, BRANCO), (230, 20))


        # Lógica de cores do checklist
        def cor_c(v):
            return (0, 255, 0) if v else (180, 180, 180)


        tela.blit(fonte_hud.render("MENU DA FASE:", True, BRANCO), (550, 10))
        tela.blit(fonte_hud.render("- Principal", True, cor_c(game.fez_principal)), (550, 35))
        tela.blit(fonte_hud.render("- Sobremesa", True, cor_c(game.fez_sobremesa)), (710, 35))
        tela.blit(fonte_hud.render("- Bebida", True, cor_c(game.fez_bebida)), (870, 35))

        # Mensagens do sistema no centro
        txt_m = fonte_hud.render(game.mensagens, True, BRANCO)
        tela.blit(txt_m, (LARGURA // 2 - txt_m.get_width() // 2, 70))

        # Mesa de Preparo
        pygame.draw.rect(tela, (235, 235, 235), (30, 110, 770, 610), border_radius=15)
        btn_combinar.desenhar(tela, fonte_hud)
        for it in game.bancada: it.desenhar(tela, fonte_hud)

        # Painel da Loja
        pygame.draw.rect(tela, (210, 210, 210), (810, 100, 190, 650))
        for i, (nome, custo, img) in enumerate(game.itens_loja):
            # Se não tem dinheiro, pinta o card da loja de vermelho clarinho
            bg_loja = BRANCO if game.dinheiro >= custo else (255, 200, 200)
            pygame.draw.rect(tela, bg_loja, (820, 110 + i * 70, 170, 60), border_radius=5)
            tela.blit(fonte_hud.render(nome, True, PRETO), (830, 115 + i * 70))
            tela.blit(fonte_hud.render(f"R$ {custo}", True, VERDE_SUCCESS), (830, 135 + i * 70))

    pygame.display.flip()
    relogio.tick(60)