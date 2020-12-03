import numpy as np


def policy_evaluation(env, policy, gamma, theta, max_iterations):
    """
        Method to evaluate a policy and calculate the best value for that policy
        Algorithm:
            1. initialisation:
                        - generate a flat value array with a size equal to number of states
                        - create an identity matrix to represent actions
                          [[1 0 0 0], -> Up
                           [0 1 0 0], -> Down
                           [0 0 1 0], -> Left
                           [0 0 0 1]] -> Right
                        - calculate probability & rewards only once for environment with PolicyRewardSingleton class
            2. while stop condition or maximum number of iterations is not reached:
                        - initialise exact difference term 𝛿 (named delta in code) to use in stop condition later
            3. for all states:
                        - get current state's current value from value array
                        - get the probability of actions with respect to current policy
                          e.g. if current policy includes action 'up' for a state
                          policy_action_prob = [1 0 0 0] (first row of identity matrix)
                        - calculate new value of current state under current policy
                        - calculate new exact difference between current and new value of the state
            4. Get the values with respect to current policy computed in step 3

    :param env: Environment for which the policy should be evaluated
    :param policy: Policy that has to be evaluated
    :param gamma: Parameter to decay the future rewards, should be between 0 and 1.
    :param theta: Threshold that is used to identify when to stop the policy evaluation
    :param max_iterations: Maximum number of time-steps allowed for evaluating the policy
    :return: value array
    """

    value = np.zeros(env.n_states, dtype=np.float)
    identity = np.identity(env.n_actions)
    p, r = env.get_prob_rewards()

    curr_iteration = 0
    stop = False

    while curr_iteration < max_iterations and not stop:
        delta = 0

        for s in range(env.n_states):
            current_value = value[s]
            policy_action_prob = identity[policy[s]]
            value[s] = np.sum(policy_action_prob * p[s] * (r[s] + (gamma * value.reshape(-1, 1))))
            delta = max(delta, abs(current_value - value[s]))

        curr_iteration += 1
        stop = delta < theta

    return value


def policy_improvement(env, policy, value, gamma):
    """
        Method to improve the policy based on the value provided
        Algorithm:
            1. initialisation:
                        - generate improved policy array with a size equal to number of states
                        - calculate probability & rewards only once for environment with PolicyRewardSingleton class
            2. for all states:
                        - assign the action with maximum value to improved policy array
            3. Get improved policy and stop condition
              if policy and improved_policy are exact same stop condition will be True

    :param env: Environment for which the policy should be evaluated
    :param policy: Policy that has to be evaluated
    :param value: Value array used to improve the policy
    :param gamma: Parameter to decay the future rewards, should be between 0 and 1
    :return: policy array
    """

    improved_policy = np.zeros(env.n_states, dtype=int)
    p, r = env.get_prob_rewards()

    for s in range(env.n_states):
        improved_policy[s] = np.argmax(np.sum(p[s] * (r[s] + (gamma * value.reshape(-1, 1))), axis=0))

    return improved_policy, np.all(np.equal(policy, improved_policy))


def policy_iteration(env, gamma, theta, max_iterations):
    """
        Method to perform policy iteration until convergence
        It evaluates a policy, improves it in a loop until convergence
        Algorithm:
            1. initialisation:
                        - generate policy array with a size equal to number of states
                        - generate value array with a size equal to number of states
            2. while stop condition or maximum number of iterations is not reached:
                        - call policy evaluation function to evaluate current policy
                        - call policy improvement function to improve current policy
            3. Get the best policy and values for that policy


    :param env: Environment for which the policy should be evaluated
    :param gamma: Parameter to decay the future rewards, should be between 0 and 1
    :param theta: Threshold that is used to identify when to stop the policy evaluation
    :param max_iterations: Maximum number of time-steps allowed for evaluating the policy
    :return: Policy and Value arrays as a tuple
    """

    policy = np.zeros(env.n_states, dtype=int)
    value = np.zeros(env.n_states, dtype=np.float)

    stop = False
    current_iteration = 0

    while current_iteration < max_iterations and not stop:
        value = policy_evaluation(env, policy, gamma, theta, max_iterations)
        policy, stop = policy_improvement(env, policy, value, gamma)
        current_iteration += 1


    if (env.n_states == 17):
        npy_filename = 'data/small_frozenlake_policy_evaluation.npy'
    else:
        npy_filename = 'data/big_frozenlake_policy_evaluation.npy'

    save_file(npy_filename,value)

    return policy, value


def value_iteration(env, gamma, theta, max_iterations):
    """
        Method to perform value iteration until convergence
        It finds the best value for the environment, creates an optimal policy based on best value found
        Algorithm:
            1. initialisation:
                        - generate policy array with a size equal to number of states
                        - generate value array with a size equal to number of states
                        - calculate probability & rewards only once for environment with PolicyRewardSingleton class
            2. while stop condition or maximum number of iterations is not reached:
                        - initialise exact difference term 𝛿 (named delta in code) to use in stop condition later
            3. for all states:
                        - get current state's current value from value array
                        - calculate new values for all actions at once and get the maximum value for all states
                        - calculate new exact difference between current and new value of the state
            4. Get the best policy with respect to calculated values

    :param env: Environment for which the policy should be evaluated
    :param gamma: Parameter to decay the future rewards, should be between 0 and 1
    :param theta: Threshold that is used to identify when to stop the policy evaluation
    :param max_iterations: Maximum number of time-steps allowed for evaluating the policy
    :return: Policy and Value arrays as a tuple
    """
    policy = np.zeros(env.n_states, dtype=int)
    value = np.zeros(env.n_states, dtype=np.float)

    curr_iteration = 0
    stop = False
    p, r = env.get_prob_rewards()

    while curr_iteration < max_iterations and not stop:
        delta = 0

        for s in range(env.n_states):
            current_value = value[s]
            value[s] = np.max(np.sum(p[s] * (r[s] + (gamma * value.reshape(-1, 1))), axis=0))
            delta = max(delta, abs(current_value - value[s]))

        curr_iteration += 1
        stop = delta < theta

    policy, _ = policy_improvement(env, policy, value, gamma)

    return policy, value


def save_file(npy_filename, value):
    policy_value = {}
    policy_value['value'] = value

    np.save(npy_filename,policy_value)