import pygame
import sys

CORES = {
    'M': (139, 69, 19),
    'A': (30, 144, 255),
    'F': (34, 139, 34),
    'R': (169, 169, 169),
    '.': (245, 245, 220),
    '1': (255, 215, 0),
    'U': (148, 0, 211),
    'AGENTE': (0, 0, 0),
    'RASTRO': (255, 0, 0),
    'VISITADO': (200, 220, 200),  
    'FRONTEIRA': (255, 255, 150)  
}

def obter_cor(celula):
    if celula in CORES:
        return CORES[celula]
    return (255, 69, 0) # Ginásios

def iniciar_app(mapa, funcao_ia, fps=60, tamanho_celula=8):
    pygame.init()
    linhas = len(mapa)
    colunas = len(mapa[0])
    
    largura_mapa = colunas * tamanho_celula
    altura_mapa = linhas * tamanho_celula
    altura_painel = 200 
    
    tela = pygame.display.set_mode((largura_mapa, altura_mapa + altura_painel))
    pygame.display.set_caption("Busca Heurística - Pokémon Kanto")
    relogio = pygame.time.Clock()
    
    fonte = pygame.font.SysFont("Arial", 16)
    fonte_titulo = pygame.font.SysFont("Arial", 20, bold=True)
    
    estado = "AGUARDANDO" 
    dados_ia = None
    passo_atual = 0
    
    painel_y = altura_mapa
    botao_rect = pygame.Rect(largura_mapa - 240, painel_y + 30, 220, 50)
    
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if botao_rect.collidepoint(evento.pos):
                    if estado == "AGUARDANDO":
                        estado = "CALCULANDO"
                    elif estado == "ANIMANDO":
                        estado = "PAUSADO"
                    elif estado == "PAUSADO":
                        estado = "ANIMANDO"
                    elif estado == "FINALIZADO":
                        estado = "AGUARDANDO"
                        dados_ia = None
                        passo_atual = 0
                
        tela.fill((20, 20, 20)) # fundo da tela principal
        
        # monta o mapa e estados da Busca
        for i in range(linhas):
            for j in range(colunas):
                cor = obter_cor(mapa[i][j])
                
                if dados_ia and mapa[i][j] not in ['1', 'U', 'M', 'A', 'F'] and mapa[i][j] not in "23456789BCDEGHIJKLNOPQST":
                    if (i, j) in dados_ia["visitados"]:
                        cor = CORES['VISITADO']
                    elif (i, j) in dados_ia["fronteira"]:
                        cor = CORES['FRONTEIRA']
                
                rect = (j * tamanho_celula, i * tamanho_celula, tamanho_celula, tamanho_celula)
                pygame.draw.rect(tela, cor, rect)

        pygame.draw.rect(tela, (30, 30, 30), (0, painel_y, largura_mapa, altura_painel))
        pygame.draw.line(tela, (100, 100, 100), (0, painel_y), (largura_mapa, painel_y), 2)
        
        cor_botao = (100, 100, 100)
        texto_botao = ""
        
        if estado == "AGUARDANDO":
            texto_botao = "INICIAR"
            cor_botao = (34, 139, 34) # Verde
            texto = fonte_titulo.render("Busca Heurística - Pokémon Kanto. Clique em INICIAR", True, (255, 255, 255))
            tela.blit(texto, (20, painel_y + 30))
            
        elif estado == "CALCULANDO":
            texto_botao = "AGUARDE..."
            cor_botao = (169, 169, 169) # Cinza
            texto = fonte_titulo.render("Calculando rotas e batalhas...", True, (255, 255, 0))
            tela.blit(texto, (20, painel_y + 30))
            texto_sub = fonte.render("Verifique o progresso no console.", True, (200, 200, 200))
            tela.blit(texto_sub, (20, painel_y + 60))
            
        elif estado in ["ANIMANDO", "PAUSADO", "FINALIZADO"]:
            if estado == "ANIMANDO":
                texto_botao = "PAUSAR"
                cor_botao = (200, 50, 50) # vermelho
            elif estado == "PAUSADO":
                texto_botao = "RETOMAR"
                cor_botao = (255, 140, 0) # laranja
                
            for i in range(passo_atual):
                linha, coluna = dados_ia["rota"][i]
                x_centro = coluna * tamanho_celula + tamanho_celula // 2
                y_centro = linha * tamanho_celula + tamanho_celula // 2
                pygame.draw.circle(tela, CORES['RASTRO'], (x_centro, y_centro), max(1, tamanho_celula // 3))
            
            # mover e desenhar Agente
            if passo_atual < len(dados_ia["rota"]):
                linha_ag, coluna_ag = dados_ia["rota"][passo_atual]
                if estado == "ANIMANDO":
                    passo_atual += 1
            else:
                linha_ag, coluna_ag = dados_ia["rota"][-1]
                estado = "FINALIZADO"
                texto_botao = "VOLTAR AO INÍCIO"
                cor_botao = (30, 144, 255) # Azul
                
            x_ag = coluna_ag * tamanho_celula + tamanho_celula // 2
            y_ag = linha_ag * tamanho_celula + tamanho_celula // 2
            pygame.draw.circle(tela, CORES['AGENTE'], (x_ag, y_ag), max(2, tamanho_celula // 2))
            
            # mostra resultados
            y_offset = painel_y + 15
            linhas_texto_col1 = [
                ("RESULTADOS FINAIS", (0, 255, 0), fonte_titulo),
                (f"Melhor Algoritmo: {dados_ia['melhor_algoritmo']}", (200, 255, 255), fonte),
                (f"Custo Total: {round(dados_ia['custo_total'], 3)} min", (255, 255, 255), fonte),
                (f"Custo Rotas: {dados_ia['custo_rota']} min", (255, 255, 255), fonte),
                (f"Custo Batalhas: {round(dados_ia['custo_batalhas'], 3)} min", (255, 255, 255), fonte),
                (f"Nós Expandidos (A*): {dados_ia['expandidos']}", (255, 255, 0), fonte_titulo),
                (f"Passos no mapa: {len(dados_ia['rota']) - 1}", (255, 255, 255), fonte)
            ]
            
            for txt, cor, font_obj in linhas_texto_col1:
                surface = font_obj.render(txt, True, cor)
                tela.blit(surface, (20, y_offset))
                y_offset += 25

            y_offset2 = painel_y + 15
            tela.blit(fonte_titulo.render("Energia Final dos Pokémon:", True, (200, 200, 200)), (400, y_offset2))
            y_offset2 += 30
            
            for pk, en in dados_ia['energia'].items():
                texto_energia = fonte.render(f" - {pk}: {en} pts", True, (255, 255, 255))
                tela.blit(texto_energia, (400, y_offset2))
                y_offset2 += 25

        
        pygame.draw.rect(tela, cor_botao, botao_rect, border_radius=5)
        superficie_texto = fonte_titulo.render(texto_botao, True, (255, 255, 255))
        rect_texto = superficie_texto.get_rect(center=botao_rect.center)
        tela.blit(superficie_texto, rect_texto)

        pygame.display.flip()
        
        
        if estado == "CALCULANDO" and dados_ia is None:
            dados_ia = funcao_ia(mapa)
            estado = "ANIMANDO"

        relogio.tick(fps)
        
    pygame.quit()