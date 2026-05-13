from __future__ import annotations

from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st


class InsuranceVisualizer:
    def __init__(self) -> None:
        self.coverage_config: Dict[str, Dict[str, str]] = {
            "SOB": {"display_name": "Sobrevivência"},
            "INV": {"display_name": "Invalidez"},
            "MOR": {"display_name": "Mortalidade"},
        }

    def _filt(
        self,
        df: pd.DataFrame,
        selected_company: str,
        selected_sex: str | None = None,
        selected_product: str | None = None,
        selected_year: int | str | None = None,
    ) -> pd.DataFrame:
        cond = pd.Series(True, index=df.index)

        if selected_company != "Todas" and "EMP" in df.columns:
            cond &= df["EMP"] == selected_company

        if selected_sex and selected_sex != "Todos" and "SEXO" in df.columns:
            cond &= df["SEXO"] == selected_sex

        if (
            selected_product
            and selected_product != "Todos"
            and "PRODUTO" in df.columns
        ):
            product_filter = selected_product.strip()
            produtos = df["PRODUTO"].astype(str).str.strip()
            cond &= produtos == product_filter

        if (
            selected_year is not None
            and selected_year != "Todos"
            and "REF_INFO" in df.columns
        ):
            cond &= df["REF_INFO"] == selected_year

        return df.loc[cond].copy()

    @staticmethod
    def _ensure_age_column(df: pd.DataFrame) -> pd.DataFrame:
        if "IDADE_31_DEZ" not in df.columns and "IDADE" in df.columns:
            df = df.rename(columns={"IDADE": "IDADE_31_DEZ"})
        return df

    @staticmethod
    def _get_numeric(df: pd.DataFrame, column: str) -> pd.Series:
        if column not in df.columns:
            return pd.Series(0, index=df.index, dtype="float64")
        return pd.to_numeric(df[column], errors="coerce").fillna(0)

    def _sum_columns(self, df: pd.DataFrame, columns: list[str]) -> pd.Series:
        total = pd.Series(0, index=df.index, dtype="float64")
        for column in columns:
            total = total.add(self._get_numeric(df, column), fill_value=0)
        return total

    def render_data_debug(self, df: pd.DataFrame) -> None:
        with st.expander("🔍 Metadados dos dados"):
            st.write("**Colunas presentes:**", list(df.columns))
            st.write("**Configuração ativa:**", self.coverage_config)
            st.write("**Amostra dos dados:**", df.head(3))

    def distribuicao_estoque_inicial_por_ano(
        self, dfs: Dict[str, pd.DataFrame], selected_company: str
    ) -> None:
        plot_data: list[pd.DataFrame] = []

        for coverage_type, df in dfs.items():
            if not {"REF_INFO", "ESTOQUE_INICIAL"}.issubset(df.columns):
                continue

            df_filtro = self._filt(df, selected_company)
            grouped = (
                df_filtro.groupby("REF_INFO")["ESTOQUE_INICIAL"]
                .sum()
                .reset_index()
            )
            display_name = self.coverage_config[coverage_type]["display_name"]
            plot_data.append(grouped.rename(columns={"ESTOQUE_INICIAL": display_name}))

        if not plot_data:
            st.error("Nenhum dado disponível para exibir estoques iniciais.")
            return

        df_joined = plot_data[0]
        for df_next in plot_data[1:]:
            df_joined = df_joined.merge(df_next, on="REF_INFO", how="outer")

        df_joined = df_joined.fillna(0).sort_values("REF_INFO")
        cols = [c for c in df_joined.columns if c != "REF_INFO"]

        fig = px.line(
            df_joined,
            x="REF_INFO",
            y=cols,
            markers=True,
            title="Distribuição de Estoque Inicial por Ano",
            labels={"REF_INFO": "Ano", "value": "Estoque Inicial", "variable": "Cobertura"},
        )
        fig.update_layout(
            xaxis=dict(dtick=1),
            yaxis_title="Estoque Inicial",
            legend_title_text="Cobertura",
            hovermode="x unified",
        )

        st.subheader("Estoque Inicial por Ano")
        st.plotly_chart(fig, use_container_width=True)

    def continuidade_estoque_por_ano(
        self, dfs: Dict[str, pd.DataFrame], selected_company: str
    ) -> None:
        start_cols = ["ESTOQUE_INICIAL", "ENTRADA"]
        end_cols = [
            "ESTOQUE_FINAL",
            "OBITOS",
            "OBITO_100",
            "OBITO_200",
            "OBITO_300",
            "ENTRADAS_INVALIDEZ",
            "ENTRADA_INVALIDEZ_400",
            "ENTRADA_INVALIDEZ_500",
            "ENTRADA_INVALIDEZ_600",
            "ENTRADA_INVALIDEZ_700",
            "APOSENTADORIA",
            "OUTRAS_SAIDAS",
        ]

        frames = []
        for df in dfs.values():
            if "REF_INFO" not in df.columns:
                continue
            df_f = self._filt(df, selected_company)
            df_f = df_f.assign(
                INICIO_MAIS_ENTRADA=self._sum_columns(df_f, start_cols),
                ESTOQUE_FINAL_MAIS_SAIDAS=self._sum_columns(df_f, end_cols),
            )
            grouped = (
                df_f.groupby("REF_INFO")[["INICIO_MAIS_ENTRADA", "ESTOQUE_FINAL_MAIS_SAIDAS"]]
                .sum()
                .reset_index()
            )
            frames.append(grouped)

        if not frames:
            st.warning("Sem dados suficientes para cálculo de continuidade.")
            return

        df_total = pd.concat(frames).groupby("REF_INFO", as_index=False).sum()
        long_df = df_total.melt(
            id_vars="REF_INFO",
            value_vars=["INICIO_MAIS_ENTRADA", "ESTOQUE_FINAL_MAIS_SAIDAS"],
            var_name="Categoria",
            value_name="Quantidade",
        ).replace(
            {
                "INICIO_MAIS_ENTRADA": "Estoque Inicial + Entradas",
                "ESTOQUE_FINAL_MAIS_SAIDAS": "Estoque Final + Saídas",
            }
        )

        fig = px.line(
            long_df,
            x="REF_INFO",
            y="Quantidade",
            color="Categoria",
            markers=True,
            title="Controle do Estoque ao Longo do Tempo",
        )
        fig.update_layout(yaxis_tickformat=".0f", legend_title_text="")
        st.subheader("Continuidade do Estoque")
        st.plotly_chart(fig, use_container_width=True)

    def continuidade_estoque_barras(
        self, dfs: Dict[str, pd.DataFrame], selected_company: str
    ) -> None:
        frames = []
        for df in dfs.values():
            if "REF_INFO" not in df.columns:
                continue
            df_f = self._filt(df, selected_company)
            df_f = df_f.assign(
                INICIAL_ENTRADA=self._sum_columns(df_f, ["ESTOQUE_INICIAL"]),
                FINAL_SAIDAS=self._sum_columns(
                    df_f,
                    [
                        "ESTOQUE_FINAL"
                    ],
                ),
            )
            grouped = (
                df_f.groupby("REF_INFO")[["INICIAL_ENTRADA", "FINAL_SAIDAS"]]
                .sum()
                .reset_index()
            )
            frames.append(grouped)

        if not frames:
            st.warning("Sem dados para montar o comparativo de barras.")
            return

        df_tot = pd.concat(frames).groupby("REF_INFO", as_index=False).sum()
        long_df = df_tot.melt(
            id_vars="REF_INFO",
            value_vars=["INICIAL_ENTRADA", "FINAL_SAIDAS"],
            var_name="Período",
            value_name="Quantidade",
        ).replace({"INICIAL_ENTRADA": "COMEÇO", "FINAL_SAIDAS": "FIM"})

        fig = px.bar(
            long_df,
            x="REF_INFO",
            y="Quantidade",
            color="Período",
            barmode="group",
            text_auto=".2s",
            title="Controle da Continuidade do Estoque Entre Períodos",
        )
        fig.update_layout(xaxis_title="Ano", yaxis_title="Quantidade")
        st.subheader("Continuidade em Barras")
        st.plotly_chart(fig, use_container_width=True)

    def variacao_estoque_entre_periodos(
        self, dfs: Dict[str, pd.DataFrame], selected_company: str
    ) -> None:
        frames = []
        for df in dfs.values():
            if not {"REF_INFO", "ESTOQUE_INICIAL", "ESTOQUE_FINAL"}.issubset(df.columns):
                continue
            df_f = self._filt(df, selected_company)
            grouped = (
                df_f.groupby("REF_INFO")[["ESTOQUE_INICIAL", "ESTOQUE_FINAL"]]
                .sum()
                .reset_index()
            )
            frames.append(grouped)

        if not frames:
            st.warning("Sem dados para calcular variação de estoque.")
            return

        df_tot = pd.concat(frames).groupby("REF_INFO", as_index=False).sum()
        df_tot["VARIACAO"] = df_tot["ESTOQUE_FINAL"] - df_tot["ESTOQUE_INICIAL"]

        fig = px.line(
            df_tot,
            x="REF_INFO",
            y="VARIACAO",
            markers=True,
            text="VARIACAO",
            title="Variação do Estoque Entre Períodos",
        )
        fig.update_traces(texttemplate="%{text:.0f}", textposition="top center")
        fig.update_layout(
            xaxis_title="Ano",
            yaxis_title="Variação",
            showlegend=False,
        )
        st.subheader("Variação de Estoque")
        st.plotly_chart(fig, use_container_width=True)

    def cobertura_estoque_por_empresa(
        self,
        dfs: Dict[str, pd.DataFrame],
        selected_company: str,
        year_range: tuple[int, int],
    ) -> None:
        required = {"EMP", "COD_EMP", "REF_INFO"}
        frames: list[pd.DataFrame] = []

        for df in dfs.values():
            if not required.issubset(df.columns):
                continue

            subset_cols = [
                "EMP",
                "COD_EMP",
                "REF_INFO",
                "ESTOQUE_INICIAL",
                "ESTOQUE_FINAL",
            ]
            present_cols = [col for col in subset_cols if col in df.columns]
            subset = df.loc[:, present_cols].copy()
            for missing in set(subset_cols) - set(present_cols):
                subset[missing] = pd.NA
            subset["EMP"] = subset["EMP"].astype(str).str.strip()
            subset["COD_EMP"] = subset["COD_EMP"].astype(str).str.strip()
            subset = subset[
                subset["COD_EMP"].notna()
                & subset["COD_EMP"].ne("")
                & subset["EMP"].notna()
                & subset["EMP"].ne("")
            ]

            if selected_company != "Todas":
                subset = subset[subset["EMP"] == selected_company]

            subset = subset[subset["EMP"].ne("ICA")]
            subset = subset[subset["EMP"].ne("MAP")]
            subset = subset[
                subset["REF_INFO"].between(year_range[0], year_range[1], inclusive="both")
            ]
            if subset.empty:
                continue

            subset["ESTOQUE_INICIAL"] = pd.to_numeric(
                subset["ESTOQUE_INICIAL"], errors="coerce"
            )
            subset["ESTOQUE_FINAL"] = pd.to_numeric(
                subset["ESTOQUE_FINAL"], errors="coerce"
            )
            subset["HAS_INICIAL"] = subset["ESTOQUE_INICIAL"].fillna(0) > 0
            subset["HAS_FINAL"] = subset["ESTOQUE_FINAL"].fillna(0) > 0
            subset = subset[subset["HAS_INICIAL"] | subset["HAS_FINAL"]]
            if subset.empty:
                continue
            frames.append(
                subset[["EMP", "COD_EMP", "REF_INFO", "HAS_INICIAL", "HAS_FINAL"]]
            )

        if not frames:
            st.info("Sem dados suficientes para validar estoques por empresa/código.")
            return

        combined = pd.concat(frames, ignore_index=True)
        grouped = (
            combined.groupby(["EMP", "COD_EMP", "REF_INFO"], as_index=False)[
                ["HAS_INICIAL", "HAS_FINAL"]
            ]
            .max()
            .sort_values(["EMP", "COD_EMP", "REF_INFO"])
        )

        years = list(range(year_range[0], year_range[1] + 1))
        company_codes = grouped[["EMP", "COD_EMP"]].drop_duplicates()
        if company_codes.empty:
            st.info("Nenhum código encontrado para montar o comparativo de estoques.")
            return

        grid = pd.DataFrame(
            [
                {"EMP": emp, "COD_EMP": code, "REF_INFO": year}
                for emp, code in company_codes.itertuples(index=False)
                for year in years
            ]
        )
        merged = grid.merge(grouped, on=["EMP", "COD_EMP", "REF_INFO"], how="left")
        merged["HAS_INICIAL"] = merged["HAS_INICIAL"].astype("boolean")
        merged["HAS_FINAL"] = merged["HAS_FINAL"].astype("boolean")

        def _status(row: pd.Series) -> str | None:
            has_inicial = (
                None if pd.isna(row["HAS_INICIAL"]) else bool(row["HAS_INICIAL"])
            )
            has_final = None if pd.isna(row["HAS_FINAL"]) else bool(row["HAS_FINAL"])

            if has_inicial is None and has_final is None:
                return None
            if has_inicial and has_final:
                return "OK"
            if has_inicial and not has_final:
                return "Sem Estoque Final"
            if (has_inicial is False) and has_final:
                return "Sem Estoque Inicial"
            return None

        merged["STATUS"] = merged.apply(_status, axis=1)
        merged["EMP_COD"] = merged["EMP"] + " - " + merged["COD_EMP"]
        pivot = (
            merged.pivot(index="EMP_COD", columns="REF_INFO", values="STATUS")
            .sort_index()
            .sort_index(axis=1)
        )
        pivot = pivot.dropna(how="all")

        if pivot.empty:
            st.info("Não foi possível montar a matriz de estoques por empresa/código.")
            return

        status_order = ["Sem Estoque Final", "Sem Estoque Inicial", "OK"]
        status_to_code = {status: idx for idx, status in enumerate(status_order)}
        color_scale = [
            (0.0, "#ef6c00"),  # Sem Estoque Final
            (0.5, "#f9a825"),  # Sem Estoque Inicial
            (1.0, "#2e7d32"),  # OK
        ]
        z_values = pivot.applymap(lambda value: status_to_code.get(value, float("nan")))

        fig = px.imshow(
            z_values,
            labels={"x": "Ano", "y": "Empresa / Código", "color": "Situação"},
            aspect="auto",
            color_continuous_scale=color_scale,
            zmin=0,
            zmax=len(status_order) - 1,
        )
        fig.update_traces(
            text=pivot.fillna("").values,
            texttemplate="%{text}",
            hovertemplate="Empresa/Código: %{y}<br>Ano: %{x}<br>Situação: %{text}<extra></extra>",
        )
        fig.update_coloraxes(
            colorbar=dict(
                tickmode="array",
                tickvals=list(status_to_code.values()),
                ticktext=status_order,
            )
        )

        st.subheader("Cobertura de Estoques por Empresa/Código")
        st.caption(
            "Cada célula indica se existem valores de estoque inicial/final para o ano selecionado."
        )
        st.plotly_chart(fig, use_container_width=True)

    def exposicao_por_idade_sexo(
        self,
        dfs: Dict[str, pd.DataFrame],
        selected_company: str,
        selected_sex: str,
        selected_product: str,
        selected_year: int | str,
    ) -> None:
        plot_data = []

        for coverage_type, df in dfs.items():
            if "EXPOSICAO" not in df.columns:
                continue

            df_f = self._ensure_age_column(
                self._filt(
                    df,
                    selected_company,
                    selected_sex,
                    selected_product,
                    selected_year,
                )
            )
            if "IDADE_31_DEZ" not in df_f.columns:
                continue

            grouped = (
                df_f.groupby("IDADE_31_DEZ")["EXPOSICAO"].sum().reset_index()
            )
            display_name = self.coverage_config[coverage_type]["display_name"]
            plot_data.append(grouped.rename(columns={"EXPOSICAO": display_name}))

        if not plot_data:
            st.info("Sem dados de exposição para os filtros selecionados.")
            return

        df_joined = plot_data[0]
        for nxt in plot_data[1:]:
            df_joined = df_joined.merge(nxt, on="IDADE_31_DEZ", how="outer")
        df_joined = df_joined.fillna(0).sort_values("IDADE_31_DEZ")

        cols = [c for c in df_joined.columns if c != "IDADE_31_DEZ"]
        fig = px.line(
            df_joined,
            x="IDADE_31_DEZ",
            y=cols,
            labels={
                "IDADE_31_DEZ": "Idade",
                "value": "Exposição",
                "variable": "Cobertura",
            },
        )
        fig.update_layout(yaxis_title="Exposição", xaxis_title="Idade")
        st.subheader(f"Exposicao por Idade ({selected_sex}, {selected_year}, {selected_product})")
        st.plotly_chart(fig, use_container_width=True)

    def obitos_por_idade_sexo(
        self,
        dfs: Dict[str, pd.DataFrame],
        selected_company: str,
        selected_sex: str,
        selected_product: str,
        selected_year: int | str,
    ) -> None:
        plot_data = []
        obito_cols = ["OBITO_100", "OBITO_200", "OBITO_300"]

        for coverage_type, df in dfs.items():
            df_f = self._ensure_age_column(
                self._filt(
                    df,
                    selected_company,
                    selected_sex,
                    selected_product,
                    selected_year,
                )
            )
            if "IDADE_31_DEZ" not in df_f.columns:
                continue

            df_f["OBITOS_TOTAL"] = self._sum_columns(df_f, obito_cols)
            grouped = (
                df_f.groupby("IDADE_31_DEZ")["OBITOS_TOTAL"]
                .sum()
                .reset_index()
            )
            display_name = self.coverage_config[coverage_type]["display_name"]
            plot_data.append(grouped.rename(columns={"OBITOS_TOTAL": display_name}))

        if not plot_data:
            st.info("Sem dados de óbitos para os filtros selecionados.")
            return

        df_joined = plot_data[0]
        for nxt in plot_data[1:]:
            df_joined = df_joined.merge(nxt, on="IDADE_31_DEZ", how="outer")
        df_joined = df_joined.fillna(0).sort_values("IDADE_31_DEZ")

        cols = [c for c in df_joined.columns if c != "IDADE_31_DEZ"]
        fig = px.line(
            df_joined,
            x="IDADE_31_DEZ",
            y=cols,
            labels={
                "IDADE_31_DEZ": "Idade",
                "value": "Óbitos",
                "variable": "Cobertura",
            },
        )
        fig.update_layout(yaxis_title="Óbitos", xaxis_title="Idade")
        st.subheader(f"Óbitos por Idade ({selected_sex}, {selected_year}, {selected_product})")
        st.plotly_chart(fig, use_container_width=True)

    def entradas_invalidez_por_idade_sexo(
        self,
        dfs: Dict[str, pd.DataFrame],
        selected_company: str,
        selected_sex: str,
        selected_product: str,
        selected_year: int | str,
    ) -> None:
        inval_cols = [
            "ENTRADA_INVALIDEZ_400",
            "ENTRADA_INVALIDEZ_500",
            "ENTRADA_INVALIDEZ_600",
            "ENTRADA_INVALIDEZ_700",
        ]
        plot_data = []

        for coverage_type, df in dfs.items():
            df_f = self._ensure_age_column(
                self._filt(
                    df,
                    selected_company,
                    selected_sex,
                    selected_product,
                    selected_year,
                )
            )
            if "IDADE_31_DEZ" not in df_f.columns:
                continue

            df_f["INVAL_TOTAL"] = self._sum_columns(df_f, inval_cols)
            grouped = (
                df_f.groupby("IDADE_31_DEZ")["INVAL_TOTAL"]
                .sum()
                .reset_index()
            )
            display_name = self.coverage_config[coverage_type]["display_name"]
            plot_data.append(grouped.rename(columns={"INVAL_TOTAL": display_name}))

        if not plot_data:
            st.info("Sem dados de entradas de invalidez para os filtros selecionados.")
            return

        df_joined = plot_data[0]
        for nxt in plot_data[1:]:
            df_joined = df_joined.merge(nxt, on="IDADE_31_DEZ", how="outer")
        df_joined = df_joined.fillna(0).sort_values("IDADE_31_DEZ")

        cols = [c for c in df_joined.columns if c != "IDADE_31_DEZ"]
        fig = px.line(
            df_joined,
            x="IDADE_31_DEZ",
            y=cols,
            labels={
                "IDADE_31_DEZ": "Idade",
                "value": "Entradas",
                "variable": "Cobertura",
            },
        )
        fig.update_layout(yaxis_title="Entradas", xaxis_title="Idade")
        st.subheader(f"Entradas de Invalidez ({selected_sex}, {selected_year}, {selected_product})")
        st.plotly_chart(fig, use_container_width=True)

    def exposicao_por_idade_por_ano(
        self,
        dfs: Dict[str, pd.DataFrame],
        selected_company: str,
        selected_sex: str,
        selected_product: str,
        selected_coverage: str,
        selected_cod_emp: str,
    ) -> None:
        if selected_coverage == "Todas":
            df = pd.concat([frame.copy() for frame in dfs.values()], ignore_index=True)
        else:
            df = dfs[selected_coverage].copy()

        df = self._ensure_age_column(df)
        if "IDADE_31_DEZ" not in df.columns or "REF_INFO" not in df.columns:
            st.info("Dados de idade ou ano indisponíveis para análise cruzada.")
            return

        cond = pd.Series(True, index=df.index)
        if selected_company != "Todas" and "EMP" in df.columns:
            cond &= df["EMP"] == selected_company
        if selected_sex != "Todos" and "SEXO" in df.columns:
            cond &= df["SEXO"] == selected_sex
        if selected_product != "Todos" and "PRODUTO" in df.columns:
            produtos = df["PRODUTO"].astype(str).str.strip()
            cond &= produtos == selected_product
        if selected_cod_emp != "Todos" and "COD_EMP" in df.columns:
            cond &= df["COD_EMP"].astype(str) == selected_cod_emp

        df = df.loc[cond]
        if df.empty:
            st.info("Sem dados para a combinação escolhida.")
            return

        df_grouped = (
            df.groupby(["REF_INFO", "IDADE_31_DEZ"])["EXPOSICAO"]
            .sum()
            .reset_index()
        )

        df_pivot = (
            df_grouped.pivot(index="IDADE_31_DEZ", columns="REF_INFO", values="EXPOSICAO")
            .fillna(0)
            .reset_index()
        )

        anos = [col for col in df_pivot.columns if col != "IDADE_31_DEZ"]
        fig = px.line(
            df_pivot,
            x="IDADE_31_DEZ",
            y=anos,
            labels={"IDADE_31_DEZ": "Idade", "value": "Exposição", "variable": "Ano"},
            markers=True,
        )
        fig.update_layout(xaxis_title="Idade", yaxis_title="Exposição")
        st.subheader(
            f"Exposicao por Idade ({selected_sex}, {selected_product}) - Cobertura {selected_coverage}"
        )
        st.plotly_chart(fig, use_container_width=True)

    def mot_cobertura_confusion(
        self,
        dfs: Dict[str, pd.DataFrame],
        selected_company: str,
        selected_sex: str,
        selected_product: str,
        selected_year: int | str,
    ) -> None:
        default_map = {
            "INV": [
                "OBITO_100",
                "OBITO_200",
                "OBITO_300",
                "ENTRADA_INVALIDEZ_400",
                "ENTRADA_INVALIDEZ_500",
                "ENTRADA_INVALIDEZ_600",
                "ENTRADA_INVALIDEZ_700",
                "APOSENTADORIA",
                "OUTRAS_SAIDAS",
            ],
            "MOR": [
                "OBITO_100",
                "OBITO_200",
                "OBITO_300",
                "ENTRADA_INVALIDEZ_400",
                "ENTRADA_INVALIDEZ_500",
                "ENTRADA_INVALIDEZ_600",
                "ENTRADA_INVALIDEZ_700",
                "APOSENTADORIA",
                "OUTRAS_SAIDAS",
            ],
            "SOB": [
                "OBITO_100",
                "OBITO_200",
                "OBITO_300",
                "ENTRADA_INVALIDEZ_400",
                "ENTRADA_INVALIDEZ_500",
                "ENTRADA_INVALIDEZ_600",
                "ENTRADA_INVALIDEZ_700",
                "APOSENTADORIA",
                "OUTRAS_SAIDAS",
            ],
        }

        plot_data = []

        for coverage, df in dfs.items():
            df_f = self._filt(
                df,
                selected_company,
                selected_sex,
                selected_product,
                selected_year,
            )
            if df_f.empty:
                continue

            event_cols = [
                col
                for col in default_map.get(coverage, [])
                if col in df_f.columns and col.split("_")[-1].isdigit()
            ]
            if not event_cols:
                st.warning(f"{coverage}: sem colunas numéricas para gerar matriz de motivos.")
                continue

            mask = df_f[event_cols].gt(0).any(axis=1)
            df_events = df_f[mask].copy()
            if df_events.empty:
                continue

            codes = (
                df_events[event_cols]
                .idxmax(axis=1)
                .str.split("_")
                .str[-1]
                .astype(int)
            )
            df_events["MOT_SAIDA"] = codes

            display_name = self.coverage_config[coverage]["display_name"]
            grouped = df_events.groupby("MOT_SAIDA").size().reset_index(name=display_name)
            plot_data.append(grouped)

        if not plot_data:
            st.error("Não há dados suficientes para montar a matriz de motivo x cobertura.")
            return

        df_joined = plot_data[0]
        for nxt in plot_data[1:]:
            df_joined = df_joined.merge(nxt, on="MOT_SAIDA", how="outer")
        df_joined = df_joined.fillna(0).set_index("MOT_SAIDA")

        fig = px.imshow(
            df_joined,
            text_auto=True,
            aspect="auto",
            labels={"x": "Cobertura", "y": "Motivo de Saída", "color": "Contagem"},
            title=f"Matriz Motivo x Cobertura - {selected_company} / {selected_sex} / {selected_product} / {selected_year}",
        )
        st.subheader("Motivo da Saída por Cobertura")
        st.plotly_chart(fig, use_container_width=True)


__all__ = ["InsuranceVisualizer"]
