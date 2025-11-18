"""
Food Delivery Dataset Loader for VRPTW (CORRECTED)
Author: Rafael Lopes Pinheiro
Date: 2025-11-18
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

from src.utils import Customer, VRPTWInstance


class FoodDeliveryLoader:
    """Carrega e processa dataset de food delivery para VRPTW."""
    
    def __init__(self, data_path: str = 'data/raw/food_delivery/train.csv'):
        """
        Inicializa loader.
        
        Parameters:
        -----------
        data_path : str
            Caminho para arquivo train.csv
        """
        self.data_path = data_path
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """Carrega e faz pré-processamento básico do dataset."""
        
        print(f"\n{'='*70}")
        print("CARREGANDO FOOD DELIVERY DATASET (KAGGLE)")
        print(f"{'='*70}\n")
        
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"\n❌ Arquivo não encontrado: {self.data_path}\n"
                f"   Baixe de: https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018\n"
                f"   E extraia em: data/raw/food_delivery/\n"
            )
        
        print(f"📂 Carregando arquivo: {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        
        print(f"✓ Dados carregados: {len(self.df):,} registros")
        print(f"✓ Colunas disponíveis: {list(self.df.columns)}")
        
        # Info do dataset
        print(f"\n📊 Estatísticas do Dataset:")
        print(f"  • Semanas: {self.df['week'].min()} a {self.df['week'].max()}")
        print(f"  • Centros de distribuição: {self.df['center_id'].nunique()}")
        print(f"  • Tipos de refeições: {self.df['meal_id'].nunique()}")
        print(f"  • Total de pedidos: {self.df['num_orders'].sum():,.0f}")
        print(f"  • Média de pedidos por linha: {self.df['num_orders'].mean():.1f}")
        
        return self.df
    
    def generate_coordinates(self, center_id: int, meal_id: int, 
                            price_ratio: float, seed: int = None) -> Tuple[float, float]:
        """
        Gera coordenadas sintéticas baseadas em IDs e preço.
        
        Estratégia:
        - Center_id define região do depot
        - Meal_id define dispersão dos clientes
        - Price_ratio define distância do depot
        
        Parameters:
        -----------
        center_id : int
            ID do centro de distribuição
        meal_id : int
            ID da refeição
        price_ratio : float
            Razão checkout_price/base_price (indica distância)
        seed : int, optional
            Seed para reprodutibilidade
            
        Returns:
        --------
        Tuple[float, float]
            Coordenadas (x, y)
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Center_id determina posição do depot (clusters)
        center_angle = (center_id * 137.5) % 360  # Golden angle
        center_radius = 5 + (center_id % 5) * 3
        
        # Meal_id determina ângulo do cliente em relação ao depot
        meal_angle = (meal_id * 222.5) % 360
        
        # Price_ratio determina distância (mais caro = mais longe)
        distance = 15 + (price_ratio - 1) * 25
        distance = max(10, min(distance, 45))  # Limita entre 10-45
        
        # Calcula coordenadas
        x = 50 + center_radius * np.cos(np.radians(center_angle)) + \
            distance * np.cos(np.radians(meal_angle))
        y = 50 + center_radius * np.sin(np.radians(center_angle)) + \
            distance * np.sin(np.radians(meal_angle))
        
        # Garante que está dentro do grid 0-100
        x = max(5, min(x, 95))
        y = max(5, min(y, 95))
        
        return x, y
    
    def aggregate_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados por (center_id, meal_id) para criar clientes únicos.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame filtrado
            
        Returns:
        --------
        pd.DataFrame
            DataFrame agregado com clientes únicos
        """
        print(f"\n📦 Agregando dados por cliente (center_id + meal_id)...")
        
        # Agrega por centro e refeição
        customers_df = df.groupby(['center_id', 'meal_id']).agg({
            'num_orders': 'sum',           # Demanda total
            'checkout_price': 'mean',      # Preço médio
            'base_price': 'mean',          # Preço base médio
            'week': 'mean',                # Semana média
            'id': 'count'                  # Número de transações
        }).reset_index()
        
        customers_df.columns = ['center_id', 'meal_id', 'total_orders', 
                               'avg_checkout_price', 'avg_base_price', 
                               'avg_week', 'num_transactions']
        
        print(f"✓ {len(customers_df)} clientes únicos criados")
        print(f"  (cada cliente = combinação única de centro + refeição)")
        
        return customers_df
    
    def create_vrptw_instance(self, 
                             max_customers: int = 50,
                             center_id: int = None,
                             week_filter: int = None,
                             vehicle_capacity: float = None) -> VRPTWInstance:
        """
        Cria instância VRPTW a partir dos dados de food delivery.
        
        Parameters:
        -----------
        max_customers : int
            Número máximo de clientes
        center_id : int, optional
            Filtrar por centro específico
        week_filter : int, optional
            Filtrar por semana específica
        vehicle_capacity : float, optional
            Capacidade do veículo (calcula automaticamente se None)
            
        Returns:
        --------
        VRPTWInstance
            Instância do problema VRPTW
        """
        
        # Carrega dados se ainda não carregou
        if self.df is None:
            self.load_data()
        
        print(f"\n{'='*70}")
        print("PRÉ-PROCESSAMENTO PARA VRPTW")
        print(f"{'='*70}\n")
        
        df = self.df.copy()
        
        # Filtra por centro se especificado
        if center_id is not None:
            df = df[df['center_id'] == center_id]
            print(f"✓ Filtrado por centro: {center_id}")
        else:
            # Escolhe centro com mais pedidos
            top_center = df.groupby('center_id')['num_orders'].sum().idxmax()
            df = df[df['center_id'] == top_center]
            center_id = top_center
            print(f"✓ Selecionado centro com mais pedidos: {center_id}")
        
        # Filtra por semana se especificado
        if week_filter is not None:
            df = df[df['week'] == week_filter]
            print(f"✓ Filtrado por semana: {week_filter}")
        else:
            # Escolhe semana com mais pedidos
            top_week = df.groupby('week')['num_orders'].sum().idxmax()
            df = df[df['week'] == top_week]
            print(f"✓ Selecionado semana com mais pedidos: {top_week}")
        
        # Agrega por cliente
        customers_df = self.aggregate_customers(df)
        
        # Limita número de clientes
        customers_df = customers_df.nlargest(max_customers, 'total_orders')
        
        print(f"\n✓ {len(customers_df)} clientes selecionados")
        print(f"  Total de pedidos: {customers_df['total_orders'].sum():,.0f}")
        
        print(f"\n{'='*70}")
        print("CRIANDO INSTÂNCIA VRPTW")
        print(f"{'='*70}\n")
        
        # Depot = Centro de distribuição (posição central)
        depot = Customer(
            id=0,
            x=50.0,
            y=50.0,
            demand=0.0,
            ready_time=0.0,
            due_time=480.0,  # 8 horas de operação
            service_time=0.0
        )
        
        print(f"🏪 Depot (Centro {center_id}):")
        print(f"   Posição: Centro do grid (50, 50)")
        
        # Clientes
        customers = []
        
        for idx, row in customers_df.iterrows():
            cust_id = len(customers) + 1
            
            # Calcula razão de preço (indica distância)
            price_ratio = row['avg_checkout_price'] / max(row['avg_base_price'], 1)
            
            # Gera coordenadas sintéticas
            x, y = self.generate_coordinates(
                center_id=int(row['center_id']),
                meal_id=int(row['meal_id']),
                price_ratio=price_ratio,
                seed=42 + cust_id
            )
            
            # Demanda = número de pedidos (normalizado para valores menores)
            # CORREÇÃO: Escala muito reduzida para evitar capacidade absurda
            demand = row['total_orders'] / 100  # Divide por 100 ao invés de 10
            
            # CORREÇÃO: Janelas de tempo realistas (dentro de 8 horas)
            # Normaliza semana para 0-1
            week_normalized = (row['avg_week'] - 1) / 144  # 145 semanas -> 0-1
            
            # Ready time: distribuído ao longo do dia
            ready_time = week_normalized * 300  # 0-300 minutos (5 horas)
            
            # Due time: sempre MAIOR que ready_time
            time_window_size = 60 + (price_ratio - 1) * 30  # 60-90 minutos
            due_time = ready_time + time_window_size
            
            # Garante que está dentro do limite
            due_time = min(due_time, 480.0)
            
            # Se due_time ficou menor que ready_time, ajusta
            if due_time <= ready_time:
                ready_time = max(0, due_time - 60)
            
            # Tempo de serviço proporcional à demanda
            service_time = 5 + (demand / 50) * 10  # 5-15 minutos
            
            customer = Customer(
                id=cust_id,
                x=x,
                y=y,
                demand=demand,
                ready_time=ready_time,
                due_time=due_time,
                service_time=service_time
            )
            
            customers.append(customer)
        
        print(f"\n📦 Clientes: {len(customers)}")
        print(f"   Demanda média: {np.mean([c.demand for c in customers]):.2f}")
        print(f"   Demanda total: {sum(c.demand for c in customers):.2f}")
        
        # Calcula parâmetros dos veículos
        total_demand = sum(c.demand for c in customers)
        
        # CORREÇÃO: Capacidade baseada em argumento ou automática
        if vehicle_capacity is None:
            vehicle_capacity = total_demand / 5  # ~5 veículos
        
        num_vehicles = max(5, int(np.ceil(total_demand / vehicle_capacity)) + 2)
        
        print(f"\n🚗 Frota:")
        print(f"   Número de veículos: {num_vehicles}")
        print(f"   Capacidade por veículo: {vehicle_capacity:.2f}")
        print(f"   Demanda total: {total_demand:.2f}")
        print(f"   Taxa de ocupação esperada: {(total_demand / (num_vehicles * vehicle_capacity) * 100):.1f}%")
        
        # Cria instância
        instance = VRPTWInstance(
            name=f"FoodDelivery_Center{center_id}_{len(customers)}customers",
            customers=customers,
            depot=depot,
            num_vehicles=num_vehicles,
            vehicle_capacity=vehicle_capacity
        )
        
        print(f"\n✓ Instância VRPTW criada!")
        print(f"  Nome: {instance.name}")
        print(f"  Clientes: {len(instance.customers)}")
        print(f"  Veículos: {instance.num_vehicles}")
        print(f"  Capacidade: {instance.vehicle_capacity:.2f}")
        
        # VALIDAÇÃO: Verifica janelas de tempo
        invalid_windows = sum(1 for c in customers if c.ready_time >= c.due_time)
        if invalid_windows > 0:
            print(f"\n⚠️  AVISO: {invalid_windows} clientes com janelas inválidas (corrigindo...)")
            for c in customers:
                if c.ready_time >= c.due_time:
                    c.due_time = c.ready_time + 60
        
        print(f"\n{'='*70}\n")
        
        return instance


def load_food_delivery_instance(max_customers: int = 50,
                                center_id: int = None,
                                vehicle_capacity: float = None,
                                data_path: str = 'data/raw/food_delivery/train.csv') -> VRPTWInstance:
    """
    Função helper para carregar instância de food delivery.
    
    Parameters:
    -----------
    max_customers : int
        Número máximo de clientes
    center_id : int, optional
        ID do centro de distribuição
    vehicle_capacity : float, optional
        Capacidade do veículo (auto-calcula se None)
    data_path : str
        Caminho para train.csv
        
    Returns:
    --------
    VRPTWInstance
        Instância do problema
    """
    
    loader = FoodDeliveryLoader(data_path)
    instance = loader.create_vrptw_instance(
        max_customers=max_customers,
        center_id=center_id,
        vehicle_capacity=vehicle_capacity
    )
    
    return instance


if __name__ == "__main__":
    # Teste
    print("\n🧪 TESTANDO FOOD DELIVERY LOADER\n")
    
    try:
        instance = load_food_delivery_instance(
            max_customers=40,
            center_id=None,
            vehicle_capacity=50.0  # AGORA ACEITA ESTE ARGUMENTO
        )
        
        print("\n✓ Teste concluído com sucesso!")
        print(f"\nInstância criada:")
        print(f"  {instance}")
        
        print(f"\n📊 Amostra de clientes:")
        for i in range(min(5, len(instance.customers))):
            c = instance.customers[i]
            print(f"  Cliente {c.id}: pos=({c.x:.1f}, {c.y:.1f}), "
                  f"demand={c.demand:.1f}, window=[{c.ready_time:.0f}, {c.due_time:.0f}]")
        
        # Validação
        print(f"\n🔍 Validação:")
        invalid = [c for c in instance.customers if c.ready_time >= c.due_time]
        if invalid:
            print(f"  ⚠️  {len(invalid)} clientes com janelas inválidas!")
            for c in invalid[:3]:
                print(f"    Cliente {c.id}: [{c.ready_time:.0f} >= {c.due_time:.0f}]")
        else:
            print(f"  ✅ Todas as janelas de tempo são válidas")
        
    except FileNotFoundError as e:
        print(e)
        print("\n💡 Instruções:")
        print("  1. Baixe o dataset de:")
        print("     https://www.kaggle.com/datasets/ghoshsaptarshi/av-genpact-hack-dec2018")
        print("  2. Extraia train.csv em: data/raw/food_delivery/")
        print("  3. Execute novamente")