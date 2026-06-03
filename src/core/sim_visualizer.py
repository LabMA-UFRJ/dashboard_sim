"""
SIM (Sistema de Informação sobre Mortalidade) Data Visualization Module

This module provides functions for visualizing mortality data (óbitos) by various demographic
categories including race/color, marital status, education level, age, and sex.
"""

from __future__ import annotations

import pandas as pd
from plotly import data
from plotly import data
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple, Optional


# Dictionary mapping categories to color schemes
DICTIONARY_COLORS = {
    'estado_civil': {'1': '#FF0000', '2': '#0000FF', '3': '#008000', '4': '#FFA500', '5': '#800080'},
    'sexo': {'1': '#00FFFF', '2': '#FF00FF'},
    'escolaridade': {'1': '#FFFF00', '2': '#A52A2A', '3': '#FFC0CB', '4': '#808080', '5': '#808000'},
    'raca_cor': {'1': '#006400', '2': '#000080', '3': '#FFD700', '4': '#800000', '5': '#FF0000'}
}

# Dictionary mapping categories to human-readable labels
DICTIONARY_LABELS = {
    'estado_civil': {
        '1': 'Solteiro(a)',
        '2': 'Casado(a)',
        '3': 'Viúvo(a)',
        '4': 'Divorciado(a)',
        '5': 'União Consensual'
    },
    'sexo': {'1': 'Masculino', '2': 'Feminino'},
    'escolaridade': {
        '1': 'Nenhuma',
        '2': '1 a 3 anos',
        '3': '4 a 7 anos',
        '4': '8 a 11 anos',
        '5': '12 anos ou mais'
    },
    'raca_cor': {'1': 'Branca', '2': 'Preta', '3': 'Amarela', '4': 'Parda', '5': 'Indígena'}
}


def _normalize_key(v) -> str:
    """
    Normalize values to string format for dictionary mapping.
    
    Handles numeric floats like 1.0 -> '1' and preserves string keys.
    
    Parameters:
    - v: Value to normalize
    
    Returns:
    - Normalized string value
    """
    if pd.isna(v):
        return '0'
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return str(v)
    return str(v).strip()


