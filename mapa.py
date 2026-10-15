from config import dificuldade_ginasios

def carregar_mapa(caminho_arquivo="mapa.txt"):
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
