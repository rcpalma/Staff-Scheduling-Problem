import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from solver import solve_NSP
from data import dados
import gurobipy as gp

app = FastAPI(title="NSP Optimization API")

# Allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizationRequest(BaseModel):
    instance_number: int = Field(6, title="Instance Number (1, 2, 3, or 6)")

@app.post("/solve")
async def solve_model(req: OptimizationRequest):
    try:
        # 1. Provide a clean way to load instance properties using existing logic
        try:
            I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt = dados(req.instance_number)
        except Exception as e:
            return {"status": "ERROR", "message": f"Could not load instance {req.instance_number} parameters. Ensure the file exists."}
            
        # 2. Run Optimization
        try:
            x_val,y_val,z_val,k_val,obj_val, status_code, gap = solve_NSP(
                I,h,D,W,T,Rt,Ni,lt,max_it,bmin_i,bmax_i,cmin_i,cmax_i,omin_i,amax_i,q_idt,p_idt,u_dt,vmin_dt,vmax_dt
            )
            
            # Map Gurobi status codes to human readable strings
            status_map = {
                2: "OPTIMAL",
                3: "INFEASIBLE",
                4: "INF_OR_UNBD",
                5: "UNBOUNDED",
                9: "TIME_LIMIT",
                11: "INTERRUPTED",
                13: "SUBOPTIMAL"
            }
            status_str = status_map.get(status_code, f"STATUS_{status_code}")

            if not x_val and status_code == 3:
                 return {"status": "INFEASIBLE", "message": "The problem is infeasible."}
                 
        except Exception as e:
            return {"status": "ERROR", "message": f"Optimization error: {str(e)}"}

        # 3. Format Data for Frontend
        x_res = []
        for (i, d, t), val in x_val.items():
            if val > 0.5:
                x_res.append({"employee": i, "day": d, "shift": t, "val": 1})
        
        employees = sorted(list(set([chave[0] for chave in x_val.keys()])))
        days = sorted(list(set([chave[1] for chave in x_val.keys()])))
        shifts = sorted(list(set([chave[2] for chave in x_val.keys()])))

        # Pre-compute requirements vs actual coverage for easy frontend processing
        actual_dt = {(d, t): 0 for d in days for t in shifts}
        for (i, d, t), val in x_val.items():
            if val > 0.5:
                actual_dt[(d, t)] += 1
        
        coverage_res = []
        for t in shifts:
                for d in days:
                    coverage_res.append({
                        "shift": t,
                        "day": d,
                        "actual": actual_dt[(d,t)],
                        "required": u_dt.get((d,t), 0)
                    })

        # Pre-compute employee shift allocations globally
        # Maps an employee to a list of shift objects for the schedule grid
        schedule_grid = []
        for i in employees:
            shifts_for_emp = []
            for d in days:
                # Find which shift this employee is working on day d
                worked_shift = "Folga"
                for t in shifts:
                    if x_val.get((i, d, t), 0) > 0.5:
                        worked_shift = t
                        break
                shifts_for_emp.append({"day": d, "shift": worked_shift})
            schedule_grid.append({"employee": i, "days": shifts_for_emp})

        return {
            "status": status_str,
            "objective": obj_val,
            "gap": gap,
            "metadata": {
                "employees": employees,
                "days": days,
                "shifts": shifts
            },
            "results": {
                "schedule": x_res,
                "schedule_grid": schedule_grid,
                "coverage": coverage_res
            }
        }
            
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
