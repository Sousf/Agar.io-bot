import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from simulation import Simulation, DEFAULT_MAP_WIDTH, DEFAULT_MAP_HEIGHT
from agar import MAX_CURSOR_RANGE, SmartBot, MIN_AGAR_MASS
from vectors import Vector
from dataclasses import dataclass
import pygame
from time import sleep


RENDER_ENV = True
clock = pygame.time.Clock()


class Environment(gym.Env):  
    # required for stable baselines 
    metadata = { 'render.modes': ['human'] }
    MAX_EPISODE_TIMESTEPS = 3000
    
    def __init__(self):
        ''' Initialising JUST the environment '''
        self.logger = []
        
        self._seed()
        
        # define the action space dimensions
        self.n_grid_rows = 1
        self.n_grid_cols = 10
        self.n_channels = 2 + 1 # (enemies, blobs), info
        self.action_space = spaces.Box(low=-1, high=1, shape = (1, ))
        self.parameter_combination = None

        # define the observation space dimensions
        self.observation_space = spaces.Box(low=0, high=1, shape = (self.n_grid_rows, self.n_grid_cols, self.n_channels))

        self.t = 0
        self.reset(first_sim=True)

    def _next_observation(self):        
        ''' Return the matrices and vector that represents the new state - an observation (that exists in the observation_space) ''' 
        channel_obs = np.zeros((self.n_grid_rows, self.n_grid_cols, self.n_channels))
        self.player.get_channel_obs(channel_obs)
        
        return channel_obs

    def _take_action(self, action) -> None:
        ''' Takes in an action vector (which exists in the action_space) and enacts that action on the state
            Translates RL agent's action into the simulation '''
        v = Vector(action[0] * MAX_CURSOR_RANGE + self.player.position.x, self.player.position.y)
        # v = Vector(-MAX_CURSOR_RANGE + self.player.position.x, self.player.position.y)
        self.player.target_point = v
        
    def step(self, action):
        ''' Updates environment with action taken, returns new state and reward from state transition '''    

        self.simulation.update()

        # Take action
        self._take_action(action)
        reward = 0

        # Check if simulation is over (Did we die?)
        if self.player.is_eaten:
            #reward = -100 # 0
            done = True
            self.player.mass = 0
        else:
            done = False
            #reward = 5*(self.player.mass - self.last_mass) + 0.01
            self.last_mass = self.player.mass

        # print(self.player.mass, end=' ')
         
        obs = self._next_observation()

        # print(obs)
        # print('Mass:', int(self.last_mass))
        
        # print('Agars')
        # for agar in self.simulation.agars:
        #    print(f'x: {int(agar.rect.center[0]):<5}, mass: {int(agar.mass):<5}')
            
        # print('Blobs')
        # for blob in self.simulation.blobs:
        #    print(f'x: {int(blob.rect.center[0]):<5}, mass: {int(blob.mass):<5}')

        # self.simulation.renderer.render_frame
        # sleep(100000)

        if (self.player.mass > self.max_mass):
            reward += self.player.mass - self.max_mass # 0
            self.max_mass = self.player.mass

        self.t += 1
        if self.t >= self.MAX_EPISODE_TIMESTEPS:    
            done = True

        log_dict = { 
            "step": self.t, 
            "player mass": self.last_mass,
            "player max mass": self.max_mass, 
            "blobs": len(self.simulation.blobs), 
            "agars": len(self.simulation.agars)
        }
        if self.parameter_combination is not None:
            log_dict = {**log_dict, **self.parameter_combination}
            
        return obs, reward, done, log_dict 
    
    def reset(self, first_sim=False):
        '''Reset everything as if we just started (for a new episode)
           Involves setting up a new simulation etc. '''

        if not first_sim:
            # print(self.max_mass)
            self.simulation.end()
        
        self.simulation = Simulation(render=RENDER_ENV, player=False, map_dimensions=(DEFAULT_MAP_WIDTH, 0))
        
        self.player = self.simulation.agars[0]
        self.last_mass = MIN_AGAR_MASS
        self.max_mass = self.last_mass
        self.t = 0

        obs = self._next_observation() 
        return obs

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]