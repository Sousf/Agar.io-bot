
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from simulation import Simulation, DEFAULT_MAP_WIDTH
from agar import MAX_CURSOR_RANGE, SmartBot, MIN_AGAR_MASS
from vectors import Vector
from dataclasses import dataclass
import pygame

class Environment(gym.Env):  
    # required for stable baselines 
    metadata = { 'render.modes': ['human'] }
    
    def __init__(self):
        ''' Initialising JUST the environment '''
        
        self.logger = []
        self.epoch_count = 0
        
        self.done = False
        self._seed()
        
        # define the action space dimensions
        self.n_grid_rows = 1
        self.n_grid_cols = 10
        self.n_channels = 2 + 1 # (enemies, blobs), info
        self.action_space = spaces.Box(low=-1, high=1, shape = (1, ))
        # channel_space = spaces.Box(low=0, high=1, shape = (self.n_grid_rows, self.n_grid_cols, self.n_channels))
        # info_space = spaces.Box(low=0, high=1, shape=(1,))

        # define the observation space dimensions
        self.observation_space = spaces.Box(low=0, high=1, shape = (self.n_grid_rows, self.n_grid_cols, self.n_channels))

        self.simulation = Simulation(render = False, player = True, map_dimensions=(DEFAULT_MAP_WIDTH, 0))
        self.player = self.simulation.agars[0]
        self.last_mass = MIN_AGAR_MASS
        self.reward = 0
        self.action = 0
        self.obs = 0
        self.t = 0

        self.max_mass = 0

    def _next_observation(self):        
        ''' Return the matrices and vector that represents the new state - an observation (that exists in the observation_space) ''' 
        channel_obs = np.zeros((self.n_grid_rows, self.n_grid_cols, self.n_channels))
        self.player.get_channel_obs(channel_obs)
        return channel_obs

    def _take_action(self, action) -> None:
        ''' Takes in an action vector (which exists in the action_space) and enacts that action on the state
            Translates RL agent's action into the simulation '''
        v = Vector(action[0] * MAX_CURSOR_RANGE + self.player.position.x, self.player.position.y)
        self.player.target_point = v
        
    def step(self, action):
        ''' Updates environment with action taken, returns new state and reward from state transition '''    

        # Take action
        self._take_action(action)
    
        # Calculate rewards (if applicable)
        reward = None

        # Check if simulation is over (Did we die?)
        if self.player.is_eaten:
            reward = -10000 #sorry it was underlining everything on my comp
            self.done = True
        else:
            reward = self.player.mass - self.last_mass
            self.last_mass = self.player.mass
         
        obs = self._next_observation()
        self.obs = obs 
        self.action = action
        # required to return: observation, reward, done, info

        self.simulation.update()

        self.max_mass = max(self.max_mass, self.player.mass)

        self.t += 1
        #print(self.t)
        return obs, reward, self.done, {'Step': self.t}
    
    def reset(self, rand_start=True):
        '''Reset everything as if we just started (for a new episode)
           Involves setting up a new simulation etc. '''
        
        self.epoch_count += 1
        self.simulation.end()
        self.done = False

        print(int(self.max_mass))
        self.max_mass = 0

        self.simulation = Simulation(render = False, player = True, map_dimensions=(DEFAULT_MAP_WIDTH, 0))
        self.player = self.simulation.agars[0]
        self.last_mass = MIN_AGAR_MASS
        self.reward = 0
        self.action = 0
        self.obs = 0

        obs = self._next_observation() 
        return obs   

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.reward}, {self.action}, {self.obs}'

@dataclass
class Agent():

    def get_action(self):
        return np.array([0])
        
#agent = Agent()
env = Environment()
clock = pygame.time.Clock()

from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO

model = PPO('MlpPolicy', env, verbose=1)


for i in range(3, 10):
    model.learn(total_timesteps=i)
    print("total_timestep =", i, "\n")

#check_env(env)
# from time import sleep
# for i in range(1000):
#     action = agent.get_action()
#     env.step(action)
#     print(f'{env.reward}, {env.action}, {env.obs}')
#     #sleep(0.01)
#     if (env.simulation.is_running == False):
#         break
#     clock.tick(100)

# TODO: Fix total_timestep bug, and 
# TODO: Random game popup at start before restarting with rectangles
# TODO: Black screen of death on Peter's machine
# TODO: 2048 total_timesteps incompatibility bug