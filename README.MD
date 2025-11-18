# Vehicle Routing Problem with Time Windows - Genetic Algorithm

## 📋 Descrição do Projeto

Implementação de um **Algoritmo Genético Híbrido** para resolver o **Vehicle Routing Problem with Time Windows (VRPTW)**, baseado no artigo científico:

> **"Research on Vehicle Routing Problem with Time Windows Based on Improved Genetic Algorithm"**  
> MDPI Electronics, 2025  
> DOI: https://doi.org/10.3390/electronics14040647

### 🎯 Objetivo

Minimizar a distância total percorrida por uma frota de veículos para atender todos os clientes, respeitando:
- Capacidade dos veículos
- Janelas de tempo de cada cliente
- Tempo máximo de rota

---

## 🧬 Algoritmos Implementados

### 1. Heurística de Inserção de Solomon (I1)
- Construção gulosa de solução inicial
- Critério de inserção baseado em custo de distância e urgência temporal
- **Complexidade:** O(n³)

### 2. Algoritmo Genético Híbrido
- **Representação:** Sequência de clientes agrupados em rotas
- **Inicialização:** Solomon + Construção Aleatória + Mutações
- **Seleção:** Torneio (tamanho 5)
- **Crossover:** Order Crossover (OX)
- **Mutação:** Swap, Insertion, Inversion
- **Busca Local:** 2-opt intra-rota
- **Estratégias:** Elitismo + Reinicialização Adaptativa
- **Complexidade:** O(G × P × n²)

---

## 📁 Estrutura do Projeto
VRPTW-Genetic-Algorithm/ ├── data/ │ ├── raw/ │ │ └── sales_data.csv # Dados de entrada │ └── processed/ │ └── vrptw_instances.json # Instância VRPTW gerada ├── src/ │ ├── utils.py # Funções utilitárias │ ├── heuristics.py # Heurística de Solomon │ ├── genetic_algorithm.py # Algoritmo Genético │ └── visualization.py # Visualizações ├── results/ │ ├── solutions/ # Soluções em JSON │ ├── plots/ # Gráficos gerados │ └── report.txt # Relatório técnico ├── main.py # Pipeline principal ├── requirements.txt # Dependências └── README.md # Este arquivo