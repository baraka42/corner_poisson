# --- NOVA ABA: SIMULAÇÃO DE WINRATE COM PLOTLY ---
with tab_winrate_sim:
    st.markdown("##### 🎯 Simulador de Taxa de Vitória")
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    with col_sim1:
        winrate_target = st.slider("Taxa de Vitória Alvo (%)", 1.0, 99.0, 47.5, 0.5)
    with col_sim2:
        num_simulations = st.slider("Número de Simulações", 10, 5000, 1000, 100)  # 🔥 Máximo 5000
    with col_sim3:
        auto_run = st.checkbox("Executar automaticamente", value=True)
    
    if num_simulations > 2000:
        st.info("ℹ️ Simulações acima de 2.000 podem levar alguns segundos.")
    
    run_simulation = st.button("Executar Simulação")
    
    if run_simulation or auto_run:
        # Mostrar parâmetros
        st.subheader("Parâmetros da Simulação")
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            st.metric("Taxa de Vitória Alvo", f"{winrate_target}%")
        with col_param2:
            st.metric("Número de Simulações", f"{num_simulations:,}".replace(",", "."))
        
        # Barra de progresso para simulações maiores
        if num_simulations > 1000:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Simulação
        results = []
        for i in range(num_simulations):
            result = 1 if np.random.rand() < (winrate_target / 100.0) else 0
            results.append(result)
            if num_simulations > 1000 and i % 500 == 0:  # 🔥 Atualização a cada 500
                progress_bar.progress((i + 1) / num_simulations)
                status_text.text(f"Simulando... {i+1}/{num_simulations}")
        
        winrate_accumulated = np.cumsum(results) / np.arange(1, num_simulations + 1)
        
        if num_simulations > 1000:
            progress_bar.empty()
            status_text.empty()
        
        # Estatísticas
        final_winrate = winrate_accumulated[-1] * 100
        total_wins = sum(results)
        
        st.subheader("Resultados da Simulação")
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Vitórias", f"{total_wins:,}".replace(",", "."))
        with col_stats2:
            st.metric("Derrotas", f"{num_simulations - total_wins:,}".replace(",", "."))
        with col_stats3:
            st.metric("Winrate Final", f"{final_winrate:.2f}%")
        
        # Gráfico com Plotly
        st.subheader("Evolução da Taxa de Vitória")
        
        # Otimização - com máximo 5000, podemos mostrar mais pontos
        if num_simulations > 500:
            step = max(1, num_simulations // 250)  # 🔥 Mais pontos para melhor visualização
            indices = range(0, num_simulations, step)
            sampled_winrate = winrate_accumulated[indices] * 100
            sampled_indices = [i + 1 for i in indices]
        else:
            sampled_winrate = winrate_accumulated * 100
            sampled_indices = range(1, num_simulations + 1)
        
        # Criar gráfico Plotly
        fig = go.Figure()
        
        # Linha do winrate
        fig.add_trace(go.Scatter(
            x=sampled_indices,
            y=sampled_winrate,
            mode='lines',
            name=f'Winrate Real ({final_winrate:.1f}%)',
            line=dict(color='#00D4AA', width=2),
            hovertemplate='Simulação: %{x}<br>Winrate: %{y:.2f}%<extra></extra>'
        ))
        
        # Linha do target
        fig.add_trace(go.Scatter(
            x=[sampled_indices[0], sampled_indices[-1]],
            y=[winrate_target, winrate_target],
            mode='lines',
            name=f'Target ({winrate_target}%)',
            line=dict(color='#FF6B6B', width=2, dash='dash'),
            hovertemplate='Target: %{y}%<extra></extra>'
        ))
        
        # Layout do gráfico
        fig.update_layout(
            title=f"Evolução do Winrate • {num_simulations:,} simulações".replace(",", "."),
            xaxis_title="Número de Simulações",
            yaxis_title="Winrate (%)",
            plot_bgcolor='#1E1E1E',
            paper_bgcolor='#1E1E1E',
            font=dict(color='#FFFFFF', size=12),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Configurações dos eixos
        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='#444444')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='#444444')
        
        st.plotly_chart(fig, use_container_width=True)