from src.food_delivery_loader import load_food_delivery_instance

print("="*70)
print("TESTE: CARREGAMENTO DO FOOD DELIVERY DATASET")
print("="*70)

try:
    instance = load_food_delivery_instance(
        max_customers=40,
        center_id=None
    )
    
    print("\n✅ SUCESSO!")
    print(f"\n📊 Resumo da Instância:")
    print(f"   Nome: {instance.name}")
    print(f"   Clientes: {len(instance.customers)}")
    print(f"   Veículos: {instance.num_vehicles}")
    print(f"   Capacidade: {instance.vehicle_capacity:.2f}")
    
    print(f"\n📍 Amostra de Clientes:")
    for i in range(min(3, len(instance.customers))):
        c = instance.customers[i]
        print(f"   • Cliente {c.id}:")
        print(f"     Posição: ({c.x:.2f}, {c.y:.2f})")
        print(f"     Demanda: {c.demand:.2f}")
        print(f"     Janela: [{c.ready_time:.0f} - {c.due_time:.0f}]")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")