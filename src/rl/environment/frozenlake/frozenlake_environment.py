import numpy as np

from rl.environment.env_helper import index_to_position, position_to_index
from rl.environment.environment import Environment


class FrozenLake(Environment):
    def __init__(self, lake, slip, max_steps, seed=None):
        """
            Constructor for the Frozen lake environment that inherits the class Environment
            1. initialization - create an array of size of the lake
                              - create rows and columns with the shape of lake, e.g. 4*4 or 8*8, etc.
                              - assign a tuple of (x,y) tuples ((-1, 0), (1, 0), (0, -1), (0, 1)) to account for
                                movement in directions            left  , right,  down   , up
                              - allocate number of states (n_states) with size of lake + 1, to account for the absorbing state
                              - allocate number of actions (n_actions) with the length of number of actions
                              - allocate actual number of states to absorbing state, i.e, n_states - 1
                              - create 1D array representing the probability distribution of size of number of states,
                                and then allocate starting position(&) with a probability of 1
                              - create a 3D array to store the transitional probabilities computed of moving from the current state
                                to the next state considering all the probable actions of up, down, left, right
                                The size of this array will be n_states * n_actions * n_states
                                To explain further, for the current state i,......................
                                [] - up
                                [] - down
                                [] - left
                                [] - right
                              - call the function   _populate_probabilities() to load the precomputed probabilities in the 3D array

        :param lake: A matrix that represents the lake.
                Example:
                    lake =  [['&', '.', '.', '.'],
                             ['.', '#', '.', '#'],
                             ['.', '.', '.', '#'],
                             ['#', '.', '.', '$']]
                    & -> start
                    . -> frozen
                    # -> hole
                    $ -> goal
        :param slip: The probability that the agent will slip
        :param max_steps: The maximum number of time steps in an episode
        :param seed: A seed to control the random number generator (optional)
        """

        self.lake = np.array(lake)
        self.rows, self.columns = self.lake.shape
        self.slip = slip
        self.actions = ((-1, 0), (1, 0), (0, -1), (0, 1))

        n_states = self.lake.size + 1
        n_actions = len(self.actions)

        self.absorbing_state = n_states - 1

        pi = np.zeros(n_states, dtype=float)
        pi[np.where(self.lake.reshape(-1) == '&')[0]] = 1.0

        super(FrozenLake, self).__init__(n_states, n_actions, max_steps, pi, seed)

        self._p = np.zeros((self.n_states, self.n_actions, self.n_states), dtype=float)
        self._populate_probabilities()

    def p(self, next_state, state, action):
        """
            Method to return the probability of transitioning from current state to the next state with action

        :param next_state: Index of next state
        :param state: Index of current state
        :param action: Action to be taken
        :return: Probability of transitioning between state and next_state with action
        """

        return self._p[state, action, next_state]

    def r(self, next_state, state, action):
        """
            TODO Change the algorithm for the rewards
            Method to return the reward when transitioning from current state to the next state with action
            Algorithm:
                1. If the probability of transitioning for the current state to next state is 0, reward is 0
                2. Any action in the absorbing state leads to a reward of 0 if it is not a goal state
                3. Any action in the goal state gives a reward of 1

        :param next_state: Index of next state
        :param state: Index of current state
        :param action: Action to be taken
        :return: Reward for transitioning between state and next_state with action
        """
        if self._p[state, action, next_state] == 0 or self.absorbing_state == state:
            return 0
        elif self.lake[index_to_position(state, self.columns)] == '$':
            return 1
        else:
            return 0

    def step(self, action):
        """
            Method to take a step for choosing action from current state

        :param action: Action to be taken
        :return: next state, reward, done as a tuple for taking action
        """

        state, reward, done = super(FrozenLake, self).step(action)

        done = (state == self.absorbing_state) or done

        return state, reward, done

    def render(self, policy=None, value=None):
        """
            Method to visualize the FrozenLake
            Algorithm:
                1. Prints the FrozenLake
                2. If policy is provided, prints policy and value

        :param policy: policy to be rendered
        :param value: value to be rendered
        :return: None
        """

        print('FrozenLake:')
        lake = self.lake.copy()
        if self.state < self.absorbing_state:
            lake[index_to_position(self.state, self.columns)] = '@'
        print(lake)

        if policy is not None:
            actions = ['u', 'd', 'l', 'r']

            print('Policy:')
            policy = np.array([actions[a] for a in policy[:-1]])
            print(policy.reshape(self.lake.shape))

            print('Value:')
            with self._printoptions(precision=3, suppress=True):
                print(value[:-1].reshape(self.lake.shape))

    def _populate_probabilities(self):
        """
            Method to calculate probability of transitioning between state and next_state with action
            Algorithm:
                1. for each state do the steps below
                2. calculate row and column indices for the state
                3. if the state is an absoring state or a hol or goal, then probability of transitioning to the absorbing state is 1
                   and go back to step 1
                4. for every possible action (up, down, left, right), go to step 5
                5. for slippage in each action do steps ....

                6.

        :return: None
        """

        for state in range(self.n_states):
            x, y = index_to_position(state, self.columns)

            if state == self.absorbing_state or self.lake[x, y] in ('#', '$'):
                self._p[state, :, self.absorbing_state] = 1
                continue

            for action in range(self.n_actions):
                for slip_action in range(self.n_actions):
                    next_state = state
                    next_x, next_y = x + self.actions[slip_action][0], y + self.actions[slip_action][1]
                    if 0 <= next_x < self.rows and 0 <= next_y < self.columns:
                        next_state = position_to_index(next_x, next_y, self.columns)

                    self._p[state, action, next_state] += self.slip / self.n_actions
                    if action == slip_action:
                        self._p[state, action, next_state] += 1 - self.slip

