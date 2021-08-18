# --- LIBRARIES --- #
import matplotlib.pyplot as plt
import numpy as np
import os
from itertools import product
from copy import deepcopy
import logging

# --- MODULES --- #
from env import Environment

# --- STABLE BASELINES --- #
# from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import A2C, DDPG
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

#from stable_baselines3.common.schedules import ConstantSchedule
#from stable_baselines3.common.results_plotter import load_results, ts2xy

# --- GLOBAL --- #
TIME_STEPS = 1_000_000
PARAMETERS = {
    'learning_rate': [0.001, 0.0001, 0.00001],
    'policy_kwargs': [dict(net_arch=[dict(pi=n_layers*[size], vf=n_layers*[size])]) for size in [10, 50] for n_layers in [2, 3]]
}

# --- MAIN --- #
def main():
    # directory for data
    log_dir = "/tmp/gym/"
    os.makedirs(log_dir, exist_ok=True)

    # initialize an environment
    # env = make_vec_env(Environment, n_envs=1, monitor_dir=log_dir)
    env = Monitor(Environment(), filename=log_dir+"test_log", info_keywords=("step", "player mass", "player max mass", "blobs", "agars") + tuple(PARAMETERS.keys()))

    # All parameters to try
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy

    # Reformat the above parameters into list of dictionaries, (each dictionary will be kwargs of parameter values for model)
    # param_combs = [dict(zip(parPARAMETERSameters.keys(), values)) for values in list(product(*PARAMETERS.values()))]

    # PARAMETERS.values = the different hyper parameter values e.g. learning rate values, the different network architectures
    
    parameter_combinations = []
    for values in list(product(*PARAMETERS.values())):
        parameter_combinations.append(dict(zip(PARAMETERS.keys(), values)))

    for parameter_combination in parameter_combinations:
        try:
            # Copying this because the model is messing with the variable.
            parameter_combination_copy = deepcopy(parameter_combination)
            print('PARAMETER COMBINATION', parameter_combination_copy)
            env.env.parameter_combination = parameter_combination_copy
            #print("env.parameter_combination #######################", env.parameter_combination)
            model = A2C('MlpPolicy', env, verbose=0 , **parameter_combination_copy)
            
            # training
            model.learn(total_timesteps=TIME_STEPS)
        except Exception as e:
            with open('error_log.txt', 'a') as f:
                f.write(str(e) + '\n')
        
if __name__ == "__main__":
    main()