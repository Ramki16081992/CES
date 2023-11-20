#!/usr/bin/env python
# coding: utf-8

# In[99]:


pip install pyomo


# In[100]:


import pyomo
import pyomo.environ


# In[1]:


conda update -n base -c defaults conda


# In[2]:


conda install -c conda-forge pyomo


# In[3]:


conda install -c conda-forge glpk


# In[101]:


from pyomo.environ import *


# In[102]:


model = ConcreteModel()


# In[103]:


num_days = 5
num_hours = 24
SOC_initial = 0  # Replace with your actual initial state of charge
SOC_min = 0  # Replace with your actual minimum state of charge
SOC_max = 40  # Replace with your actual maximum state of charge
charging_efficiency = 0.9  # Replace with your actual charging efficiency
discharging_efficiency = 1.0  # Replace with your actual discharging efficiency
Max_Charging_Power = 10  # Replace with your actual maximum charging power
Max_Total_Discharge = 36


# In[104]:


model.C = Var(range(1, num_hours + 1), range(1, num_days + 1), domain=NonNegativeReals)  # Charging
model.D = Var(range(1, num_hours + 1), range(1, num_days + 1), domain=NonNegativeReals)  # Discharging
model.SOC = Var(range(1, num_hours + 1), range(1, num_days + 1), bounds=(SOC_min, SOC_max))  # State of Charge


# In[105]:


price_data = [
    [66.92,66.26,63.35,62.62,64.58,73.41,83,61.23,2.78,17.93,20.85,25.73,27.16,27.32,27.82,28.22,23.47,16.4,53.45,84.94,85.38,75.02,67.1,60.53],
    [59.62,58.92,58.23,57.28,59.68,64.34,67.08,48.54,10.4,27.72,34.06,32.48,29.96,33.2,30.59,31.8,21.3,5.76,66.15,82.02,86.31,78.52,67.45,62.38],
    [58.77,56.07,55.27,54.64,55.76,61.28,91.88,76.5,0.03,16.78,12.73,15.34,18.96,19.43,19.47,14.84,0.00,13.02,75.72,93.25,91.12,84.22,74.68,66.88],
    [71.36,68.61,68,70.73,73.03,84.23,100.14,45.39,17.59,34.8,28.38,26.7,28.77,22.37,28.76,14.18,21.07,14.79,72.32,92.32,94.9,88.75,75.46,74.33],
    [91.46,91.52,93.84,93.84,102.55,120.49,149.29,108.81,21.09,19.31,17.27,17.05,16.17,17.82,18.31,17.75,-0.2,46.96,108.59,128.38,123.39,115.45,106.14,102.03],
]


# In[106]:


def objective_rule(model):
    revenue = sum((model.D[i, j] * price_data[j - 1][i - 1]) - (model.C[i, j] * price_data[j - 1][i - 1]) - (model.C[i, j] - 10) for i in range(1, num_hours + 1) for j in range(1, num_days + 1))
    return revenue
model.objective = Objective(rule=objective_rule, sense=maximize)


# In[107]:


def energy_balance_rule(model, i, j):
    if i == 1:
        return model.SOC[i, j] == SOC_initial + model.C[i, j] * charging_efficiency - model.D[i, j] * discharging_efficiency
    else:
        return model.SOC[i, j] == model.SOC[i - 1, j] + model.C[i, j] * charging_efficiency - model.D[i, j] * discharging_efficiency
model.energy_balance_constraint = Constraint(range(1, num_hours + 1), range(1, num_days + 1), rule=energy_balance_rule)


# In[108]:


model.SOC_min_constraint = Constraint(range(1, num_hours + 1), range(1, num_days + 1), rule=lambda model, i, j: model.SOC[i, j] >= SOC_min)
model.SOC_max_constraint = Constraint(range(1, num_hours + 1), range(1, num_days + 1), rule=lambda model, i, j: model.SOC[i, j] <= SOC_max)


# In[109]:


model.charging_constraint = Constraint(range(1, num_hours + 1), range(1, num_days + 1), rule=lambda model, i, j: model.C[i, j] <= Max_Charging_Power)
model.discharging_constraint = Constraint(range(1, num_hours + 1), range(1, num_days + 1), rule=lambda model, i, j: model.D[i, j] <= Max_Charging_Power)


# In[110]:


def total_discharge_constraint_rule(model, j):
    return sum(model.D[i, j] for i in range(1, num_hours + 1)) <= Max_Total_Discharge
model.total_discharge_constraint = Constraint(range(1, num_days + 1), rule=total_discharge_constraint_rule)


# In[111]:


solver = SolverFactory('glpk')  # Replace with your preferred solver
solver.solve(model)


# In[112]:


total_revenue = 0 


# for j in range(1, num_days + 1):
#     for i in range(1, num_hours + 1):
#         print(f"Day {j}, Hour {i}:")
#         print(f"   Discharge (MWh): {model.D[i, j].value}")
#         print(f"   Charge (MWh): {model.C[i, j].value}")
#         revenue_hourly = (model.D[i, j].value * price_data[j - 1][i - 1] - model.C[i, j].value * price_data[j - 1][i - 1])
#         total_revenue += revenue_hourly
#         print(f"   Revenue for Hour {i}: ${revenue_hourly:.2f}")
#         print(f"   SoC (MWh): {model.SOC[i,j].value}")

# In[115]:


for j in range(1, num_days + 1):
    for i in range(1, num_hours + 1):
        print(f"Day {j}, Hour {i}:")
        print(f"   Discharge (MWh): {model.D[i, j].value}")
        print(f"   Charge (MWh): {model.C[i, j].value}")
        revenue_hourly = (model.D[i, j].value * price_data[j - 1][i - 1] - model.C[i, j].value * price_data[j - 1][i - 1])
        total_revenue += revenue_hourly
        print(f"   Revenue for Hour {i}: ${revenue_hourly:.2f}")
        print(f" SOC (MWh): {model.SOC[i,j].value}")


# In[ ]:


print(f"\nTotal Revenue: ${total_revenue:.2f}")

