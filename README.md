# Staff Scheduling Problem do paper: https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf

Nesse projeto pessoal, implementei no python usando gurobi/gurobipy o problema descrito no paper acima.

## Descrição
O problema Staff Scheduling consiste em atribuir turnos a empregados durante um horizonte de planejamento satisfazendo um conjunto de restrições operacionais e regulatorias.

## Instâncias
O paper disponibiliza 20 instâncias construídas a partir de dados reais.  **Apenas as primeiras 10 instâncias estão incluídas neste repositório**

## Estrutura do Projeto
```text
├── main.py        # main
├── Solver.py      # Modelagem e otimização (Gurobi)
├── Data.py        # Leitura e tratamento dos dados utilizando pandas (.txt → parâmetros)
├── plot.py        # Visualizações da solução
├── api.py         # API 
└── frontend/
    └── src/
        └── App.jsx

```
**A API e a interface web foram desenvolvidas com auxílio de IA como forma de tornar o modelo acessível e iterativo via browser. O tratamento de dados utilizando pandas, modelagem e resolução foi feita exclusivamente pelo autor**

## Resultados e Gráficos

Dois gráficos são gerados ao executar main.py

**Primeiro - Mapa das atribuições:** Heatmap com os empregados no eixo y e o horizonte de planejamento no eixo x. Cada célula representa o turno atribuído ao empregado naquele dia. 
<img width="1923" height="700" alt="mapa_calor" src="https://github.com/user-attachments/assets/e82d0d05-40b6-4684-a3c9-683bea0115e1" />


**Segundo - Grafico de Cobertura diária:** Barplot com a quantidade de empregados ativos por dia.
<img width="1200" height="800" alt="Cobertura" src="https://github.com/user-attachments/assets/9099e7b4-19b5-4b7a-91c1-3d952171db7b" />

## Como usar
No diretório do projeto execute o comando: "python main.py <número da instância>"
Exemplo: python main.py 3

## Requirements

- Python 3.10+
- Gurobi (with valid license — academic license available at gurobi.com)
- **Python dependencies:**
  - `matplotlib`
  - `seaborn`
  - `pandas`
  - `gurobipy`
```
pip install -r requirements.txt
```





## References
*   **NRP Benchmark Dataset**: [Scheduling Benchmarks - Nurse Rostering](https://www.schedulingbenchmarks.org/nrp/)
*   **Technical Report**: Curtois, T., & Qu, R. (2014). *Computational results on new staff scheduling benchmark instances*. [Link para o PDF](https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf)
