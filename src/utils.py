"""
Utility Functions for VRPTW Genetic Algorithm
Author: Rafael Lopes Pinheiro
Date: 2025-11-18
Based on: "Research on Vehicle Routing Problem with Time Windows Based on 
          Improved Genetic Algorithm" (MDPI Electronics, 2025)
"""

import numpy as np
import pandas as pd
import json
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import os


class Customer:
    """Representa um cliente no problema VRPTW."""
    
    def __init__(self, id: int, x: float, y: float, demand: float,
                 ready_time: float, due_time: float, service_time: float):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand
        self.ready_time = ready_time
        self.due_time = due_time
        self.service_time = service_time
    
    def distance_to(self, other: 'Customer') -> float:
        """Calcula distância Euclidiana para outro cliente."""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __repr__(self):
        return f"Customer(id={self.id}, pos=({self.x:.2f},{self.y:.2f}), demand={self.demand})"


class Vehicle:
    """Representa um veículo no problema VRPTW."""
    
    def __init__(self, id: int, capacity: float, max_route_time: float = 480.0):
        self.id = id
        self.capacity = capacity
        self.max_route_time = max_route_time
        self.route = []
        self.load = 0.0
        self.total_distance = 0.0
        self.total_time = 0.0
    
    def can_add_customer(self, customer: Customer, depot: Customer,
                        current_time: float) -> bool:
        """Verifica se pode adicionar cliente respeitando restrições."""
        # Verifica capacidade
        if self.load + customer.demand > self.capacity:
            return False
        
        # Verifica janela de tempo
        if current_time > customer.due_time:
            return False
        
        # Verifica tempo máximo de rota
        if self.total_time > self.max_route_time:
            return False
        
        return True
    
    def add_customer(self, customer: Customer, depot: Customer):
        """Adiciona cliente à rota."""
        self.route.append(customer)
        self.load += customer.demand
    
    def calculate_metrics(self, depot: Customer):
        """Calcula métricas totais da rota."""
        if not self.route:
            self.total_distance = 0.0
            self.total_time = 0.0
            return
        
        distance = 0.0
        time = 0.0
        
        # Depot -> primeiro cliente
        current = depot
        for customer in self.route:
            distance += current.distance_to(customer)
            time += current.distance_to(customer)
            
            # Espera se chegar antes da janela
            if time < customer.ready_time:
                time = customer.ready_time
            
            # Adiciona tempo de serviço
            time += customer.service_time
            current = customer
        
        # Último cliente -> depot
        distance += current.distance_to(depot)
        time += current.distance_to(depot)
        
        self.total_distance = distance
        self.total_time = time
    
    def __repr__(self):
        route_ids = [c.id for c in self.route]
        return f"Vehicle(id={self.id}, route={route_ids}, load={self.load:.1f}/{self.capacity})"


class VRPTWInstance:
    """Instância do problema VRPTW."""
    
    def __init__(self, name: str, customers: List[Customer], 
                 depot: Customer, num_vehicles: int, vehicle_capacity: float):
        self.name = name
        self.customers = customers
        self.depot = depot
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity
        
        # Calcula matriz de distâncias
        self.distance_matrix = self._calculate_distance_matrix()
    
    def _calculate_distance_matrix(self) -> np.ndarray:
        """Calcula matriz de distâncias entre todos os pontos."""
        n = len(self.customers) + 1  # +1 para depot
        matrix = np.zeros((n, n))
        
        all_locations = [self.depot] + self.customers
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = all_locations[i].distance_to(all_locations[j])
        
        return matrix
    
    def get_distance(self, i: int, j: int) -> float:
        """Retorna distância entre dois pontos (0 = depot)."""
        return self.distance_matrix[i][j]
    
    def __repr__(self):
        return f"VRPTWInstance(name={self.name}, customers={len(self.customers)}, vehicles={self.num_vehicles})"


