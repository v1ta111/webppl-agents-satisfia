const { StateDataPoint, ActionDataPoint } = require('./data-model.js')
module.exports = function SequenceSampler(mdp, agent, webppl) {
    const simulate = function* (stacks) {
        let t = 0;
        while (stacks.length > 0) {
            const { state, aleph } = stacks.pop()
            const aleph4state = webppl.asInterval(aleph)
            yield new StateDataPoint(state, aleph4state)
            const localPolicy = agent.localPolicy(state, aleph4State)
            const [ action, aleph4action ] = webppl.sample(localPolicy)
            const E_delta = mdp.expectedDelta(state, action)
            yield new ActionDataPoint(action, aleph4action, { 'Edel': E_delta })

            const nextState = mdp.transition(state, action)
            const nextAleph4state = agent.propagateAspiration(state, action, aleph4action, E_delta, nextState);
            if (state.terminalteAfterAction) {
                yield new StateDataPoint(nextState, nextAleph4state)
            }
            else {
                stacks.push( { state: nextState, aleph: nextAleph4state } )
            }
        }
    }

    return function (state, aleph) {
        return simulate ([{state, aleph}])
    }
}
