import pygame
import sys
import os
from classes import Botao, ItemDraggable, Game

# --- INICIALIZAÇÃO ---
pygame.init()
LARGURA, ALTURA = 1000, 750
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mestre das Receitas")
relogio = pygame.time.Clock()

# Cores
BRANCO, PRETO = (255, 255, 255), (30, 30, 30)
VERDE_SUCCESS, AZUL_UI = (46, 139, 87), (70, 130, 180)
COR_BOTAO, OURO, VERMELHO = (100, 100, 100), (218, 165, 32), (200, 50, 50)


# --- FONTES ---
def carregar_fonte(nome_arquivo, tamanho, fallback):
    caminho = os.path.join("assets", nome_arquivo)
    try:
        return pygame.font.Font(caminho, tamanho)
    except:
        return pygame.font.SysFont(fallback, tamanho)


# As fontes solicitadas
fonte_titulo = carregar_fonte("Sunny Spells.ttf", 115, "Arial")
fonte_livro = carregar_fonte("Youth Shandey.otf", 34, "Verdana")
fonte_texto = carregar_fonte("DynaPuff_Condensed-Regular.ttf", 26, "Arial")
fonte_hud = carregar_fonte("DynaPuff_Condensed-Regular.ttf", 20, "Arial")

game = Game()
btn_combinar = Botao("COMBINAR", 420, 550, 150, 50, VERDE_SUCCESS, "COMBINAR")

botoes_menu = [
    Botao("INICIAR", 375, 280, 250, 50, AZUL_UI, "JOGANDO"),
    Botao("LIVRO DE RECEITAS", 375, 350, 250, 50, OURO, "LIVRO"),
    Botao("INSTRUÇÕES", 375, 420, 250, 50, COR_BOTAO, "INSTRUCOES"),
    Botao("CRÉDITOS", 375, 490, 250, 50, COR_BOTAO, "CREDITOS"),
    Botao("SAIR", 375, 560, 250, 50, VERMELHO, "SAIR")
]

# Áreas e Scroll
rect_loja = pygame.Rect(810, 100, 190, 650)
rect_bancada = pygame.Rect(30, 110, 770, 610)
scroll_loja = 0
scroll_livro = 0

