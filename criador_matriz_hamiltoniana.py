import random
import networkx as nx
import matplotlib.pyplot as plt
import os
import multiprocessing
import psutil
import time
from datetime import timedelta


def aumentar_valencia_otimizado(matriz, m):
    n = len(matriz)
    alvo = 1 + m
    graus = [sum(linha) for linha in matriz]
    
    # Lista de todas as arestas possíveis
    todas_arestas = [(i, j) for i in range(n) for j in range(i+1, n) if matriz[i][j] == 0]
    random.shuffle(todas_arestas)
    
    for u, v in todas_arestas:
        if graus[u] < alvo and graus[v] < alvo:
            matriz[u][v] = 1
            matriz[v][u] = 1
            graus[u] += 1
            graus[v] += 1
        # Se todos atingiram o alvo, pode parar
        if all(g == alvo for g in graus):
            break
    
    return matriz


def matriz_hamiltoniana_aleatoria(n):
    matriz = [[0 for _ in range(n)] for _ in range(n)]
    vertices = list(range(n))
    random.shuffle(vertices)
    ciclo = []
    for i in range(n - 1):
        u, v = vertices[i], vertices[i + 1]
        matriz[u][v] = 1
        matriz[v][u] = 1    # grafo não direcionado
        ciclo.append((u, v))
    # Fecha o ciclo conectando último ao primeiro
    matriz[vertices[0]][vertices[-1]] = 1
    matriz[vertices[-1]][vertices[0]] = 1
    ciclo.append((vertices[-1], vertices[0]))
    return matriz, vertices, ciclo

def verificar_graus(matriz):
    graus = [sum(linha) for linha in matriz]
    return graus

def salvar_grafo(nome, matriz, ciclo, grau, arquivo):
    n = len(matriz)
    arestas = []
    for i in range(n):
        for j in range(i+1, n):
            if matriz[i][j] == 1:
                arestas.append((i+1, j+1))  # indexação 1-based
    
    ciclo_str = "-".join(str(v+1) for v in ciclo) + "-" + str(ciclo[0]+1)
    
    conteudo = []
    conteudo.append(f"NAME : {nome}")
    conteudo.append(f"COMMENT : {n}-vertex graph with degree {grau} and HC {ciclo_str}")
    conteudo.append("TYPE : HCP")
    conteudo.append(f"DIMENSION : {n}")
    conteudo.append("EDGE_DATA_FORMAT : EDGE_LIST")
    conteudo.append("EDGE_DATA_SECTION")
    for u, v in arestas:
        conteudo.append(f"{u} {v}")
    conteudo.append("-1")
    conteudo.append("EOF")
    
    with open(arquivo, "w") as f:
        f.write("\n".join(conteudo))


def salvar_tour(nome, ciclo, arquivo):
    n = len(ciclo)
    conteudo = []
    conteudo.append(f"NAME : {nome} tour file")
    conteudo.append("COMMENT : Tour found")
    conteudo.append("TYPE : TOUR")
    conteudo.append(f"DIMENSION : {n}")
    conteudo.append("TOUR_SECTION")
    for v in ciclo:
        conteudo.append(str(v+1))  # indexação 1-based
    conteudo.append("-1")
    conteudo.append("EOF")
    
    with open(arquivo, "w") as f:
        f.write("\n".join(conteudo))


def desenhar_grafo(matriz, ciclo):
    n = len(matriz)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    # Adiciona arestas
    for i in range(n):
        for j in range(i+1, n):
            if matriz[i][j] == 1:
                G.add_edge(i, j)
    
    # Layout circular
    pos = nx.circular_layout(G)
    
    # Desenha nós
    nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=800)
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    # Arestas do ciclo em vermelho
    nx.draw_networkx_edges(G, pos, edgelist=ciclo, edge_color="red", width=2)
    
    # Outras arestas em cinza
    outras_arestas = [e for e in G.edges() if e not in ciclo and (e[1], e[0]) not in ciclo]
    nx.draw_networkx_edges(G, pos, edgelist=outras_arestas, edge_color="gray", style="dashed")
    
    plt.show()

def instancias(dimensao, x, pasta):
    for y in range(1, 167):
        n = dimensao  # tamanho do grafo
        m = x   # grau/valência do grafo a ser aumentado

        regular = False
        cont = 0
        while not regular:
            matriz, ciclo_vertices, ciclo_arestas = matriz_hamiltoniana_aleatoria(n)
            matriz = aumentar_valencia_otimizado(matriz, m)
            graus = verificar_graus(matriz)

            grau = 1+m
            if all(g == 1+m for g in graus):
                # print("✅ O grafo é regular de grau", 2+m)
                regular = True
            else:
                cont += 1
                print(f"⚠️ O grafo não é regular {x} | {cont:04}", end="\r")

            if regular:
                # Salvar grafo e tour
                nome_arquivo_graph = f"graph_edges_n{n}_{x:02}{y:03}.hcp"
                caminho = os.path.join(pasta, nome_arquivo_graph)
                salvar_grafo(f"Graph edges {x:02}{y:03}", matriz, ciclo_vertices, grau, caminho)
                
                nome_arquivo_sols = f"graph_solution_n{n}_{x:02}{y:03}.tour"
                caminho = os.path.join(pasta + "sols", nome_arquivo_sols)
                salvar_tour(f"Graph solution {x:02}{y:03}", ciclo_vertices, caminho)

                print(f"✅ Arquivos salvos: {nome_arquivo_graph} e {nome_arquivo_sols}")

                # # Desenhar grafo com ciclo destacado
                # desenhar_grafo(matriz, ciclo_arestas)


if __name__ == "__main__":
    pasta = "hcp"
    # Verifica se a pasta existe, senão cria
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    pastasols = f"{pasta}sols"
    if not os.path.exists(pastasols):
        os.makedirs(pastasols)

    # dimensão do grafo, quantidade de vértices 
    dimensao = 200 

    # nivel x, x >= 1 (grau = x + 1)
    nivel_inicial = 80 
    nivel_final = nivel_inicial + 2 

    # lista de argumentos (x, pasta)
    args = [(dimensao, x, pasta) for x in range(nivel_inicial, nivel_final + 1)]

    # Núcleos físicos com FALSE e lógicos com TRUE
    nucleos = psutil.cpu_count(logical=False) 

    t1 = time.perf_counter()
    # limita para 1 processo simultâneo por nucleo físico ou lógico
    with multiprocessing.Pool(processes=nucleos) as pool:
        pool.starmap(instancias, args)
    t2 = time.perf_counter()
    
    duracao = t2-t1
    t_formatado = str(timedelta(seconds=duracao))
    texto = f'\nTempo de execução: {t_formatado}\n'
    print(texto)
