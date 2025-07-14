async function buscarDados() {
    const ticker = document.getElementById("tickerInput").value.toUpperCase();
    const dadosDiv = document.getElementById("dados");
    const ctx = document.getElementById("grafico").getContext("2d");

    dadosDiv.innerHTML = "Carregando...";

    try {
        const resInfo = await fetch(`http://127.0.0.1:8000/empresa/${ticker}`);
        if (!resInfo.ok) throw new Error("Erro na rota /empresa");
        const info = await resInfo.json();

        dadosDiv.innerHTML = `
            <h2>${info.nome}</h2>
            <p>Preço atual: ${info.preco_atual}</p>
            <p>Dividend Yield: ${info.dividend_yield ?? 'N/A'}</p>
            <p>Lucro por Ação (EPS): ${info.lucro_por_acao ?? 'N/A'}</p>
            <p>Setor: ${info.setor ?? 'N/A'}</p>
        `;

        const resHist = await fetch(`http://127.0.0.1:8000/historico/${ticker}`);
        if (!resHist.ok) throw new Error("Erro na rota /historico");
        const historico = await resHist.json();

        // Se não há histórico, apenas exibe aviso e mantém os dados
        if (historico.length === 0) {
            dadosDiv.innerHTML += `<p><strong>Aviso:</strong> Sem dados históricos disponíveis.</p>`;
            if (window.grafico instanceof Chart) {
                window.grafico.destroy();
            }
            return;
        }

        const labels = historico.map(item => item.data);
        const dados = historico.map(item => item.preco_fechamento);

        if (window.grafico instanceof Chart) {
            window.grafico.destroy();
        }

        window.grafico = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Preço (${ticker})`,
                    data: dados,
                    borderWidth: 2,
                    fill: false
                }]
            }
        });

    } catch (error) {
        dadosDiv.innerHTML = "Erro ao buscar dados. Verifique o ticker.";
        console.error(error);
    }
}
