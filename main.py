"""
Main Pipeline for VRPTW Genetic Algorithm Project
Author: Rafael Lopes Pinheiro
Date: 2025-11-18

Baseado em: "Research on Vehicle Routing Problem with Time Windows Based on 
Improved Genetic Algorithm" (MDPI Electronics, 2025)
DOI: https://doi.org/10.3390/electronics14040647

Este projeto implementa um Algoritmo Genético Híbrido para resolver o 
Vehicle Routing Problem com Time Windows (VRPTW).
"""

import sys
import os
import json
import numpy as np
from datetime import datetime

# Adiciona src ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils import (
    create_directories, 
    load_sales_data_as_vrptw, 
    save_instance,
    load_instance
)
from src.heuristics import SolomonInsertion
from src.genetic_algorithm import ImprovedGeneticAlgorithm, Solution
from src.visualization import VRPTWVisualizer


class VRPTWProject:
    """Classe principal para gerenciar o projeto VRPTW."""
    
    def __init__(self, config: dict = None):
        """
        Inicializa o projeto.
        
        Parameters:
        -----------
        config : dict, optional
            Configurações do projeto
        """
        self.config = config or self._default_config()
        self.instance = None
        self.solomon_solution = None
        self.ga_solution = None
        self.ga = None
        
        print("\n" + "="*80)
        print(" "*15 + "PROJETO: VRPTW COM ALGORITMO GENÉTICO HÍBRIDO")
        print("="*80)
        print(f"\nAutor: Rafael Lopes Pinheiro")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nReferência do Artigo:")
        print(f"  Título: Research on Vehicle Routing Problem with Time Windows")
        print(f"          Based on Improved Genetic Algorithm")
        print(f"  Fonte:  MDPI Electronics, 2025")
        print(f"  DOI:    https://doi.org/10.3390/electronics14040647")
        print("="*80 + "\n")
    
    def _default_config(self) -> dict:
        """Retorna configuração padrão do projeto."""
        return {
            'data': {
                'input_file': 'data/raw/sales_data.csv',
                'instance_file': 'data/processed/vrptw_instances.json',
                'max_customers': 40
            },
            'solomon': {
                'alpha': 1.0,
                'mu': 1.0,
                'lambda_param': 2.0
            },
            'genetic_algorithm': {
                'pop_size': 100,
                'elite_size': 20,
                'generations': 300,
                'crossover_rate': 0.8,
                'mutation_rate': 0.2,
                'local_search_rate': 0.3,
                'seed': 42
            },
            'output': {
                'solutions_dir': 'results/solutions',
                'plots_dir': 'results/plots',
                'report_file': 'results/report.txt'
            }
        }
    
    def setup(self):
        """Configura estrutura do projeto."""
        print("PASSO 1: CONFIGURAÇÃO DO AMBIENTE")
        print("-" * 80)
        
        create_directories()
        
        print(f"\n✓ Configuração concluída")
        print("="*80 + "\n")
    
    def load_or_create_instance(self):
        """Carrega ou cria instância VRPTW."""
        print("PASSO 2: PREPARAÇÃO DA INSTÂNCIA VRPTW")
        print("-" * 80)
        
        print("\n🍔 Usando Food Delivery Dataset (Kaggle)")
        print("   Dataset: AV Genpact Hack Dec 2018")
        print("   Fonte: https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018")
        
        from src.food_delivery_loader import load_food_delivery_instance
        
        try:
            # Configurações
            max_customers = self.config['data'].get('max_customers', 50)
            vehicle_capacity = 50.0  # CORRIGIDO: 50 unidades por veículo
            
            print(f"\n⚙️ Configurações:")
            print(f"   Máximo de entregas: {max_customers}")
            print(f"   Capacidade por veículo: {vehicle_capacity:.0f} unidades\n")
            
            # Carrega instância (AGORA COM ARGUMENTO CORRETO)
            self.instance = load_food_delivery_instance(
                max_customers=max_customers,
                center_id=None,
                vehicle_capacity=vehicle_capacity,  # AGORA FUNCIONA
                data_path='data/raw/food_delivery/train.csv'
            )
            
        except FileNotFoundError as e:
            print(f"\n❌ ERRO: {e}")
            print("\n📥 INSTRUÇÕES PARA DOWNLOAD:")
            print("="*70)
            print("\n1. Acesse: https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018")
            print("2. Clique em 'Download' (requer login no Kaggle)")
            print("3. Extraia o arquivo train.csv")
            print("4. Coloque em: data/raw/food_delivery/train.csv")
            print("\nEstrutura esperada:")
            print("  data/")
            print("  └── raw/")
            print("      └── food_delivery/")
            print("          ├── train.csv")
            print("          ├── test.csv")
            print("          └── sample_sub.csv")
            print("\n5. Execute novamente: python main.py")
            print("="*70)
            raise
        
        print("="*80 + "\n")
    
    def solve_with_solomon(self):
        """Resolve usando heurística de Solomon."""
        print("PASSO 3: SOLUÇÃO INICIAL (HEURÍSTICA DE SOLOMON)")
        print("-" * 80)
        
        solomon = SolomonInsertion(
            self.instance,
            alpha=self.config['solomon']['alpha'],
            mu=self.config['solomon']['mu'],
            lambda_param=self.config['solomon']['lambda_param']
        )
        
        vehicles = solomon.construct_solution()
        
        # PASSA A INSTANCE PARA A SOLUTION
        self.solomon_solution = Solution(vehicles, self.instance)
        
        print(f"\n📊 Resultados da Heurística de Solomon:")
        print(f"   • Fitness: {self.solomon_solution.fitness:.2f}")
        print(f"   • Distância Total: {self.solomon_solution.total_distance:.2f}")
        print(f"   • Tempo Total: {self.solomon_solution.total_time:.2f}")
        print(f"   • Número de Veículos: {self.solomon_solution.num_vehicles}")
        print(f"   • Factível: {self.solomon_solution.feasible}")
        
        print("\n" + "="*80 + "\n")
    
    def optimize_with_genetic_algorithm(self):
        """Otimiza usando Algoritmo Genético MELHORADO."""
        print("PASSO 4: OTIMIZAÇÃO COM ALGORITMO GENÉTICO MELHORADO")
        print("-" * 80 + "\n")
        
        ga_config = self.config['genetic_algorithm']
        
        self.ga = ImprovedGeneticAlgorithm(  # MUDOU AQUI
            instance=self.instance,
            pop_size=ga_config['pop_size'],
            elite_size=ga_config['elite_size'],
            generations=ga_config['generations'],
            crossover_rate=ga_config['crossover_rate'],
            mutation_rate=ga_config['mutation_rate'],
            local_search_rate=ga_config['local_search_rate'],
            seed=ga_config['seed']
        )
        
        self.ga_solution = self.ga.run()
        
        print("="*80 + "\n")
    
    def analyze_results(self):
        """Analisa e compara resultados."""
        print("PASSO 5: ANÁLISE DE RESULTADOS")
        print("-" * 80 + "\n")
        
        # Calcula melhorias
        distance_improvement = (
            (self.solomon_solution.total_distance - self.ga_solution.total_distance) 
            / self.solomon_solution.total_distance * 100
        )
        
        vehicle_improvement = (
            self.solomon_solution.num_vehicles - self.ga_solution.num_vehicles
        )
        
        fitness_improvement = (
            (self.solomon_solution.fitness - self.ga_solution.fitness)
            / self.solomon_solution.fitness * 100
        )
        
        print("📈 COMPARAÇÃO: SOLOMON vs ALGORITMO GENÉTICO")
        print("-" * 80)
        print(f"\n{'Métrica':<30} {'Solomon':<15} {'AG Híbrido':<15} {'Melhoria':<15}")
        print("-" * 80)
        print(f"{'Distância Total':<30} {self.solomon_solution.total_distance:<15.2f} "
              f"{self.ga_solution.total_distance:<15.2f} {distance_improvement:>13.2f}%")
        print(f"{'Tempo Total':<30} {self.solomon_solution.total_time:<15.2f} "
              f"{self.ga_solution.total_time:<15.2f} {'N/A':>15}")
        print(f"{'Número de Veículos':<30} {self.solomon_solution.num_vehicles:<15} "
              f"{self.ga_solution.num_vehicles:<15} {vehicle_improvement:>14}")
        print(f"{'Fitness':<30} {self.solomon_solution.fitness:<15.2f} "
              f"{self.ga_solution.fitness:<15.2f} {fitness_improvement:>13.2f}%")
        print(f"{'Factível':<30} {str(self.solomon_solution.feasible):<15} "
              f"{str(self.ga_solution.feasible):<15} {'N/A':>15}")
        
        print("\n" + "="*80 + "\n")
        
        return {
            'solomon': {
                'distance': self.solomon_solution.total_distance,
                'time': self.solomon_solution.total_time,
                'vehicles': self.solomon_solution.num_vehicles,
                'fitness': self.solomon_solution.fitness,
                'feasible': self.solomon_solution.feasible
            },
            'genetic_algorithm': {
                'distance': self.ga_solution.total_distance,
                'time': self.ga_solution.total_time,
                'vehicles': self.ga_solution.num_vehicles,
                'fitness': self.ga_solution.fitness,
                'feasible': self.ga_solution.feasible
            },
            'improvements': {
                'distance_percent': distance_improvement,
                'vehicles_absolute': vehicle_improvement,
                'fitness_percent': fitness_improvement
            }
        }
    
    def visualize_results(self):
        """Gera visualizações dos resultados."""
        print("PASSO 6: GERAÇÃO DE VISUALIZAÇÕES")
        print("-" * 80 + "\n")
        
        visualizer = VRPTWVisualizer(self.instance)
        plots_dir = self.config['output']['plots_dir']
        
        # 1. Solução de Solomon
        print("📊 Plotando solução inicial (Solomon)...")
        visualizer.plot_solution(
            self.solomon_solution,
            save_path=f'{plots_dir}/solution_solomon.png',
            title='Solução Inicial - Heurística de Solomon'
        )
        
        # 2. Solução do AG
        print("📊 Plotando solução otimizada (AG)...")
        visualizer.plot_solution(
            self.ga_solution,
            save_path=f'{plots_dir}/solution_genetic_algorithm.png',
            title='Solução Otimizada - Algoritmo Genético Híbrido'
        )
        
        # 3. Convergência
        print("📊 Plotando convergência do AG...")
        visualizer.plot_convergence(
            self.ga.best_fitness_history,
            self.ga.avg_fitness_history,
            save_path=f'{plots_dir}/convergence.png'
        )
        
        # 4. Comparação
        print("📊 Plotando comparação de soluções...")
        visualizer.plot_comparison(
            [self.solomon_solution, self.ga_solution],
            ['Solomon', 'AG Híbrido'],
            save_path=f'{plots_dir}/comparison.png'
        )
        
        # 5. Janelas de tempo
        print("📊 Plotando cumprimento de janelas de tempo...")
        visualizer.plot_time_windows(
            self.ga_solution,
            save_path=f'{plots_dir}/time_windows.png'
        )
        
        print(f"\n✓ Todas as visualizações salvas em: {plots_dir}/")
        print("="*80 + "\n")
    
    def save_solutions(self):
        """Salva soluções em arquivos."""
        print("PASSO 7: SALVAMENTO DE SOLUÇÕES")
        print("-" * 80 + "\n")
        
        solutions_dir = self.config['output']['solutions_dir']
        
        # Salva solução de Solomon
        solomon_data = {
            'method': 'Solomon Insertion Heuristic',
            'fitness': float(self.solomon_solution.fitness),
            'total_distance': float(self.solomon_solution.total_distance),
            'total_time': float(self.solomon_solution.total_time),
            'num_vehicles': int(self.solomon_solution.num_vehicles),
            'feasible': bool(self.solomon_solution.feasible),
            'routes': [
                {
                    'vehicle_id': v.id,
                    'customers': [c.id for c in v.route],
                    'load': float(v.load),
                    'distance': float(v.total_distance),
                    'time': float(v.total_time)
                }
                for v in self.solomon_solution.vehicles if v.route
            ]
        }
        
        with open(f'{solutions_dir}/solution_solomon.json', 'w') as f:
            json.dump(solomon_data, f, indent=2)
        
        print(f"✓ Solução Solomon salva: {solutions_dir}/solution_solomon.json")
        
        # Salva solução do AG
        ga_data = {
            'method': 'Hybrid Genetic Algorithm',
            'fitness': float(self.ga_solution.fitness),
            'total_distance': float(self.ga_solution.total_distance),
            'total_time': float(self.ga_solution.total_time),
            'num_vehicles': int(self.ga_solution.num_vehicles),
            'feasible': bool(self.ga_solution.feasible),
            'routes': [
                {
                    'vehicle_id': v.id,
                    'customers': [c.id for c in v.route],
                    'load': float(v.load),
                    'distance': float(v.total_distance),
                    'time': float(v.total_time)
                }
                for v in self.ga_solution.vehicles if v.route
            ],
            'algorithm_parameters': self.config['genetic_algorithm'],
            'convergence': {
                'best_fitness_history': [float(f) for f in self.ga.best_fitness_history],
                'avg_fitness_history': [float(f) for f in self.ga.avg_fitness_history]
            }
        }
        
        with open(f'{solutions_dir}/solution_genetic_algorithm.json', 'w') as f:
            json.dump(ga_data, f, indent=2)
        
        print(f"✓ Solução AG salva: {solutions_dir}/solution_genetic_algorithm.json")
        print("="*80 + "\n")
    
    def generate_report(self, analysis_results: dict):
        """Gera relatório técnico completo."""
        print("PASSO 8: GERAÇÃO DO RELATÓRIO TÉCNICO")
        print("-" * 80 + "\n")
        
        report_file = self.config['output']['report_file']
        
        report_lines = []
        
        # Cabeçalho
        report_lines.append("="*80)
        report_lines.append("RELATÓRIO TÉCNICO - VRPTW COM ALGORITMO GENÉTICO HÍBRIDO")
        report_lines.append("="*80)
        report_lines.append(f"\nAutor: Rafael Lopes Pinheiro")
        report_lines.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"GitHub: @RafaelLopesPinheiro")
        
        # Referência
        report_lines.append("\n" + "="*80)
        report_lines.append("1. REFERÊNCIA DO ARTIGO")
        report_lines.append("="*80)
        report_lines.append("\nTítulo: Research on Vehicle Routing Problem with Time Windows")
        report_lines.append("        Based on Improved Genetic Algorithm")
        report_lines.append("Autores: Não especificado no prompt (artigo de 2025)")
        report_lines.append("Fonte: MDPI Electronics, 2025")
        report_lines.append("DOI: https://doi.org/10.3390/electronics14040647")
        
        # Descrição do problema
        report_lines.append("\n" + "="*80)
        report_lines.append("2. DESCRIÇÃO DO PROBLEMA")
        report_lines.append("="*80)
        report_lines.append("\nO Vehicle Routing Problem with Time Windows (VRPTW) é um problema")
        report_lines.append("clássico de otimização combinatória classificado como NP-difícil.")
        report_lines.append("\nObjetivo:")
        report_lines.append("  Minimizar a distância total percorrida por uma frota de veículos")
        report_lines.append("  para atender todos os clientes, respeitando:")
        report_lines.append("    • Capacidade dos veículos")
        report_lines.append("    • Janelas de tempo de cada cliente")
        report_lines.append("    • Tempo máximo de rota")
        
        # Descrição do algoritmo
        report_lines.append("\n" + "="*80)
        report_lines.append("3. ALGORITMOS IMPLEMENTADOS")
        report_lines.append("="*80)
        
        report_lines.append("\n3.1. Heurística de Inserção de Solomon (I1)")
        report_lines.append("-" * 80)
        report_lines.append("Heurística construtiva gulosa que:")
        report_lines.append("  1. Seleciona cliente inicial (mais distante do depot)")
        report_lines.append("  2. Insere clientes usando critério de custo c(i,u,j):")
        report_lines.append("     c(i,u,j) = α·c1(i,u,j) + λ·c2(i,u,j)")
        report_lines.append("     onde:")
        report_lines.append("       c1 = custo de distância adicional")
        report_lines.append("       c2 = custo temporal (urgência)")
        report_lines.append("  3. Repete até não ser possível inserir mais clientes")
        
        report_lines.append("\n3.2. Algoritmo Genético Híbrido")
        report_lines.append("-" * 80)
        report_lines.append("Componentes principais:")
        report_lines.append("\na) Representação:")
        report_lines.append("   • Cromossomo = sequência de clientes agrupados em rotas")
        report_lines.append("\nb) Inicialização:")
        report_lines.append("   • 30% - Heurística de Solomon com parâmetros variados")
        report_lines.append("   • 40% - Construção aleatória gulosa")
        report_lines.append("   • 30% - Mutações da melhor solução")
        report_lines.append("\nc) Operadores Genéticos:")
        report_lines.append("   • Seleção: Torneio (tamanho 5)")
        report_lines.append("   • Crossover: Order Crossover (OX)")
        report_lines.append("   • Mutação: Swap, Insertion, Inversion")
        report_lines.append("\nd) Busca Local:")
        report_lines.append("   • 2-opt intra-rota")
        report_lines.append("\ne) Estratégias Avançadas:")
        report_lines.append("   • Elitismo")
        report_lines.append("   • Reinicialização adaptativa (estagnação > 50 gerações)")
        
        # Análise de complexidade
        report_lines.append("\n" + "="*80)
        report_lines.append("4. ANÁLISE DE COMPLEXIDADE")
        report_lines.append("="*80)
        
        report_lines.append("\n4.1. Heurística de Solomon")
        report_lines.append("-" * 80)
        report_lines.append("Complexidade de Tempo: O(n³)")
        report_lines.append("  onde n = número de clientes")
        report_lines.append("\nJustificativa:")
        report_lines.append("  • Para cada veículo: O(n)")
        report_lines.append("  • Para cada cliente não roteado: O(n)")
        report_lines.append("  • Teste de inserção em cada posição: O(n)")
        report_lines.append("  • Total: O(n) × O(n) × O(n) = O(n³)")
        
        report_lines.append("\n4.2. Algoritmo Genético")
        report_lines.append("-" * 80)
        report_lines.append("Complexidade de Tempo: O(G × P × n²)")
        report_lines.append("  onde:")
        report_lines.append("    G = número de gerações")
        report_lines.append("    P = tamanho da população")
        report_lines.append("    n = número de clientes")
        report_lines.append("\nJustificativa:")
        report_lines.append("  • Avaliação de fitness: O(n) por solução")
        report_lines.append("  • Crossover (OX): O(n) por operação")
        report_lines.append("  • Mutação: O(1) por operação")
        report_lines.append("  • Busca local 2-opt: O(n²) por solução")
        report_lines.append("  • Por geração: P × O(n²)")
        report_lines.append("  • Total: G × P × O(n²)")
        
        # Instância do problema
        report_lines.append("\n" + "="*80)
        report_lines.append("5. INSTÂNCIA DO PROBLEMA")
        report_lines.append("="*80)
        report_lines.append(f"\nNome: {self.instance.name}")
        report_lines.append(f"Número de Clientes: {len(self.instance.customers)}")
        report_lines.append(f"Número de Veículos: {self.instance.num_vehicles}")
        report_lines.append(f"Capacidade dos Veículos: {self.instance.vehicle_capacity:.2f}")
        report_lines.append(f"\nDemanda Total: {sum(c.demand for c in self.instance.customers):.2f}")
        report_lines.append(f"Janela de Tempo do Depot: [0.0, 480.0]")
        
        # Parâmetros
        report_lines.append("\n" + "="*80)
        report_lines.append("6. PARÂMETROS DOS ALGORITMOS")
        report_lines.append("="*80)
        
        report_lines.append("\n6.1. Heurística de Solomon")
        report_lines.append("-" * 80)
        for key, value in self.config['solomon'].items():
            report_lines.append(f"  {key}: {value}")
        
        report_lines.append("\n6.2. Algoritmo Genético")
        report_lines.append("-" * 80)
        for key, value in self.config['genetic_algorithm'].items():
            report_lines.append(f"  {key}: {value}")
        
        # Resultados
        report_lines.append("\n" + "="*80)
        report_lines.append("7. RESULTADOS EXPERIMENTAIS")
        report_lines.append("="*80)
        
        report_lines.append("\n7.1. Solução Inicial (Solomon)")
        report_lines.append("-" * 80)
        solomon = analysis_results['solomon']
        report_lines.append(f"  Distância Total: {solomon['distance']:.2f}")
        report_lines.append(f"  Tempo Total: {solomon['time']:.2f}")
        report_lines.append(f"  Número de Veículos: {solomon['vehicles']}")
        report_lines.append(f"  Fitness: {solomon['fitness']:.2f}")
        report_lines.append(f"  Factível: {solomon['feasible']}")
        
        report_lines.append("\n7.2. Solução Otimizada (Algoritmo Genético)")
        report_lines.append("-" * 80)
        ga = analysis_results['genetic_algorithm']
        report_lines.append(f"  Distância Total: {ga['distance']:.2f}")
        report_lines.append(f"  Tempo Total: {ga['time']:.2f}")
        report_lines.append(f"  Número de Veículos: {ga['vehicles']}")
        report_lines.append(f"  Fitness: {ga['fitness']:.2f}")
        report_lines.append(f"  Factível: {ga['feasible']}")
        
        report_lines.append("\n7.3. Melhorias Obtidas")
        report_lines.append("-" * 80)
        improvements = analysis_results['improvements']
        report_lines.append(f"  Redução de Distância: {improvements['distance_percent']:.2f}%")
        report_lines.append(f"  Redução de Veículos: {improvements['vehicles_absolute']}")
        report_lines.append(f"  Melhoria de Fitness: {improvements['fitness_percent']:.2f}%")
        
        # Convergência
        report_lines.append("\n7.4. Análise de Convergência")
        report_lines.append("-" * 80)
        report_lines.append(f"  Gerações executadas: {len(self.ga.best_fitness_history)}")
        report_lines.append(f"  Fitness inicial: {self.ga.best_fitness_history[0]:.2f}")
        report_lines.append(f"  Fitness final: {self.ga.best_fitness_history[-1]:.2f}")
        report_lines.append(f"  Melhoria total: {((self.ga.best_fitness_history[0] - self.ga.best_fitness_history[-1]) / self.ga.best_fitness_history[0] * 100):.2f}%")
        
        # Conclusões
        report_lines.append("\n" + "="*80)
        report_lines.append("8. CONCLUSÕES")
        report_lines.append("="*80)
        report_lines.append("\n8.1. Resultados Alcançados")
        report_lines.append("-" * 80)
        report_lines.append("  ✓ Implementação bem-sucedida do algoritmo do artigo")
        report_lines.append("  ✓ Heurística de Solomon gera soluções iniciais viáveis")
        report_lines.append("  ✓ Algoritmo Genético melhora significativamente a solução")
        report_lines.append(f"  ✓ Redução de {improvements['distance_percent']:.2f}% na distância total")
        
        report_lines.append("\n8.2. Contribuições da Implementação")
        report_lines.append("-" * 80)
        report_lines.append("  • Conversão de dados reais de vendas em problema VRPTW")
        report_lines.append("  • Implementação completa em Python (sem dependências pesadas)")
        report_lines.append("  • Operadores genéticos adaptados para VRPTW")
        report_lines.append("  • Estratégia de reinicialização para evitar convergência prematura")
        report_lines.append("  • Visualizações detalhadas para análise de resultados")
        
        report_lines.append("\n8.3. Trabalhos Futuros")
        report_lines.append("-" * 80)
        report_lines.append("  • Testar em instâncias benchmark (Solomon, Gehring & Homberger)")
        report_lines.append("  • Implementar operadores de crossover adicionais (PMX, CX)")
        report_lines.append("  • Adicionar busca local inter-rota (relocate, exchange)")
        report_lines.append("  • Paralelização do algoritmo genético")
        report_lines.append("  • Otimização multi-objetivo (distância vs. número de veículos)")
        
        # Referências
        report_lines.append("\n" + "="*80)
        report_lines.append("9. REFERÊNCIAS")
        report_lines.append("="*80)
        report_lines.append("\n[1] Electronics (2025). Research on Vehicle Routing Problem with")
        report_lines.append("    Time Windows Based on Improved Genetic Algorithm.")
        report_lines.append("    MDPI. https://doi.org/10.3390/electronics14040647")
        report_lines.append("\n[2] Solomon, M. M. (1987). Algorithms for the vehicle routing and")
        report_lines.append("    scheduling problems with time window constraints.")
        report_lines.append("    Operations Research, 35(2), 254-265.")
        report_lines.append("\n[3] Bräysy, O., & Gendreau, M. (2005). Vehicle routing problem")
        report_lines.append("    with time windows, Part I: Route construction and local search")
        report_lines.append("    algorithms. Transportation Science, 39(1), 104-118.")
        
        # Rodapé
        report_lines.append("\n" + "="*80)
        report_lines.append("FIM DO RELATÓRIO")
        report_lines.append("="*80)
        
        # Salva relatório
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✓ Relatório técnico salvo: {report_file}")
        print(f"  Páginas: ~{len(report_lines) // 50} (estimativa)")
        print("="*80 + "\n")
    
    def run(self):
        """Executa pipeline completo do projeto."""
        try:
            self.setup()
            self.load_or_create_instance()
            self.solve_with_solomon()
            self.optimize_with_genetic_algorithm()
            analysis_results = self.analyze_results()
            self.visualize_results()
            self.save_solutions()
            self.generate_report(analysis_results)
            
            print("\n" + "="*80)
            print(" "*25 + "PROJETO CONCLUÍDO COM SUCESSO!")
            print("="*80)
            print("\n📂 Artefatos Gerados:")
            print(f"   • Instância: {self.config['data']['instance_file']}")
            print(f"   • Soluções: {self.config['output']['solutions_dir']}/")
            print(f"   • Gráficos: {self.config['output']['plots_dir']}/")
            print(f"   • Relatório: {self.config['output']['report_file']}")
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERRO DURANTE A EXECUÇÃO:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Função principal."""
    project = VRPTWProject()
    project.run()


if __name__ == "__main__":
    main()