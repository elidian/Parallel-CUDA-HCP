import os

def pegar_dimensao(caminho_arquivo):
    """Lê a dimensão declarada em um arquivo TSPLIB/HCP."""
    with open(caminho_arquivo, "r") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("DIMENSION"):
                partes = linha.split(":")
                if len(partes) > 1:
                    return int(partes[1].strip())
    return None

def pegar_grau_regular(caminho_arquivo):
    """Lê a dimensão declarada em um arquivo TSPLIB/HCP."""
    with open(caminho_arquivo, "r") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("COMMENT"):
                partes = linha.split()
                # encontra o índice da palavra 'degree' e pega o próximo elemento
                degree = int(partes[partes.index("degree") + 1])
                return degree  # saída: o grau
    return None

def salvar_grafos_para_teste(pasta, dimensao_inicial, dimensao_final=0, grau_inicial=2, grau_final=3, arquivo_saida="grafos_para_teste.txt", extensao=".hcp"):
    """Percorre todos os arquivos da pasta e salva de acordo com a DIMENSÃO e o GRAU REGULAR"""
    with open(arquivo_saida, "w") as out:
        for arquivo in os.listdir(pasta):
            if arquivo.endswith(extensao):
                caminho = os.path.join(pasta, arquivo)
                dimensao = pegar_dimensao(caminho)
                grau = pegar_grau_regular(caminho)
                if dimensao_final == 0:
                    if grau is not None and grau >= grau_inicial and grau <= grau_final and dimensao == dimensao_inicial:
                        out.write(f"{arquivo}; DIMENSION={dimensao}; DEGREE={grau}\n")
                        print(f"Salvo: {arquivo} (DIMENSION={dimensao}; DEGREE={grau})")
                else:
                    if grau is not None and grau >= grau_inicial and grau <= grau_final and dimensao >= dimensao_inicial and dimensao <= dimensao_final:
                        out.write(f"{arquivo}; DIMENSION={dimensao}; DEGREE={grau}\n")
                        print(f"Salvo: {arquivo} (DIMENSION={dimensao}; DEGREE={grau})")

    print(f"\nResultados salvos em: {arquivo_saida}")


pasta_dos_grafos = "hcp" 

dimensao_inicial = 100
dimensao_final = dimensao_inicial
grau_inicial = 2
grau_final = grau_inicial + 83

salvar_grafos_para_teste(pasta=pasta_dos_grafos, dimensao_inicial=dimensao_inicial, grau_inicial=grau_inicial, grau_final=grau_final)
