let dados = [];

async function carregarDados() {
    try {
        // carrega JSONs
        const responseDF = await fetch("data/empresas_df.json");
        const responseGO = await fetch("data/empresas_go.json");
        
        if (!responseDF.ok || !responseGO.ok) {
            throw new Error('Erro ao carregar arquivos JSON');
        }
        
        const df = await responseDF.json();
        const go = await responseGO.json();
        
        console.log('DF carregado:', df); // Para debug
        console.log('GO carregado:', go); // Para debug

        // adiciona campo estado dentro de cada objeto
        const dfComEstado = df.map(item => ({ ...item, Estado: "DF" }));
        const goComEstado = go.map(item => ({ ...item, Estado: "GO" }));

        // junta os dois
        dados = [...dfComEstado, ...goComEstado];

        console.log('Todos os dados:', dados); // Para debug
        renderTabela(dados);
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        document.getElementById("resultado").innerHTML = `
            <tr>
                <td colspan="4" style="color: red; text-align: center;">
                    Erro ao carregar dados: ${error.message}
                </td>
            </tr>
        `;
    }
}

function pesquisar() {
    const termo = document.getElementById("buscar").value.toLowerCase();
    const estado = document.getElementById("estado").value;

    const filtrados = dados.filter(item => {
        const nome = (item.Nome || "").toLowerCase();

        return (
            nome.includes(termo) &&
            (estado === "" || item.Estado === estado)
        );
    });

    renderTabela(filtrados);
}

function renderTabela(lista) {
    const tbody = document.getElementById("resultado");
    tbody.innerHTML = "";

    lista.forEach(item => {
        const contato = item.Telefone || item.Email || "-";

        tbody.innerHTML += `
            <tr>
                <td>${item.Nome || "-"}</td>
                <td>${contato}</td>
                <td>${item.Endereço || "-"}</td>
                <td>${item.Estado}</td>
            </tr>
        `;
    });
}



carregarDados();
