import gurobipy as gp
from gurobipy import GRB

def solve_NSP(I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt):

    D = list(D)
    model = gp.Model("NSP")

    x = model.addVars(I,D,T, vtype = GRB.BINARY, name = "x")
    k = model.addVars(I,W,vtype = GRB.BINARY, name = "k")
    y = model.addVars(D,T,lb = 0,vtype = GRB.INTEGER, name = "y")
    z = model.addVars(D,T,lb = 0,vtype = GRB.INTEGER, name = "z")


    model.addConstrs(
        (gp.quicksum(x[i,d,t] for t in T) <= 1 for i in I for d in D),
        name = "oneshift_perday"
    )


    model.addConstrs(
        ( (x[i,d,t]+ x[i,d+1,u] <= 1 ) for i in I for d in range(h-1) for t in T if t in Rt.keys() for u in Rt[t]),
        name = "consec_shifts"
    )


    model.addConstrs(
        (gp.quicksum(x[i,d,t] for d in D) <= max_it[i,t] for i in I for t in T),
        name = "num_max_shifts"
    )



    model.addConstrs(
        (gp.quicksum(lt[t] * x[i,d,t] for d in D for t in T) <=bmax_i[i] for i in I ),
         name = "max_work_time"
    )

    model.addConstrs(
        (gp.quicksum(lt[t] * x[i,d,t] for d in D for t in T) >=bmin_i[i] for i in I ),
         name = "min_work_time"
    )

    model.addConstrs(
        (gp.quicksum(x[i,j,t] for t in T for j in range(d,d+cmax_i[i]+1)) <= cmax_i[i] for i in I for d in range(h-cmax_i[i])),
        name = "max_numer_consec_shifts"
    )

    model.addConstrs(
        (gp.quicksum(x[i,d,t] for t in T) +   (s - gp.quicksum(x[i,j,t] for t in T for j in range(d+1,d+s+1)) ) +gp.quicksum(x[i,d+s+1,t] for t in T) >= 1 for i in I
         for s in range(1,cmin_i[i]) for d in range(h-s-1)),
         name = "sequences_not_allowed"
    )


    model.addConstrs(
        ( 1 - gp.quicksum(x[i,d,t] for t in T) + (gp.quicksum(x[i,j,t] for t in T for j in range(d+1,d+s+1))) + 1 - gp.quicksum(x[i,d+s+1,t] for t in T)>=1  for i in I
         for s in range(1,omin_i[i]) for d in range(h-s-1)),
         name = "sequences_not_allowed2"
    )





    model.addConstrs(
        (gp.quicksum(x[i,7*w+5,t] for t in T) + gp.quicksum(x[i,7*w+6,t] for t in T) <= 2*k[i,w] for i in I for w in W),
        name = "max_numb_weekends"
    )

    model.addConstrs(
        (gp.quicksum(x[i,7*w+5,t] for t in T) + gp.quicksum(x[i,7*w+6,t] for t in T) >= k[i,w] for i in I for w in W),
        name = "min_numb_weekends"
    )

    model.addConstrs(
        (gp.quicksum(k[i,w] for w in W) <= amax_i[i] for i in I),
        name = "num_weekends"
    )

    model.addConstrs(
        (x[i,d,t] == 0 for i in I for d in Ni[i] for t in T),
        name = "days_off"
    )
    

    model.addConstrs(
        (gp.quicksum(x[i,d,t] for i in I) -z[d,t] +y[d,t] == u_dt[d,t]  for d in D for t in T),
        name = "conver_requirements"
    )

    model.setObjective(
        gp.quicksum(q_idt[i,d,t] * (1 - x[i,d,t]) for i, d, t in q_idt.keys())
        + gp.quicksum(p_idt[i,d,t] * (x[i,d,t]) for i, d, t in p_idt.keys())
        + gp.quicksum(y[d,t] * vmin_dt[d,t] for d in D for t in T)
        + gp.quicksum(z[d,t] * vmax_dt[d,t] for d in D for t in T),
        GRB.MINIMIZE
    )

    model.setParam('TimeLimit', 120)

    model.optimize()

    status = model.Status
    gap = 100.0 
    obj_val = 0
    
    x_val = {}
    k_val = {}
    y_val = {}
    z_val = {}

    if model.SolCount > 0:
        obj_val = model.objVal
        if status == GRB.OPTIMAL:
            gap = 0.0
        else:
            try:
                gap = model.MIPGap * 100 
            except:
                gap = 100.0

        x_val = {key: var.X for key, var in x.items()}
        k_val = {key: var.X for key, var in k.items()}
        y_val = {key: var.X for key, var in y.items()}
        z_val = {key: var.X for key, var in z.items()}
    
    if status == GRB.INFEASIBLE:
        print("Modelo infactível!")
        model.computeIIS()
        model.write("NSP_infeasible.ilp")
    
    return x_val, y_val, z_val, k_val, obj_val, status, gap