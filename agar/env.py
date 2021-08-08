import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from simulation import Simulation, DEFAULT_MAP_WIDTH
from agar import MAX_CURSOR_RANGE, SmartBot, MIN_AGAR_MASS
from vectors import Vector
from dataclasses import dataclass
import pygame

RENDER_ENV = False
clock = pygame.time.Clock()


class Environment(gym.Env):  
    # required for stable baselines 
    metadata = { 'render.modes': ['human'] }
    
    def __init__(self):
        ''' Initialising JUST the environment '''
        
        self.logger = []
        self.epoch_count = 0
        
        self._seed()
        
        # define the action space dimensions
        self.n_grid_rows = 1
        self.n_grid_cols = 10
        self.n_channels = 2 + 1 # (enemies, blobs), info
        self.action_space = spaces.Box(low=-1, high=1, shape = (1, ))

        # define the observation space dimensions
        self.observation_space = spaces.Box(low=0, high=1, shape = (self.n_grid_rows, self.n_grid_cols, self.n_channels))

        self.t = 0
        self.reset(init=True)

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
        reward = 0

        # Check if simulation is over (Did we die?)
        if self.player.is_eaten:
            #reward = -100 # 0
            done = True
        else:
            done = False
            #reward = 5*(self.player.mass - self.last_mass) + 0.01
            self.last_mass = self.player.mass
         
        obs = self._next_observation()

        # while (1):
        #   pass

        self.simulation.update()

        if self.player.mass > self.max_mass:
            reward += self.player.mass - self.max_mass # 0
            self.max_mass = self.player.mass

        self.t += 1
        return obs, reward, done, {'Step': self.t}
    
    def reset(self, init=False, rand_start=True):
        '''Reset everything as if we just started (for a new episode)
           Involves setting up a new simulation etc. '''
        if not init:
            self.simulation.end()
        
        self.simulation = Simulation(render=RENDER_ENV, player=True, map_dimensions=(DEFAULT_MAP_WIDTH, 0))
        
        self.epoch_count += 1

        self.player = self.simulation.agars[0]
        self.last_mass = MIN_AGAR_MASS
        self.max_mass = self.last_mass

        obs = self._next_observation() 
        return obs

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]