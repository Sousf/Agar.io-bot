
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
from simulation import Simulation

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
        self.action_space = spaces.Discrete(3)

        # define the observation space dimensions
        self.observation_space = spaces.Box(low=0, high=1, shape = (10, ))

    def _next_observation(self):        
        ''' Return the matrices and vector that represents the new state - an observation (that exists in the observation_space) '''
        obs = None      
        return obs

    def _take_action(self, action) -> None:
        ''' Takes in an action vector (which exists in the action_space) and enacts that action on the state
            Translates RL agent's action into the simulation '''
        ...
        
    def step(self, action):
        ''' Updates environment with action taken, returns new state and reward from state transition '''    

        # Take action
        self._take_action(action)
    
        # Calculate rewards (if applicable)
        reward = None

        # Check if simulation is over (Did we die?)
        
        obs = self._next_observation()
        # required to return: observation, reward, done, info
        return obs, reward, self.done, {} #{"logs": self.logger}
    
    def reset(self, rand_start=True):
        '''Reset everything as if we just started (for a new episode)
           Involves setting up a new simulation etc. '''
        
        self.epoch_count += 1
        
        obs = self._next_observation()  
        return obs   

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    def __repr__(self):
        return 'Hi'