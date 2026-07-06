'''
    Author: Elidian de Albuquerque Alencar
    
    HAMILTON CYCLE PROBLEM ALGORITHM
    Status: concluido - 06/07/2026

    versions {
        python: 3.12.10,
        numpy: 2.3.5,
        cupy-cuda13x: 13.6.0,
        cuda-toolkit: 13.0.00
    }
'''
# import numpy as np
import cupy as cp
import time

kernel_code = r'''
extern "C" __global__
void kernel_cuda(
    bool* matriz,
    double* pesos,
    int* lista,
    int* lista_inversa,
    int tamanho
) {
    int linha = blockIdx.y * blockDim.y + threadIdx.y;
    int coluna = blockIdx.x * blockDim.x + threadIdx.x;

    if (linha<tamanho && coluna<tamanho && matriz[linha*tamanho + coluna] && lista[linha]==-1 && lista_inversa[coluna]==-1) {
        double soma = 0.0;
        double log_produto = 0.0;
        double conta = 0.0;

        //calcular opositores de linha e coluna
        for(int e=0; e<tamanho; e++) {
            if (e!=linha && e!=coluna) {
                if (matriz[linha*tamanho + e]) {
                    soma += 1;
                    conta += 1;
                }
                else {
                    soma += 2;
                    log_produto += log(2.0);
                    conta += 1;
                }
                if (matriz[e*tamanho + coluna]) {
                    soma += 1;
                    conta += 1;
                }
                else {
                    soma += 2;
                    log_produto += log(2.0);
                    conta += 1;
                }
            }
        }

        //calcular o opositor oposto direto
        if (matriz[coluna*tamanho + linha]) {
            soma += 1;
            conta += 1;
        }
        else {
            soma += 2;
            log_produto += log(2.0);
            conta += 1;
        }

        //calcular o opositor de subciclo após inserção na lista
        int proximo = coluna;
        for (int i=0; i<tamanho; i++) {
            if (lista[proximo] == -1){break;}
            
            proximo = lista[proximo];
            
            if (proximo == coluna){break;}
        }
        int anterior = linha;
        for (int i=0; i<tamanho; i++) {
            if (lista_inversa[anterior] == -1){break;}
            
            anterior = lista_inversa[anterior];
            
            if (anterior == linha){break;}
        }
        if (anterior != linha || proximo != coluna) {
            if (matriz[proximo*tamanho + anterior]) {
                soma += 1;
                conta += 1;
            }
            else {
                soma += 2;
                log_produto += log(2.0);
                conta += 1;
            }
        }

        pesos[linha*tamanho + coluna] = log_produto + log(soma) - 2*log(conta);
    }
}
'''

def pontas_sub_ciclo(lista, lista_inversa, linha, coluna):
    tamanho = lista.shape[0]
    prox = coluna
    for _ in range(tamanho):
        if lista[prox] == -1:
            break
        prox = lista[prox]
        if prox == coluna:
            break

    back = linha
    for _ in range(tamanho):
        if lista_inversa[back] == -1:
            break
        back = lista_inversa[back]
        if back == linha:
            break
    
    return prox, back

def hcp(matriz_base):
    matriz_base = cp.array(matriz_base, dtype=cp.int32)
    cp.fill_diagonal(matriz_base, 0)
    
    tamanho = matriz_base.shape[0]
    matriz = cp.array(matriz_base)
    matriz = cp.where(matriz == 0, False, True)
    lista = cp.full((tamanho), -1, dtype=cp.int32)
    lista_inversa = cp.full((tamanho), -1, dtype=cp.int32)


    '''configuração de kernel cuda cupy'''
    module = cp.RawModule(code=kernel_code)
    peso_kernel = module.get_function("kernel_cuda")
    threads = (16, 16)
    blocks = ((tamanho + threads[0] - 1) // threads[0],
                (tamanho + threads[1] - 1) // threads[1])
    
    print('Total de Blocks: ', blocks[0] * blocks[1])
    print('Total de Threads: ', (blocks[0] * threads[0]) * (blocks[1] * threads[1]))

    tempo_inicial = time.perf_counter()
    print(f'iteração {1} | tamanho {tamanho} | ', end='\r')
    for iteracao in range(tamanho-2):

        tempo_atual = time.perf_counter()
        if iteracao > 0:
            tempo_corrido = tempo_atual - tempo_inicial
            tempo_medio = tempo_corrido / iteracao
            tempo_restante = tempo_medio * (tamanho - iteracao - 1)
            dias_restante = int(tempo_restante // 86400)
            
            tempo_corrido = time.strftime("%H:%M:%S", time.gmtime(tempo_corrido))
            tempo_restante = time.strftime("%H:%M:%S", time.gmtime(tempo_restante))
            print(f'iteração {iteracao+1} | tamanho {tamanho} | tempo restante {dias_restante}d {tempo_restante} | tempo corrido {tempo_corrido}', end='\r')

        pesos = cp.full_like(matriz, -cp.inf, dtype=cp.float64)
        '''executando o kernel cuda'''
        peso_kernel(blocks, threads,
                    (matriz, pesos, lista, lista_inversa, tamanho))
        cp.cuda.Stream.null.synchronize()


        idx, idy = [e.item() for e in cp.unravel_index(cp.argmax(pesos), pesos.shape)]

        if not matriz[idx, idy]:
            print(f'ciclo falso1')
            return cp.asnumpy(lista), False
        

        lista[idx] = idy
        lista_inversa[idy] = idx
        matriz[idx,:] = False
        matriz[:,idy] = False
        matriz[idx, idy] = True
        matriz[idy, idx] = False

        prox, back = pontas_sub_ciclo(lista, lista_inversa, idx, idy)

        matriz[prox, back] = False

    soma_true = cp.sum(matriz)
    print(f'\nsoma true {soma_true}')

    for idx in range(tamanho):
        if lista[idx] == -1:
            idy = cp.argmax(matriz[idx])
            if not matriz[idx, idy]:
                print(f'ciclo falso2')
                return cp.asnumpy(lista), False
            
            lista[idx] = idy
            lista_inversa[idy] = idx

    return cp.asnumpy(lista), True

if __name__ == '__main__':
    pass