def total_deaths_by_category(
    data: pd.DataFrame,
    category: str,
    dictionary_colors: Optional[Dict] = None,
    dictionary_labels: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Calculate total deaths by category with labels and colors.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data
    - category: Column name for the category (e.g., 'raca_cor', 'sexo')
    - dictionary_colors: Dict mapping category to {id: color} (uses default if None)
    - dictionary_labels: Dict mapping category to {id: label} (uses default if None)
    
    Returns:
    - DataFrame with category, total_obitos, colors, and labels
    """
    if dictionary_colors is None:
        dictionary_colors = DICTIONARY_COLORS
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    df_cat = data.groupby(category).size().reset_index(name='total_obitos')
    
    # Normalize keys to match dictionary keys
    df_cat['cat_str'] = df_cat[category].apply(_normalize_key)
    
    # Map colors and labels
    df_cat['colors'] = df_cat['cat_str'].map(dictionary_colors.get(category, {})).fillna('#808080')
    df_cat['label'] = df_cat['cat_str'].map(dictionary_labels.get(category, {}))
    
    # Remove rows with NaN labels (unmapped values)
    df_cat = df_cat.dropna(subset=['label'])
    
    return df_cat


def plot_deaths_by_category(
    data: pd.DataFrame,
    category: str,
    title: Optional[str] = None,
    use_streamlit: bool = True,
    dictionary_colors: Optional[Dict] = None,
    dictionary_labels: Optional[Dict] = None
) -> Optional[go.Figure]:
    """
    Create a bar chart showing total deaths by category.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data
    - category: Column name for the category (e.g., 'raca_cor', 'sexo', 'estado_civil')
    - title: Custom title for the chart (auto-generated if None)
    - use_streamlit: Whether to display using st.plotly_chart (True) or return figure (False)
    - dictionary_colors: Dict mapping category to {id: color}
    - dictionary_labels: Dict mapping category to {id: label}
    
    Returns:
    - Plotly Figure object
    """
    if dictionary_colors is None:
        dictionary_colors = DICTIONARY_COLORS
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    df_cat = total_deaths_by_category(data, category, dictionary_colors, dictionary_labels)
    
    if df_cat.empty:
        st.warning(f"Sem dados disponíveis para categoria: {category}")
        return None
    
    fig = px.bar(
        df_cat,
        x='label',
        y='total_obitos',
        color='label',
        color_discrete_map=dict(zip(df_cat['label'], df_cat['colors'])),
        title=title or f'Total de Óbitos por {category.capitalize()}',
        labels={'label': category.capitalize(), 'total_obitos': 'Total de Óbitos'},
        text='total_obitos'
    )
    
    fig.update_traces(textposition='auto')
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title=category.capitalize(),
        yaxis_title='Total de Óbitos',
        hovermode='x unified'
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


def plot_deaths_by_age(
    data: pd.DataFrame,
    title: str = 'Total de Óbitos por Idade',
    use_streamlit: bool = True,
    color: str = '#1f77b4'
) -> go.Figure:
    """
    Create a line chart showing total deaths by age.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data with 'idade' column
    - title: Title for the chart
    - use_streamlit: Whether to display using st.plotly_chart (True) or return figure (False)
    - color: Color for the line
    
    Returns:
    - Plotly Figure object
    """
    df_filtered = data.groupby('idade').size().reset_index(name='total_obitos')
    df_filtered = df_filtered.sort_values('idade')
    
    fig = px.line(
        df_filtered,
        x='idade',
        y='total_obitos',
        title=title,
        markers=True,
        labels={'idade': 'Idade', 'total_obitos': 'Total de Óbitos'}
    )
    
    fig.update_traces(line=dict(color=color, width=2))
    fig.update_layout(
        height=400,
        hovermode='x unified',
        xaxis_title='Idade',
        yaxis_title='Total de Óbitos'
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig

def plot_calculated_mx_by_age(
    death_data: pd.DataFrame,
    population_data: pd.DataFrame,
    title: str = 'Taxa de Mortalidade por Idade',
    use_streamlit: bool = True,
    color: str = '#1f77b4'
) -> go.Figure:
    """
    Create a line chart showing calculated mortality rates by age.
    
    Parameters:
    - death_data: Pandas DataFrame containing mortality data with 'idade' column
    - population_data: Pandas DataFrame containing population data with 'idade' column
    - title: Title for the chart
    - use_streamlit: Whether to display using st.plotly_chart (True) or return figure (False)
    - color: Color for the line
    
    Returns:
    - Plotly Figure object
    """
    # Placeholder implementation - replace with actual calculation logic
    df_death_filtered = death_data.groupby('idade').size().reset_index(name='total_obitos')
    df_population_filtered = population_data.groupby('idade').size().reset_index(name='population')

    # Merge the two DataFrames on 'idade', renaming columns to avoid conflicts
    df_death_filtered.rename(columns={'idade': 'idade_death'}, inplace=True)
    df_population_filtered.rename(columns={'idade': 'idade_population'}, inplace=True)
    df_filtered = pd.merge(df_death_filtered, df_population_filtered, left_on='idade_death', right_on='idade_population', how='inner')

    # Calculate mortality rate by age (D/N)
    df_filtered['mortality_rate'] = df_filtered['total_obitos'] / df_filtered['population']
    
    fig = px.line(
        df_filtered,
        x='idade',
        y='mortality_rate',
        title=title,
        markers=True,
        labels={'idade': 'Idade', 'mortality_rate': 'Taxa de Mortalidade'}
    )
    
    fig.update_traces(line=dict(color=color, width=2))
    fig.update_layout(
        height=400,
        hovermode='x unified',
        xaxis_title='Idade',
        yaxis_title='Taxa de Mortalidade'
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig

def plot_deaths_by_subcategory_and_age(
    data: pd.DataFrame,
    category: str,
    title: Optional[str] = None,
    use_streamlit: bool = True,
    dictionary_colors: Optional[Dict] = None,
    dictionary_labels: Optional[Dict] = None
) -> go.Figure:
    """
    Create a line chart showing deaths by age for each subcategory.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data
    - category: Column name for the category (e.g., 'raca_cor', 'sexo')
    - title: Custom title for the chart
    - use_streamlit: Whether to display using st.plotly_chart (True) or return figure (False)
    - dictionary_colors: Dict mapping category to {id: color}
    - dictionary_labels: Dict mapping category to {id: label}
    
    Returns:
    - Plotly Figure object
    """
    if dictionary_colors is None:
        dictionary_colors = DICTIONARY_COLORS
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    colors = dictionary_colors.get(category, {})
    labels = dictionary_labels.get(category, {})
    
    # Get unique subcategories
    subcategories = sorted(data[category].dropna().unique())
    
    fig = go.Figure()
    
    for subcategory in subcategories:
        subcategory_str = _normalize_key(subcategory)
        
        # Filter data for this subcategory
        df_filtered = data[data[category] == subcategory].groupby('idade').size().reset_index(name='total_obitos')
        df_filtered = df_filtered.sort_values('idade')
        
        # Get color and label
        color = colors.get(subcategory_str, '#808080')
        label = labels.get(subcategory_str, f'Categoria {subcategory_str}')
        
        fig.add_trace(go.Scatter(
            x=df_filtered['idade'],
            y=df_filtered['total_obitos'],
            mode='lines+markers',
            name=label,
            line=dict(color=color, width=2),
            hovertemplate=f'<b>{label}</b><br>Idade: %{{x}}<br>Óbitos: %{{y}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title or f'Total de Óbitos por Idade - {category.capitalize()}',
        xaxis_title='Idade',
        yaxis_title='Total de Óbitos',
        height=500,
        hovermode='x unified',
        legend=dict(orientation='v', yanchor='top', y=0.99, xanchor='left', x=0.01)
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


def plot_all_categories(
    data: pd.DataFrame,
    categories: Optional[list[str]] = None,
    dictionary_colors: Optional[Dict] = None,
    dictionary_labels: Optional[Dict] = None
) -> None:
    """
    Display bar charts for all specified categories.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data
    - categories: List of category names to plot (uses default if None)
    - dictionary_colors: Dict mapping category to {id: color}
    - dictionary_labels: Dict mapping category to {id: label}
    """
    if categories is None:
        categories = ['raca_cor', 'sexo', 'escolaridade', 'estado_civil']
    
    if dictionary_colors is None:
        dictionary_colors = DICTIONARY_COLORS
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    for category in categories:
        plot_deaths_by_category(
            data,
            category,
            dictionary_colors=dictionary_colors,
            dictionary_labels=dictionary_labels
        )


def get_category_statistics(
    data: pd.DataFrame,
    category: str,
    dictionary_labels: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Get statistics for a category including total deaths, percentage, and labels.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data
    - category: Column name for the category
    - dictionary_labels: Dict mapping category to {id: label}
    
    Returns:
    - DataFrame with statistics
    """
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    df_stats = data.groupby(category).size().reset_index(name='total_obitos')
    df_stats['cat_str'] = df_stats[category].apply(_normalize_key)
    df_stats['label'] = df_stats['cat_str'].map(dictionary_labels.get(category, {}))
    df_stats['percentual'] = (df_stats['total_obitos'] / df_stats['total_obitos'].sum() * 100).round(2)
    
    return df_stats.dropna(subset=['label'])


def compare_categories_distribution(
    data: pd.DataFrame,
    category1: str,
    category2: str,
    title: Optional[str] = None,
    use_streamlit: bool = True
) -> go.Figure:
    """
    Create a comparison chart between two categories.
    
    Parameters:
    - data: Pandas DataFrame containing mortality data
    - category1: First category to compare
    - category2: Second category to compare
    - title: Custom title for the chart
    - use_streamlit: Whether to display using st.plotly_chart
    
    Returns:
    - Plotly Figure object
    """
    stats1 = get_category_statistics(data, category1)
    stats2 = get_category_statistics(data, category2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=stats1['label'],
        y=stats1['total_obitos'],
        name=category1.capitalize(),
        text=stats1['total_obitos'],
        textposition='auto'
    ))
    
    # This is a side-by-side comparison, so we need to normalize if different number of categories
    if len(stats2) > 0:
        fig.add_trace(go.Bar(
            x=stats2['label'],
            y=stats2['total_obitos'],
            name=category2.capitalize(),
            text=stats2['total_obitos'],
            textposition='auto'
        ))
    
    fig.update_layout(
        title=title or f'Comparação: {category1.capitalize()} vs {category2.capitalize()}',
        xaxis_title='Categoria',
        yaxis_title='Total de Óbitos',
        height=400,
        barmode='group',
        hovermode='x unified'
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


# ============================================================================
# FUNÇÕES PARA ANÁLISE COMPARATIVA POR ANO
# ============================================================================

def load_sim_data_by_year(
    base_path: str,
    year: int
) -> Optional[pd.DataFrame]:
    """
    Carrega dados SIM-DATASUS para um ano específico.
    
    Parameters:
    - base_path: Caminho base (ex: //Projetos2/Wrk/SIM-DATASUS/MICRODADOS/)
    - year: Ano desejado (ex: 2020)
    
    Returns:
    - DataFrame ou None se arquivo não existir
    """
    try:
        file_path = f"{base_path}/SIM-DATASUS-{year}.csv"
        data = pd.read_csv(file_path)
        data['ano'] = year
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados de {year}: {str(e)}")
        return None


def load_sim_data_range(
    base_path: str,
    year_start: int,
    year_end: int
) -> Dict[int, pd.DataFrame]:
    """
    Carrega dados SIM-DATASUS para um intervalo de anos.
    
    Parameters:
    - base_path: Caminho base dos arquivos
    - year_start: Ano inicial (inclusive)
    - year_end: Ano final (inclusive)
    
    Returns:
    - Dicionário {ano: DataFrame}
    """
    dfs = {}
    years_loaded = []
    years_missing = []
    
    for year in range(year_start, year_end + 1):
        data = load_sim_data_by_year(base_path, year)
        if data is not None:
            dfs[year] = data
            years_loaded.append(year)
        else:
            years_missing.append(year)
    
    if years_loaded:
        st.success(f"✅ Carregados: {', '.join(map(str, years_loaded))}")
    
    if years_missing:
        st.warning(f"⚠️ Não encontrados: {', '.join(map(str, years_missing))}")
    
    return dfs

def combine_sim_data(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Combina múltiplos DataFrames de diferentes anos.
    
    Parameters:
    - dfs: Array de DataFrames {ano: DataFrame}
    
    Returns:
    - DataFrame combinado com coluna 'ano'
    """
    return pd.concat(dfs, ignore_index=True)


def plot_deaths_by_year(
    dfs: Dict[int, pd.DataFrame],
    use_streamlit: bool = True
) -> Optional[go.Figure]:
    """
    Cria gráfico de evolução de óbitos ao longo dos anos.
    
    Parameters:
    - dfs: Dicionário {ano: DataFrame}
    - use_streamlit: Se deve exibir com st.plotly_chart
    
    Returns:
    - Plotly Figure
    """
    if not dfs:
        st.error("Nenhum dado disponível")
        return None
    
    years_data = []
    for year in sorted(dfs.keys()):
        total = len(dfs[year])
        years_data.append({'ano': year, 'total_obitos': total})
    
    df_years = pd.DataFrame(years_data)
    
    fig = px.line(
        df_years,
        x='ano',
        y='total_obitos',
        markers=True,
        title='Evolução de Óbitos por Ano',
        labels={'ano': 'Ano', 'total_obitos': 'Total de Óbitos'}
    )
    
    fig.update_traces(line=dict(color='#1f77b4', width=2), marker=dict(size=8))
    fig.update_layout(height=400, hovermode='x unified')
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


def plot_category_comparison_by_year(
    dfs: Dict[int, pd.DataFrame],
    category: str,
    use_streamlit: bool = True,
    dictionary_labels: Optional[Dict] = None
) -> Optional[go.Figure]:
    """
    Compara evolução de uma categoria ao longo dos anos.
    
    Parameters:
    - dfs: Dicionário {ano: DataFrame}
    - category: Categoria a analisar (ex: 'sexo')
    - use_streamlit: Se deve exibir com st.plotly_chart
    - dictionary_labels: Dicionário de rótulos
    
    Returns:
    - Plotly Figure
    """
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    if not dfs:
        st.error("Nenhum dado disponível")
        return None
    
    # Combina dados de todos os anos
    combined_data = combine_sim_data(dfs)
    
    if category not in combined_data.columns:
        st.error(f"Coluna '{category}' não encontrada")
        return None
    
    # Agrupa por ano e categoria
    df_grouped = combined_data.groupby(['ano', category]).size().reset_index(name='total_obitos')
    
    # Normaliza e adiciona rótulos
    labels_map = dictionary_labels.get(category, {})
    df_grouped['cat_str'] = df_grouped[category].apply(lambda v: _normalize_key(v))
    df_grouped['label'] = df_grouped['cat_str'].map(labels_map)
    
    fig = px.line(
        df_grouped,
        x='ano',
        y='total_obitos',
        color='label',
        markers=True,
        title=f'Evolução de Óbitos por {category.capitalize()} (2004-2022)',
        labels={'ano': 'Ano', 'total_obitos': 'Total de Óbitos', 'label': category.capitalize()},
        height=500
    )
    
    fig.update_layout(hovermode='x unified')
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


def plot_category_heatmap_by_year(
    dfs: Dict[int, pd.DataFrame],
    category: str,
    use_streamlit: bool = True,
    dictionary_labels: Optional[Dict] = None
) -> Optional[go.Figure]:
    """
    Cria heatmap de uma categoria ao longo dos anos.
    
    Parameters:
    - dfs: Dicionário {ano: DataFrame}
    - category: Categoria a analisar
    - use_streamlit: Se deve exibir com st.plotly_chart
    - dictionary_labels: Dicionário de rótulos
    
    Returns:
    - Plotly Figure (heatmap)
    """
    if dictionary_labels is None:
        dictionary_labels = DICTIONARY_LABELS
    
    if not dfs:
        st.error("Nenhum dado disponível")
        return None
    
    combined_data = combine_sim_data(dfs)
    
    if category not in combined_data.columns:
        st.error(f"Coluna '{category}' não encontrada")
        return None
    
    # Pivot table: anos vs categoria
    df_pivot = combined_data.groupby(['ano', category]).size().reset_index(name='total_obitos')
    
    # Normaliza e adiciona rótulos
    labels_map = dictionary_labels.get(category, {})
    df_pivot['cat_str'] = df_pivot[category].apply(lambda v: _normalize_key(v))
    df_pivot['label'] = df_pivot['cat_str'].map(labels_map)
    
    # Cria pivot table para heatmap
    heatmap_data = df_pivot.pivot_table(
        index='label',
        columns='ano',
        values='total_obitos',
        fill_value=0
    )
    
    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='YlOrRd',
            hovertemplate='Ano: %{x}<br>%{y}: %{z}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title=f'Heatmap de Óbitos por {category.capitalize()} (2004-2022)',
        xaxis_title='Ano',
        yaxis_title=category.capitalize(),
        height=500
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


def plot_age_distribution_by_year(
    dfs: Dict[int, pd.DataFrame],
    use_streamlit: bool = True
) -> Optional[go.Figure]:
    """
    Compara distribuição etária entre anos selecionados.
    
    Parameters:
    - dfs: Dicionário {ano: DataFrame}
    - use_streamlit: Se deve exibir com st.plotly_chart
    
    Returns:
    - Plotly Figure
    """
    if not dfs:
        st.error("Nenhum dado disponível")
        return None
    
    fig = go.Figure()
    
    for year in sorted(dfs.keys()):
        data_year = dfs[year]
        if 'idade' in data_year.columns:
            df_age = data_year.groupby('idade').size().reset_index(name='total_obitos')
            fig.add_trace(go.Scatter(
                x=df_age['idade'],
                y=df_age['total_obitos'],
                mode='lines+markers',
                name=str(year),
                hovertemplate=f'<b>{year}</b><br>Idade: %{{x}}<br>Óbitos: %{{y}}<extra></extra>'
            ))
    
    fig.update_layout(
        title='Distribuição Etária de Óbitos por Ano',
        xaxis_title='Idade',
        yaxis_title='Total de Óbitos',
        height=500,
        hovermode='x unified',
        legend=dict(orientation='v', yanchor='top', y=0.99, xanchor='right', x=0.99)
    )
    
    if use_streamlit:
        st.plotly_chart(fig, use_container_width=True)
    
    return fig


def get_statistics_by_year(
    dfs: Dict[int, pd.DataFrame],
    category: Optional[str] = None
) -> pd.DataFrame:
    """
    Gera estatísticas agregadas por ano.
    
    Parameters:
    - dfs: Dicionário {ano: DataFrame}
    - category: Categoria opcional para detalhar (ex: 'sexo')
    
    Returns:
    - DataFrame com estatísticas por ano
    """
    stats = []
    
    for year in sorted(dfs.keys()):
        data_year = dfs[year]
        
        stat_dict = {
            'ano': year,
            'total_obitos': len(data_year),
        }
        
        if 'sexo' in data_year.columns:
            stat_dict['masculino'] = len(data_year[data_year['sexo'] == 1])
            stat_dict['feminino'] = len(data_year[data_year['sexo'] == 2])
        
        if 'idade' in data_year.columns:
            stat_dict['idade_media'] = round(data_year['idade'].mean(), 2)
            stat_dict['idade_mediana'] = round(data_year['idade'].median(), 2)
        
        if category and category in data_year.columns:
            for cat_val in data_year[category].unique():
                if pd.notna(cat_val):
                    cat_str = _normalize_key(cat_val)
                    cat_label = DICTIONARY_LABELS.get(category, {}).get(cat_str, cat_str)
                    count = len(data_year[data_year[category] == cat_val])
                    stat_dict[f'{category}_{cat_label}'] = count
        
        stats.append(stat_dict)
    
    return pd.DataFrame(stats)
