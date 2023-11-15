#!/usr/bin/env python
# coding: utf-8

# In[270]:


import pulp
import numpy as np
import matplotlib.pyplot as plt 


# In[271]:


num_hours = 24
num_days = 5
a = None


# In[272]:


problem = pulp.LpProblem("BESS_Optimization", pulp.LpMaximize)


# In[273]:


#Decision variable
D = pulp.LpVariable.dicts("Discharge_MWh", ((i, j) for i in range(1, num_hours + 1) for j in range(1, num_days + 1)), lowBound=0, upBound=None, cat=pulp.LpContinuous)
C = pulp.LpVariable.dicts("Charge_MWh", ((i, j) for i in range(1, num_hours + 1) for j in range(1, num_days + 1)), lowBound=0, upBound=None, cat=pulp.LpContinuous)
SOC = pulp.LpVariable.dicts("SOC_MWh", ((i, j) for i in range(1, num_hours + 1) for j in range(1, num_days + 1)), lowBound=0, upBound=None, cat=pulp.LpContinuous)


# In[274]:


price_data = [
    [66.92,66.26,63.35,62.62,64.58,73.41,83,61.23,2.78,17.93,20.85,25.73,27.16,27.32,27.82,28.22,23.47,16.4,53.45,84.94,85.38,75.02,67.1,60.53],
    [59.62,58.92,58.23,57.28,59.68,64.34,67.08,48.54,10.4,27.72,34.06,32.48,29.96,33.2,30.59,31.8,21.3,5.76,66.15,82.02,86.31,78.52,67.45,62.38],
    [58.77,56.07,55.27,54.64,55.76,61.28,91.88,76.5,0.03,16.78,12.73,15.34,18.96,19.43,19.47,14.84,0.00,13.02,75.72,93.25,91.12,84.22,74.68,66.88],
    [71.36,68.61,68,70.73,73.03,84.23,100.14,45.39,17.59,34.8,28.38,26.7,28.77,22.37,28.76,14.18,21.07,14.79,72.32,92.32,94.9,88.75,75.46,74.33],
    [91.46,91.52,93.84,93.84,102.55,120.49,149.29,108.81,21.09,19.31,17.27,17.05,16.17,17.82,18.31,17.75,-0.2,46.96,108.59,128.38,123.39,115.45,106.14,102.03],
]
charging_efficiency = 0.90
discharging_efficiency = 1.00
degradation_cost = 10  # $/MWh
Max_Total_Discharge = 180  # MWh
Max_Charging_Power = 10  # MW
Max_Discharging_Power = 10  # MW
Max_Energy_Stored = 40  # MWh
SOC_initial = 0  # Initial SOC in MWh
SOC_min = 0.05 * Max_Energy_Stored
SOC_max = Max_Energy_Stored


# In[275]:


#Objective function
revenue = pulp.lpSum([(D[(i, j)] * price_data[j-1][i-1]) - (C[(i, j)] * price_data[j-1][i-1]) - (C[(i, j)] * 10) for i in range(1, num_hours + 1) for j in range(1, num_days + 1)])
problem += revenue


# In[276]:


#constraints
for j in range(1, num_days + 1):
    for i in range(1, num_hours + 1):
        if i == 1:
            problem += SOC[(i, j)] == SOC_initial + (C[(i, j)] * charging_efficiency) - (D[(i, j)] * discharging_efficiency)
        else:
            problem += SOC[(i, j)] == SOC[(i - 1, j)] + (C[(i, j)] * charging_efficiency) - (D[(i, j)] * discharging_efficiency)
        problem += SOC_min <= SOC[(i, j)] <= SOC_max
        problem += C[(i, j)] <= Max_Charging_Power
        problem += D[(i, j)] <= Max_Discharging_Power

total_discharge = pulp.lpSum(D[(i, j)] for i in range(1, num_hours + 1) for j in range(1, num_days + 1))
problem += total_discharge <= Max_Total_Discharge


# In[277]:


problem.solve()


# In[278]:


for j in range(1, num_days + 1):
    for i in range(1, num_hours + 1):
        print(f"Day {j}, Hour {i}:")
        print(f"   Discharge (MWh): {D[(i, j)].varValue}")
        print(f"   Charge (MWh): {C[(i, j)].varValue}")
        print(f"   SOC (MWh): {SOC[(i, j)].varValue}")


# In[279]:


total_revenue = pulp.value(problem.objective)
print(f"Total Revenue: ${total_revenue:.2f}")


# In[ ]:




