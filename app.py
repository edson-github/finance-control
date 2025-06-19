# app.py - será preenchido com o código completo

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os

# Configuração da página
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("💰 Controle Financeiro Pessoal")
st.markdown("---")


# Funções auxiliares
def carregar_dados(arquivo):
    """Carrega dados do CSV ou cria um DataFrame vazio"""
    caminho = f"dados/{arquivo}.csv"
    if os.path.exists(caminho) and os.path.getsize(caminho) > 0:
        df = pd.read_csv(caminho)
        df['data'] = pd.to_datetime(df['data'])
        return df
    else:
        return pd.DataFrame(
            columns=['data', 'descricao', 'valor', 'categoria']
        )


def salvar_dados(df, arquivo):
    """Salva dados no CSV"""
    caminho = f"dados/{arquivo}.csv"
    df.to_csv(caminho, index=False)


def adicionar_registro(df, data, descricao, valor, categoria):
    """Adiciona um novo registro ao DataFrame"""
    novo_registro = pd.DataFrame({
        'data': [data],
        'descricao': [descricao],
        'valor': [valor],
        'categoria': [categoria]
    })
    return pd.concat([df, novo_registro], ignore_index=True)


# Sidebar para navegação
st.sidebar.title("📊 Navegação")
pagina = st.sidebar.selectbox(
    "Escolha uma seção:",
    ["🏠 Dashboard", "💰 Receitas", "💸 Despesas", "🎯 Metas", 
     "⚙️ Configurações"]
)

# Carregar dados
receitas_df = carregar_dados('receitas')
despesas_df = carregar_dados('despesas')
metas_df = carregar_dados('metas')

# Dashboard
if pagina == "🏠 Dashboard":
    st.header("📊 Dashboard Financeiro")

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_receitas = (receitas_df['valor'].sum()
                         if not receitas_df.empty else 0)
        st.metric("Total Receitas", f"R$ {total_receitas:,.2f}")

    with col2:
        total_despesas = (despesas_df['valor'].sum() 
                if not despesas_df.empty else 0)

        st.metric("Total Despesas", f"R$ {total_despesas:,.2f}")

    with col3:
        saldo = total_receitas - total_despesas
        st.metric("Saldo", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}")

    with col4:
        if total_receitas > 0:
            percentual_despesas = (total_despesas / total_receitas) * 100
        else:
            percentual_despesas = 0
        st.metric("Despesas/Receitas", f"{percentual_despesas:.1f}%")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Receitas vs Despesas (Últimos 6 meses)")
        if not receitas_df.empty or not despesas_df.empty:
            # Preparar dados para o gráfico
            hoje = datetime.now()
            if hoje.month > 6:
                seis_meses_atras = hoje.replace(month=hoje.month-6)
            else:
                seis_meses_atras = hoje.replace(
                    year=hoje.year-1, month=hoje.month+6
                )

            if not receitas_df.empty:
                receitas_filtradas = receitas_df[
                    receitas_df['data'] >= seis_meses_atras
                ]
            else:
                receitas_filtradas = pd.DataFrame()

            if not despesas_df.empty:
                despesas_filtradas = despesas_df[
                    despesas_df['data'] >= seis_meses_atras
                ]
            else:
                despesas_filtradas = pd.DataFrame()

            if not receitas_filtradas.empty or not despesas_filtradas.empty:
                fig = go.Figure()

                if not receitas_filtradas.empty:
                    receitas_mensais = receitas_filtradas.groupby(
                        receitas_filtradas['data'].dt.to_period('M')
                    )['valor'].sum()
                    fig.add_trace(go.Scatter(
                        x=receitas_mensais.index.astype(str),
                        y=receitas_mensais.values,
                        mode='lines+markers',
                        name='Receitas',
                        line=dict(color='green', width=3)
                    ))

                if not despesas_filtradas.empty:
                    despesas_mensais = despesas_filtradas.groupby(
                        despesas_filtradas['data'].dt.to_period('M')
                    )['valor'].sum()
                    fig.add_trace(go.Scatter(
                        x=despesas_mensais.index.astype(str),
                        y=despesas_mensais.values,
                        mode='lines+markers',
                        name='Despesas',
                        line=dict(color='red', width=3)
                    ))

                fig.update_layout(
                    xaxis_title="Mês",
                    yaxis_title="Valor (R$)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhum dado disponível para os últimos 6 meses")
        else:
            st.info("Nenhum dado disponível")

    with col2:
        st.subheader("🍕 Distribuição por Categoria")
        if not despesas_df.empty:
            categorias_despesas = despesas_df.groupby('categoria')['valor'].sum()
            if not categorias_despesas.empty:
                fig = px.pie(
                    values=categorias_despesas.values,
                    names=categorias_despesas.index,
                    title="Despesas por Categoria"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhuma categoria de despesa encontrada")
        else:
            st.info("Nenhuma despesa registrada")

    # Tabelas recentes
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Últimas Receitas")
        if not receitas_df.empty:
            receitas_recentes = receitas_df.sort_values(
                'data', ascending=False
            ).head(5)
            st.dataframe(
                receitas_recentes[['data', 'descricao', 'valor', 'categoria']],
                use_container_width=True
            )
        else:
            st.info("Nenhuma receita registrada")

    with col2:
        st.subheader("💸 Últimas Despesas")
        if not despesas_df.empty:
            despesas_recentes = despesas_df.sort_values(
                'data', ascending=False
            ).head(5)
            st.dataframe(
                despesas_recentes[['data', 'descricao', 'valor', 'categoria']],
                use_container_width=True
            )
        else:
            st.info("Nenhuma despesa registrada")

# Receitas
elif pagina == "💰 Receitas":
    st.header("💰 Gerenciar Receitas")

    # Formulário para adicionar receita
    with st.expander("➕ Adicionar Nova Receita", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            data_receita = st.date_input("Data", value=date.today())
            descricao_receita = st.text_input("Descrição")

        with col2:
            valor_receita = st.number_input(
                "Valor (R$)", min_value=0.01, value=1.0, step=0.01
            )
            categoria_receita = st.selectbox(
                "Categoria",
                ["Salário", "Freelance", "Investimentos", "Outros"]
            )

        if st.button("➕ Adicionar Receita"):
            if descricao_receita:
                receitas_df = adicionar_registro(
                    receitas_df, data_receita, descricao_receita,
                    valor_receita, categoria_receita
                )
                salvar_dados(receitas_df, 'receitas')
                st.success("Receita adicionada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha a descrição")

    # Visualizar receitas
    st.subheader("📋 Lista de Receitas")

    if not receitas_df.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            categorias_filtro = ["Todas"] + list(receitas_df['categoria'].unique())
            categoria_filtro = st.selectbox("Filtrar por categoria", categorias_filtro)

        with col2:
            data_inicio = st.date_input(
                "Data início", value=receitas_df['data'].min().date()
            )

        with col3:
            data_fim = st.date_input(
                "Data fim", value=receitas_df['data'].max().date()
            )

        # Aplicar filtros
        receitas_filtradas = receitas_df.copy()
        if categoria_filtro != "Todas":
            receitas_filtradas = receitas_filtradas[
                receitas_filtradas['categoria'] == categoria_filtro
            ]

        receitas_filtradas = receitas_filtradas[
            (receitas_filtradas['data'].dt.date >= data_inicio) &
            (receitas_filtradas['data'].dt.date <= data_fim)
        ] 
        # Exibir dados
        st.dataframe(receitas_filtradas, use_container_width=True)

        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Filtrado", 
                f"R$ {receitas_filtradas['valor'].sum():,.2f}"
            )
        with col2:
            st.metric(
                "Média", f"R$ {receitas_filtradas['valor'].mean():,.2f}"
            )
        with col3:
            st.metric("Quantidade", len(receitas_filtradas))

        # Opção para excluir
        st.subheader("🗑️ Excluir Receita")
        if not receitas_filtradas.empty:
            indice_excluir = st.selectbox(
                "Selecione o índice da receita para excluir:",
                receitas_filtradas.index,
                format_func=lambda x: (
                    f"{receitas_filtradas.loc[x, 'data'].strftime('%d/%m/%Y')} - "
                    f"{receitas_filtradas.loc[x, 'descricao']} - "
                    f"R$ {receitas_filtradas.loc[x, 'valor']:.2f}"
                )
            )

            if st.button("🗑️ Excluir"):
                receitas_df = receitas_df.drop(indice_excluir)
                salvar_dados(receitas_df, 'receitas')
                st.success("Receita excluída com sucesso!")
                st.rerun()
    else:
        st.info("Nenhuma receita registrada")

# Despesas
elif pagina == "💸 Despesas":
    st.header("💸 Gerenciar Despesas")

    # Formulário para adicionar despesa
    with st.expander("➕ Adicionar Nova Despesa", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            data_despesa = st.date_input("Data", value=date.today())
            descricao_despesa = st.text_input("Descrição")

        with col2:
            valor_despesa = st.number_input(
                "Valor (R$)", min_value=0.01, value=1.0, step=0.01
            )
            categoria_despesa = st.selectbox(
                "Categoria",
                ["Alimentação", "Transporte", "Moradia", "Saúde", "Educação", 
                 "Lazer", "Vestuário", "Outros"]
            )

        if st.button("➕ Adicionar Despesa"):
            if descricao_despesa:
                despesas_df = adicionar_registro(
                    despesas_df, data_despesa, descricao_despesa,
                    valor_despesa, categoria_despesa
                )
                salvar_dados(despesas_df, 'despesas')
                st.success("Despesa adicionada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha a descrição")

    # Visualizar despesas
    st.subheader("📋 Lista de Despesas")

    if not despesas_df.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            categorias_filtro = ["Todas"] + list(despesas_df['categoria'].unique())
            categoria_filtro = st.selectbox("Filtrar por categoria", categorias_filtro)

        with col2:
            data_inicio = st.date_input(
                "Data início", value=despesas_df['data'].min().date()
            )

        with col3:
            data_fim = st.date_input(
                "Data fim", value=despesas_df['data'].max().date()
            )

        # Aplicar filtros
        despesas_filtradas = despesas_df.copy()
        if categoria_filtro != "Todas":
            despesas_filtradas = despesas_filtradas[
                despesas_filtradas['categoria'] == categoria_filtro
            ]

        despesas_filtradas = despesas_filtradas[
            (despesas_filtradas['data'].dt.date >= data_inicio) &
            (despesas_filtradas['data'].dt.date <= data_fim)
        ]

        # Exibir dados
        st.dataframe(despesas_filtradas, use_container_width=True)

        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Filtrado", 
                f"R$ {despesas_filtradas['valor'].sum():,.2f}"
            )
        with col2:
            st.metric(
                "Média", f"R$ {despesas_filtradas['valor'].mean():,.2f}"
            )
        with col3:
            st.metric("Quantidade", len(despesas_filtradas))

        # Opção para excluir
        st.subheader("🗑️ Excluir Despesa")
        if not despesas_filtradas.empty:
            indice_excluir = st.selectbox(
                "Selecione o índice da despesa para excluir:",
                despesas_filtradas.index,
                format_func=lambda x: (
                    f"{despesas_filtradas.loc[x, 'data'].strftime('%d/%m/%Y')} - "
                    f"{despesas_filtradas.loc[x, 'descricao']} - "
                    f"R$ {despesas_filtradas.loc[x, 'valor']:.2f}"
                )
            )

            if st.button("🗑️ Excluir"):
                despesas_df = despesas_df.drop(indice_excluir)
                salvar_dados(despesas_df, 'despesas')
                st.success("Despesa excluída com sucesso!")
                st.rerun()
    else:
        st.info("Nenhuma despesa registrada")

# Metas
elif pagina == "🎯 Metas":
    st.header("🎯 Gerenciar Metas Financeiras")

    # Formulário para adicionar meta
    with st.expander("➕ Adicionar Nova Meta", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            data_meta = st.date_input("Data Limite", value=date.today())
            descricao_meta = st.text_input("Descrição da Meta")

        with col2:
            valor_meta = st.number_input(
                "Valor Meta (R$)", min_value=0.01, value=1000.0, step=0.01
            )
            categoria_meta = st.selectbox(
                "Categoria",
                ["Viagem", "Compras", "Investimento", "Emergência", "Outros"]
            )

        if st.button("➕ Adicionar Meta"):
            if descricao_meta:
                metas_df = adicionar_registro(
                    metas_df, data_meta, descricao_meta, valor_meta, categoria_meta
                )
                salvar_dados(metas_df, 'metas')
                st.success("Meta adicionada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha a descrição")

    # Visualizar metas
    st.subheader("📋 Lista de Metas")

    if not metas_df.empty:
        # Calcular progresso das metas
        metas_com_progresso = metas_df.copy()
        metas_com_progresso['progresso'] = 0.0

        for idx, meta in metas_com_progresso.iterrows():
            # Calcular quanto já foi economizado (receitas - despesas até a data da meta)
            data_meta = meta['data']

            if not receitas_df.empty:
                receitas_ate_meta = receitas_df[
                    receitas_df['data'] <= data_meta
                ]['valor'].sum()
            else:
                receitas_ate_meta = 0

            if not despesas_df.empty:
                despesas_ate_meta = despesas_df[
                    despesas_df['data'] <= data_meta
                ]['valor'].sum()
            else:
                despesas_ate_meta = 0

            economias = receitas_ate_meta - despesas_ate_meta
            progresso = min((economias / meta['valor']) * 100, 100) if meta['valor'] > 0 else 0

            metas_com_progresso.loc[idx, 'progresso'] = progresso
            metas_com_progresso.loc[idx, 'economias'] = economias

        # Exibir metas com progresso
        for idx, meta in metas_com_progresso.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{meta['descricao']}**")
                    st.write(f"Categoria: {meta['categoria']}")
                    st.write(f"Data limite: {meta['data'].strftime('%d/%m/%Y')}")

                with col2:
                    st.write(f"Meta: R$ {meta['valor']:,.2f}")
                    st.write(f"Economias: R$ {meta['economias']:,.2f}")

                with col3:
                    st.progress(meta['progresso'] / 100)
                    st.write(f"{meta['progresso']:.1f}%")

                st.markdown("---")

        # Estatísticas das metas
        st.subheader("📊 Estatísticas das Metas")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_metas = metas_com_progresso['valor'].sum()
            st.metric("Total das Metas", f"R$ {total_metas:,.2f}")

        with col2:
            media_progresso = metas_com_progresso['progresso'].mean()
            st.metric("Progresso Médio", f"{media_progresso:.1f}%")

        with col3:
            metas_concluidas = len(
                metas_com_progresso[metas_com_progresso['progresso'] >= 100]
            )
            st.metric("Metas Concluídas", metas_concluidas)

        # Opção para excluir
        st.subheader("🗑️ Excluir Meta")
        indice_excluir = st.selectbox(
            "Selecione o índice da meta para excluir:",
            metas_com_progresso.index,
            format_func=lambda x: (
                f"{metas_com_progresso.loc[x, 'descricao']} - "
                f"R$ {metas_com_progresso.loc[x, 'valor']:.2f}"
            )
        )

        if st.button("🗑️ Excluir"):
            metas_df = metas_df.drop(indice_excluir)
            salvar_dados(metas_df, 'metas')
            st.success("Meta excluída com sucesso!")
            st.rerun()
    else:
        st.info("Nenhuma meta registrada")

# Configurações
elif pagina == "⚙️ Configurações":
    st.header("⚙️ Configurações")

    st.subheader("📊 Backup e Restauração")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Exportar Dados**")
        if st.button("📥 Exportar Receitas"):
            if not receitas_df.empty:
                csv = receitas_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Receitas CSV",
                    data=csv,
                    file_name="receitas.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhuma receita para exportar")

        if st.button("📥 Exportar Despesas"):
            if not despesas_df.empty:
                csv = despesas_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Despesas CSV",
                    data=csv,
                    file_name="despesas.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhuma despesa para exportar")

    with col2:
        st.write("**Limpar Dados**")
        if st.button("🗑️ Limpar Todos os Dados"):
            if st.checkbox("Confirmar limpeza de todos os dados"):
                # Criar DataFrames vazios
                receitas_df = pd.DataFrame(
                    columns=['data', 'descricao', 'valor', 'categoria']
                )
                despesas_df = pd.DataFrame(
                    columns=['data', 'descricao', 'valor', 'categoria']
                )
                metas_df = pd.DataFrame(
                    columns=['data', 'descricao', 'valor', 'categoria']
                )

                # Salvar
                salvar_dados(receitas_df, 'receitas')
                salvar_dados(despesas_df, 'despesas')
                salvar_dados(metas_df, 'metas')

                st.success("Todos os dados foram limpos!")
                st.rerun()

    st.subheader("📈 Estatísticas do Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Receitas", len(receitas_df))
        st.metric("Total de Despesas", len(despesas_df))

    with col2:
        st.metric("Total de Metas", len(metas_df))
        if not receitas_df.empty:
            primeiro_registro = receitas_df['data'].min().strftime('%d/%m/%Y')
        else:
            primeiro_registro = "N/A"
        st.metric("Primeiro Registro", primeiro_registro)

    with col3:
        if not receitas_df.empty or not despesas_df.empty:
            if not receitas_df.empty and not despesas_df.empty:
                ultimo_registro = max(
                    receitas_df['data'].max(), despesas_df['data'].max()
                ).strftime('%d/%m/%Y')
                dias_uso = (
                    max(receitas_df['data'].max(), despesas_df['data'].max()) -
                    min(receitas_df['data'].min(), despesas_df['data'].min())
                ).days
            elif not receitas_df.empty:
                ultimo_registro = receitas_df['data'].max().strftime('%d/%m/%Y')
                dias_uso = 0
            else:
                ultimo_registro = despesas_df['data'].max().strftime('%d/%m/%Y')
                dias_uso = 0
        else:
            ultimo_registro = "N/A"
            dias_uso = 0

        st.metric("Último Registro", ultimo_registro)
        st.metric("Dias de Uso", dias_uso)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        💰 Controle Financeiro Pessoal | Desenvolvido com Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
