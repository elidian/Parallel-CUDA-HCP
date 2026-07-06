import os
import new_hcp_cuda_final as hcp
import numpy as np
import time
from datetime import timedelta

def carregar_matriz(caminho_arquivo):
    """
    Lê um arquivo HCP e retorna a matriz de adjacência.
    """
    dimensao = None
    lendo_arestas = False
    arestas = []

    with open(caminho_arquivo, "r") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("DIMENSION"):
                partes = linha.split(":")
                if len(partes) > 1:
                    dimensao = int(partes[1].strip())
            
            elif linha.startswith("EDGE_DATA_SECTION"):
                lendo_arestas = True
                continue
            
            elif linha in ("-1", "EOF"):
                lendo_arestas = False
            
            elif lendo_arestas and linha:
                u, v = map(int, linha.split())
                arestas.append((u, v))

    # Criar matriz de adjacência
    matriz = [[0] * dimensao for _ in range(dimensao)]
    for u, v in arestas:
        matriz[u-1][v-1] = 1
        matriz[v-1][u-1] = 1  # grafo não-direcionado

    return matriz, dimensao


def processar_grafos(arquivo_lista, pasta="hcp"):
    """
    Lê o arquivo grafos_para_teste.txt e chama hcp(matriz) para cada grafo.
    """
    cont_true = 0
    cont_false = 0
    d_true = []
    d_false = []
    grau_ant = 0
    time_graus = 0
    time_graus_ini = 0
    time_ind = 0
    with open(arquivo_lista, "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            nome_arquivo = linha.split(";")[0].strip()
            caminho = os.path.join(pasta, nome_arquivo)
            
            matriz, dimensao = carregar_matriz(caminho)

            print(f'Nome: {nome_arquivo} | Dimensão: {dimensao}')
            soma_linhas = np.sum(matriz, axis=1)
            soma_colunas = np.sum(matriz, axis=0)
            print(f'soma das linhas: {soma_linhas}')
            print(f'soma das colunas: {soma_colunas}')
            
            graus = soma_linhas[0].item()
            if np.min(soma_linhas)==0 or np.min(soma_colunas)==0:
                print(f'linha ou coluna sem valor')


            if grau_ant != graus:                
                if grau_ant != 0:
                    if cont_false == 0:
                        d_true.append([grau_ant, cont_true])
                    else:
                        d_false.append([grau_ant, cont_false])

                    time_graus = time.perf_counter() - time_graus_ini
                    t_formatado = str(timedelta(seconds=time_graus))
                    texto = f"Dimensão: {dimensao} | grau: {grau_ant} | verdadeiro: {cont_true} | falso: {cont_false} | tempo: {t_formatado}\n"
                    print(texto)
                    caminho = os.path.join(pasta, "resultado_geral.txt")
                    with open(caminho, "a", encoding="utf-8") as arquivo:
                        arquivo.write(texto)

                cont_true = 0
                cont_false = 0
                time_graus_ini = time.perf_counter()

            time_ini = time.perf_counter()
            list, result = hcp.hcp(matriz)
            time_ind = time.perf_counter() - time_ini
            
            if result:
                lista_final = []
                lista_final.append(list[0].item()+1)
                for i in range(len(list)):
                    lista_final.append(list[lista_final[-1]-1].item()+1)
                print(f'list={lista_final}')
            else:
                print(f'list={list}')
            
            t_formatado = str(timedelta(seconds=time_ind))
            texto = f"{nome_arquivo} | dimensão: {dimensao} | grau: {graus} | resultado: {result} | tempo: {t_formatado}\n"
            print(texto)
            
            caminho = os.path.join(pasta, "resultados_individuais.txt")
            # Abrindo o arquivo em modo append (adiciona no final)
            with open(caminho, "a", encoding="utf-8") as arquivo:
                arquivo.write(texto)

            if result:
                cont_true += 1
            else:
                cont_false += 1
            
            grau_ant = graus


    if cont_false == 0:
        d_true.append([grau_ant, cont_true])
    else:
        d_false.append([grau_ant, cont_false])

    time_graus = time.perf_counter() - time_graus_ini
    t_formatado = str(timedelta(seconds=time_graus))
    texto = f"Dimensão: {dimensao} | grau: {grau_ant} | verdadeiro: {cont_true} | falso: {cont_false} | tempo: {t_formatado}\n"
    caminho = os.path.join(pasta, "resultado_geral.txt")
    with open(caminho, "a", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    texto = f"""\nLinha True | quantidade ultimo: {cont_true} | resultado por dimensões: {d_true}
Linha False | quantidade ultimo: {cont_false} | resultado por dimensões: {d_false}\n"""
    print(texto)
    
    caminho = os.path.join(pasta, "resultado_geral.txt")
    with open(caminho, "a", encoding="utf-8") as arquivo:
        arquivo.write(texto)

pasta="hcp"

caminho = os.path.join(pasta, "resultado_geral.txt")
# Verifica se o arquivo existe
if not os.path.exists(caminho):
    # Cria o arquivo vazio
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("")  

caminho = os.path.join(pasta, "resultados_individuais.txt")
if not os.path.exists(caminho):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("")  

t1 = time.perf_counter()
processar_grafos("grafos_para_teste.txt", pasta=pasta)
t2 = time.perf_counter()

duracao = t2-t1
t_formatado = str(timedelta(seconds=duracao))
texto = f'\nTempo de execução: {t_formatado}\n\n'
print(texto)

caminho = os.path.join(pasta, "resultado_geral.txt")
with open(caminho, "a", encoding="utf-8") as arquivo:
    arquivo.write(texto)  
