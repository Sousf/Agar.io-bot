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
TIME_STEPS = 100_000
TRAINING = True
PARAMETERS = {
    #'learning_rate': [1e-04, 1e-05, 1e-06, 1e-07],
    'policy_kwargs': [dict(net_arch=[dict(pi=arch, vf=arch)]) for arch in [[100, 100, 100]]]
}

def learning_rate(progress_remaining, start_lr=1e-04, final_lr=1e-06):
    return final_lr * (start_lr / final_lr) ** progress_remaining

# --- MAIN --- #
def main():
    # directory for data
    log_dir = "/tmp/gym/"
    os.makedirs(log_dir, exist_ok=True)

    # initialize an environment
    # env = make_vec_env(Environment, n_envs=1, monitor_dir=log_dir)
    env = Monitor(Environment(), filename=log_dir+"tr_500k", info_keywords=("step", "player mass", "player max mass", "blobs", "agars") + tuple(PARAMETERS.keys()))

    # All parameters to try
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy

    # Reformat the above parameters into list of dictionaries, (each dictionary will be kwargs of parameter values for model)
    # param_combs = [dict(zip(PARAMETERS.keys(), values)) for values in list(product(*PARAMETERS.values()))]

    # PARAMETERS.values = the different hyper parameter values e.g. learning rate values, the different network architectures

    if TRAINING:
        parameter_combinations = []
        for values in list(product(*PARAMETERS.values())):
            parameter_combinations.append(dict(zip(PARAMETERS.keys(), values)))

        for i, parameter_combination in enumerate(parameter_combinations):
            # Copying this because the model is messing with the variable.
            parameter_combination_copy = deepcopy(parameter_combination)
            print('PARAMETER COMBINATION', parameter_combination_copy)
            env.env.parameter_combination = parameter_combination_copy
            #print("env.parameter_combination #######################", env.parameter_combination)

            model = A2C('MlpPolicy', env, verbose=0 , learning_rate=learning_rate, **parameter_combination_copy)
            model.learn(total_timesteps=TIME_STEPS)
            model.save(f'/tmp/gym/models/A2C_3layers_100nodes_test{i}')

    else:
        model = A2C.load('/tmp/gym/good_models1D/A2C_3layers_100nodes_test1')

        while (1):
            obs = env.reset()
            for i in range(TIME_STEPS):
                action, state = model.predict(obs)
                obs, reward, done, log_dict  = env.step(action)
                # env.render() Should do this eventually


if __name__ == "__main__":
    main()
