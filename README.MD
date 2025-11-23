# VRPTW - Algoritmo Genético Híbrido

## 📚 PROJETO ACADÊMICO - PAA-2 (Projeto Extra)

**Disciplina:** Projeto de Análise de Algoritmos  
**Autor:** Rafael Lopes Pinheiro  
**GitHub:** [@RafaelLopesPinheiro](https://github.com/RafaelLopesPinheiro)  
**Data:** Novembro 2025

---

## 📋 Descrição do Projeto

Implementação completa de um **Algoritmo Genético Híbrido** para resolver o **Vehicle Routing Problem with Time Windows (VRPTW)**, um problema NP-difícil de otimização combinatória.

**Baseado no artigo científico:**  
*"Research on Vehicle Routing Problem with Time Windows Based on Improved Genetic Algorithm"*  
MDPI Electronics, 2025  
DOI: https://doi.org/10.3390/electronics14040647

---

## 🎯 Objetivo do Problema

Minimizar a **distância total** percorrida por uma frota de veículos para atender todos os clientes, respeitando:

✅ **Capacidade dos veículos** (carga máxima)  
✅ **Janelas de tempo** de cada cliente (horário de atendimento)  
✅ **Tempo máximo de rota** por veículo  
✅ **Cada cliente visitado exatamente uma vez**  
✅ **Todas as rotas iniciam e terminam no depósito**

---

## 📖 INSTRUÇÕES COMPLETAS

**🔴 LEIA PRIMEIRO:** [`GUIA_EXECUCAO.md`](GUIA_EXECUCAO.md)

Este guia contém:
1. ✅ **Como executar** o programa passo a passo
2. ✅ **Significado dos parâmetros** de entrada
3. ✅ **Significado da saída** exibida
4. ✅ **Como variar a entrada** e testar diferentes cenários
5. ✅ Resolução de problemas comuns

---

## 🚀 Execução Rápida (TL;DR)

```powershell
# 1. Clone o repositório
git clone https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA.git
cd PAA-2---PROJETO-EXTRA

# 2. Crie e ative ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Instale dependências
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Baixe os dados (OBRIGATÓRIO)
# Acesse: https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018
# Baixe train.csv e coloque em: data/raw/food_delivery/train.csv

# 5. Execute o programa principal
python main.py
```

**Tempo de execução:** 8-12 minutos (configuração padrão)

---

## 🧬 Algoritmos Implementados

### 1. Heurística de Inserção de Solomon (I1)

Método construtivo guloso que gera soluções iniciais viáveis:

```
Para cada rota:
  1. Seleciona cliente inicial (mais distante do depot)
  2. Insere clientes usando critério:
     c(i,u,j) = α·c1(i,u,j) + λ·c2(i,u,j)
     onde:
       c1 = custo adicional de distância
       c2 = custo temporal (urgência)
  3. Repete até não ser possível inserir mais clientes
```

**Complexidade:** O(n³) onde n = número de clientes

### 2. Algoritmo Genético Híbrido

Método evolutivo que otimiza a solução inicial:

**Componentes:**
- **Representação:** Sequência de clientes agrupados em rotas
- **População inicial (diversificada):**
  - 30% Solomon com parâmetros variados
  - 40% Construção aleatória gulosa
  - 30% Mutações da melhor solução
- **Seleção:** Torneio (tamanho 5)
- **Crossover:** Order Crossover (OX) - taxa 80%
- **Mutações:** Swap, Insertion, Inversion - taxa 20%
- **Busca Local:** 2-opt intra-rota - taxa 30%
- **Elitismo:** Top 20 soluções preservadas
- **Reinicialização:** Após 50 gerações sem melhoria

**Complexidade:** O(G × P × n²) onde:
- G = número de gerações (padrão: 300)
- P = tamanho da população (padrão: 100)
- n = número de clientes

---

## 📊 Datasets Suportados

### 1. Food Delivery Dataset (Principal)
- **Fonte:** Kaggle - AV Genpact Hack Dec 2018
- **URL:** https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018
- **Descrição:** Dados reais de entregas de comida
- **Formato:** CSV com coordenadas lat/lng, itens, timestamps

### 2. Solomon Benchmarks (Opcional)
- **Fonte:** Solomon (1987)
- **URL:** http://web.cba.neu.edu/~msolomon/problems.htm
- **Instâncias:** C101, R101, RC101, etc.

---

## � Estrutura do Código-Fonte

```
PAA-2---PROJETO-EXTRA/
│
├── main.py                          ← EXECUTAR ESTE ARQUIVO
├── GUIA_EXECUCAO.md                 ← LEIA ESTE GUIA PRIMEIRO
├── README.MD                        ← Você está aqui
├── requirements.txt                 ← Dependências Python
│
├── src/                             ← Código-fonte modular
│   ├── __init__.py
│   ├── utils.py                     # Funções auxiliares
│   ├── food_delivery_loader.py      # Carregador de dados reais
│   ├── solomon_loader.py            # Carregador benchmarks
│   ├── heuristics.py                # Heurística de Solomon
│   ├── genetic_algorithm.py         # Algoritmo Genético
│   └── visualization.py             # Geração de gráficos
│
├── data/
│   ├── raw/
│   │   └── food_delivery/
│   │       └── train.csv            ← BAIXE ESTE ARQUIVO
│   └── processed/
│       └── vrptw_instances.json     # Instâncias processadas
│
└── results/                         ← Saídas geradas automaticamente
    ├── solutions/                   # JSON com rotas
    ├── plots/                       # Gráficos PNG
    └── report.txt                   # Relatório técnico completo
```

---

## 📈 Resultados e Saídas

O programa gera automaticamente:

### 1. Soluções em JSON
- `results/solutions/solution_solomon.json` - Solução inicial
- `results/solutions/solution_genetic_algorithm.json` - Solução otimizada

### 2. Visualizações (PNG)
- `solution_solomon.png` - Mapa de rotas inicial
- `solution_genetic_algorithm.png` - Mapa de rotas otimizado
- `convergence.png` - Gráfico de convergência do AG
- `comparison.png` - Comparação lado a lado
- `time_windows.png` - Cumprimento de janelas de tempo

### 3. Relatório Técnico
- `results/report.txt` - Relatório completo com:
  - Referência do artigo
  - Descrição do problema
  - Algoritmos implementados
  - Análise de complexidade
  - Resultados experimentais
  - Conclusões

---

## 🔧 Parâmetros Configuráveis

### Dados
- `max_customers`: 40 (padrão) - Número de entregas
- `vehicle_capacity`: 50.0 (padrão) - Capacidade por veículo

### Solomon
- `alpha`: 1.0 - Peso para distância
- `lambda_param`: 2.0 - Peso para urgência

### Algoritmo Genético
- `pop_size`: 100 - Tamanho da população
- `generations`: 300 - Número de gerações
- `crossover_rate`: 0.8 - Taxa de crossover
- `mutation_rate`: 0.2 - Taxa de mutação

**Para detalhes completos:** veja [`GUIA_EXECUCAO.md`](GUIA_EXECUCAO.md) seção 2

---

## � Resultados Típicos

Melhoria média do AG sobre Solomon:
- ✅ **Distância:** -15% a -25%
- ✅ **Veículos:** -1 a -2 veículos
- ✅ **Fitness:** -20% a -30%

---

## 🔍 Análise de Complexidade

### Heurística de Solomon
- **Tempo:** O(n³)
- **Espaço:** O(n²)

### Algoritmo Genético
- **Tempo:** O(G × P × n²)
  - G = 300 gerações
  - P = 100 população
  - n = 40 clientes
  - Total: ~360M operações
- **Espaço:** O(P × n)

**Tempo real (hardware médio):** 8-12 minutos

---

## 📚 Referências

1. **Electronics (2025).** Research on Vehicle Routing Problem with Time Windows Based on Improved Genetic Algorithm. MDPI. https://doi.org/10.3390/electronics14040647

2. **Solomon, M. M. (1987).** Algorithms for the vehicle routing and scheduling problems with time window constraints. Operations Research, 35(2), 254-265.

3. **Bräysy, O., & Gendreau, M. (2005).** Vehicle routing problem with time windows, Part I: Route construction and local search algorithms. Transportation Science, 39(1), 104-118.

---

## 📝 Licença

Este é um projeto acadêmico para fins educacionais.

---

## 👤 Autor

**Rafael Lopes Pinheiro**  
GitHub: [@RafaelLopesPinheiro](https://github.com/RafaelLopesPinheiro)  
Repositório: https://github.com/RafaelLopesPinheiro/PAA-2---PROJETO-EXTRA

---

**Última atualização:** 23/11/2025