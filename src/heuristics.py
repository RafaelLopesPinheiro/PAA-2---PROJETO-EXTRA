"""
Heuristics for VRPTW - Solomon Insertion Heuristic
Author: Rafael Lopes Pinheiro
Date: 2025-11-18

Implementa a heurística de inserção de Solomon para inicialização de soluções.
"""

import numpy as np
from typing import List, Tuple
from src.utils import Customer, Vehicle, VRPTWInstance


class SolomonInsertion:
    """
    Heurística de Inserção de Solomon (I1) para VRPTW.
    
    Referência: Solomon, M. M. (1987). "Algorithms for the vehicle routing 
    and scheduling problems with time window constraints."
    """
    
    def __init__(self, instance: VRPTWInstance, alpha: float = 1.0, 
                 mu: float = 1.0, lambda_param: float = 1.0):
        """
        Inicializa heurística de Solomon.
        
        Parameters:
        -----------
        instance : VRPTWInstance
            Instância do problema
        alpha : float
            Peso para distância
        mu : float
            Peso para urgência temporal
        lambda_param : float
            Peso para penalização de tempo de espera
        """
        self.instance = instance
        self.alpha = alpha
        self.mu = mu
        self.lambda_param = lambda_param
    
    def calculate_c1(self, route: List[Customer], customer: Customer,
                     position: int, depot: Customer) -> float:
        """
        Calcula custo c1 (distância adicional ao inserir cliente).
        
        c1(i,u,j) = d(i,u) + d(u,j) - μ * d(i,j)
        """
        if position == 0:
            prev_customer = depot
        else:
            prev_customer = route[position - 1]
        
        if position >= len(route):
            next_customer = depot
        else:
            next_customer = route[position]
        
        d_iu = prev_customer.distance_to(customer)
        d_uj = customer.distance_to(next_customer)
        d_ij = prev_customer.distance_to(next_customer)
        
        c1 = d_iu + d_uj - self.mu * d_ij
        return c1
    
    def calculate_c2(self, route: List[Customer], customer: Customer,
                     position: int, depot: Customer) -> float:
        """
        Calcula custo c2 (impacto temporal ao inserir cliente).
        
        c2(i,u,j) = b_u - t_i
        onde b_u é o início da janela e t_i é o tempo de chegada.
        """
        # Calcula tempo de chegada no cliente u
        current_time = 0.0
        current_loc = depot
        
        for idx in range(position):
            travel_time = current_loc.distance_to(route[idx])
            current_time += travel_time
            
            # Espera se necessário
            if current_time < route[idx].ready_time:
                current_time = route[idx].ready_time
            
            current_time += route[idx].service_time
            current_loc = route[idx]
        
        # Tempo até o novo cliente
        travel_time = current_loc.distance_to(customer)
        arrival_time = current_time + travel_time
        
        c2 = customer.ready_time - arrival_time
        return c2
    
    def calculate_insertion_cost(self, route: List[Customer], customer: Customer,
                                 position: int, depot: Customer) -> float:
        """
        Calcula custo total de inserção.
        
        c(i,u,j) = α * c1(i,u,j) + λ * c2(i,u,j)
        """
        c1 = self.calculate_c1(route, customer, position, depot)
        c2 = self.calculate_c2(route, customer, position, depot)
        
        cost = self.alpha * c1 + self.lambda_param * c2
        return cost
    
    def find_best_insertion(self, route: List[Customer], customer: Customer,
                           depot: Customer, vehicle_capacity: float,
                           current_load: float) -> Tuple[int, float]:
        """
        Encontra melhor posição para inserir cliente na rota.
        
        Returns:
        --------
        Tuple[int, float]
            (posição, custo) ou (-1, inf) se não for viável
        """
        best_position = -1
        best_cost = float('inf')
        
        # Tenta cada posição
        for pos in range(len(route) + 1):
            # Verifica capacidade
            if current_load + customer.demand > vehicle_capacity:
                continue
            
            # Verifica viabilidade temporal
            if not self._is_feasible_insertion(route, customer, pos, depot):
                continue
            
            # Calcula custo
            cost = self.calculate_insertion_cost(route, customer, pos, depot)
            
            if cost < best_cost:
                best_cost = cost
                best_position = pos
        
        return best_position, best_cost
    
    def _is_feasible_insertion(self, route: List[Customer], customer: Customer,
                            position: int, depot: Customer) -> bool:
        """
        Verifica se inserção é viável temporalmente COM VALIDAÇÃO RIGOROSA.
        """
        # Simula inserção e verifica restrições
        test_route = route[:position] + [customer] + route[position:]
        
        current_time = 0.0
        current_loc = depot
        
        for c in test_route:
            travel_time = current_loc.distance_to(c)
            arrival_time = current_time + travel_time
            
            # VALIDAÇÃO RIGOROSA: Chegou tarde demais?
            if arrival_time > c.due_time:
                return False
            
            # Atualiza tempo (espera se necessário)
            service_start = max(arrival_time, c.ready_time)
            current_time = service_start + c.service_time
            current_loc = c
        
        # Verifica retorno ao depot
        return_time = current_time + current_loc.distance_to(depot)
        if return_time > depot.due_time:
            return False
        
        return True
    
    def construct_solution(self) -> List[Vehicle]:
        """
        Constrói solução inicial usando heurística de Solomon.
        
        Returns:
        --------
        List[Vehicle]
            Lista de veículos com rotas atribuídas
        """
        print("\n" + "="*70)
        print("HEURÍSTICA DE SOLOMON - CONSTRUÇÃO DE SOLUÇÃO INICIAL")
        print("="*70 + "\n")
        
        unrouted = self.instance.customers.copy()
        vehicles = []
        vehicle_id = 0
        
        while unrouted and vehicle_id < self.instance.num_vehicles:
            # Cria novo veículo
            vehicle = Vehicle(
                id=vehicle_id,
                capacity=self.instance.vehicle_capacity
            )
            
            # Seleciona cliente inicial (mais distante do depot)
            if unrouted:
                seed_customer = max(unrouted, 
                                   key=lambda c: self.instance.depot.distance_to(c))
                vehicle.route.append(seed_customer)
                vehicle.load += seed_customer.demand
                unrouted.remove(seed_customer)
            
            # Insere clientes até não ser mais possível
            while unrouted:
                best_customer = None
                best_position = -1
                best_cost = float('inf')
                
                # Tenta inserir cada cliente não roteado
                for customer in unrouted:
                    position, cost = self.find_best_insertion(
                        vehicle.route,
                        customer,
                        self.instance.depot,
                        vehicle.capacity,
                        vehicle.load
                    )
                    
                    if position != -1 and cost < best_cost:
                        best_customer = customer
                        best_position = position
                        best_cost = cost
                
                # Se encontrou inserção viável, adiciona
                if best_customer is not None:
                    vehicle.route.insert(best_position, best_customer)
                    vehicle.load += best_customer.demand
                    unrouted.remove(best_customer)
                else:
                    break  # Não consegue inserir mais ninguém
            
            # Calcula métricas do veículo
            vehicle.calculate_metrics(self.instance.depot)
            vehicles.append(vehicle)
            
            print(f"Veículo {vehicle_id}: {len(vehicle.route)} clientes, "
                  f"carga={vehicle.load:.1f}/{vehicle.capacity:.1f}, "
                  f"distância={vehicle.total_distance:.2f}")
            
            vehicle_id += 1
        
        # Verifica se todos foram roteados
        if unrouted:
            print(f"\n⚠ AVISO: {len(unrouted)} clientes não foram roteados!")
            print(f"  Clientes não atendidos: {[c.id for c in unrouted]}")
        else:
            print(f"\n✓ Todos os {len(self.instance.customers)} clientes foram roteados!")
        
        print(f"✓ Solução inicial construída com {len(vehicles)} veículos")
        print("="*70 + "\n")
        
        return vehicles


if __name__ == "__main__":
    # Teste
    from src.utils import load_instance
    
    instance = load_instance('data/processed/vrptw_instances.json')
    solomon = SolomonInsertion(instance, alpha=1.0, mu=1.0, lambda_param=2.0)
    solution = solomon.construct_solution()
    
    print("\nSolução construída:")
    for v in solution:
        print(v)