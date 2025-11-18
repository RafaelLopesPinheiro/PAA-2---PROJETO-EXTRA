"""
Visualization Module for VRPTW Solutions
Author: Rafael Lopes Pinheiro
Date: 2025-11-18
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List
import os

# Importa apenas o necessário de utils
from src.utils import VRPTWInstance


class VRPTWVisualizer:
    """Classe para visualização de soluções VRPTW."""
    
    def __init__(self, instance: VRPTWInstance):
        self.instance = instance
        sns.set_style("whitegrid")
        self.colors = plt.cm.tab20.colors
    
    def plot_solution(self, solution, save_path: str = None, title: str = "Solução VRPTW"):
        """
        Plota solução do VRPTW.
        
        Parameters:
        -----------
        solution : Solution
            Solução a ser plotada (aceita qualquer objeto com atributo .vehicles)
        save_path : str, optional
            Caminho para salvar figura
        title : str
            Título do gráfico
        """
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Plota depot
        ax.scatter(self.instance.depot.x, self.instance.depot.y, 
                  c='red', s=400, marker='s', label='Depot', 
                  zorder=10, edgecolors='black', linewidth=2)
        
        # Plota clientes
        customer_x = [c.x for c in self.instance.customers]
        customer_y = [c.y for c in self.instance.customers]
        ax.scatter(customer_x, customer_y, c='lightblue', s=200, 
                  marker='o', label='Clientes', zorder=5,
                  edgecolors='black', linewidth=1)
        
        # Anota IDs dos clientes
        for customer in self.instance.customers:
            ax.annotate(str(customer.id), (customer.x, customer.y),
                       ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Plota rotas de cada veículo
        for idx, vehicle in enumerate(solution.vehicles):
            if not vehicle.route:
                continue
            
            color = self.colors[idx % len(self.colors)]
            
            # Depot -> primeiro cliente
            route = [self.instance.depot] + vehicle.route + [self.instance.depot]
            
            x_coords = [loc.x for loc in route]
            y_coords = [loc.y for loc in route]
            
            ax.plot(x_coords, y_coords, c=color, linewidth=2, 
                   alpha=0.7, marker='o', markersize=4,
                   label=f'Veículo {vehicle.id} (dist={vehicle.total_distance:.1f})')
        
        ax.set_xlabel('Coordenada X', fontsize=12)
        ax.set_ylabel('Coordenada Y', fontsize=12)
        ax.set_title(f'{title}\n'
                    f'Distância Total: {solution.total_distance:.2f} | '
                    f'Veículos: {solution.num_vehicles} | '
                    f'Fitness: {solution.fitness:.2f}',
                    fontsize=14, fontweight='bold')
        
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo em: {save_path}")
        
        plt.show()
    
    def plot_convergence(self, best_fitness_history: List[float],
                        avg_fitness_history: List[float],
                        save_path: str = None):
        """
        Plota convergência do algoritmo genético.
        
        Parameters:
        -----------
        best_fitness_history : List[float]
            Histórico do melhor fitness
        avg_fitness_history : List[float]
            Histórico do fitness médio
        save_path : str, optional
            Caminho para salvar figura
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        generations = range(len(best_fitness_history))
        
        # Gráfico 1: Fitness
        ax1.plot(generations, best_fitness_history, 'b-', linewidth=2, 
                label='Melhor Fitness')
        ax1.plot(generations, avg_fitness_history, 'r--', linewidth=2, 
                label='Fitness Médio', alpha=0.7)
        ax1.set_xlabel('Geração', fontsize=12)
        ax1.set_ylabel('Fitness', fontsize=12)
        ax1.set_title('Convergência do Algoritmo Genético', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Melhoria percentual
        if len(best_fitness_history) > 1:
            initial = best_fitness_history[0]
            improvement = [(initial - f) / initial * 100 for f in best_fitness_history]
            
            ax2.plot(generations, improvement, 'g-', linewidth=2)
            ax2.set_xlabel('Geração', fontsize=12)
            ax2.set_ylabel('Melhoria (%)', fontsize=12)
            ax2.set_title('Melhoria Percentual em Relação à Solução Inicial', 
                         fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico de convergência salvo em: {save_path}")
        
        plt.show()
    
    def plot_comparison(self, solutions: List, labels: List[str],
                       save_path: str = None):
        """
        Compara múltiplas soluções.
        
        Parameters:
        -----------
        solutions : List
            Lista de soluções (objetos com atributos distance, vehicles, fitness)
        labels : List[str]
            Rótulos para cada solução
        save_path : str, optional
            Caminho para salvar figura
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        distances = [s.total_distance for s in solutions]
        vehicles = [s.num_vehicles for s in solutions]
        fitness = [s.fitness for s in solutions]
        
        # Distância total
        axes[0].bar(labels, distances, color='steelblue', edgecolor='black')
        axes[0].set_ylabel('Distância Total', fontsize=11)
        axes[0].set_title('Comparação de Distância', fontsize=12, fontweight='bold')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Número de veículos
        axes[1].bar(labels, vehicles, color='coral', edgecolor='black')
        axes[1].set_ylabel('Número de Veículos', fontsize=11)
        axes[1].set_title('Comparação de Veículos', fontsize=12, fontweight='bold')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(axis='y', alpha=0.3)
        
        # Fitness
        axes[2].bar(labels, fitness, color='lightgreen', edgecolor='black')
        axes[2].set_ylabel('Fitness', fontsize=11)
        axes[2].set_title('Comparação de Fitness', fontsize=12, fontweight='bold')
        axes[2].tick_params(axis='x', rotation=45)
        axes[2].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico de comparação salvo em: {save_path}")
        
        plt.show()
    
    def plot_time_windows(self, solution, save_path: str = None):
        """
        Visualização MELHORADA e COMPACTA das janelas de tempo.
        VERSÃO FINAL: Tamanho otimizado e centralizado.
        """
        # Calcula estatísticas para ajustar escala
        all_ready_times = [c.ready_time for v in solution.vehicles for c in v.route]
        all_due_times = [c.due_time for v in solution.vehicles for c in v.route]
        
        min_time = min(all_ready_times) if all_ready_times else 0
        max_time = max(all_due_times) if all_due_times else 480
        
        # Adiciona margem de 5%
        time_range = max_time - min_time
        min_time = max(0, min_time - time_range * 0.05)
        max_time = min(480, max_time + time_range * 0.05)
        
        # TAMANHO REDUZIDO (era 20x14)
        fig, ax = plt.subplots(figsize=(16, 10))
        
        y_pos = 0
        vehicle_data = []
        colors = plt.cm.tab10.colors
        
        # Estatísticas de violações
        total_violations = 0
        total_customers = 0
        
        for v_idx, vehicle in enumerate(solution.vehicles):
            if not vehicle.route:
                continue
            
            color = colors[v_idx % len(colors)]
            vehicle_start_y = y_pos
            
            current_time = 0.0
            current_loc = self.instance.depot
            
            violations_in_vehicle = 0
            
            for customer in vehicle.route:
                total_customers += 1
                travel_time = current_loc.distance_to(customer)
                arrival_time = current_time + travel_time
                
                # Janela de tempo (barra azul)
                window_width = customer.due_time - customer.ready_time
                ax.barh(y_pos, window_width, 
                    left=customer.ready_time, 
                    height=0.7,
                    color='lightblue', 
                    alpha=0.6, 
                    edgecolor='blue',
                    linewidth=2)
                
                # Tempo de atendimento
                service_start = max(arrival_time, customer.ready_time)
                service_end = service_start + customer.service_time
                
                # VERIFICA VIOLAÇÃO
                is_late = arrival_time > customer.due_time
                
                if is_late:
                    violations_in_vehicle += 1
                    total_violations += 1
                    marker_color = 'red'
                    line_color = 'red'
                    linewidth = 7
                    markersize = 12
                    # X vermelho
                    ax.text(arrival_time, y_pos, '❌', 
                        fontsize=14, ha='center', va='center',
                        color='red', fontweight='bold')
                else:
                    marker_color = color
                    line_color = color
                    linewidth = 5
                    markersize = 9
                
                # Linha de atendimento
                ax.plot([service_start, service_end], 
                    [y_pos, y_pos], 
                    color=line_color,
                    linewidth=linewidth,
                    marker='o',
                    markersize=markersize,
                    markerfacecolor=marker_color,
                    markeredgecolor='black',
                    markeredgewidth=1.5,
                    alpha=0.9)
                
                # Label do cliente (à direita da janela)
                label_x = customer.due_time + time_range * 0.01
                ax.text(label_x, y_pos, f'C{customer.id}', 
                    va='center', ha='left',
                    fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='white',
                                edgecolor='gray',
                                alpha=0.8))
                
                # CORRIGIDO: Marca tempo de espera DENTRO da visualização
                if arrival_time < customer.ready_time:
                    wait_time = customer.ready_time - arrival_time
                    # Posiciona ACIMA da linha, dentro do gráfico
                    wait_x = (arrival_time + customer.ready_time) / 2
                    
                    # Só mostra se houver espaço
                    if wait_x > min_time:
                        ax.plot([arrival_time, customer.ready_time],
                            [y_pos, y_pos],
                            color='orange',
                            linestyle='--',
                            linewidth=3,
                            alpha=0.7)
                        ax.text(wait_x, y_pos + 0.35, 
                            f'⏱{wait_time:.0f}min', 
                            fontsize=8, color='orange',
                            ha='center', fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2',
                                        facecolor='white',
                                        alpha=0.7))
                
                # Atualiza tempo
                current_time = service_end
                current_loc = customer
                y_pos += 1
            
            # Dados do veículo
            vehicle_data.append({
                'y_end': y_pos,
                'y_start': vehicle_start_y,
                'y_mid': (vehicle_start_y + y_pos) / 2,
                'id': vehicle.id,
                'n_customers': len(vehicle.route),
                'color': color,
                'violations': violations_in_vehicle
            })
            
            y_pos += 0.5  # Espaço entre veículos
        
        # CORRIGIDO: Desenha labels dos veículos DENTRO do gráfico
        for vdata in vehicle_data:
            # Linha separadora
            ax.axhline(y=vdata['y_end'] - 0.25, 
                    color='black', 
                    linestyle='-', 
                    linewidth=2, 
                    alpha=0.3)
            
            # CORRIGIDO: Box do veículo na PRIMEIRA linha do veículo
            violation_text = f"\n⚠️ {vdata['violations']} atrasos" if vdata['violations'] > 0 else ""
            
            # Posiciona no início da linha (logo após o eixo Y)
            label_x = min_time + time_range * 0.02
            
            ax.text(label_x, 
                vdata['y_mid'], 
                f"Veículo {vdata['id']}\n({vdata['n_customers']} clientes){violation_text}",
                fontsize=11, 
                fontweight='bold',
                ha='left',  # ALINHAMENTO À ESQUERDA
                va='center',
                bbox=dict(boxstyle='round,pad=0.6', 
                            facecolor=vdata['color'], 
                            edgecolor='black',
                            linewidth=2,
                            alpha=0.4))
            
            # ADICIONA: Linha vertical tracejada separando label da área de dados
            separator_x = min_time + time_range * 0.1
            ax.axvline(x=separator_x, 
                    ymin=(vdata['y_start'] - 0.5) / y_pos,
                    ymax=(vdata['y_end'] - 0.25) / y_pos,
                    color='gray',
                    linestyle=':',
                    linewidth=1,
                    alpha=0.3)
        
        # Grid vertical (horas)
        hour_start = int(min_time // 60)
        hour_end = int(max_time // 60) + 1
        
        for hour in range(hour_start, hour_end + 1):
            minute = hour * 60
            if min_time <= minute <= max_time:
                ax.axvline(x=minute, color='gray', linestyle=':', 
                        linewidth=1, alpha=0.4)
                ax.text(minute, -0.8, f'{hour}h', 
                    ha='center', fontsize=10, 
                    color='gray', fontweight='bold')
        
        # CORRIGIDO: Ajusta limites para centralizar
        ax.set_xlim(min_time, max_time)
        ax.set_ylim(-1, y_pos)
        
        # Labels
        ax.set_xlabel('Tempo (minutos desde início da operação)', 
                    fontsize=13, fontweight='bold', labelpad=10)
        ax.set_ylabel('Clientes (agrupados por veículo)', 
                    fontsize=13, fontweight='bold', labelpad=10)
        
        # Título com estatísticas
        violation_rate = (total_violations / total_customers * 100) if total_customers > 0 else 0
        status = "✅ TODAS OK" if total_violations == 0 else f"❌ {total_violations} VIOLAÇÕES"
        
        ax.set_title(f'Cumprimento das Janelas de Tempo - {status}\n'
                    f'{total_customers} clientes | Taxa de violação: {violation_rate:.1f}%\n'
                    f'Barras azuis = Janela permitida | Linhas coloridas = Atendimento real',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Legenda
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        
        legend_elements = [
            Patch(facecolor='lightblue', edgecolor='blue', linewidth=2,
                label='Janela de tempo permitida'),
            Line2D([0], [0], color='green', linewidth=5, marker='o', markersize=9,
                label='□ Atendimento OK (dentro da janela)'),
            Line2D([0], [0], color='red', linewidth=5, marker='o', markersize=9,
                label='□ VIOLAÇÃO (chegou atrasado)'),
            Line2D([0], [0], color='orange', linewidth=3, linestyle='--',
                label='⏱ Tempo de espera'),
        ]
        
        ax.legend(handles=legend_elements, 
                loc='upper right', 
                fontsize=10, 
                framealpha=0.95, 
                shadow=True,
                edgecolor='black',
                fancybox=True)
        
        ax.grid(axis='x', alpha=0.3, linewidth=0.8)
        ax.set_yticks([])
        
        # Remove spines superiores
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Gráfico salvo: {save_path}")
            print(f"  Violações detectadas: {total_violations}/{total_customers}")
        
        plt.show()


if __name__ == "__main__":
    # Teste
    from src.utils import load_instance
    from src.heuristics import SolomonInsertion
    from src.genetic_algorithm import Solution
    
    instance = load_instance('data/processed/vrptw_instances.json')
    solomon = SolomonInsertion(instance)
    vehicles = solomon.construct_solution()
    solution = Solution(vehicles)
    
    visualizer = VRPTWVisualizer(instance)
    visualizer.plot_solution(solution, title="Solução Inicial (Solomon)")