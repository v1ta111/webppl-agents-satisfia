# webppl-agents-satisfia

Extension of webppl-agents with [additional non-maximizing agent types](/src/agents/makeMDPAgentSatisfia.wppl)

(original README.md:)

# webppl-agents

This package provides constructors for MDP and POMDP agents, for gridworld and bandit environments, and a function for visualizing gridworlds:

- Environments:
  - [`makeGridWorldMDP`](https://github.com/agentmodels/webppl-agents/blob/master/src/environments/makeGridWorldMDP.wppl)
  - [`makeGridWorldPOMDP`](https://github.com/agentmodels/webppl-agents/blob/master/src/environments/makeGridWorldPOMDP.wppl)
  - [`makeBanditPOMDP`](https://github.com/agentmodels/webppl-agents/blob/master/src/environments/makeBanditPOMDP.wppl)
- Agents:
  - [`makeMDPAgent`](https://github.com/agentmodels/webppl-agents/blob/master/src/agents/makeMDPAgent.wppl) + [`simulateMDP`](https://github.com/agentmodels/webppl-agents/blob/master/src/simulation/simulateMDP.wppl)
  - [`makePOMDPAgent`](https://github.com/agentmodels/webppl-agents/blob/master/src/agents/makePOMDPAgent.wppl) + [`simulatePOMDP`](https://github.com/agentmodels/webppl-agents/blob/master/src/simulation/simulatePOMDP.wppl)
- Visualization:
  - [`GridWorld.draw`](https://github.com/agentmodels/webppl-agents/blob/master/src/visualization/gridworld.js) (also available as `viz.gridworld` if [webppl-viz](https://github.com/probmods/webppl-viz) is used)

## Installation

To globally install `webppl-agents`, run:

    mkdir -p ~/.webppl
    npm install --prefix ~/.webppl webppl-agents

This may print warnings (`npm WARN ENOENT`...) which can be ignored.

To upgrade to the latest version, run:

    npm install --prefix ~/.webppl webppl-agents --force

For the agent functions, you will also need to install [webppl-dp](https://github.com/stuhlmueller/webppl-dp).

## Usage

Once installed, you can make the environment and agent functions available to `program.wppl` by running:

    webppl --require webppl-dp --require webppl-agents program.wppl

## Testing

Run the included test using:

    webppl --require webppl-dp --require . tests/tests.wppl

## License

MIT

## Additions in this fork:

We added a non-maximizing agent based on aspiration levels: `makeMDPAgentSatisfia`.
Rather than maximizing the return, this agent is given an initial aspiration point or interval `aleph0` and uses a policy that produce a return (here called `total`) whose expectation equals this point or falls into this interval, if that is possible.
To achieve this, the agent propagates the initial aspiration from step to step, taking into account the reward (here called `delta`) it gets and the possible total that is still achievable from the current state. It does so in such a way that the total equals the initial aspiration in expectation, using what we call "aspiration rescaling". 

Since there are in general many possible policies that fulfil the constraint regarding the expected total, the agent will use a number of additional criteria to determine its actions.
In each timestep, it will use a mix of actions that can satisfy the aspiration in expectation, selected on the basis of a loss function mixed from, amongst others, the following terms using adjustable loss coefficients:
- variance of resulting total
- squared deviation of the local relative aspiration (the relative position of an action's Q-value in the feasible interval) of each step from 0.5
- "messing potential" (maximal trajectory entropy that one may produce from the successor state when taking a certain action)
- behavioral entropy of the policy
- deviation from a reference policy (KL divergence)
- "power" as measured by the squared width of the interval of feasible totals
- other user-supplied safety loss terms
- random noise

