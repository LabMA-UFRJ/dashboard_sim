#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar a análise SIM-DATASUS
Uso: python run_sim_analysis.py [opcoes]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_streamlit_app(data_path: str = None):
    """
    Executa a aplicação Streamlit.
    
    Args:
        data_path: Caminho opcional do arquivo de dados
    """
    print("🚀 Iniciando aplicação SIM-DATASUS...")
    print(f"📊 Versão: 1.0")
    print(f"📝 Arquivo: app.py")
    
    cmd = ["streamlit", "run", "app.py"]
    
    if data_path:
        print(f"📂 Arquivo de dados: {data_path}")
        # Você pode passar como argumento se necessário
    
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("❌ Erro: Streamlit não encontrado!")
        print("   Execute: pip install streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⛔ Aplicação interrompida pelo usuário")
        sys.exit(0)


def run_jupyter_notebook():
    """Executa o notebook Jupyter para desenvolvimento."""
    print("📓 Abrindo Jupyter Notebook...")
    
    cmd = ["jupyter", "notebook", "main.ipynb"]
    
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("❌ Erro: Jupyter não encontrado!")
        print("   Execute: pip install jupyter")
        sys.exit(1)


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    dependencies = {
        "pandas": "Manipulação de dados",
        "streamlit": "Framework web",
        "plotly": "Gráficos interativos",
    }
    
    print("✅ Verificando dependências...\n")
    
    missing = []
    for pkg, desc in dependencies.items():
        try:
            __import__(pkg)
            print(f"  ✓ {pkg:15} - {desc}")
        except ImportError:
            print(f"  ✗ {pkg:15} - {desc} [FALTANDO]")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠️  Faltam {len(missing)} dependência(s)")
        print(f"   Execute: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ Todas as dependências estão instaladas!")
    return True


def install_requirements():
    """Instala os requisitos necessários."""
    requirements = [
        "pandas>=1.3.0",
        "streamlit>=1.0.0",
        "plotly>=5.0.0",
    ]
    
    print("📦 Instalando dependências...\n")
    
    cmd = ["pip", "install"] + requirements
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False


def main():
    """Função principal com argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Análise de Mortalidade SIM-DATASUS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Executar o app Streamlit
  python run_sim_analysis.py --app

  # Verificar dependências
  python run_sim_analysis.py --check

  # Instalar dependências
  python run_sim_analysis.py --install

  # Abrir notebook de desenvolvimento
  python run_sim_analysis.py --notebook

  # Executar app com arquivo específico
  python run_sim_analysis.py --app --data "caminho/arquivo.csv"
        """
    )
    
    parser.add_argument(
        "--app",
        action="store_true",
        help="Executar aplicação Streamlit"
    )
    
    parser.add_argument(
        "--data",
        type=str,
        help="Caminho do arquivo SIM-DATASUS"
    )
    
    parser.add_argument(
        "--notebook",
        action="store_true",
        help="Abrir Jupyter Notebook"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verificar dependências instaladas"
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="Instalar dependências necessárias"
    )
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi passado, mostrar ajuda
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Executar ação apropriada
    if args.install:
        install_requirements()
    
    elif args.check:
        check_dependencies()
    
    elif args.app:
        if check_dependencies():
            run_streamlit_app(args.data)
    
    elif args.notebook:
        run_jupyter_notebook()


if __name__ == "__main__":
    main()
