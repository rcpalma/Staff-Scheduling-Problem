from data import *
from solver import solve_NSP
from plot import *
import sys


def run_project(n_instancia):
    print(f"Iniciando NSP com a instância {n_instancia}")

    print(f" Fase 1: Carregando dados")
    I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt = dados(n_instancia)

    print(f" Fase 2: Resolvendo o modelo")
    x_val, y_val, z_val, k_val, obj_val, status, gap = solve_NSP(I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt)

    print(f" Fase 3: Exibindo resultados")

    print(f"Status: {status}")
    print(f"Gap: {gap}")
    print(f"Objective: {obj_val}")

    print(f" Fase 4: Gerando gráficos")
    plot_grid(x_val)
    plot_bar(x_val, u_dt)

if __name__ == "__main__":
    instancia = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    run_project(instancia)