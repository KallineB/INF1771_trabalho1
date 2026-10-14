import random
import statistics
from interface import iniciar_app
from mapa import carregar_mapa, achar_pontos
from config import dificuldade_ginasios
from busca import tabela_distancias
from rotas import melhor_ordem, rota_completa
from batalhas import hill_climbing, simulated_annealing, algoritmo_genetico, solucao_valida

def executar_experimentos(algoritmo, execucoes=30, **kwargs):
    resultados = []
    melhor_solucao = None
    melhor_custo = float('inf')

    for semente in range(execucoes):
        random.seed(semente)
        solucao, custo, energia = algoritmo(**kwargs)
        if not solucao_valida(solucao):
            continue
        resultados.append(custo)
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_solucao = solucao

    if not resultados:
        return None, float('inf')

    return melhor_solucao, melhor_custo

def executar_ia(mapa):
    pontos = achar_pontos(mapa)
    ginasios = [g for g in pontos if g not in ['1', 'U']]

    # 1. Rotas no Mapa (A*)
    print("\nCalculando distâncias no mapa com A*...")
    custos, caminhos, visitados_mapa, fronteiras_mapa = tabela_distancias(mapa, pontos)

    print("Calculando a melhor ordem dos ginásios (TSP)...")
    ordem, custo_rota, expandidos = melhor_ordem(ginasios, custos)

    rota, visitados_total, fronteira_total = rota_completa(
        ordem, caminhos, visitados_mapa, fronteiras_mapa
    )

    # 2. Otimização de Batalhas
    print("\nExecutando algoritmos de batalha...")
    solucao_hc, custo_hc = executar_experimentos(hill_climbing)
    solucao_sa, custo_sa = executar_experimentos(simulated_annealing)
    solucao_ag, custo_ag = executar_experimentos(algoritmo_genetico)

    # Escolher o melhor algoritmo de batalha
    nome_algoritmo = "Hill Climbing"
    equipes = solucao_hc
    custo_batalhas = custo_hc

    if custo_sa < custo_batalhas:
        nome_algoritmo = "Simulated Annealing"
        equipes = solucao_sa
        custo_batalhas = custo_sa

    if custo_ag < custo_batalhas:
        nome_algoritmo = "Algoritmo Genético"
        equipes = solucao_ag
        custo_batalhas = custo_ag

    # Calcular a energia final da equipa escolhida
    from batalhas import energia_final
    energia = energia_final(equipes)

    return {
        "rota": rota,
        "visitados": visitados_total,
        "fronteira": fronteira_total,
        "ordem": ordem,
        "equipes": equipes,
        "custo_rota": custo_rota,
        "custo_batalhas": custo_batalhas,
        "custo_total": custo_rota + custo_batalhas,
        "expandidos": expandidos,
        "energia": energia,
        "melhor_algoritmo": nome_algoritmo
    }

def main():
    mapa = carregar_mapa("mapa.txt")
    iniciar_app(mapa, executar_ia, fps=60, tamanho_celula=8)

if __name__ == "__main__":
    main()