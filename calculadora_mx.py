import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

path = r'c:\Users\joao.victor.verardo\OneDrive - Accenture\Desktop\datasus'

# Anos pares de 2004 a 2020
anos = list(range(2004, 2021, 2))

# ============================================================
# MAPEAMENTOS DATASUS -> ELEITORADO
# ============================================================

def mapear_idade_datasus(idade):
    """Converte idade numérica do DATASUS para formato do eleitorado."""
    if pd.isna(idade) or idade < 0:
        return None
    idade_int = int(np.floor(idade))
    if idade_int < 16:
        return None
    elif idade_int >= 100:
        return "100 anos ou mais"
    else:
        return f"{idade_int} anos"

mapa_sexo = {
    1: "MASCULINO",
    2: "FEMININO",
    0: "NÃO INFORMADO"
}

mapa_estado_civil = {
    1.0: "SOLTEIRO",
    2.0: "CASADO",
    3.0: "VIÚVO",
    4.0: "SEPARADO/DIVORCIADO",
    5.0: "CASADO",
    9.0: "NÃO INFORMADO"
}

mapa_escolaridade_datasus = {
    0.0: "SEM ESCOLARIDADE",
    1.0: "FUNDAMENTAL INCOMPLETO",
    2.0: "FUNDAMENTAL COMPLETO",
    3.0: "MEDIO COMPLETO",
    4.0: "SUPERIOR INCOMPLETO",
    5.0: "SUPERIOR COMPLETO",
    9.0: "NÃO INFORMADO"
}

mapa_escolaridade_eleitorado = {
    "ANALFABETO": "SEM ESCOLARIDADE",
    "LÊ E ESCREVE": "SEM ESCOLARIDADE",
    "ENSINO FUNDAMENTAL INCOMPLETO": "FUNDAMENTAL INCOMPLETO",
    "ENSINO FUNDAMENTAL COMPLETO": "FUNDAMENTAL COMPLETO",
    "ENSINO MÉDIO INCOMPLETO": "FUNDAMENTAL COMPLETO",
    "ENSINO MÉDIO COMPLETO": "MEDIO COMPLETO",
    "SUPERIOR INCOMPLETO": "SUPERIOR INCOMPLETO",
    "SUPERIOR COMPLETO": "SUPERIOR COMPLETO",
    "NÃO INFORMADO": "NÃO INFORMADO"
}

def extrair_idade_num(s):
    if s == "100 anos ou mais":
        return 100
    elif s == "Inválida":
        return -1
    else:
        return int(s.replace(" anos", ""))


