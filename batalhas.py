import math
import random

from config import dificuldade_ginasios, pokemons

PENALIDADE = 1000

def tempo_batalha(ginasio, equipe):
    poder_total = 0
    for pokemon in equipe:
        poder_total += pokemons[pokemon]['poder']
    return dificuldade_ginasios[ginasio] / poder_total

def energia_final(solucao):
    energia = {}
    for pokemon in pokemons:
        energia[pokemon] = pokemons[pokemon]['energia']

    for ginasio in solucao:
        for pokemon in solucao[ginasio]:
            energia[pokemon] -= 1

    return energia

def custo_solucao(solucao):
    custo = 0
    for ginasio in solucao:
        custo += tempo_batalha(ginasio, solucao[ginasio])

    energia = energia_final(solucao)
    for pokemon in energia:
        if energia[pokemon] < 0:
            custo += PENALIDADE * -energia[pokemon]

    if max(energia.values()) < 1:
        custo += PENALIDADE

    return custo

def solucao_valida(solucao):
    for ginasio in dificuldade_ginasios:
        if ginasio not in solucao or len(solucao[ginasio]) == 0:
            return False
        if len(solucao[ginasio]) != len(set(solucao[ginasio])):
            return False

    energia = energia_final(solucao)
    return min(energia.values()) >= 0 and max(energia.values()) >= 1

def copiar_solucao(solucao):
    copia = {}
    for ginasio in solucao:
        copia[ginasio] = list(solucao[ginasio])
    return copia

def gerar_solucao_inicial():
    ginasios = list(dificuldade_ginasios)
    random.shuffle(ginasios)
    nomes = list(pokemons)
    random.shuffle(nomes)

    # rodizio: o pokemon da vez luta no ginasio, e volta ao primeiro depois do ultimo
    solucao = {}
    for i in range(len(ginasios)):
        solucao[ginasios[i]] = [nomes[i % len(nomes)]]

    return solucao

def gerar_vizinho(solucao):
    vizinho = copiar_solucao(solucao)

    ginasio, outro_ginasio = random.sample(list(vizinho), 2)
    equipe = vizinho[ginasio]
    outra_equipe = vizinho[outro_ginasio]

    fora = []
    for pokemon in pokemons:
        if pokemon not in equipe:
            fora.append(pokemon)

    operador = random.choice(['adicionar', 'remover', 'trocar', 'trocar_entre', 'mover'])

    # se o operador nao puder ser aplicado, o vizinho fica igual a solucao atual
    if operador == 'adicionar':
        if fora:
            equipe.append(random.choice(fora))

    elif operador == 'remover':
        if len(equipe) > 1:
            equipe.remove(random.choice(equipe))

    elif operador == 'trocar':
        if fora:
            equipe.remove(random.choice(equipe))
            equipe.append(random.choice(fora))

    elif operador == 'trocar_entre':
        p1 = random.choice(equipe)
        p2 = random.choice(outra_equipe)
        if p2 not in equipe and p1 not in outra_equipe:
            equipe[equipe.index(p1)] = p2
            outra_equipe[outra_equipe.index(p2)] = p1

    elif operador == 'mover':
        p = random.choice(equipe)
        if len(equipe) > 1 and p not in outra_equipe:
            equipe.remove(p)
            outra_equipe.append(p)

    return vizinho

def hill_climbing(iteracoes=20000):
    atual = gerar_solucao_inicial()
    custo_atual = custo_solucao(atual)

    for i in range(iteracoes):
        vizinho = gerar_vizinho(atual)
        custo_vizinho = custo_solucao(vizinho)

        # so aceita se melhorar
        if custo_vizinho < custo_atual:
            atual = vizinho
            custo_atual = custo_vizinho

    return atual, custo_atual, energia_final(atual)

def simulated_annealing(temp_inicial=10, taxa_resfriamento=0.999, iteracoes=20000):
    atual = gerar_solucao_inicial()
    custo_atual = custo_solucao(atual)

    melhor = atual
    custo_melhor = custo_atual
    temperatura = temp_inicial

    for i in range(iteracoes):
        vizinho = gerar_vizinho(atual)
        custo_vizinho = custo_solucao(vizinho)
        diferenca = custo_vizinho - custo_atual

        # melhora sempre aceita, piora aceita com chance que diminui com a temperatura
        if diferenca <= 0 or random.random() < math.exp(-diferenca / temperatura):
            atual = vizinho
            custo_atual = custo_vizinho

            if custo_atual < custo_melhor:
                melhor = atual
                custo_melhor = custo_atual

        temperatura = temperatura * taxa_resfriamento

    return melhor, custo_melhor, energia_final(melhor)

def torneio(populacao, custos, tamanho=3):
    sorteados = random.sample(range(len(populacao)), tamanho)

    vencedor = sorteados[0]
    for i in sorteados:
        if custos[i] < custos[vencedor]:
            vencedor = i

    return populacao[vencedor]

def cruzamento(pai1, pai2):
    filho = {}
    for ginasio in pai1:
        # cada ginásio vem inteiro de um dos pais
        if random.random() < 0.5:
            filho[ginasio] = list(pai1[ginasio])
        else:
            filho[ginasio] = list(pai2[ginasio])
    return filho

def algoritmo_genetico(tamanho_populacao=100, geracoes=600, taxa_mutacao=0.9):
    populacao = []
    for i in range(tamanho_populacao):
        populacao.append(gerar_solucao_inicial())

    for geracao in range(geracoes):
        custos = []
        for individuo in populacao:
            custos.append(custo_solucao(individuo))

        ranking = []
        for i in range(len(populacao)):
            ranking.append((custos[i], i))
        ranking.sort()

        # elitismo: os 2 melhores passam direto
        nova_populacao = [populacao[ranking[0][1]], populacao[ranking[1][1]]]

        while len(nova_populacao) < tamanho_populacao:
            pai1 = torneio(populacao, custos)
            pai2 = torneio(populacao, custos)
            filho = cruzamento(pai1, pai2)

            if random.random() < taxa_mutacao:
                filho = gerar_vizinho(filho)

            nova_populacao.append(filho)

        populacao = nova_populacao

    # a última geração ainda não foi avaliada
    melhor = populacao[0]
    custo_melhor = custo_solucao(melhor)
    for individuo in populacao:
        custo = custo_solucao(individuo)
        if custo < custo_melhor:
            melhor = individuo
            custo_melhor = custo

    return melhor, custo_melhor, energia_final(melhor)