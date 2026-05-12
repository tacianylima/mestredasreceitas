import pygame
import sys
import os
from classes import Botao, ItemDraggable, Game

# --- INICIALIZAÇÃO E ÁUDIO ---
pygame.init()
pygame.mixer.init()

# TELA AUMENTADA PARA CABER NOMES LONGOS E MAIS ITENS
LARGURA, ALTURA = 1200, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mestre das Receitas")
relogio = pygame.time.Clock()

# Cores
BRANCO, PRETO = (255, 255, 255), (30, 30, 30)
VERDE_SUCCESS, AZUL_UI = (46, 139, 87), (70, 130, 180)
COR_BOTAO, OURO, VERMELHO = (100, 100, 100), (218, 165, 32), (200, 50, 50)


# --- CARREGADORES E CACHE ---
def carregar_fonte(nome_arquivo, tamanho, fallback):
    caminho = os.path.join("assets", nome_arquivo)
    try:
        return pygame.font.Font(caminho, tamanho)
    except:
        return pygame.font.SysFont(fallback, tamanho)


def carregar_som(nome_arquivo):
    caminho = os.path.join("assets", nome_arquivo)
    try:
        return pygame.mixer.Sound(caminho)
    except:
        return None


# Cache inteligente de imagens para não pesar o PC recarregando toda hora
cache_imagens = {}


