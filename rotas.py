import heapq

from busca import custo_casa

QTD_GINASIOS_CHAVE = 16

def esta_no_conjunto(conjunto, i):
    return (conjunto & (1 << i)) != 0

def colocar_no_conjunto(conjunto, i):
    return conjunto | (1 << i)

def tirar_do_conjunto(conjunto, i):
    return conjunto & ~(1 << i)

def escolher_ginasios_chave(ginasios, custos, quantidade):
    pontos = ginasios + ['1', 'U']
    isolamento = {}

    for g in ginasios:
        distancias = []
        for outro in pontos:
            if outro != g:
                distancias.append(custos[(g, outro)])
        distancias.sort()
        isolamento[g] = distancias[0] + distancias[1]

    escolhidos = []
    for qtd in range(quantidade):
        mais_isolado = None
        for g in ginasios:
            if g in escolhidos:
                continue
            if mais_isolado is None or isolamento[g] > isolamento[mais_isolado]:
                mais_isolado = g
        escolhidos.append(mais_isolado)

    return escolhidos

def montar_tabela_heuristica(chave, custos):
    qtd_chaves = len(chave)
    total_grupos = 2 ** qtd_chaves

    tabela = []
    
    # Monta a tabela
    for a in range(total_grupos):
        tabela.append([0] * qtd_chaves)

    for grupo in range(total_grupos):
        for i in range(qtd_chaves):
            if esta_no_conjunto(grupo, i):
                continue

            if grupo == 0:
                tabela[grupo][i] = custos[(chave[i], 'U')]
                continue

            melhor = float('inf')
            for j in range(qtd_chaves):
                if esta_no_conjunto(grupo, j):
                    resto = tirar_do_conjunto(grupo, j)
                    custo = custos[(chave[i], chave[j])] + tabela[resto][j]
                    if custo < melhor:
                        melhor = custo
            tabela[grupo][i] = melhor

    return tabela

def calcular_heuristica(atual, visitados, chave, posicoes_chave, tabela, custos):
    faltam = 0
    for i in range(len(chave)):
        if not esta_no_conjunto(visitados, posicoes_chave[i]):
            faltam = colocar_no_conjunto(faltam, i)

    if faltam == 0:
        return custos[(atual, 'U')]

    melhor = float('inf')
    for j in range(len(chave)):
        if esta_no_conjunto(faltam, j):
            resto = tirar_do_conjunto(faltam, j)
            custo = custos[(atual, chave[j])] + tabela[resto][j]
            if custo < melhor:
                melhor = custo

    return melhor

def melhor_ordem(ginasios, custos):
    n = len(ginasios)
    todos = 2 ** n - 1

    chave = escolher_ginasios_chave(ginasios, custos, QTD_GINASIOS_CHAVE)
    tabela = montar_tabela_heuristica(chave, custos)

    posicoes_chave = []
    for g in chave:
        posicoes_chave.append(ginasios.index(g))

    custo_origem = custo_casa('1')
    inicio = ('1', 0)
    melhor_g = {inicio: custo_origem}
    anteriores = {inicio: None}
    h_inicio = calcular_heuristica('1', 0, chave, posicoes_chave, tabela, custos)
    
    fronteira = [(custo_origem + h_inicio, custo_origem, '1', 0)]
    expandidos = 0

    while fronteira:
        f, g, atual, visitados = heapq.heappop(fronteira)

        if atual == 'U':
            break

        if g > melhor_g.get((atual, visitados), float('inf')):
            continue

        expandidos += 1
        proximos = []
        
        if visitados == todos:
            proximos.append(('U', visitados))
        else:
            for i in range(n):
                if not esta_no_conjunto(visitados, i):
                    proximos.append((ginasios[i], colocar_no_conjunto(visitados, i)))

        for proximo, novos_visitados in proximos:
            novo_g = g + custos[(atual, proximo)]
            estado = (proximo, novos_visitados)

            if estado not in melhor_g or novo_g < melhor_g[estado]:
                melhor_g[estado] = novo_g
                anteriores[estado] = (atual, visitados)

                if proximo == 'U':
                    h = 0
                else:
                    h = calcular_heuristica(proximo, novos_visitados, chave, posicoes_chave, tabela, custos)

                heapq.heappush(fronteira, (novo_g + h, novo_g, proximo, novos_visitados))

    ordem = []
    estado = anteriores[('U', todos)]
    while estado is not None and estado[0] != '1':
        ordem.append(estado[0])
        estado = anteriores[estado]
    ordem.reverse()

    return ordem, melhor_g[('U', todos)], expandidos

def rota_completa(ordem, tabela_caminhos, tabela_visitados, tabela_fronteira):
    pontos = ['1'] + ordem + ['U']
    rota = []
    visitados_total = set()
    fronteira_total = set()

    for i in range(len(pontos) - 1):
        origem = pontos[i]
        destino = pontos[i + 1]
        
        trecho = tabela_caminhos[(origem, destino)]
        visitados_total.update(tabela_visitados[(origem, destino)])
        fronteira_total.update(tabela_fronteira[(origem, destino)])

        if i == 0:
            rota.extend(trecho)
        else:
            rota.extend(trecho[1:])

    return rota, visitados_total, fronteira_total