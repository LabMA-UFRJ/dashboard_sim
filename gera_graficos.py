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