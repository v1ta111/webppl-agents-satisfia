// functions for estimating a metalog distribution from a number of moments and for the metalog CDF:

/* TODO:
 * - where to list this file in package.json?
 * Stragegy:
 * - Solve the polynomial moment equations for the parameters: https://www.wikiwand.com/en/Metalog_distribution#Moments
 * - Substitute the approximated parameters into the quantile function: https://www.wikiwand.com/en/Metalog_distribution#Definition_and_quantile_function
 * - Solve the latter for the lower and upper aspiration bound to get the desired probability.
 * - use https://github.com/Pterodactylus/Ceres.js as solver?
 */

module.exports = {

    estimateMetalog: function (moments) { 
        /*
         * Example for computing the probability p2-p1 of falling into interval [b1,b2] 
         * for given mean, variance, and skewness, using three parameters a1, a2, a3:
         *    mean = a1 + a3/2
         *    variance = pi²a2²/3 + a3²/12 + pi²a3²/36
         *    skewness = pi²a2²a3 + pi²a3³/24
         * TODO: how to form this system of equations for arbitrary number of moments? Does this help: http://www.metalogdistributions.com/moments.html ?
         */
        return undefined; // TODO
    },
        
    metalogCDF: function (params, x) { 
        /*
         * Example for three parameters a1, a2, a3:
         *    x = a1 + (a2 + a3 (p - .5)) logit(p)
         * In general:
         *    z = p - 1/2
         *    mu = a1 + a4 z + a5 z² + a7 z³ + a9 z⁴ + ...
         *    s = a2 + a3 z + a6 z² + a8 z³ + ...
         *    x = mu + s logit(p).
         */
        return undefined; // TODO
    },

    moments2probInInterval: function (moments, lo, hi) {
        var params = this.estimateMetalog(moments);
        return this.metalogCDF(params, hi) - this.metalogCDF(params, lo);
    },
};