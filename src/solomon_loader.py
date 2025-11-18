"""
Solomon Benchmark Loader
Author: Rafael Lopes Pinheiro
"""

import requests
import os
from src.utils import Customer, VRPTWInstance


class SolomonBenchmarkLoader:
    """Carrega instâncias benchmark de Solomon."""
    
    # URLs das instâncias
    INSTANCES = {
        'C101': 'https://raw.githubusercontent.com/luismiguel010/VRP/master/Solomon%20Benchmark/C101.txt',
        'C201': 'https://raw.githubusercontent.com/luismiguel010/VRP/master/Solomon%20Benchmark/C201.txt',
        'R101': 'https://raw.githubusercontent.com/luismiguel010/VRP/master/Solomon%20Benchmark/R101.txt',
        'R201': 'https://raw.githubusercontent.com/luismiguel010/VRP/master/Solomon%20Benchmark/R201.txt',
        'RC101': 'https://raw.githubusercontent.com/luismiguel010/VRP/master/Solomon%20Benchmark/RC101.txt',
        'RC201': 'https://raw.githubusercontent.com/luismiguel010/VRP/master/Solomon%20Benchmark/RC201.txt',
    }
    
    @staticmethod
    def download_instance(name: str, save_dir: str = 'data/raw/solomon/') -> str:
        """
        Baixa instância Solomon.
        
        Parameters:
        -----------
        name : str
            Nome da instância (ex: 'C101')
        save_dir : str
            Diretório para salvar
            
        Returns:
        --------
        str
            Caminho do arquivo baixado
        """
        if name not in SolomonBenchmarkLoader.INSTANCES:
            raise ValueError(f"Instância {name} não encontrada. Disponíveis: {list(SolomonBenchmarkLoader.INSTANCES.keys())}")
        
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f'{name}.txt')
        
        if os.path.exists(filepath):
            print(f"✓ Instância {name} já existe: {filepath}")
            return filepath
        
        print(f"⬇ Baixando instância {name}...")
        url = SolomonBenchmarkLoader.INSTANCES[name]
        
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filepath, 'w') as f:
            f.write(response.text)
        
        print(f"✓ Instância salva: {filepath}")
        return filepath
    
    @staticmethod
    def load_instance(filepath: str, max_customers: int = None) -> VRPTWInstance:
        """
        Carrega instância Solomon de arquivo.
        
        Format:
        Line 1-4: Header
        Line 5-9: Vehicle info
        Line 10+: Customer data (id x y demand ready due service)
        
        Parameters:
        -----------
        filepath : str
            Caminho do arquivo
        max_customers : int, optional
            Limitar número de clientes
            
        Returns:
        --------
        VRPTWInstance
            Instância do problema
        """
        print(f"\n{'='*70}")
        print(f"CARREGANDO INSTÂNCIA SOLOMON: {os.path.basename(filepath)}")
        print(f"{'='*70}\n")
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Extrai nome da instância
        instance_name = lines[0].strip()
        
        # Linha 5: NUMBER     CAPACITY
        vehicle_info = lines[4].strip().split()
        num_vehicles = int(vehicle_info[0])
        vehicle_capacity = float(vehicle_info[1])
        
        # Clientes (linha 9 em diante)
        customers = []
        depot_data = None
        
        for i, line in enumerate(lines[9:], start=9):
            parts = line.strip().split()
            if len(parts) < 7:
                continue
            
            cust_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            demand = float(parts[3])
            ready_time = float(parts[4])
            due_time = float(parts[5])
            service_time = float(parts[6])
            
            customer = Customer(
                id=cust_id,
                x=x,
                y=y,
                demand=demand,
                ready_time=ready_time,
                due_time=due_time,
                service_time=service_time
            )
            
            # Primeiro é o depot (id=0)
            if cust_id == 0:
                depot_data = customer
            else:
                customers.append(customer)
            
            # Limita número de clientes
            if max_customers and len(customers) >= max_customers:
                break
        
        if depot_data is None:
            raise ValueError("Depot (customer 0) não encontrado no arquivo!")
        
        print(f"✓ Instância: {instance_name}")
        print(f"✓ Clientes carregados: {len(customers)}")
        print(f"✓ Veículos: {num_vehicles}")
        print(f"✓ Capacidade: {vehicle_capacity}")
        print(f"{'='*70}\n")
        
        instance = VRPTWInstance(
            name=instance_name,
            customers=customers,
            depot=depot_data,
            num_vehicles=num_vehicles,
            vehicle_capacity=vehicle_capacity
        )
        
        return instance


# Função helper para main.py
def load_solomon_instance(name: str = 'C101', max_customers: int = None) -> VRPTWInstance:
    """
    Baixa e carrega instância Solomon.
    
    Parameters:
    -----------
    name : str
        Nome da instância (C101, R101, RC101, etc.)
    max_customers : int, optional
        Limitar clientes (ex: 25, 50)
        
    Returns:
    --------
    VRPTWInstance
    """
    loader = SolomonBenchmarkLoader()
    filepath = loader.download_instance(name)
    instance = loader.load_instance(filepath, max_customers)
    return instance


if __name__ == "__main__":
    # Teste
    instance = load_solomon_instance('C101', max_customers=25)
    print(instance)