# --- LOOP PRINCIPAL ---
while True:
    tela.fill(BRANCO)
    eventos = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT: pygame.quit(); sys.exit()

        # EVENTO DE ROLAGEM (Scroll do Mouse)
        if evento.type == pygame.MOUSEWHEEL:
            if game.estado == "JOGANDO" and rect_loja.collidepoint(pygame.mouse.get_pos()):
                scroll_loja += evento.y * 30
                limite = min(0, 600 - (len(game.itens_loja) * 75))
                scroll_loja = max(limite, min(0, scroll_loja))
            elif game.estado == "LIVRO":
                scroll_livro += evento.y * 30
                limite = min(0, 500 - (len(game.receitas_descobertas) * 45))
                scroll_livro = max(limite, min(0, scroll_livro))

        if game.estado == "MENU":
            for b in botoes_menu:
                a = b.clicou(evento)
                if a == "SAIR": pygame.quit(); sys.exit()
                if a: game.estado = a

        elif game.estado in ["INSTRUCOES", "LIVRO", "CREDITOS"]:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: game.estado = "MENU"

        elif game.estado == "JOGANDO":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: game.estado = "MENU"
            if btn_combinar.clicou(evento) == "COMBINAR": game.acao_combinar()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Clicar para comprar na Loja (considerando o scroll)
                for i, (nome, custo, img) in enumerate(game.itens_loja):
                    y_pos = 110 + i * 75 + scroll_loja
                    r_item = pygame.Rect(820, y_pos, 170, 65)
                    if r_item.collidepoint(evento.pos):
                        # Limita a compra para não clicar enquanto o item está escondido no cabeçalho
                        if evento.pos[1] > 100:
                            if game.dinheiro >= custo:
                                game.dinheiro -= custo
                                novo = ItemDraggable(nome, custo, evento.pos[0] - 30, evento.pos[1] - 30, img)
                                novo.dragging = True
                                game.bancada.append(novo)
                                game.item_selecionado = novo
                            else:
                                game.mensagens = "Saldo insuficiente!"

                # Arrastar da bancada
                for it in reversed(game.bancada):
                    if it.rect.collidepoint(evento.pos):
                        it.dragging = True
                        game.item_selecionado = it
                        game.bancada.remove(it)
                        game.bancada.append(it)
                        break

            if evento.type == pygame.MOUSEBUTTONUP:
                if game.item_selecionado:
                    game.item_selecionado.dragging = False
                    # DEVOLVER: Soltar na área da loja devolve o dinheiro
                    if rect_loja.collidepoint(evento.pos):
                        game.dinheiro += game.item_selecionado.custo
                        game.bancada.remove(game.item_selecionado)
                        game.mensagens = f"{game.item_selecionado.nome} devolvido!"
                    game.item_selecionado = None

            if evento.type == pygame.MOUSEMOTION and game.item_selecionado:
                game.item_selecionado.rect.center = evento.pos

    # --- DESENHO ---
    if game.estado == "MENU":
        try:
            fundo = pygame.transform.scale(pygame.image.load(os.path.join("assets", "fundo_menu.png")),
                                           (LARGURA, ALTURA))
            tela.blit(fundo, (0, 0))
        except:
            tela.fill((230, 245, 230))

        t_tit = fonte_titulo.render("Mestre das Receitas", True, PRETO)
        tela.blit(t_tit, (LARGURA // 2 - t_tit.get_width() // 2, 80))
        for b in botoes_menu: b.desenhar(tela, fonte_texto)

    elif game.estado == "LIVRO":
        try:
            f_livro = pygame.transform.scale(pygame.image.load(os.path.join("assets", "fundo_livro.png")),
                                             (LARGURA, ALTURA))
            tela.blit(f_livro, (0, 0))
        except:
            tela.fill((245, 222, 179))

        t_liv = fonte_titulo.render("Descobertas", True, (60, 30, 0))
        tela.blit(t_liv, (LARGURA // 2 - t_liv.get_width() // 2, 20))

        # O set_clip cria uma máscara para a rolagem não invadir o título
        tela.set_clip(pygame.Rect(50, 150, 900, 550))
        for i, (nome, ing) in enumerate(game.receitas_descobertas.items()):
            txt = fonte_livro.render(f"• {nome}: feito com {ing}", True, (80, 40, 10))
            tela.blit(txt, (80, 160 + i * 45 + scroll_livro))
        tela.set_clip(None)

        tela.blit(fonte_texto.render("ESC para voltar", True, PRETO), (50, ALTURA - 50))

    elif game.estado == "INSTRUCOES":
        tela.fill(BRANCO)
        t_inst = fonte_titulo.render("Como Jogar", True, PRETO)
        tela.blit(t_inst, (LARGURA // 2 - t_inst.get_width() // 2, 50))
        inst = ["1. Use a rodinha do mouse para rolar a LOJA e o LIVRO.",
                "2. Arraste itens para o centro e clique COMBINAR.",
                "3. Para evoluir de fase, faça um Prato Principal, uma Sobremesa e uma Bebida.",
                "4. Arraste um item da bancada de volta para a loja para devolvê-lo.",
                "5. Cuidado para não ficar sem dinheiro!"
                "", "Pressione ESC para voltar."]
        for i, l in enumerate(inst):
            tela.blit(fonte_texto.render(l, True, PRETO), (100, 200 + i * 45))

    elif game.estado == "CREDITOS":
        tela.fill(BRANCO)
        t_cred = fonte_titulo.render("Creditos", True, PRETO)
        tela.blit(t_cred, (LARGURA // 2 - t_cred.get_width() // 2, 50))
        cred = ["DESENVOLVIDO POR: Taciany Campos de Lima",
                "DISCIPLINA: Linguagem de Programação Aplicada",
                "FONTES: Sunny Spells, Youth Shandey, DynaPuff",
                "IMAGENS: Magnific: https://www.magnific.com/",
                "", "Pressione ESC para voltar."]
        for i, l in enumerate(cred):
            tela.blit(fonte_texto.render(l, True, PRETO), (100, 200 + i * 45))

    elif game.estado == "JOGANDO":
        pygame.draw.rect(tela, AZUL_UI, (0, 0, LARGURA, 100))

        tela.blit(fonte_texto.render(f"R$ {game.dinheiro}", True, OURO), (30, 15))
        tela.blit(fonte_hud.render(f"Cargo: {game.titulo}", True, BRANCO), (30, 60))


        def cor_c(v):
            return (0, 255, 0) if v else (180, 180, 180)


        tela.blit(fonte_hud.render("CHECKLIST DA FASE:", True, BRANCO), (450, 15))
        tela.blit(fonte_hud.render("Principal", True, cor_c(game.fez_principal)), (450, 50))
        tela.blit(fonte_hud.render("Sobremesa", True, cor_c(game.fez_sobremesa)), (600, 50))
        tela.blit(fonte_hud.render("Bebida", True, cor_c(game.fez_bebida)), (750, 50))

        txt_m = fonte_hud.render(game.mensagens, True, BRANCO)
        tela.blit(txt_m, (LARGURA // 2 - txt_m.get_width() // 2, 70))

        pygame.draw.rect(tela, (235, 235, 235), rect_bancada, border_radius=15)
        pygame.draw.rect(tela, (210, 210, 210), rect_loja)

        btn_combinar.desenhar(tela, fonte_texto)
        for it in game.bancada: it.desenhar(tela, fonte_hud)

        # Atualiza a animação por cima da mesa, mas não por cima da loja
        game.atualizar_animacao()
        game.desenhar_animacao(tela, fonte_texto)

        # Painel da Loja com Scroll e Corte (set_clip)
        tela.set_clip(rect_loja)
        for i, (nome, custo, img) in enumerate(game.itens_loja):
            bg_l = BRANCO if game.dinheiro >= custo else (255, 200, 200)
            y_pos = 110 + i * 75 + scroll_loja
            pygame.draw.rect(tela, bg_l, (820, y_pos, 170, 65), border_radius=5)
            tela.blit(fonte_hud.render(nome, True, PRETO), (830, y_pos + 10))
            tela.blit(fonte_hud.render(f"R$ {custo}", True, VERDE_SUCCESS), (830, y_pos + 35))
        tela.set_clip(None)

    pygame.display.flip()
    relogio.tick(60)