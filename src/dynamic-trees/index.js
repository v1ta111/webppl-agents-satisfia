const { StateDataPoint, ActionDataPoint } = require('./sampling/data-model.js')
const structure = {
    Sequence: {
        enumerate: function(s, k, a, {
            collection,
            method
        }) {
            const enumerateAsync = async (collection, method) => {
                for await (const item of collection) {
                    method(s, k, a, item)
                }
            }
            return k(s, enumerateAsync(collection, method))
        },
        generate: function(s, k, a,
            {
                agent,
                mdp,
                aleph0
            }
        ) {
            console.log('generate', s, k, a, agent, mdp, aleph0)
            function asIntervalAsync(x) {
                return Promise.resolve(_.isArray(x) ? x : [x,x])
            }
            function localPolicyAsync(state, aleph4State) {
                return new Promise(
                    (resolve, reject) => {
                        agent.localPolicy(s,
                            (s, result) => {
                                resolve(result)
                            },
                            a.concat('_dynamic_trees_local_policy'),
                            state, aleph4State)
                    }
                )
            }

            function sampleAsync(policy) {
                return new Promise(
                    (resolve, reject) =>
                        sample(
                            s,
                            (s, result) => resolve(result),
                            a.concat('_dynamic_trees_sample'),
                            policy
                        )
                )
            }

            const simulate = async function* (stacks) {
                console.log('simulate', stacks)
                let t = 0;
                while (stacks.length > 0) {
                    const { state, aleph } = stacks.pop()
                    const aleph4state = await asIntervalAsync(aleph)
                    yield new StateDataPoint(state, aleph4state)
                    const localPolicy = await localPolicyAsync(state, aleph4state)
                    const [ action, aleph4action ] = await sampleAsync(localPolicy)
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
            console.log('dynamic-trees', 'start', s, k, a)
            try {
                return () => k(s,
                    simulate(
                        [
                            {
                                state: mdp.startState,
                                aleph: aleph0|| mdp.aleph0
                            }
                        ]
                    )
                )
            }
            finally {
                console.log('dynamic-trees', 'end', s, k, a)
            }
        }
    },
    structure: {
        PrefixTree: require('./structure/prefix-tree.js')
    },
    visitors: {
        forward: require('./visitors/forward-diagram-visitor.js'),
        backward: require('./visitors/backward-diagram-visitor.js')
    }
}

module.exports = structure
