const structure = {
    structure: {
        PrefixTree: require('./structure/prefix-tree.js')
    },
    visitors: {
        forward: require('./visitors/forward-diagram-visitor.js'),
        backward: require('./visitors/backward-diagram-visitor.js')
    }
}

module.exports = function(s, k, a) {
    console.log('dynamic-trees', s, k, a)
    return () => k(s,[1])
}
