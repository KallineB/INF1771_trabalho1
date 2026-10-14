from config import dificuldade_ginasios

def carregar_mapa(caminho_arquivo="mapa_2.txt"):
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()

    linhas = texto.strip().splitlines()
    mapa = [list(linha) for linha in linhas]
    return mapa

def achar_pontos(mapa):
    pontos = {}
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            terreno = mapa[i][j]
            if terreno == '1' or terreno == 'U' or terreno in dificuldade_ginasios:
                pontos[terreno] = (i, j)
    return pontos

def get_vizinhos(mapa, posicao):
    linha, coluna = posicao

    total_linhas = len(mapa)
    total_colunas = len(mapa[0])
    vizinhos = []
    # cima
    if linha-1 >= 0:
        vizinhos.append((linha-1, coluna))
    # baixo
    if linha+1 < total_linhas:
        vizinhos.append((linha+1, coluna))
    # esquerda
    if coluna-1  >= 0:
        vizinhos.append((linha, coluna-1))
    # direita
    if coluna+1 < total_colunas:
        vizinhos.append((linha, coluna+1))
    return vizinhos