def load_sales_data_as_vrptw(filepath: str, max_customers: int = 50) -> VRPTWInstance:
    """
    Converte dados de vendas em instância VRPTW.
    
    Parameters:
    -----------
    filepath : str
        Caminho para sales_data.csv
    max_customers : int
        Número máximo de clientes a considerar
        
    Returns:
    --------
    VRPTWInstance
        Instância do problema
    """
    print(f"\n{'='*70}")
    print("CONVERSÃO: DADOS DE VENDAS -> PROBLEMA VRPTW")
    print(f"{'='*70}\n")
    
    # Carrega dados
    df = pd.read_csv(filepath, encoding='latin-1')
    df.columns = ['date', 'store_id', 'product_id', 'sales_qty']
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    
    print(f"✓ Dados carregados: {len(df)} registros")
    
    # Agrega por loja (cada loja = um cliente)
    store_demand = df.groupby('store_id')['sales_qty'].sum().reset_index()
    store_demand.columns = ['store_id', 'total_demand']
    store_demand = store_demand.sort_values('total_demand', ascending=False).head(max_customers)
    
    print(f"✓ {len(store_demand)} lojas selecionadas como clientes")
    
    # Gera coordenadas aleatórias (grid 100x100)
    np.random.seed(42)
    n = len(store_demand)
    
    # Depot no centro
    depot = Customer(
        id=0,
        x=50.0,
        y=50.0,
        demand=0.0,
        ready_time=0.0,
        due_time=480.0,  # 8 horas
        service_time=0.0
    )
    
    # Clientes distribuídos aleatoriamente
    customers = []
    for idx, row in enumerate(store_demand.itertuples(), start=1):
        # Coordenadas aleatórias
        x = np.random.uniform(10, 90)
        y = np.random.uniform(10, 90)
        
        # Demanda normalizada (escala 1-50)
        demand = min(50, max(1, row.total_demand / 100))
        
        # Janelas de tempo aleatórias
        ready_time = np.random.uniform(0, 120)
        due_time = ready_time + np.random.uniform(180, 360)
        
        # Tempo de serviço proporcional à demanda
        service_time = 5 + (demand / 50) * 15  # 5-20 minutos
        
        customer = Customer(
            id=idx,
            x=x,
            y=y,
            demand=demand,
            ready_time=ready_time,
            due_time=due_time,
            service_time=service_time
        )
        customers.append(customer)
    
    # Define número de veículos e capacidade
    total_demand = sum(c.demand for c in customers)
    vehicle_capacity = total_demand / (len(customers) / 5)  # ~5 clientes por veículo
    num_vehicles = int(np.ceil(total_demand / vehicle_capacity)) + 2
    
    print(f"✓ Demanda total: {total_demand:.2f}")
    print(f"✓ Capacidade por veículo: {vehicle_capacity:.2f}")
    print(f"✓ Número de veículos: {num_vehicles}")
    
    instance = VRPTWInstance(
        name="Sales_VRPTW",
        customers=customers,
        depot=depot,
        num_vehicles=num_vehicles,
        vehicle_capacity=vehicle_capacity
    )
    
    print(f"\n✓ Instância VRPTW criada com sucesso!")
    print(f"  - Nome: {instance.name}")
    print(f"  - Clientes: {len(instance.customers)}")
    print(f"  - Veículos: {instance.num_vehicles}")
    print(f"{'='*70}\n")
    
    return instance


def save_instance(instance: VRPTWInstance, filepath: str):
    """Salva instância VRPTW em JSON."""
    data = {
        'name': instance.name,
        'num_vehicles': instance.num_vehicles,
        'vehicle_capacity': instance.vehicle_capacity,
        'depot': {
            'id': instance.depot.id,
            'x': instance.depot.x,
            'y': instance.depot.y,
            'demand': instance.depot.demand,
            'ready_time': instance.depot.ready_time,
            'due_time': instance.depot.due_time,
            'service_time': instance.depot.service_time
        },
        'customers': [
            {
                'id': c.id,
                'x': c.x,
                'y': c.y,
                'demand': c.demand,
                'ready_time': c.ready_time,
                'due_time': c.due_time,
                'service_time': c.service_time
            }
            for c in instance.customers
        ]
    }
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Instância salva em: {filepath}")


def load_instance(filepath: str) -> VRPTWInstance:
    """Carrega instância VRPTW de JSON."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    depot = Customer(**data['depot'])
    customers = [Customer(**c) for c in data['customers']]
    
    instance = VRPTWInstance(
        name=data['name'],
        customers=customers,
        depot=depot,
        num_vehicles=data['num_vehicles'],
        vehicle_capacity=data['vehicle_capacity']
    )
    
    print(f"✓ Instância carregada: {instance}")
    return instance


def create_directories():
    """Cria estrutura de diretórios do projeto."""
    dirs = [
        'data/raw',
        'data/processed',
        'results/solutions',
        'results/plots',
        'src'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✓ Estrutura de diretórios criada")


if __name__ == "__main__":
    # Teste
    create_directories()
    instance = load_sales_data_as_vrptw('data/raw/sales_data.csv', max_customers=30)
    save_instance(instance, 'data/processed/vrptw_instances.json')