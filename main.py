from data import *
from solver import solve_NSP
from plot import *



I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt = dados(3)

x_val,y_val,z_val,k_val,obj_val = solve_NSP(I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt)



print(obj_val)

plot_grid(x_val)

plot_bar(x_val, u_dt)