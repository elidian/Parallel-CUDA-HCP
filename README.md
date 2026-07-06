# Parallel-CUDA-HCP

Este projeto faz parte do **Trabalho de Conclusão de Curso (TCC)**, sendo apresentada uma nova **heurística para o Problema do Ciclo Hamiltoniano (HCP)**.  
O algoritmo foi implementado em **Python** e **C**, com utilização da biblioteca **CuPy** para execução de núcleos CUDA em GPU.

## 🎯 Objetivos
- Propor uma nova heurística para o HCP
- Explorar paralelização em GPU com CuPy
- DataSet para HCP: 52.954 instâncias de grafos k-regulares para tamanhos distintos (n=50, k=2 a 25; n=100, k=2 a 50; n=200, 400, 800, k=2 a 83)

## 🛠️ Tecnologias
- **Python** utilizado em algoritmos principais
- **C** utilizado em algoritmo voltado exclusivamente em núcleos CUDA
- **CuPy** para execução de kernels CUDA
- **CUDA Toolkit** para programação paralela em GPU

## 📂 Estrutura
- `/hcp_n50_1-24.7z` → pasta compactada com todos os grafos de tamanho 50: do nível 1 ao 24 (grau 2 ao 25)
- `/hcpsols_n50_1-24.7z` → pasta compactada com uma solução para cada grafo de tamanho 50: do nível 1 ao 24 (grau 2 ao 25)

## 🚀 Execução
- "criador_matriz_hamiltoniana.py" para gerar grafos k-regulares
- "hcp_cont_dimension.py" para escolher os grafos gerados para os testes: salvo em "grafos_para_teste.txt"
- "hcp_test.py" para testar cada grafo escolhido em "grafos_para_teste.txt": executa "new_hco_cuda_final.py" passando cada grafo

