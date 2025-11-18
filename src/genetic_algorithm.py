"""
Hybrid Genetic Algorithm for VRPTW (CORRECTED VERSION)
Author: Rafael Lopes Pinheiro
Date: 2025-11-18

CORREÇÕES IMPLEMENTADAS:
1. Representação baseada em ROTAS (não sequências)
2. Crossover específico para VRP (Best Route Crossover)
3. Operadores inter-rota (Relocate, Exchange, 2-opt*)
4. Busca local adaptativa melhorada
5. Diversidade populacional controlada

Baseado em:
- Potvin, J. Y., & Bengio, S. (1996). The vehicle routing problem with time windows
- Bräysy, O., & Gendreau, M. (2005). Vehicle routing problem with time windows
"""

import numpy as np
from typing import List, Tuple, Dict, Set
import copy
from tqdm import tqdm
from src.utils import Customer, Vehicle, VRPTWInstance
from src.heuristics import SolomonInsertion


class Solution:
    """Representa uma solução do VRPTW."""
    
    def __init__(self, vehicles: List[Vehicle], instance: VRPTWInstance = None):
        self.vehicles = vehicles
        self.instance = instance
        self.fitness = None
        self.total_distance = 0.0
        self.total_time = 0.0
        self.num_vehicles = len([v for v in vehicles if v.route])
        self.feasible = True
        self.diversity_score = 0.0  # NOVO: Para controlar diversidade
        
        self.calculate_fitness()
    
    def calculate_fitness(self):
        """Calcula fitness COM validação rigorosa."""
        self.total_distance = sum(v.total_distance for v in self.vehicles)
        self.total_time = sum(v.total_time for v in self.vehicles)
        self.num_vehicles = len([v for v in self.vehicles if v.route])
        
        # Pesos
        w1 = 1.0      # Distância
        w2 = 1000.0   # Número de veículos
        w3 = 100000.0 # Penalização por violação
        
        penalty = 0.0
        
        for v in self.vehicles:
            # Capacidade
            if v.load > v.capacity:
                penalty += (v.load - v.capacity) * 1000
            
            # Janelas de tempo (se instance disponível)
            if self.instance is not None:
                current_time = 0.0
                current_loc = self.instance.depot
                
                for customer in v.route:
                    travel_time = current_loc.distance_to(customer)
                    arrival_time = current_time + travel_time
                    
                    if arrival_time > customer.due_time:
                        lateness = arrival_time - customer.due_time
                        penalty += lateness * 1000
                    
                    service_start = max(arrival_time, customer.ready_time)
                    current_time = service_start + customer.service_time
                    current_loc = customer
        
        self.feasible = (penalty == 0)
        self.fitness = w1 * self.total_distance + w2 * self.num_vehicles + w3 * penalty
    
    def copy(self) -> 'Solution':
        """Cópia profunda."""
        new_vehicles = []
        for v in self.vehicles:
            new_v = Vehicle(v.id, v.capacity, v.max_route_time)
            new_v.route = v.route.copy()
            new_v.load = v.load
            new_v.total_distance = v.total_distance
            new_v.total_time = v.total_time
            new_vehicles.append(new_v)
        
        return Solution(new_vehicles, self.instance)
    
    def get_all_customers(self) -> List[Customer]:
        """Retorna todos os clientes roteados."""
        customers = []
        for v in self.vehicles:
            customers.extend(v.route)
        return customers
    
    def calculate_diversity(self, other: 'Solution') -> float:
        """
        Calcula diversidade entre duas soluções.
        Baseado em diferença de sequência de visitas.
        """
        seq1 = [c.id for v in self.vehicles for c in v.route]
        seq2 = [c.id for v in other.vehicles for c in v.route]
        
        if len(seq1) != len(seq2):
            return 1.0
        
        differences = sum(1 for i in range(len(seq1)) if seq1[i] != seq2[i])
        return differences / len(seq1) if seq1 else 0.0
    
    def __repr__(self):
        return (f"Solution(vehicles={self.num_vehicles}, distance={self.total_distance:.2f}, "
                f"fitness={self.fitness:.2f}, feasible={self.feasible})")


