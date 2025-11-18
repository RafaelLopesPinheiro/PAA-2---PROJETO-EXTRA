# Vehicle Routing Problem with Time Windows - Genetic Algorithm

## 📋 Descrição

Implementação de um **Algoritmo Genético Híbrido** para resolver o **Vehicle Routing Problem with Time Windows (VRPTW)**, otimizando rotas de entrega com restrições de capacidade e janelas de tempo.

**Baseado em:** "Research on Vehicle Routing Problem with Time Windows Based on Improved Genetic Algorithm" (MDPI Electronics, 2025)

## 🎯 Objetivo

Minimizar a distância total percorrida por uma frota de veículos respeitando:
- Capacidade dos veículos
- Janelas de tempo dos clientes
- Tempo máximo de rota

## 🧬 Implementação

### Heurística de Solomon (I1)
Construção gulosa de solução inicial baseada em critérios de distância e urgência temporal.

### Algoritmo Genético Híbrido
- **Inicialização:** Solomon + construção aleatória gulosa + mutações
- **Seleção:** Torneio (tamanho 5)
- **Crossover:** Best Route Crossover (específico para VRP)
- **Mutação:** Relocate, Exchange, 2-opt intra e inter-rotas
- **Estratégias:** Elitismo + reinicialização adaptativa

## 📊 Datasets

- **Food Delivery Dataset** (Kaggle - AV Genpact Hack Dec 2018)
- **Solomon Benchmarks** (C101, R101, RC101, etc.)

## 🚀 Execução

```bash
python main.py
```

## 📁 Estrutura

```
├── data/               # Dados de entrada e instâncias VRPTW
├── src/                # Código-fonte (utils, heuristics, GA, visualization)
├── results/            # Soluções, gráficos e relatórios
└── main.py             # Pipeline principal
```

## 📈 Resultados

O algoritmo genético consistentemente melhora a solução inicial de Solomon, reduzindo distância total e número de veículos utilizados.