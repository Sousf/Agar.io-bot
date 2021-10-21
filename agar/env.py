from gym import spaces, Env
from gym.utils import seeding
import numpy as np
from simulation import Simulation, DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT
from agar import MAX_CURSOR_RANGE, MIN_AGAR_MASS
from utils.vectors import Vector
import pygame
from typing import Optional, Tuple
from numpy import ndarray

# --- Magic Variables --- #
RENDER = True
clock = pygame.time.Clock()

class Environment(Env):  
    # required for stable baselines 
    metadata = {'render.modes': ['human']}
    MAX_EPISODE_TIMESTEPS = 10_000
    
    def __init__(self) -> None:
        ''' Initialising JUST the environment '''
        self.logger = []
        
        self._seed()
        
        # define the action space dimensions
        self.n_grid_rows = 1
        self.n_grid_cols = 12
        self.n_channels = 2 + 1 # (enemies, blobs), info
        self.action_space = spaces.Box(low=-1, high=1, shape = (2, ))
        self.parameter_combination = None

        # define the observation space dimensions
        self.observation_space = spaces.Box(low=0, high=1, shape = (self.n_grid_rows, self.n_grid_cols, self.n_channels))

        self.t = 0
        self.reset(first_sim=True)

    def _take_action(self, action: ndarray) -> None:
        ''' Takes in an action vector (which exists in the action_space) and enacts that action on the state
            Translates RL agent's action into the simulation '''
        new_target_point = Vector(action[0] * MAX_CURSOR_RANGE + self.agent.position.x, 
                                  action[1] * MAX_CURSOR_RANGE + self.agent.position.y)
        self.agent.target_point = new_target_point
        return
        
    def step(self, action: ndarray) -> Tuple:
        ''' Updates environment with action taken, returns new state and reward from state transition 
            Note that action has already been decided and passed in to this method '''    
        self.simulation.update()
        self._take_action(action)
        obs = self._get_obs()
        reward = self._get_reward()
        self.t += 1

        # Check if simulation is over (Did we die?)
        done = False
        if self.agent.is_eaten:
            done = True
            self.agent.mass = 0

        # if self.t >= self.MAX_EPISODE_TIMESTEPS:    
        #    done = True

        log_dict = self._log()
        return obs, reward, done, log_dict 

    def _log(self) -> dict:
        ''' Create logging dictionary for step method '''
        log_dict = { 
            "step": self.t, 
            "agent mass": self.last_mass,
            "agent max mass": self.max_mass, 
            "blobs": len(self.simulation.blobs), 
            "agars": len(self.simulation.agars)
        }
        if self.parameter_combination is not None:
            log_dict = {**log_dict, **self.parameter_combination}

        return log_dict

    def _get_reward(self) -> float:
        ''' Gets the reward for the current timestep '''
        reward = self.agent.mass - self.last_mass
        self.last_mass = self.agent.mass
        self.max_mass = max(self.agent.mass, self.max_mass)

        return reward

    def _get_obs(self) -> ndarray:
        ''' Gets the current observation of shape (n_grid_rows, n_grid_cols, n_channels) '''
        return self.agent.get_channel_obs(self.n_grid_rows, self.n_grid_cols, self.n_channels)

    def reset(self, first_sim: bool=False):
        '''Reset everything as if we just started (for a new episode)
           Involves setting up a new simulation etc. '''

        if not first_sim:
            self.simulation.end()
        
        self.simulation = Simulation(render=RENDER, player=False, map_dimensions=(DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT))
        
        self.agent = self.simulation.agars[0]
        self.max_mass = self.last_mass = MIN_AGAR_MASS
        self.t = 0

        return self._get_obs()

    def _seed(self, seed: Optional[int]=None) -> None:
        ''' Set seed '''
        self.np_random, seed = seeding.np_random(seed)