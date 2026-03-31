import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch
import matplotlib.lines as mlines

def plot_grid(x):
    
    # 1. Extrai funcionários e dias únicos diretamente das chaves do dicionário
    # Set() remove duplicatas, sorted() coloca em ordem alfabética/numérica
    employees = sorted(list(set([chave[0] for chave in x.keys()])))
    days = sorted(list(set([chave[1] for chave in x.keys()])))
    
    # 2. Cria os rótulos dos dias (Mon1, Tue1, ..., Mon2, ...)
    day_names = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    day_labels = [f"{day_names[d % 7]}{(d // 7) + 1}" for d in days]
    
    # 3. Inicializa a matriz da escala com zeros (todo mundo de folga)
    schedule_matrix = np.zeros((len(employees), len(days)))
    
    # Matriz para as anotações textuais (o nome do turno no centro)
    annot_matrix = np.empty((len(employees), len(days)), dtype=object)
    annot_matrix[:] = ""
    
    # Dicionário auxiliar para achar a linha (índice) de cada funcionário rápido
    emp_to_idx = {emp: idx for idx, emp in enumerate(employees)}
    
    # 4. Preenche a matriz
    for (i, j, k), val in x.items():
        if val > 0.5: # Se o valor da variável do Gurobi for 1 (trabalhando)
            col_idx = days.index(j)    # Coluna correspondente ao dia
            row_idx = emp_to_idx[i]    # Linha correspondente ao funcionário
            schedule_matrix[row_idx, col_idx] = 1 # Pinta de azul
            annot_matrix[row_idx, col_idx] = str(k) # Salva o nome do turno para exibir no quadrado
            
    # 5. Configuração visual do gráfico
    # Ajusta o tamanho da imagem dinamicamente baseado na quantidade de dias e funcionários
    plt.figure(figsize=(max(10, len(days) * 0.8), len(employees) * 0.5 + 2))
    
    # Cores: 0 = Cinza claro (Folga), 1 = Azul (Trabalho)
    cmap = sns.color_palette(["#f0f0f0", "#1f77b4"])
    
    # Desenha o heatmap
    ax = sns.heatmap(
        schedule_matrix, 
        cmap=cmap, 
        cbar=False,           
        xticklabels=day_labels, 
        yticklabels=employees,
        linewidths=1.5,       
        linecolor='white',    
        square=True,
        annot=annot_matrix,   # Coloca os textos na matriz
        fmt="",               # Formato vazio para aceitar as strings (nomes dos turnos)
        annot_kws={"size": 10, "weight": "bold", "color": "white"} # Estilo da fonte
    )
    
    # Move os dias para a parte de cima do gráfico
    ax.xaxis.tick_top()
    plt.xticks(rotation=45, ha='left', fontsize=10)
    plt.yticks(rotation=0, fontsize=11)
    
    plt.title("Escala de Trabalho", pad=40, fontsize=14, fontweight='bold')
    plt.ylabel("Funcionários", fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('escala.png')



def plot_bar(x, u_dt):
    
    # 1. Extrai dias e turnos únicos das chaves dos dicionários
    days = sorted(list(set([chave[1] for chave in x.keys()])))
    shifts = sorted(list(set([chave[2] for chave in x.keys()])))
    
    # Rótulos dos dias (Mon1, Tue1...) para manter a consistência com o gráfico anterior
    day_names = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    day_labels = [f"{day_names[d % 7]}{(d // 7) + 1}" for d in days]
    
    # 2. Calcula a quantidade REAL de funcionários alocados por (dia, turno)
    actual_dt = {(d, t): 0 for d in days for t in shifts}
    for (i, d, t), val in x.items():
        if val > 0.5: # Se o funcionário trabalhou
            actual_dt[(d, t)] += 1

    # 3. Cria subplots (um gráfico para cada turno para não misturar os dados)
    fig, axes = plt.subplots(len(shifts), 1, figsize=(12, 4 * len(shifts)), sharex=True)
    
    # Garante que axes seja uma lista mesmo se houver apenas 1 turno
    if len(shifts) == 1:
        axes = [axes]
        
    x_pos = np.arange(len(days)) # Posições no eixo X
    
    # 4. Desenha o gráfico para cada turno
    for idx, t in enumerate(shifts):
        ax = axes[idx]
        
        # Pega os valores reais e os requisitos para o turno atual
        actual_vals = [actual_dt[(d, t)] for d in days]
        req_vals = [u_dt.get((d, t), 0) for d in days] # Usa .get com default 0 por segurança
        
        # Define a cor de cada barra comparando o Real vs Requisito
        bar_colors = []
        for a, r in zip(actual_vals, req_vals):
            if a == r:
                bar_colors.append('#2ca02c') # Verde (Perfeito)
            elif a < r:
                bar_colors.append('#d62728') # Vermelho (Abaixo do requisito)
            else:
                bar_colors.append('#1f77b4') # Azul (Acima do requisito)
                
        # Plota as barras (Quantidade Real)
        ax.bar(x_pos, actual_vals, color=bar_colors, alpha=0.75, width=0.6)
        
        # Plota os marcadores do Requisito (Linhas pretas horizontais sobre as barras)
        ax.plot(x_pos, req_vals, marker='_', markersize=25, color='black', 
                linewidth=0, markeredgewidth=3, zorder=5)
        
        # Formatações do eixo
        ax.set_title(f"Cobertura do Turno: {t}", fontweight='bold', fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(day_labels, rotation=45, ha='right')
        ax.set_ylabel("Nº de Funcionários")
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        # Cria a legenda customizada
        legend_elements = [
            Patch(facecolor='#2ca02c', alpha=0.75, label='Atingiu o Requisito'),
            Patch(facecolor='#1f77b4', alpha=0.75, label='Excesso de Pessoal'),
            Patch(facecolor='#d62728', alpha=0.75, label='Falta de Pessoal'),
            mlines.Line2D([], [], color='black', marker='_', linestyle='None', 
                          markersize=15, markeredgewidth=3, label='Meta')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

    plt.tight_layout()
    plt.savefig('cobertura.png')