def get_imagem_cache(nome_arquivo, tamanho):
    chave = (nome_arquivo, tamanho)
    if chave not in cache_imagens:
        try:
            img = pygame.transform.scale(pygame.image.load(os.path.join("assets", nome_arquivo)).convert_alpha(),
                                         tamanho)
        except:
            img = pygame.Surface(tamanho, pygame.SRCALPHA)
            pygame.draw.circle(img, (218, 165, 32), (tamanho[0] // 2, tamanho[1] // 2), tamanho[0] // 2)
        cache_imagens[chave] = img
    return cache_imagens[chave]


# Fontes
fonte_titulo = carregar_fonte("Sunny Spells.ttf", 115, "Arial")
fonte_livro = carregar_fonte("Youth Shandey.otf", 34, "Verdana")
fonte_texto = carregar_fonte("DynaPuff_Condensed-Regular.ttf", 26, "Arial")
fonte_hud = carregar_fonte("DynaPuff_Condensed-Regular.ttf", 20, "Arial")
fonte_mensagem = carregar_fonte("DynaPuff_Condensed-Regular.ttf", 36, "Arial")

# SFX
sfx_pegar = carregar_som("pickup.wav")
sfx_soltar = carregar_som("drop.wav")
sfx_combinar = carregar_som("combine.wav")
sfx_sucesso = carregar_som("success.wav")
sfx_erro = carregar_som("error.wav")
sfx_vitoria = carregar_som("victory.wav")  # Opcional: Um som de vitória!

musica_atual = ""


def tocar_musica(estado):
    global musica_atual
    if estado in ["MENU", "LIVRO", "INSTRUCOES", "CREDITOS"] and musica_atual != "MENU":
        musica_atual = "MENU"
        try:
            pygame.mixer.music.load(os.path.join("assets", "menu_bgm.mp3"))
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except:
            pass
    elif estado == "JOGANDO" and musica_atual != "JOGANDO":
        musica_atual = "JOGANDO"
        try:
            pygame.mixer.music.load(os.path.join("assets", "game_bgm.mp3"))
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
        except:
            pass
    elif estado == "VITORIA":
        pygame.mixer.music.stop()
        musica_atual = "VITORIA"


# --- INSTÂNCIAS E LAYOUT ---
game = Game()

# Centralizando elementos para a tela maior (1200 de largura)
btn_combinar = Botao("COMBINAR", 325, 710, 250, 60, VERDE_SUCCESS, "COMBINAR")

centro_x = LARGURA // 2
botoes_menu = [
    Botao("INICIAR", centro_x - 125, 280, 250, 55, AZUL_UI, "JOGANDO"),
    Botao("LIVRO DE RECEITAS", centro_x - 125, 360, 250, 55, OURO, "LIVRO"),
    Botao("INSTRUÇÕES", centro_x - 125, 440, 250, 55, COR_BOTAO, "INSTRUCOES"),
    Botao("CRÉDITOS", centro_x - 125, 520, 250, 55, COR_BOTAO, "CREDITOS"),
    Botao("SAIR", centro_x - 125, 600, 250, 55, VERMELHO, "SAIR")
]

btn_voltar_vitoria = Botao("VOLTAR AO MENU", centro_x - 150, 600, 300, 60, AZUL_UI, "MENU")

# Nova Área (Aumentada para caber imagens e textos grandes na loja)
rect_bancada = pygame.Rect(30, 140, 850, 630)
rect_loja = pygame.Rect(900, 140, 280, 630)
scroll_loja = 0
scroll_livro = 0

tocar_musica("MENU")

# --- LOOP PRINCIPAL ---
while True:
    tela.fill(BRANCO)
    eventos = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT: pygame.quit(); sys.exit()

        if evento.type == pygame.MOUSEWHEEL:
            if game.estado == "JOGANDO" and rect_loja.collidepoint(pygame.mouse.get_pos()):
                scroll_loja += evento.y * 30
                limite = min(0, 610 - (len(game.itens_loja) * 85))
                scroll_loja = max(limite, min(0, scroll_loja))
            elif game.estado == "LIVRO":
                scroll_livro += evento.y * 30
                limite = min(0, 550 - (len(game.receitas_descobertas) * 45))
                scroll_livro = max(limite, min(0, scroll_livro))

        # --- EVENTOS POR ESTADO ---
        if game.estado == "MENU":
            tocar_musica("MENU")
            for b in botoes_menu:
                a = b.clicou(evento)
                if a == "SAIR": pygame.quit(); sys.exit()
                if a: game.estado = a

        elif game.estado in ["INSTRUCOES", "LIVRO", "CREDITOS"]:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: game.estado = "MENU"

        elif game.estado == "VITORIA":
            tocar_musica("VITORIA")
            a = btn_voltar_vitoria.clicou(evento)
            if a == "MENU":
                game = Game()  # Reseta o jogo inteiro!
                scroll_loja = 0
                game.estado = "MENU"

        elif game.estado == "JOGANDO":
            tocar_musica("JOGANDO")

            # Condição de Vitória (Gatilho ativado no classes.py)
            if game.venceu:
                if sfx_vitoria: sfx_vitoria.play()
                game.estado = "VITORIA"
                continue

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE: game.estado = "MENU"

            if btn_combinar.clicou(evento) == "COMBINAR":
                if sfx_combinar: sfx_combinar.play()
                resultado = game.acao_combinar()
                if resultado == "SUCESSO" and sfx_sucesso:
                    sfx_sucesso.play()
                elif resultado == "ERRO" and sfx_erro:
                    sfx_erro.play()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Compras
                for i, (nome, custo, img) in enumerate(game.itens_loja):
                    y_pos = 150 + i * 85 + scroll_loja
                    r_item = pygame.Rect(910, y_pos, 260, 75)  # Retângulo maior
                    if r_item.collidepoint(evento.pos) and rect_loja.collidepoint(evento.pos) and evento.pos[1] > 140:
                        if game.dinheiro >= custo:
                            game.dinheiro -= custo
                            novo = ItemDraggable(nome, custo, evento.pos[0] - 30, evento.pos[1] - 30, img)
                            novo.dragging = True
                            game.bancada.append(novo)
                            game.item_selecionado = novo
                            if sfx_pegar: sfx_pegar.play()
                        else:
                            game.mensagens = "Saldo insuficiente!"

                # Arrastar
                if not game.item_selecionado:
                    for it in reversed(game.bancada):
                        if it.rect.collidepoint(evento.pos):
                            it.dragging = True
                            game.item_selecionado = it
                            game.bancada.remove(it)
                            game.bancada.append(it)
                            if sfx_pegar: sfx_pegar.play()
                            break

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if game.item_selecionado:
                    game.item_selecionado.dragging = False
                    if sfx_soltar: sfx_soltar.play()
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
        tela.blit(t_tit, (centro_x - t_tit.get_width() // 2, 80))
        for b in botoes_menu: b.desenhar(tela, fonte_texto)

        pygame.draw.rect(tela, (255, 255, 255, 200), (0, ALTURA - 50, LARGURA, 50))
        txt_cmds = fonte_hud.render(
            "CONTROLES: [MOUSE] Clicar e Arrastar  |  [SCROLL] Rolar Loja e Livro  |  [ESC] Voltar ao Menu", True,
            PRETO)
        tela.blit(txt_cmds, (centro_x - txt_cmds.get_width() // 2, ALTURA - 35))

    elif game.estado == "VITORIA":
        tela.fill((255, 248, 220))  # Fundo bege comemorativo

        t_vit = fonte_titulo.render("VOCE VENCEU!", True, OURO)
        tela.blit(t_vit, (centro_x - t_vit.get_width() // 2, 150))

        t_sub = fonte_mensagem.render("Parabéns! Você alcançou o título de Chef Mestre de Receitas!", True, PRETO)
        tela.blit(t_sub, (centro_x - t_sub.get_width() // 2, 350))

        btn_voltar_vitoria.desenhar(tela, fonte_texto)

    elif game.estado == "LIVRO":
        try:
            f_livro = pygame.transform.scale(pygame.image.load(os.path.join("assets", "fundo_livro.png")),
                                             (LARGURA, ALTURA))
            tela.blit(f_livro, (0, 0))
        except:
            tela.fill((245, 222, 179))

        t_liv = fonte_titulo.render("Descobertas", True, (60, 30, 0))
        tela.blit(t_liv, (centro_x - t_liv.get_width() // 2, 30))

        tela.set_clip(pygame.Rect(50, 150, 1100, 600))
        for i, (nome, ing) in enumerate(game.receitas_descobertas.items()):
            txt = fonte_livro.render(f"• {nome}: feito com {ing}", True, (80, 40, 10))
            tela.blit(txt, (80, 160 + i * 45 + scroll_livro))
        tela.set_clip(None)
        tela.blit(fonte_texto.render("ESC para voltar", True, PRETO), (50, ALTURA - 50))

    elif game.estado == "INSTRUCOES":
        tela.fill(BRANCO)
        t_inst = fonte_titulo.render("Como Jogar", True, PRETO)
        tela.blit(t_inst, (centro_x - t_inst.get_width() // 2, 50))
        inst = ["1. Use a rodinha do mouse para rolar a LOJA e o LIVRO.",
                "2. Arraste itens para o centro e clique COMBINAR.",
                "3. Para evoluir de fase, faça um Prato Principal, uma Sobremesa e uma Bebida.",
                "4. Arraste um item da bancada de volta para a loja para devolvê-lo.",
                "5. Cuidado para não ficar sem dinheiro!",
                "", "Pressione ESC para voltar."]
        for i, l in enumerate(inst):
            tela.blit(fonte_texto.render(l, True, PRETO), (100, 200 + i * 45))

    elif game.estado == "CREDITOS":
        tela.fill(BRANCO)
        t_cred = fonte_titulo.render("Creditos", True, PRETO)
        tela.blit(t_cred, (centro_x - t_cred.get_width() // 2, 50))
        cred = ["DESENVOLVIDO POR: Taciany Campos de Lima",
                "DISCIPLINA: Linguagem de Programação Aplicada",
                "FONTES: Sunny Spells, Youth Shandey, DynaPuff",
                "IMAGENS: Magnific: https://www.magnific.com/",
                "", "Pressione ESC para voltar."]
        for i, l in enumerate(cred):
            tela.blit(fonte_texto.render(l, True, PRETO), (100, 200 + i * 45))

    elif game.estado == "JOGANDO":
        # Cabeçalho maior e mais bonito
        pygame.draw.rect(tela, AZUL_UI, (0, 0, LARGURA, 130))

        tela.blit(fonte_texto.render(f"R$ {game.dinheiro}", True, OURO), (40, 20))
        tela.blit(fonte_hud.render(f"Cargo: {game.titulo}", True, BRANCO), (40, 70))


        def cor_c(v):
            return (0, 255, 0) if v else (180, 180, 180)


        tela.blit(fonte_hud.render("CHECKLIST DA FASE:", True, BRANCO), (550, 20))
        tela.blit(fonte_hud.render("Principal", True, cor_c(game.fez_principal)), (550, 55))
        tela.blit(fonte_hud.render("Sobremesa", True, cor_c(game.fez_sobremesa)), (700, 55))
        tela.blit(fonte_hud.render("Bebida", True, cor_c(game.fez_bebida)), (850, 55))

        # Mensagem com Sombra para destacar do fundo!
        cor_msg = VERDE_SUCCESS if "SUCESSO" in game.mensagens else (
            VERMELHO if "nada" in game.mensagens or "Errada" in game.mensagens else BRANCO)

        txt_sombra = fonte_mensagem.render(game.mensagens, True, PRETO)
        txt_m = fonte_mensagem.render(game.mensagens, True, cor_msg)

        pos_msg_x = centro_x - txt_m.get_width() // 2
        tela.blit(txt_sombra, (pos_msg_x + 2, 85 + 2))  # Desenha a sombra 2 pixels pro lado
        tela.blit(txt_m, (pos_msg_x, 85))  # Desenha o texto colorido em cima

        # Painéis
        pygame.draw.rect(tela, (235, 235, 235), rect_bancada, border_radius=15)
        pygame.draw.rect(tela, (210, 210, 210), rect_loja)

        btn_combinar.desenhar(tela, fonte_texto)
        for it in game.bancada: it.desenhar(tela, fonte_hud)

        game.atualizar_animacao()
        game.desenhar_animacao(tela, fonte_mensagem)

        # LOJA COM IMAGENS
        tela.set_clip(rect_loja)
        for i, (nome, custo, img_nome) in enumerate(game.itens_loja):
            bg_l = BRANCO if game.dinheiro >= custo else (255, 200, 200)
            y_pos = 150 + i * 85 + scroll_loja

            # Caixa do Item
            pygame.draw.rect(tela, bg_l, (910, y_pos, 260, 75), border_radius=8)

            # Imagem do Item
            icone = get_imagem_cache(img_nome, (55, 55))
            tela.blit(icone, (920, y_pos + 10))

            # Textos
            tela.blit(fonte_hud.render(nome, True, PRETO), (985, y_pos + 12))
            tela.blit(fonte_hud.render(f"R$ {custo}", True, VERDE_SUCCESS), (985, y_pos + 40))
        tela.set_clip(None)

    pygame.display.flip()
    relogio.tick(60)