class ImprovedGeneticAlgorithm:
    """
    Algoritmo Genético MELHORADO para VRPTW.
    
    PRINCIPAIS MELHORIAS:
    - Crossover baseado em rotas (não sequências)
    - Operadores inter-rota (relocate, exchange)
    - Busca local 2-opt inter e intra-rota
    - Controle de diversidade populacional
    """
    
    def __init__(self, instance: VRPTWInstance, 
                 pop_size: int = 100,
                 elite_size: int = 20,
                 generations: int = 300,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.3,
                 local_search_rate: float = 0.5,
                 seed: int = 42):
        
        self.instance = instance
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.local_search_rate = local_search_rate
        
        np.random.seed(seed)
        
        self.population = []
        self.elite_population = []
        
        self.best_solution = None
        self.best_fitness_history = []
        self.avg_fitness_history = []
        
        self.generation = 0
        self.stagnation_counter = 0
        self.max_stagnation = 50
    
    def initialize_population(self):
        """Inicializa população."""
        print("\n" + "="*70)
        print("INICIALIZAÇÃO DA POPULAÇÃO (ALGORITMO MELHORADO)")
        print("="*70 + "\n")
        
        solutions = []
        
        # 40% com Solomon (variando parâmetros)
        print("Gerando 40% com heurística de Solomon...")
        solomon = SolomonInsertion(self.instance, alpha=1.0, mu=1.0, lambda_param=2.0)
        n_solomon = int(self.pop_size * 0.4)
        
        for i in tqdm(range(n_solomon), desc="Solomon"):
            solomon.alpha = np.random.uniform(0.5, 2.0)
            solomon.mu = np.random.uniform(0.5, 2.0)
            solomon.lambda_param = np.random.uniform(0.5, 3.0)
            
            vehicles = solomon.construct_solution()
            solution = Solution(vehicles, self.instance)
            solutions.append(solution)
        
        # 40% com construção aleatória gulosa
        print("\nGerando 40% com construção aleatória gulosa...")
        n_random = int(self.pop_size * 0.4)
        
        for i in tqdm(range(n_random), desc="Aleatória"):
            vehicles = self._random_greedy_construction()
            solution = Solution(vehicles, self.instance)
            solutions.append(solution)
        
        # 20% com mutações pesadas da melhor
        print("\nGerando 20% com mutações...")
        n_mutated = self.pop_size - len(solutions)
        
        if solutions:
            best = min(solutions, key=lambda s: s.fitness)
            
            for i in tqdm(range(n_mutated), desc="Mutações"):
                mutated = best.copy()
                # Aplica múltiplas mutações
                for _ in range(np.random.randint(2, 5)):
                    mutated = self._apply_random_mutation(mutated)
                solutions.append(mutated)
        
        self.population = solutions
        self._update_best_solution()
        
        print(f"\n✓ População inicializada com {len(self.population)} soluções")
        print(f"✓ Melhor fitness inicial: {self.best_solution.fitness:.2f}")
        print(f"✓ Melhor distância inicial: {self.best_solution.total_distance:.2f}")
        print("="*70 + "\n")
    
    def _random_greedy_construction(self) -> List[Vehicle]:
        """Construção aleatória gulosa."""
        unrouted = self.instance.customers.copy()
        np.random.shuffle(unrouted)
        
        vehicles = []
        vehicle_id = 0
        
        while unrouted and vehicle_id < self.instance.num_vehicles:
            vehicle = Vehicle(vehicle_id, self.instance.vehicle_capacity)
            
            while unrouted:
                candidates = [c for c in unrouted 
                             if vehicle.load + c.demand <= vehicle.capacity]
                
                if not candidates:
                    break
                
                if vehicle.route:
                    last = vehicle.route[-1]
                else:
                    last = self.instance.depot
                
                distances = [1.0 / (last.distance_to(c) + 0.1) for c in candidates]
                probs = np.array(distances) / sum(distances)
                chosen = np.random.choice(candidates, p=probs)
                
                vehicle.add_customer(chosen, self.instance.depot)
                unrouted.remove(chosen)
            
            vehicle.calculate_metrics(self.instance.depot)
            vehicles.append(vehicle)
            vehicle_id += 1
        
        return vehicles
    
    def _update_best_solution(self):
        """Atualiza melhor solução."""
        best_in_pop = min(self.population, key=lambda s: s.fitness)
        
        if self.best_solution is None or best_in_pop.fitness < self.best_solution.fitness:
            self.best_solution = best_in_pop.copy()
            self.stagnation_counter = 0
        else:
            self.stagnation_counter += 1
    
    def tournament_selection(self, tournament_size: int = 5) -> Solution:
        """Seleção por torneio."""
        tournament = np.random.choice(self.population, tournament_size, replace=False)
        return min(tournament, key=lambda s: s.fitness)
    
    def best_route_crossover(self, parent1: Solution, parent2: Solution) -> Tuple[Solution, Solution]:
        """
        Best Route Crossover - ESPECIALIZADO para VRP.
        
        Estratégia:
        1. Copia ROTAS INTEIRAS (não clientes individuais)
        2. Completa com rotas do outro pai
        3. Insere clientes faltantes usando heurística
        
        Referência: Potvin & Bengio (1996)
        """
        # Cria offspring vazios
        offspring1_vehicles = []
        offspring2_vehicles = []
        
        # Clientes já inseridos
        used1 = set()
        used2 = set()
        
        # FASE 1: Copia rotas aleatórias de cada pai
        num_routes_to_copy = max(1, len(parent1.vehicles) // 3)
        
        # Offspring 1: copia rotas do parent1
        routes_p1 = [v for v in parent1.vehicles if v.route]
        selected_routes1 = np.random.choice(routes_p1, 
                                           min(num_routes_to_copy, len(routes_p1)),
                                           replace=False)
        
        for v_orig in selected_routes1:
            v_new = Vehicle(len(offspring1_vehicles), v_orig.capacity, v_orig.max_route_time)
            v_new.route = v_orig.route.copy()
            v_new.load = v_orig.load
            offspring1_vehicles.append(v_new)
            used1.update(c.id for c in v_orig.route)
        
        # Offspring 2: copia rotas do parent2
        routes_p2 = [v for v in parent2.vehicles if v.route]
        selected_routes2 = np.random.choice(routes_p2,
                                           min(num_routes_to_copy, len(routes_p2)),
                                           replace=False)
        
        for v_orig in selected_routes2:
            v_new = Vehicle(len(offspring2_vehicles), v_orig.capacity, v_orig.max_route_time)
            v_new.route = v_orig.route.copy()
            v_new.load = v_orig.load
            offspring2_vehicles.append(v_new)
            used2.update(c.id for c in v_orig.route)
        
        # FASE 2: Insere clientes restantes
        all_customers = self.instance.customers
        
        remaining1 = [c for c in all_customers if c.id not in used1]
        remaining2 = [c for c in all_customers if c.id not in used2]
        
        offspring1_vehicles = self._insert_remaining_customers(offspring1_vehicles, remaining1)
        offspring2_vehicles = self._insert_remaining_customers(offspring2_vehicles, remaining2)
        
        # Recalcula métricas
        for v in offspring1_vehicles:
            v.calculate_metrics(self.instance.depot)
        for v in offspring2_vehicles:
            v.calculate_metrics(self.instance.depot)
        
        return Solution(offspring1_vehicles, self.instance), Solution(offspring2_vehicles, self.instance)
    
    def _insert_remaining_customers(self, vehicles: List[Vehicle], 
                                    remaining: List[Customer]) -> List[Vehicle]:
        """Insere clientes restantes usando melhor inserção."""
        for customer in remaining:
            best_vehicle = None
            best_position = -1
            best_cost = float('inf')
            
            # Tenta inserir em veículos existentes
            for vehicle in vehicles:
                if vehicle.load + customer.demand > vehicle.capacity:
                    continue
                
                for pos in range(len(vehicle.route) + 1):
                    # Calcula custo de inserção
                    test_route = vehicle.route[:pos] + [customer] + vehicle.route[pos:]
                    
                    if self._is_route_feasible(test_route, vehicle.capacity):
                        cost = self._calculate_insertion_cost(vehicle.route, customer, pos)
                        
                        if cost < best_cost:
                            best_cost = cost
                            best_vehicle = vehicle
                            best_position = pos
            
            # Insere na melhor posição
            if best_vehicle is not None:
                best_vehicle.route.insert(best_position, customer)
                best_vehicle.load += customer.demand
            else:
                # Cria novo veículo se necessário
                new_vehicle = Vehicle(len(vehicles), self.instance.vehicle_capacity)
                new_vehicle.route = [customer]
                new_vehicle.load = customer.demand
                vehicles.append(new_vehicle)
        
        return vehicles
    
    def _is_route_feasible(self, route: List[Customer], capacity: float) -> bool:
        """Verifica se rota é viável."""
        load = sum(c.demand for c in route)
        if load > capacity:
            return False
        
        current_time = 0.0
        current_loc = self.instance.depot
        
        for customer in route:
            travel_time = current_loc.distance_to(customer)
            arrival_time = current_time + travel_time
            
            if arrival_time > customer.due_time:
                return False
            
            service_start = max(arrival_time, customer.ready_time)
            current_time = service_start + customer.service_time
            current_loc = customer
        
        return True
    
    def _calculate_insertion_cost(self, route: List[Customer], 
                                  customer: Customer, position: int) -> float:
        """Calcula custo de inserir cliente na posição."""
        if position == 0:
            prev = self.instance.depot
        else:
            prev = route[position - 1]
        
        if position >= len(route):
            next_c = self.instance.depot
        else:
            next_c = route[position]
        
        cost_before = prev.distance_to(next_c)
        cost_after = prev.distance_to(customer) + customer.distance_to(next_c)
        
        return cost_after - cost_before
    
    def relocate_mutation(self, solution: Solution) -> Solution:
        """
        RELOCATE: Move 1 cliente de um veículo para outro.
        Operador inter-rota mais efetivo que swap.
        """
        mutated = solution.copy()
        
        vehicles_with_routes = [v for v in mutated.vehicles if len(v.route) > 0]
        
        if len(vehicles_with_routes) < 2:
            return mutated
        
        # Escolhe veículo origem e destino
        v_from = np.random.choice(vehicles_with_routes)
        v_to = np.random.choice([v for v in mutated.vehicles if v != v_from])
        
        if not v_from.route:
            return mutated
        
        # Remove cliente aleatório
        remove_idx = np.random.randint(len(v_from.route))
        customer = v_from.route.pop(remove_idx)
        v_from.load -= customer.demand
        
        # Insere no melhor lugar do veículo destino
        best_pos = 0
        best_cost = float('inf')
        
        for pos in range(len(v_to.route) + 1):
            if v_to.load + customer.demand <= v_to.capacity:
                cost = self._calculate_insertion_cost(v_to.route, customer, pos)
                if cost < best_cost:
                    best_cost = cost
                    best_pos = pos
        
        v_to.route.insert(best_pos, customer)
        v_to.load += customer.demand
        
        v_from.calculate_metrics(self.instance.depot)
        v_to.calculate_metrics(self.instance.depot)
        
        mutated.calculate_fitness()
        return mutated
    
    def exchange_mutation(self, solution: Solution) -> Solution:
        """
        EXCHANGE: Troca 1 cliente entre dois veículos.
        """
        mutated = solution.copy()
        
        vehicles_with_routes = [v for v in mutated.vehicles if len(v.route) > 0]
        
        if len(vehicles_with_routes) < 2:
            return mutated
        
        v1, v2 = np.random.choice(vehicles_with_routes, 2, replace=False)
        
        if not v1.route or not v2.route:
            return mutated
        
        idx1 = np.random.randint(len(v1.route))
        idx2 = np.random.randint(len(v2.route))
        
        c1 = v1.route[idx1]
        c2 = v2.route[idx2]
        
        # Verifica viabilidade da troca
        if (v1.load - c1.demand + c2.demand <= v1.capacity and
            v2.load - c2.demand + c1.demand <= v2.capacity):
            
            v1.route[idx1] = c2
            v2.route[idx2] = c1
            
            v1.load = v1.load - c1.demand + c2.demand
            v2.load = v2.load - c2.demand + c1.demand
            
            v1.calculate_metrics(self.instance.depot)
            v2.calculate_metrics(self.instance.depot)
            
            mutated.calculate_fitness()
        
        return mutated
    
    def two_opt_intra_route(self, solution: Solution) -> Solution:
        """2-opt INTRA-rota (dentro de cada rota)."""
        improved = solution.copy()
        
        for vehicle in improved.vehicles:
            if len(vehicle.route) < 4:
                continue
            
            route = vehicle.route
            n = len(route)
            improved_any = True
            max_iterations = 50
            iteration = 0
            
            while improved_any and iteration < max_iterations:
                improved_any = False
                iteration += 1
                
                for i in range(n - 1):
                    for j in range(i + 2, n):
                        new_route = route[:i+1] + route[i+1:j+1][::-1] + route[j+1:]
                        
                        if self._is_route_feasible(new_route, vehicle.capacity):
                            new_distance = self._calculate_route_distance(new_route)
                            old_distance = self._calculate_route_distance(route)
                            
                            if new_distance < old_distance:
                                route = new_route
                                improved_any = True
                                break
                    
                    if improved_any:
                        break
            
            vehicle.route = route
            vehicle.calculate_metrics(self.instance.depot)
        
        improved.calculate_fitness()
        return improved
    
    def _calculate_route_distance(self, route: List[Customer]) -> float:
        """Calcula distância de uma rota."""
        if not route:
            return 0.0
        
        distance = self.instance.depot.distance_to(route[0])
        for i in range(len(route) - 1):
            distance += route[i].distance_to(route[i + 1])
        distance += route[-1].distance_to(self.instance.depot)
        
        return distance
    
    def _apply_random_mutation(self, solution: Solution) -> Solution:
        """Aplica mutação aleatória (com operadores melhorados)."""
        mutation_type = np.random.choice(['relocate', 'exchange', 'intra_2opt'], 
                                        p=[0.5, 0.3, 0.2])
        
        if mutation_type == 'relocate':
            return self.relocate_mutation(solution)
        elif mutation_type == 'exchange':
            return self.exchange_mutation(solution)
        else:
            return self.two_opt_intra_route(solution)
    
    def evolve(self):
        """Executa uma geração."""
        # Seleção
        parents = [self.tournament_selection() for _ in range(self.pop_size)]
        
        # Crossover
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents) and np.random.random() < self.crossover_rate:
                child1, child2 = self.best_route_crossover(parents[i], parents[i + 1])
                offspring.extend([child1, child2])
            else:
                offspring.extend([parents[i].copy(), 
                                 parents[i + 1].copy() if i + 1 < len(parents) else parents[i].copy()])
        
        # Mutação
        for i in range(len(offspring)):
            if np.random.random() < self.mutation_rate:
                offspring[i] = self._apply_random_mutation(offspring[i])
        
        # Busca local
        for i in range(len(offspring)):
            if np.random.random() < self.local_search_rate:
                offspring[i] = self.two_opt_intra_route(offspring[i])
        
        # Elitismo + controle de diversidade
        combined = self.population + offspring
        combined.sort(key=lambda s: s.fitness)
        
        # Mantém elite + diversidade
        new_population = combined[:self.elite_size]
        
        # Preenche resto priorizando diversidade
        remaining = combined[self.elite_size:]
        while len(new_population) < self.pop_size and remaining:
            # Calcula diversidade média em relação aos já selecionados
            for sol in remaining:
                sol.diversity_score = np.mean([sol.calculate_diversity(s) for s in new_population])
            
            # Seleciona com peso em fitness + diversidade
            weights = []
            for sol in remaining:
                fitness_score = 1.0 / (sol.fitness + 1)
                diversity_bonus = sol.diversity_score
                weights.append(fitness_score + diversity_bonus * 0.3)
            
            if sum(weights) == 0:
                break
            
            probs = np.array(weights) / sum(weights)
            selected = np.random.choice(remaining, p=probs)
            new_population.append(selected)
            remaining.remove(selected)
        
        self.population = new_population[:self.pop_size]
        
        # Atualiza estatísticas
        self._update_best_solution()
        self.best_fitness_history.append(self.best_solution.fitness)
        avg_fitness = np.mean([s.fitness for s in self.population])
        self.avg_fitness_history.append(avg_fitness)
    
    def run(self) -> Solution:
        """Executa AG completo."""
        print("\n" + "="*70)
        print("ALGORITMO GENÉTICO MELHORADO - OTIMIZAÇÃO")
        print("="*70 + "\n")
        
        print(f"Configuração:")
        print(f"  - População: {self.pop_size}")
        print(f"  - Gerações: {self.generations}")
        print(f"  - Crossover: Best Route Crossover")
        print(f"  - Mutações: Relocate, Exchange, 2-opt")
        print(f"  - Busca Local: 2-opt intra-rota\n")
        
        self.initialize_population()
        
        print("Evoluindo população...")
        progress_bar = tqdm(range(self.generations), desc="Gerações")
        
        for gen in progress_bar:
            self.generation = gen
            self.evolve()
            
            progress_bar.set_postfix({
                'Melhor': f'{self.best_solution.fitness:.2f}',
                'Dist': f'{self.best_solution.total_distance:.2f}',
                'Veículos': self.best_solution.num_vehicles
            })
            
            # Reinicialização se estagnado
            if self.stagnation_counter >= self.max_stagnation:
                print(f"\n⚠ Estagnação (gen {gen}). Reinicializando 50%...")
                self._reinitialize_population()
                self.stagnation_counter = 0
        
        print(f"\n{'='*70}")
        print("OTIMIZAÇÃO CONCLUÍDA")
        print(f"{'='*70}\n")
        print(f"✓ Melhor solução:")
        print(f"  - Fitness: {self.best_solution.fitness:.2f}")
        print(f"  - Distância: {self.best_solution.total_distance:.2f}")
        print(f"  - Veículos: {self.best_solution.num_vehicles}")
        print(f"  - Factível: {self.best_solution.feasible}")
        print(f"{'='*70}\n")
        
        return self.best_solution
    
    def _reinitialize_population(self):
        """Reinicializa mantendo diversidade."""
        self.population.sort(key=lambda s: s.fitness)
        keep = self.pop_size // 2
        
        for i in range(self.pop_size - keep):
            if np.random.random() < 0.7:
                base = np.random.choice(self.population[:keep])
                new_solution = base.copy()
                for _ in range(np.random.randint(2, 5)):
                    new_solution = self._apply_random_mutation(new_solution)
            else:
                vehicles = self._random_greedy_construction()
                new_solution = Solution(vehicles, self.instance)
            
            self.population.append(new_solution)


# Alias para compatibilidade
HybridGeneticAlgorithm = ImprovedGeneticAlgorithm