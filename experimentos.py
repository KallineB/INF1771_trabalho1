import random
import statistics
import time

from batalhas import hill_climbing, simulated_annealing, algoritmo_genetico, solucao_valida
from config import dificuldade_ginasios, pokemons

EXECUCOES = 30

def otimo_programacao_dinamica():
    nomes = list(pokemons)
    qtd = len(nomes)
    limites = []
    for nome in nomes:
        limites.append(pokemons[nome]['energia'])

    # cada estado é um número onde cada dígito (em base 'base') é quantas vezes um pokémon já lutou
    base = max(limites) + 1
    total_estados = base ** qtd

    # para cada estado, guarda quais pokémons já gastaram toda a energia
    esgotados = []
    for estado in range(total_estados):
        mascara = 0
        resto = estado
        for i in range(qtd):
            usos = resto % base
            resto = resto // base
            if usos >= limites[i]:
                mascara = mascara | (1 << i)
        esgotados.append(mascara)

    # todas as equipes possíveis num ginásio (qualquer grupo de pokémons, menos o vazio)
    equipes = []
    for mascara in range(1, 2 ** qtd):
        poder = 0
        incremento = 0
        for i in range(qtd):
            if mascara & (1 << i):
                poder += pokemons[nomes[i]]['poder']
                incremento += base ** i
        equipes.append((mascara, incremento, poder))

    infinito = float('inf')
    custos = [infinito] * total_estados
    custos[0] = 0

    for ginasio in dificuldade_ginasios:
        dificuldade = dificuldade_ginasios[ginasio]
        novos_custos = [infinito] * total_estados

        for estado in range(total_estados):
            custo_estado = custos[estado]
            if custo_estado == infinito:
                continue

            for mascara, incremento, poder in equipes:
                # só vale se nenhum pokémon da equipe já estiver sem energia
                if (mascara & esgotados[estado]) == 0:
                    novo_custo = custo_estado + dificuldade / poder
                    if novo_custo < novos_custos[estado + incremento]:
                        novos_custos[estado + incremento] = novo_custo

        custos = novos_custos

    # no final, pelo menos um pokémon precisa ainda ter energia
    todos = 2 ** qtd - 1
    melhor = infinito
    for estado in range(total_estados):
        if esgotados[estado] != todos and custos[estado] < melhor:
            melhor = custos[estado]

    return melhor

def rodar_bateria(nome, algoritmo, otimo, **parametros):
    custos = []
    melhor_custo = float('inf')
    melhor_solucao = None
    validas = 0
    acertos = 0

    inicio = time.time()
    for semente in range(EXECUCOES):
        # mesma semente para todos os algoritmos, assim o resultado se repete
        random.seed(semente)
        solucao, custo, energia = algoritmo(**parametros)
        custos.append(custo)

        if abs(custo - otimo) < 1e-6:
            acertos += 1

        if solucao_valida(solucao):
            validas += 1
            if custo < melhor_custo:
                melhor_custo = custo
                melhor_solucao = solucao
    tempo = time.time() - inicio

    media = statistics.mean(custos)
    desvio = statistics.stdev(custos)

    print(nome)
    print("  Melhor custo:        %.6f" % melhor_custo)
    print("  Média:               %.6f" % media)
    print("  Desvio-padrão:       %.6f" % desvio)
    print("  Execuções válidas:   %d de %d" % (validas, EXECUCOES))
    print("  Atingiu o ótimo:     %d de %d" % (acertos, EXECUCOES))
    print("  Tempo total:         %.6f s" % tempo)
    print("  Tempo por execução:  %.6f s" % (tempo / EXECUCOES))
    print()

    return melhor_solucao, melhor_custo, acertos, media

def escolher_parametros_sa(otimo):
    melhor_temp = None
    melhor_taxa = None
    melhor_acertos = -1
    melhor_media = float('inf')

    for temp_inicial in (1, 10, 100):
        for taxa in (0.999, 0.9995, 0.9998):
            nome = "SA com temperatura inicial %.6f e taxa %.6f" % (temp_inicial, taxa)
            solucao, custo, acertos, media = rodar_bateria(nome, simulated_annealing, otimo,
                                                           temp_inicial=temp_inicial,
                                                           taxa_resfriamento=taxa)

            # vale quem acerta o ótimo mais vezes, no empate quem tem a menor média
            if acertos > melhor_acertos or (acertos == melhor_acertos and media < melhor_media):
                melhor_temp = temp_inicial
                melhor_taxa = taxa
                melhor_acertos = acertos
                melhor_media = media

    return melhor_temp, melhor_taxa

def executar_experimentos():
    inicio = time.time()
    otimo = otimo_programacao_dinamica()
    print("Ótimo global (programação dinâmica): %.6f" % otimo)
    print("Tempo da programação dinâmica: %.6f s" % (time.time() - inicio))
    print()

    print("Teste de parâmetros do Simulated Annealing")
    print()
    temp_inicial, taxa = escolher_parametros_sa(otimo)
    print("Escolhidos: temperatura inicial %.6f e taxa %.6f" % (temp_inicial, taxa))
    print()

    print("Bateria oficial")
    print()
    rodar_bateria("Hill Climbing", hill_climbing, otimo)
    rodar_bateria("Simulated Annealing", simulated_annealing, otimo,
                  temp_inicial=temp_inicial, taxa_resfriamento=taxa)
    rodar_bateria("Algoritmo Genético", algoritmo_genetico, otimo)

if __name__ == "__main__":
    executar_experimentos()