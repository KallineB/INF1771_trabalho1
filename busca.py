
import heapq

from config import custo_terreno

def get_vizinhos(mapa, posicao):
    linha, coluna = posicao

    total_linhas = len(mapa)
    total_colunas = len(mapa[0])
    vizinhos = []
    #cima
    if linha-1 >= 0:
        vizinhos.append((linha-1, coluna))
    #baixo
    if linha+1 < total_linhas:
        vizinhos.append((linha+1, coluna))
    #esquerda
    if coluna-1  >= 0:
        vizinhos.append((linha, coluna-1))
    #direita
    if coluna+1 < total_colunas:
        vizinhos.append((linha, coluna+1))
    return vizinhos

def custo_casa(simbolo):
    if simbolo in custo_terreno:
        return custo_terreno[simbolo]
    return 1

def distancia_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def remontar_caminho(veio_de, destino):
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = veio_de[atual]
    caminho.reverse()
    return caminho

def a_estrela(mapa, origem, destino):
    fronteira = [(distancia_manhattan(origem, destino), 0, origem)] # f, g, posicao
    custo_ate = {origem: 0}
    veio_de = {origem: None}
    visitados = set()

    while fronteira:
        f, g, atual = heapq.heappop(fronteira)

        if atual in visitados:
            continue
        visitados.add(atual)

        if atual == destino:
            break

        for vizinho in get_vizinhos(mapa, atual):
            linha, coluna = vizinho
            novo_g = g + custo_casa(mapa[linha][coluna])

            if vizinho not in custo_ate or novo_g < custo_ate[vizinho]:
                custo_ate[vizinho] = novo_g
                veio_de[vizinho] = atual
                novo_f = novo_g + distancia_manhattan(vizinho, destino)
                heapq.heappush(fronteira, (novo_f, novo_g, vizinho))

    caminho = remontar_caminho(veio_de, destino)

    casas_na_fronteira = set()
    for f, g, posicao in fronteira:
        if posicao not in visitados:
            casas_na_fronteira.add(posicao)

    return custo_ate[destino], caminho, visitados, casas_na_fronteira

def tabela_distancias(mapa, pontos):
    nomes = list(pontos)

    custos = {}
    caminhos = {}
    visitados = {}
    fronteiras = {}

    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            a = nomes[i]
            b = nomes[j]

            custo, caminho, casas_visitadas, casas_fronteira = a_estrela(mapa, pontos[a], pontos[b])

            #ida
            custos[(a, b)] = custo
            caminhos[(a, b)] = caminho
            visitados[(a, b)] = casas_visitadas
            fronteiras[(a, b)] = casas_fronteira

            #volta
            custos[(b, a)] = custo
            caminhos[(b, a)] = list(reversed(caminho))
            visitados[(b, a)] = casas_visitadas
            fronteiras[(b, a)] = casas_fronteira

    return custos, caminhos, visitados, fronteiras
