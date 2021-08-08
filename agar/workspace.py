# --- LIBRARIES --- #
import matplotlib.pyplot as plt
import numpy as np
import os

# --- MODULES --- #
from env import Environment

# --- STABLE BASELINES --- #
# from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import A2C
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback
#from stable_baselines3.common.results_plotter import load_results, ts2xy

# --- GLOBAL --- #
TIME_STEPS = 10_000

# --- MAIN --- #
def main():
    # directory for data
    log_dir = "/tmp/gym/"   
    os.makedirs(log_dir, exist_ok=True)

    # initialize an environment
    env = make_vec_env(Environment, n_envs=1, monitor_dir=log_dir)
    # initialize a network architecture
    policy_kwargs = dict(net_arch=[dict(pi=[10, 10], vf=[10, 10])])
    # initalize 
    model = A2C('MlpPolicy', env, verbose=1, policy_kwargs=policy_kwargs)


    # training
    model.learn(total_timesteps=TIME_STEPS)

if __name__ == "__main__":
    main()