def processar_ano(ano):
    """Processa um ano: calcula Mx e salva gráficos na pasta do ano."""
    print(f"\n{'='*60}")
    print(f"  PROCESSANDO ANO {ano}")
    print(f"{'='*60}")

    # Criar pasta para os gráficos
    pasta_graficos = os.path.join(path, 'graficos', str(ano))
    os.makedirs(pasta_graficos, exist_ok=True)

    # Carregar dados
    arquivo_sim = os.path.join(path, f'SIM-DATASUS-{ano}.csv')
    arquivo_el = os.path.join(path, f'eleitorado_{ano}.csv')

    if not os.path.exists(arquivo_sim):
        print(f"  AVISO: {arquivo_sim} não encontrado. Pulando ano {ano}.")
        return None
    if not os.path.exists(arquivo_el):
        print(f"  AVISO: {arquivo_el} não encontrado. Pulando ano {ano}.")
        return None

    print(f"  Carregando SIM-DATASUS-{ano}...")
    sim = pd.read_csv(arquivo_sim, encoding='utf-8', low_memory=False)
    print(f"    Obitos: {len(sim)}")

    print(f"  Carregando eleitorado_{ano}...")
    el = pd.read_csv(arquivo_el, encoding='utf-8')
    print(f"    Registros eleitorado: {len(el)}")

    # ============================================================
    # APLICAR MAPEAMENTOS NO DATASUS
    # ============================================================
    print("  Aplicando mapeamentos no DATASUS...")
    sim["idade_mapeada"] = sim["idade"].apply(mapear_idade_datasus)
    sim["sexo_mapeado"] = sim["sexo"].map(mapa_sexo)
    sim["estado_civil_mapeado"] = sim["estado_civil"].map(mapa_estado_civil)

    # escolaridade_2010 pode não existir em anos anteriores
    if "escolaridade_2010" in sim.columns:
        sim["escolaridade_mapeada"] = sim["escolaridade_2010"].map(mapa_escolaridade_datasus)
    elif "escolaridade" in sim.columns:
        sim["escolaridade_mapeada"] = sim["escolaridade"].map(mapa_escolaridade_datasus)
    else:
        sim["escolaridade_mapeada"] = None

    sim["uf"] = sim["sigla_uf"] if "sigla_uf" in sim.columns else sim.get("uf", None)

    # ============================================================
    # APLICAR MAPEAMENTOS NO ELEITORADO
    # ============================================================
    print("  Aplicando mapeamentos no eleitorado...")
    el["idade_mapeada"] = el["DS_FAIXA_ETARIA"]
    el["sexo_mapeado"] = el["DS_GENERO"]
    el["estado_civil_mapeado"] = el["DS_ESTADO_CIVIL"].replace({
        "DIVORCIADO": "SEPARADO/DIVORCIADO",
        "SEPARADO JUDICIALMENTE": "SEPARADO/DIVORCIADO"
    })
    el["escolaridade_mapeada"] = el["DS_GRAU_INSTRUCAO"].map(mapa_escolaridade_eleitorado)
    el["uf"] = el["SG_UF"]

    # Filtrar DATASUS: apenas >= 16 anos
    sim_filtrado = sim[sim["idade_mapeada"].notna()].copy()
    print(f"    Obitos com idade >= 16: {len(sim_filtrado)} de {len(sim)}")

    # ============================================================
    # 1. Mx POR IDADE
    # ============================================================
    print("  Calculando Mx por IDADE...")
    obitos_idade = sim_filtrado.groupby("idade_mapeada").size().reset_index(name='obitos')
    obitos_idade.columns = ['faixa_etaria', 'obitos']

    exposicao_idade = el.groupby("idade_mapeada")["qt_eleitores"].sum().reset_index()
    exposicao_idade.columns = ['faixa_etaria', 'exposicao']

    mx_idade = obitos_idade.merge(exposicao_idade, on='faixa_etaria', how='inner')
    mx_idade['Mx'] = mx_idade['obitos'] / mx_idade['exposicao']
    mx_idade['idade_num'] = mx_idade['faixa_etaria'].apply(extrair_idade_num)
    mx_idade = mx_idade[mx_idade['idade_num'] >= 16].sort_values('idade_num')

    # 2. Mx POR SEXO
    print("  Calculando Mx por SEXO...")
    obitos_sexo = sim_filtrado.groupby("sexo_mapeado").size().reset_index(name='obitos')
    obitos_sexo.columns = ['sexo', 'obitos']

    exposicao_sexo = el.groupby("sexo_mapeado")["qt_eleitores"].sum().reset_index()
    exposicao_sexo.columns = ['sexo', 'exposicao']

    mx_sexo = obitos_sexo.merge(exposicao_sexo, on='sexo', how='inner')
    mx_sexo['Mx'] = mx_sexo['obitos'] / mx_sexo['exposicao']

    # 3. Mx POR UF
    print("  Calculando Mx por UF...")
    obitos_uf = sim_filtrado.groupby("uf").size().reset_index(name='obitos')
    obitos_uf.columns = ['uf', 'obitos']

    exposicao_uf = el.groupby("uf")["qt_eleitores"].sum().reset_index()
    exposicao_uf.columns = ['uf', 'exposicao']

    mx_uf = obitos_uf.merge(exposicao_uf, on='uf', how='inner')
    mx_uf['Mx'] = mx_uf['obitos'] / mx_uf['exposicao']
    mx_uf = mx_uf.sort_values('Mx', ascending=False)

    # 4. Mx POR ESTADO CIVIL
    print("  Calculando Mx por ESTADO CIVIL...")
    obitos_ec = sim_filtrado.groupby("estado_civil_mapeado").size().reset_index(name='obitos')
    obitos_ec.columns = ['estado_civil', 'obitos']

    exposicao_ec = el.groupby("estado_civil_mapeado")["qt_eleitores"].sum().reset_index()
    exposicao_ec.columns = ['estado_civil', 'exposicao']

    mx_ec = obitos_ec.merge(exposicao_ec, on='estado_civil', how='inner')
    mx_ec['Mx'] = mx_ec['obitos'] / mx_ec['exposicao']

    # 5. Mx POR ESCOLARIDADE
    print("  Calculando Mx por ESCOLARIDADE...")
    obitos_esc = sim_filtrado[sim_filtrado["escolaridade_mapeada"].notna()].groupby("escolaridade_mapeada").size().reset_index(name='obitos')
    obitos_esc.columns = ['escolaridade', 'obitos']

    exposicao_esc = el[el["escolaridade_mapeada"].notna()].groupby("escolaridade_mapeada")["qt_eleitores"].sum().reset_index()
    exposicao_esc.columns = ['escolaridade', 'exposicao']

    mx_esc = obitos_esc.merge(exposicao_esc, on='escolaridade', how='inner')
    mx_esc['Mx'] = mx_esc['obitos'] / mx_esc['exposicao']

    # ============================================================
    # EXIBIR TABELAS COM RESULTADOS AGREGADOS
    # ============================================================
    print(f"\n  {'─'*50}")
    print(f"  TABELAS DE RESULTADOS - {ano}")
    print(f"  {'─'*50}")

    print(f"\n  ► mx_idade (Mx por Idade) - primeiras 10 linhas:")
    print(mx_idade[['faixa_etaria', 'obitos', 'exposicao', 'Mx']].head(10).to_string(index=False))

    print(f"\n  ► mx_sexo (Mx por Sexo):")
    print(mx_sexo[['sexo', 'obitos', 'exposicao', 'Mx']].to_string(index=False))

    print(f"\n  ► mx_uf (Mx por UF) - top 10:")
    print(mx_uf[['uf', 'obitos', 'exposicao', 'Mx']].head(10).to_string(index=False))

    print(f"\n  ► mx_ec (Mx por Estado Civil):")
    print(mx_ec[['estado_civil', 'obitos', 'exposicao', 'Mx']].to_string(index=False))

    print(f"\n  ► mx_esc (Mx por Escolaridade):")
    print(mx_esc[['escolaridade', 'obitos', 'exposicao', 'Mx']].to_string(index=False))

    print(f"\n  {'─'*50}")

    # ============================================================
    # GERAR GRÁFICOS
    # ============================================================
    print("  Gerando gráficos...")

    # 1. Mx por Idade (log scale)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(mx_idade['idade_num'], mx_idade['Mx'], 'b-', linewidth=1.5)
    ax.set_xlabel('Idade (anos)')
    ax.set_ylabel('Mx (escala log)')
    ax.set_title(f'Taxa Central de Mortalidade (Mx) por Idade - Brasil {ano}')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(16, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_idade.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Mx por Sexo
    fig, ax = plt.subplots(figsize=(8, 5))
    cores_sexo = ['#FF6B6B', '#4ECDC4']
    mx_sexo_plot = mx_sexo[mx_sexo['sexo'].isin(['MASCULINO', 'FEMININO'])]
    bars = ax.bar(mx_sexo_plot['sexo'], mx_sexo_plot['Mx'], color=cores_sexo)
    ax.set_ylabel('Mx')
    ax.set_title(f'Taxa Central de Mortalidade (Mx) por Sexo - Brasil {ano}')
    ax.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, mx_sexo_plot['Mx']):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val:.5f}', ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_sexo.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Mx por UF
    fig, ax = plt.subplots(figsize=(10, 8))
    mx_uf_sorted = mx_uf.sort_values('Mx', ascending=True)
    ax.barh(mx_uf_sorted['uf'], mx_uf_sorted['Mx'], color='steelblue')
    ax.set_xlabel('Mx')
    ax.set_title(f'Taxa Central de Mortalidade (Mx) por UF - Brasil {ano}')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_uf.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 4. Mx por Estado Civil
    fig, ax = plt.subplots(figsize=(9, 6))
    mx_ec_plot = mx_ec.sort_values('Mx', ascending=False)
    bars = ax.bar(range(len(mx_ec_plot)), mx_ec_plot['Mx'], color='coral')
    ax.set_xticks(range(len(mx_ec_plot)))
    ax.set_xticklabels(mx_ec_plot['estado_civil'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Mx')
    ax.set_title(f'Taxa Central de Mortalidade (Mx) por Estado Civil - Brasil {ano}')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_estado_civil.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 5. Mx por Escolaridade
    fig, ax = plt.subplots(figsize=(10, 6))
    ordem_esc = ["SEM ESCOLARIDADE", "FUNDAMENTAL INCOMPLETO", "FUNDAMENTAL COMPLETO",
                 "MEDIO COMPLETO", "SUPERIOR INCOMPLETO", "SUPERIOR COMPLETO"]
    mx_esc_plot = mx_esc[mx_esc['escolaridade'].isin(ordem_esc)].copy()
    mx_esc_plot['ordem'] = mx_esc_plot['escolaridade'].map({v: i for i, v in enumerate(ordem_esc)})
    mx_esc_plot = mx_esc_plot.sort_values('ordem')
    bars = ax.bar(range(len(mx_esc_plot)), mx_esc_plot['Mx'], color='mediumseagreen')
    ax.set_xticks(range(len(mx_esc_plot)))
    ax.set_xticklabels(mx_esc_plot['escolaridade'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Mx')
    ax.set_title(f'Taxa Central de Mortalidade (Mx) por Escolaridade - Brasil {ano}')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_escolaridade.png'), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Gráficos salvos em: {pasta_graficos}")

    # Retornar DataFrames com coluna de ano para consolidação
    mx_idade['ano'] = ano
    mx_sexo['ano'] = ano
    mx_uf['ano'] = ano
    mx_ec['ano'] = ano
    mx_esc['ano'] = ano

    return mx_idade, mx_sexo, mx_uf, mx_ec, mx_esc


# ============================================================
# EXECUTAR PARA TODOS OS ANOS
# ============================================================
if __name__ == "__main__":
    todos_idade = []
    todos_sexo = []
    todos_uf = []
    todos_ec = []
    todos_esc = []

    for ano in anos:
        try:
            resultado = processar_ano(ano)
            if resultado is not None:
                mx_idade, mx_sexo, mx_uf, mx_ec, mx_esc = resultado
                todos_idade.append(mx_idade)
                todos_sexo.append(mx_sexo)
                todos_uf.append(mx_uf)
                todos_ec.append(mx_ec)
                todos_esc.append(mx_esc)
        except Exception as e:
            print(f"\n  ERRO no ano {ano}: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    # SALVAR CSVs CONSOLIDADOS PARA POWER BI
    # ============================================================
    print(f"\n{'='*60}")
    print("  GERANDO CSVs CONSOLIDADOS...")
    print(f"{'='*60}")

    if todos_idade:
        df_idade = pd.concat(todos_idade, ignore_index=True)
        df_idade[['ano', 'faixa_etaria', 'idade_num', 'obitos', 'exposicao', 'Mx']].to_csv(
            os.path.join(path, 'mx_idade_todos_anos.csv'), index=False, encoding='utf-8-sig')
        print(f"  Salvo: mx_idade_todos_anos.csv ({len(df_idade)} linhas)")

    if todos_sexo:
        df_sexo = pd.concat(todos_sexo, ignore_index=True)
        df_sexo[['ano', 'sexo', 'obitos', 'exposicao', 'Mx']].to_csv(
            os.path.join(path, 'mx_sexo_todos_anos.csv'), index=False, encoding='utf-8-sig')
        print(f"  Salvo: mx_sexo_todos_anos.csv ({len(df_sexo)} linhas)")

    if todos_uf:
        df_uf = pd.concat(todos_uf, ignore_index=True)
        df_uf[['ano', 'uf', 'obitos', 'exposicao', 'Mx']].to_csv(
            os.path.join(path, 'mx_uf_todos_anos.csv'), index=False, encoding='utf-8-sig')
        print(f"  Salvo: mx_uf_todos_anos.csv ({len(df_uf)} linhas)")

    if todos_ec:
        df_ec = pd.concat(todos_ec, ignore_index=True)
        df_ec[['ano', 'estado_civil', 'obitos', 'exposicao', 'Mx']].to_csv(
            os.path.join(path, 'mx_estado_civil_todos_anos.csv'), index=False, encoding='utf-8-sig')
        print(f"  Salvo: mx_estado_civil_todos_anos.csv ({len(df_ec)} linhas)")

    if todos_esc:
        df_esc = pd.concat(todos_esc, ignore_index=True)
        df_esc[['ano', 'escolaridade', 'obitos', 'exposicao', 'Mx']].to_csv(
            os.path.join(path, 'mx_escolaridade_todos_anos.csv'), index=False, encoding='utf-8-sig')
        print(f"  Salvo: mx_escolaridade_todos_anos.csv ({len(df_esc)} linhas)")

    print(f"\n{'='*60}")
    print("  PROCESSAMENTO CONCLUÍDO!")
    print(f"  Gráficos organizados em: {path}\\graficos\\<ano>\\")
    print(f"  CSVs consolidados salvos em: {path}\\")
    print(f"{'='*60}")
