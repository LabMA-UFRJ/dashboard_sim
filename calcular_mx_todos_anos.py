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
    if pd.isna(s):
        return -1
    if s == "100 anos ou mais":
        return 100
    elif s == "Inválida":
        return -1
    elif " anos" in s:
        try:
            return int(s.replace(" anos", ""))
        except ValueError:
            return -1
    else:
        return -1


def padronizar_texto(series):
    """Padroniza textos: strip + upper."""
    return series.astype(str).str.strip().str.upper()


def calcular_mx_idade_dimensao(sim_filtrado, el, col_datasus, col_eleitorado, nome_dimensao):
    """
    Calcula Mx por idade + uma dimensão adicional.

    Parâmetros:
        sim_filtrado: DataFrame de óbitos (já filtrado >= 16 anos)
        el: DataFrame do eleitorado
        col_datasus: nome da coluna mapeada no DATASUS (ex: 'sexo_mapeado')
        col_eleitorado: nome da coluna mapeada no eleitorado (ex: 'sexo_mapeado')
        nome_dimensao: nome final da coluna de dimensão no resultado (ex: 'sexo')

    Retorna:
        DataFrame com colunas: faixa_etaria, idade_num, <dimensao>, obitos, exposicao, Mx, Mx_por_1000, _merge
    """
    # Filtrar registros com dimensão válida
    sim_valido = sim_filtrado[sim_filtrado[col_datasus].notna()].copy()
    el_valido = el[el[col_eleitorado].notna()].copy()

    # Padronizar textos
    sim_valido[col_datasus] = padronizar_texto(sim_valido[col_datasus])
    el_valido[col_eleitorado] = padronizar_texto(el_valido[col_eleitorado])

    # Agrupar óbitos por idade + dimensão
    obitos = sim_valido.groupby(["idade_mapeada", col_datasus]).size().reset_index(name='obitos')
    obitos.columns = ['faixa_etaria', nome_dimensao, 'obitos']

    # Agrupar exposição por idade + dimensão
    exposicao = el_valido.groupby(["idade_mapeada", col_eleitorado])["qt_eleitores"].sum().reset_index()
    exposicao.columns = ['faixa_etaria', nome_dimensao, 'exposicao']

    # Merge outer com indicador
    mx = obitos.merge(exposicao, on=['faixa_etaria', nome_dimensao], how='outer', indicator=True)

    # Preencher NaN em obitos/exposicao com 0
    mx['obitos'] = mx['obitos'].fillna(0).astype(int)
    mx['exposicao'] = mx['exposicao'].fillna(0).astype(int)

    # Calcular Mx com proteção contra divisão por zero
    mx['Mx'] = np.where(mx['exposicao'] > 0, mx['obitos'] / mx['exposicao'], np.nan)
    mx['Mx_por_1000'] = mx['Mx'] * 1000

    # Extrair idade numérica e filtrar >= 16
    mx['idade_num'] = mx['faixa_etaria'].apply(extrair_idade_num)
    mx = mx[mx['idade_num'] >= 16].copy()

    # Ordenar por idade e dimensão
    mx = mx.sort_values(['idade_num', nome_dimensao]).reset_index(drop=True)

    return mx


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
    # 1. Mx POR IDADE (mantido como referência)
    # ============================================================
    print("  Calculando Mx por IDADE...")
    obitos_idade = sim_filtrado.groupby("idade_mapeada").size().reset_index(name='obitos')
    obitos_idade.columns = ['faixa_etaria', 'obitos']

    exposicao_idade = el.groupby("idade_mapeada")["qt_eleitores"].sum().reset_index()
    exposicao_idade.columns = ['faixa_etaria', 'exposicao']

    mx_idade = obitos_idade.merge(exposicao_idade, on='faixa_etaria', how='outer', indicator=True)
    mx_idade['obitos'] = mx_idade['obitos'].fillna(0).astype(int)
    mx_idade['exposicao'] = mx_idade['exposicao'].fillna(0).astype(int)
    mx_idade['Mx'] = np.where(mx_idade['exposicao'] > 0, mx_idade['obitos'] / mx_idade['exposicao'], np.nan)
    mx_idade['Mx_por_1000'] = mx_idade['Mx'] * 1000
    mx_idade['idade_num'] = mx_idade['faixa_etaria'].apply(extrair_idade_num)
    mx_idade = mx_idade[mx_idade['idade_num'] >= 16].sort_values('idade_num').reset_index(drop=True)

    # ============================================================
    # 2. Mx POR IDADE + SEXO
    # ============================================================
    print("  Calculando Mx por IDADE + SEXO...")
    mx_idade_sexo = calcular_mx_idade_dimensao(
        sim_filtrado, el, 'sexo_mapeado', 'sexo_mapeado', 'sexo')

    # ============================================================
    # 3. Mx POR IDADE + UF
    # ============================================================
    print("  Calculando Mx por IDADE + UF...")
    mx_idade_uf = calcular_mx_idade_dimensao(
        sim_filtrado, el, 'uf', 'uf', 'uf')

    # ============================================================
    # 4. Mx POR IDADE + ESTADO CIVIL
    # ============================================================
    print("  Calculando Mx por IDADE + ESTADO CIVIL...")
    mx_idade_ec = calcular_mx_idade_dimensao(
        sim_filtrado, el, 'estado_civil_mapeado', 'estado_civil_mapeado', 'estado_civil')

    # ============================================================
    # 5. Mx POR IDADE + ESCOLARIDADE
    # ============================================================
    print("  Calculando Mx por IDADE + ESCOLARIDADE...")
    mx_idade_esc = calcular_mx_idade_dimensao(
        sim_filtrado, el, 'escolaridade_mapeada', 'escolaridade_mapeada', 'escolaridade')

    # ============================================================
    # EXIBIR RESUMO
    # ============================================================
    print(f"\n  {'─'*50}")
    print(f"  RESUMO - {ano}")
    print(f"  {'─'*50}")
    print(f"  mx_idade:           {len(mx_idade)} linhas")
    print(f"  mx_idade_sexo:      {len(mx_idade_sexo)} linhas")
    print(f"  mx_idade_uf:        {len(mx_idade_uf)} linhas")
    print(f"  mx_idade_ec:        {len(mx_idade_ec)} linhas")
    print(f"  mx_idade_esc:       {len(mx_idade_esc)} linhas")
    print(f"  {'─'*50}")

    # ============================================================
    # GERAR GRÁFICOS
    # ============================================================
    print("  Gerando gráficos...")

    # 1. Mx por Idade (log scale)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(mx_idade['idade_num'], mx_idade['Mx'], 'b-', linewidth=1.5)
    ax.set_xlabel('Idade (anos)')
    ax.set_ylabel('Mx (escala log)')
    ax.set_title(f'Mx por Idade - Brasil {ano}')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(16, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_idade.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Mx por Idade e Sexo (linhas separadas por sexo)
    fig, ax = plt.subplots(figsize=(10, 6))
    cores_sexo = {'MASCULINO': '#4ECDC4', 'FEMININO': '#FF6B6B'}
    for sexo, cor in cores_sexo.items():
        dados = mx_idade_sexo[mx_idade_sexo['sexo'] == sexo]
        if not dados.empty:
            ax.semilogy(dados['idade_num'], dados['Mx'], '-', color=cor,
                        linewidth=1.5, label=sexo)
    ax.set_xlabel('Idade (anos)')
    ax.set_ylabel('Mx (escala log)')
    ax.set_title(f'Mx por Idade e Sexo - Brasil {ano}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(16, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_idade_sexo.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Mx por Idade e UF (top 5 UFs com maior Mx médio)
    fig, ax = plt.subplots(figsize=(10, 6))
    mx_uf_medio = mx_idade_uf.groupby('uf')['Mx'].mean().nlargest(5)
    top_ufs = mx_uf_medio.index.tolist()
    cores_uf = plt.cm.tab10(np.linspace(0, 1, len(top_ufs)))
    for i, uf in enumerate(top_ufs):
        dados = mx_idade_uf[mx_idade_uf['uf'] == uf]
        if not dados.empty:
            ax.semilogy(dados['idade_num'], dados['Mx'], '-', color=cores_uf[i],
                        linewidth=1.2, label=uf)
    ax.set_xlabel('Idade (anos)')
    ax.set_ylabel('Mx (escala log)')
    ax.set_title(f'Mx por Idade e UF (Top 5) - Brasil {ano}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(16, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_idade_uf_top5.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 4. Mx por Idade e Estado Civil
    fig, ax = plt.subplots(figsize=(10, 6))
    ecs_validos = ['SOLTEIRO', 'CASADO', 'VIÚVO', 'SEPARADO/DIVORCIADO']
    cores_ec = plt.cm.Set2(np.linspace(0, 1, len(ecs_validos)))
    for i, ec in enumerate(ecs_validos):
        dados = mx_idade_ec[mx_idade_ec['estado_civil'] == ec]
        if not dados.empty:
            ax.semilogy(dados['idade_num'], dados['Mx'], '-', color=cores_ec[i],
                        linewidth=1.2, label=ec)
    ax.set_xlabel('Idade (anos)')
    ax.set_ylabel('Mx (escala log)')
    ax.set_title(f'Mx por Idade e Estado Civil - Brasil {ano}')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(16, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_idade_estado_civil.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 5. Mx por Idade e Escolaridade
    fig, ax = plt.subplots(figsize=(10, 6))
    ordem_esc = ["SEM ESCOLARIDADE", "FUNDAMENTAL INCOMPLETO", "FUNDAMENTAL COMPLETO",
                 "MEDIO COMPLETO", "SUPERIOR INCOMPLETO", "SUPERIOR COMPLETO"]
    cores_esc = plt.cm.viridis(np.linspace(0, 0.9, len(ordem_esc)))
    for i, esc in enumerate(ordem_esc):
        dados = mx_idade_esc[mx_idade_esc['escolaridade'] == esc]
        if not dados.empty:
            ax.semilogy(dados['idade_num'], dados['Mx'], '-', color=cores_esc[i],
                        linewidth=1.2, label=esc)
    ax.set_xlabel('Idade (anos)')
    ax.set_ylabel('Mx (escala log)')
    ax.set_title(f'Mx por Idade e Escolaridade - Brasil {ano}')
    ax.legend(fontsize=7, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(16, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_graficos, f'Mx_{ano}_idade_escolaridade.png'), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Gráficos salvos em: {pasta_graficos}")

    # Adicionar coluna ano
    mx_idade['ano'] = ano
    mx_idade_sexo['ano'] = ano
    mx_idade_uf['ano'] = ano
    mx_idade_ec['ano'] = ano
    mx_idade_esc['ano'] = ano

    return mx_idade, mx_idade_sexo, mx_idade_uf, mx_idade_ec, mx_idade_esc


# ============================================================
# EXECUTAR PARA TODOS OS ANOS
# ============================================================
if __name__ == "__main__":
    todos_idade = []
    todos_idade_sexo = []
    todos_idade_uf = []
    todos_idade_ec = []
    todos_idade_esc = []

    for ano in anos:
        try:
            resultado = processar_ano(ano)
            if resultado is not None:
                mx_idade, mx_idade_sexo, mx_idade_uf, mx_idade_ec, mx_idade_esc = resultado
                todos_idade.append(mx_idade)
                todos_idade_sexo.append(mx_idade_sexo)
                todos_idade_uf.append(mx_idade_uf)
                todos_idade_ec.append(mx_idade_ec)
                todos_idade_esc.append(mx_idade_esc)
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

    arquivos_gerados = []

    if todos_idade:
        df_idade = pd.concat(todos_idade, ignore_index=True)
        cols_idade = ['ano', 'idade_num', 'obitos', 'exposicao', 'Mx']
        df_idade[cols_idade].to_csv(
            os.path.join(path, 'mx_idade_todos_anos.csv'), index=False, encoding='utf-8-sig')
        arquivos_gerados.append(f"mx_idade_todos_anos.csv ({len(df_idade)} linhas)")

    if todos_idade_sexo:
        df_sexo = pd.concat(todos_idade_sexo, ignore_index=True)
        cols_sexo = ['ano', 'idade_num', 'sexo', 'obitos', 'exposicao', 'Mx']
        df_sexo[cols_sexo].to_csv(
            os.path.join(path, 'mx_idade_sexo_todos_anos.csv'), index=False, encoding='utf-8-sig')
        arquivos_gerados.append(f"mx_idade_sexo_todos_anos.csv ({len(df_sexo)} linhas)")

    if todos_idade_uf:
        df_uf = pd.concat(todos_idade_uf, ignore_index=True)
        cols_uf = ['ano', 'idade_num', 'uf', 'obitos', 'exposicao', 'Mx']
        df_uf[cols_uf].to_csv(
            os.path.join(path, 'mx_idade_uf_todos_anos.csv'), index=False, encoding='utf-8-sig')
        arquivos_gerados.append(f"mx_idade_uf_todos_anos.csv ({len(df_uf)} linhas)")

    if todos_idade_ec:
        df_ec = pd.concat(todos_idade_ec, ignore_index=True)
        cols_ec = ['ano', 'idade_num', 'estado_civil', 'obitos', 'exposicao', 'Mx']
        df_ec[cols_ec].to_csv(
            os.path.join(path, 'mx_idade_estado_civil_todos_anos.csv'), index=False, encoding='utf-8-sig')
        arquivos_gerados.append(f"mx_idade_estado_civil_todos_anos.csv ({len(df_ec)} linhas)")

    if todos_idade_esc:
        df_esc = pd.concat(todos_idade_esc, ignore_index=True)
        cols_esc = ['ano', 'idade_num', 'escolaridade', 'obitos', 'exposicao', 'Mx']
        df_esc[cols_esc].to_csv(
            os.path.join(path, 'mx_idade_escolaridade_todos_anos.csv'), index=False, encoding='utf-8-sig')
        arquivos_gerados.append(f"mx_idade_escolaridade_todos_anos.csv ({len(df_esc)} linhas)")

    print(f"\n{'='*60}")
    print("  PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*60}")
    print(f"\n  CSVs gerados:")
    for arq in arquivos_gerados:
        print(f"    • {arq}")
    print(f"\n  Gráficos organizados em: {path}\\graficos\\<ano>\\")
    print(f"  CSVs consolidados salvos em: {path}\\")
    print(f"{'='*60}")
