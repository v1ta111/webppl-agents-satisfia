class DataPoint {
    static None = { }
    #params = DataPoint.None
    #weight = DataPoint.None

    constructor (parameters = DataPoint.None, weight = 1) {
        this.#params = parameters
        this.#weight = weight
    }

    get params() {
        return this.#params
    }

    get weight() {
        return this.#weight
    }
}

class StateDataPoint extends DataPoint {
    #state = DataPoint.None
    #aleph = DataPoint.None

    constructor (state, aleph, parameters = DataPoint.None, weight = 1) {
        super(parameters, weight)
        this.#state = state
        this.#aleph = aleph
    }

    get state() {
        return this.#state
    }

    get aleph() {
        return this.#aleph
    }
}

class ActionDataPoint extends DataPoint {
    #action = DataPoint.None
    #aleph = DataPoint.None

    constructor (action, aleph, parameters = DataPoint.None, weight = 1) {
        super(parameters, weight)
        this.#action = action
        this.#aleph = aleph
    }

    get action() {
        return this.#action
    }

    get aleph() {
        return this.#aleph
    }
}

module.exports = {
    StateDataPoint,
    ActionDataPoint
}
