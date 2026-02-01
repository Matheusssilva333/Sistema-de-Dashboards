"""
Script de Inicialização do Banco de Dados
Cria todas as tabelas e dados iniciais
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import init_db, engine
from app.models import User, AdAccount, Campaign, AdSet, Ad, Insight
from sqlalchemy import inspect

def main():
    """Inicializa o banco de dados"""
    print("🗄️  Inicializando banco de dados...")
    
    # Verificar se as tabelas já existem
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        print(f"📋 Tabelas existentes encontradas: {', '.join(existing_tables)}")
        confirm = input("⚠️  Deseja recriar as tabelas? (isso apagará todos os dados) [y/N]: ")
        
        if confirm.lower() != 'y':
            print("❌ Operação cancelada.")
            return
        
        # Dropar todas as tabelas
        print("🗑️  Removendo tabelas antigas...")
        from app.database import Base
        Base.metadata.drop_all(bind=engine)
    
    # Criar tabelas
    print("📝 Criando tabelas...")
    init_db()
    
    # Verificar tabelas criadas
    inspector = inspect(engine)
    created_tables = inspector.get_table_names()
    
    print(f"\n✅ Banco de dados inicializado com sucesso!")
    print(f"📊 Tabelas criadas: {', '.join(created_tables)}")
    print(f"\n💡 Models disponíveis:")
    print("   - User (usuários)")
    print("   - AdAccount (contas de anúncios)")
    print("   - Campaign (campanhas)")
    print("   - AdSet (conjuntos de anúncios)")
    print("   - Ad (anúncios)")
    print("   - Insight (métricas diárias)")
    print("\n🎉 Pronto para usar!")

if __name__ == "__main__":
    main()
