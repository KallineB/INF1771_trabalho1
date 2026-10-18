from interface import iniciar_app
from mapa import carregar_mapa, achar_pontos
from busca import tabela_distancias, custo_casa
from rotas import melhor_ordem, rota_completa
from batalhas import hill_climbing, simulated_annealing, algoritmo_genetico, energia_final, tempo_batalha
from experimentos import otimo_programacao_dinamica, rodar_bateria

def executar_ia(mapa):
    pontos = achar_pontos(mapa)
    ginasios = [g for g in pontos if g not in ['1', 'U']]

    # 1. Rotas no Mapa (A*)
    print("\nCalculando distancias no mapa com A* ")
    custos, caminhos, visitados_mapa, fronteiras_mapa = tabela_distancias(mapa, pontos)

    print("Calculando a melhor ordem dos ginasios (TSP) ")
    ordem, custo_rota, expandidos = melhor_ordem(ginasios, custos)

    rota, visitados_total, fronteira_total = rota_completa(
        ordem, caminhos, visitados_mapa, fronteiras_mapa
    )

    # 2. Otimização de Batalhas
    print("\nExecutando algoritmos de batalha...")
    otimo = otimo_programacao_dinamica()

    sol_hc, custo_hc, acertos_hc, media_hc, desvio_hc, tempo_hc = rodar_bateria("Hill Climbing", hill_climbing, otimo)
    sol_sa, custo_sa, acertos_sa, media_sa, desvio_sa, tempo_sa = rodar_bateria("Simulated Annealing", simulated_annealing, otimo)
    sol_ag, custo_ag, acertos_ag, media_ag, desvio_ag, tempo_ag = rodar_bateria("Algoritmo Genético", algoritmo_genetico, otimo)

    candidatos = [
        {"nome": "Hill Climbing", "solucao": sol_hc, "custo": custo_hc, "acertos": acertos_hc, "media": media_hc, "desvio": desvio_hc, "tempo": tempo_hc},
        {"nome": "Simulated Annealing", "solucao": sol_sa, "custo": custo_sa, "acertos": acertos_sa, "media": media_sa, "desvio": desvio_sa, "tempo": tempo_sa},
        {"nome": "Algoritmo Genético", "solucao": sol_ag, "custo": custo_ag, "acertos": acertos_ag, "media": media_ag, "desvio": desvio_ag, "tempo": tempo_ag},
    ]

    candidatos.sort(key=criterios_de_desempate)

    melhor = candidatos[0]
    nome_algoritmo = melhor["nome"]
    equipes = melhor["solucao"]
    custo_batalhas = melhor["custo"]

    # Calcular a energia final da equipa escolhida
    energia = energia_final(equipes)

    # custos acumulados em cada passo da rota, para mostrar enquanto o agente anda
    custo_rota_passo = [custo_casa('1')]
    for linha, coluna in rota[1:]:
        custo_rota_passo.append(custo_rota_passo[-1] + custo_casa(mapa[linha][coluna]))

    # a batalha acontece quando o agente chega no próximo ginásio da ordem
    custo_batalha_passo = []
    passo_da_batalha = {}
    tempos = {}
    acumulado = 0
    proximo = 0
    for i in range(len(rota)):
        if proximo < len(ordem) and rota[i] == pontos[ordem[proximo]]:
            ginasio = ordem[proximo]
            tempos[ginasio] = tempo_batalha(ginasio, equipes[ginasio])
            acumulado += tempos[ginasio]
            passo_da_batalha[ginasio] = i
            proximo += 1
        custo_batalha_passo.append(acumulado)

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
        "melhor_algoritmo": nome_algoritmo,
        "custo_rota_passo": custo_rota_passo,
        "custo_batalha_passo": custo_batalha_passo,
        "passo_da_batalha": passo_da_batalha,
        "tempo_batalha": tempos
    }

def criterios_de_desempate(candidato):
        return (
            round(candidato["custo"], 4),
            -candidato["acertos"], # negativo inverte a ordem
            round(candidato["media"], 4),
            round(candidato["desvio"], 4),
            candidato["tempo"]
        )

def main():
    mapa = carregar_mapa("mapa.txt")
    iniciar_app(mapa, executar_ia, fps=60, tamanho_celula=8)

if __name__ == "__main__":
    main()
