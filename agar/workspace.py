# --- LIBRARIES --- #
import matplotlib.pyplot as plt
import numpy as np
import time
import os
from os import path
from itertools import product
from copy import deepcopy
import logging

import warnings
warnings.filterwarnings("ignore", "Distutils was imported before Setuptools. This usage is discouraged and may exhibit undesirable behaviors or errors. Please use Setuptools' objects directly or at least import Setuptools first.",  UserWarning, "setuptools.distutils_patch")

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
TIME_STEPS = 1000
TRAINING = True
PARAMETERS = {
    #'learning_rate': [1e-04, 1e-05, 1e-06, 1e-07],
    'policy_kwargs': [dict(net_arch=[dict(pi=arch, vf=arch)]) for arch in 1*[[100, 100], [100, 100, 100], [1000, 1000], [1000, 1000, 1000]]]
}

def learning_rate(progress_remaining, start_lr=1e-04, final_lr=1e-06):
    return final_lr * (start_lr / final_lr) ** progress_remaining

def get_time_estimate(combinations, total_steps = TIME_STEPS, test_steps = 1e3, threshold = 2.5e6):
    if (total_steps < threshold):
        return

    print("Getting approximate time for simulation \n")

    comb_copy = deepcopy(combinations) # just to be safe
    dummy_env = Monitor(Environment())

    start_time = time.time()
    for i, comb_copy in enumerate(comb_copy):
        dummy_env.env.parameter_combination = comb_copy
        model = A2C('MlpPolicy', dummy_env, verbose=0, learning_rate=learning_rate, **comb_copy)
        model.learn(total_timesteps=test_steps)
    end_time = time.time() - start_time

    total_time = end_time * total_steps / test_steps
    print("Test took around: ", time.strftime('%H:%M:%S', time.gmtime(end_time)), "\n")
    print("Approximating simulation time at: ", time.strftime('%H:%M:%S', time.gmtime(total_time)), "\n")
    return


def main():
    # directory for data
    log_dir = "/tmp/gym/"
    os.makedirs(log_dir, exist_ok=True)
    # initialize an environment
    # env = make_vec_env(Environment, n_envs=1, monitor_dir=log_dir)
    env = Monitor(Environment(), filename=log_dir+"tr_500k", info_keywords=("step", "agent mass", "agent max mass", "blobs", "agars") + tuple(PARAMETERS.keys()))

    if TRAINING:
        # All parameters to try
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy

        # Reformat the above parameters into list of dictionaries, (each dictionary will be kwargs of parameter values for model)
        # param_combs = [dict(zip(PARAMETERS.keys(), values)) for values in list(product(*PARAMETERS.values()))]

        # PARAMETERS.values = the different hyper parameter values e.g. learning rate values, the different network architectures
        parameter_combinations = []
        for values in list(product(*PARAMETERS.values())):
            parameter_combinations.append(dict(zip(PARAMETERS.keys(), values)))

        # get_time_estimate(parameter_combinations)

        for i, parameter_combination in enumerate(parameter_combinations):
            # Copying this because the model is messing with the variable.
            #parameter_combination_copy = deepcopy(parameter_combination)
            parameter_combination_copy = parameter_combination
            print('PARAMETER COMBINATION', parameter_combination_copy, 'env ts', env.env.t)
            env.env.parameter_combination = parameter_combination_copy

            model = A2C('CnnPolicy', env, verbose=0, learning_rate=learning_rate, **parameter_combination_copy)
            model.learn(total_timesteps=TIME_STEPS)
            print('PARAMETER COMBINATION', parameter_combination_copy)
            model.save(log_dir + f'models/A2C_3layers_100nodes_test{i}')

    else:
        model = A2C.load(log_dir + "batch1_2D/A2C_3layers_100nodes_test3") # A2C.load(log_dir + f'models/A2C_3layers_100nodes_test1')

        while True:
            obs = env.reset()
            for i in range(TIME_STEPS):
                action, state = model.predict(obs)
                obs, reward, done, log_dict  = env.step(action)

if __name__ == "__main__":
    main()
