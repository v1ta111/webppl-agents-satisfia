'''
Python functions for approximating the feasibility region of a state from the feasibility regions of the actions when the criteria-space has several dimensions (but is still low-dimensional).
There is an optimal version that uses cvxpy to solve a convex optimization problem, and a fast version that uses a greedy algorithm.
The fast version is about 30 times faster and reaches an optimality of roughly 90% on average and roughly 50% in the worst case, measured in terms of the volume of the found region.
In higher dimensions, both speedup and optimality of the fast solution decrease.
'''

from itertools import product
import numpy as np
import scipy as sp
from scipy.spatial import ConvexHull
import cvxpy as cp


def action2state_feasibility_opt(state_action_feasibility_lo, state_action_feasibility_hi, initial_guess=None):

    # get no. of actions k and dimension d from the shape of state_action_feasibility_lo:
    k, d = state_action_feasibility_lo.shape
    rd = range(d)

    # list of index tuples of the 2**d many corners of a hypercube, 0 for lower, 1 for upper bound:
    corner_indices = list(product([0,1], repeat=d))  # d-th cartesian power of {0,1}

    # all box corners:
    action_corners = [
        [state_action_feasibility_lo[a, i] if ind[i] == 0 else state_action_feasibility_hi[a, i] for i in range(d)]
        for ind in corner_indices
        for a in range(k)
    ]

    # find the convex hull U of the union of the k boxes:
    U = ConvexHull(np.array(action_corners))  # ! bottleneck !

    # vertices, center (avg. of vertices), bounding box, dimensions, and inequalities of U:
    Uvertices = U.points[U.vertices]
    Ucenter = np.mean(Uvertices, axis=0)
    Uineqs = U.equations.tolist()

    # main task: find the maximum volume hyperrectangle that is contained in U...

    # use cvxpy to solve the problem:
    blo = cp.Variable(d)
    bhi = cp.Variable(d)
    constraints = [
        cp.sum(cp.multiply(blo, np.minimum(coeffs[:d], 0))) 
        + cp.sum(cp.multiply(bhi, np.maximum(coeffs[:d], 0))) 
        + coeffs[-1] <= 0
        for coeffs in Uineqs
    ] + [
        blo[i] + 1e-3 <= bhi[i]
        for i in rd
    ]
    objective = cp.Maximize(cp.sum(cp.log(bhi - blo)))  # maximize log volume since that is a convex function with a simple gradient and diagonal hessian
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCS)  # verbose=True # see https://www.cvxpy.org/related_projects/index.html#solvers for solvers
    return U, Uvertices, Ucenter, blo.value, bhi.value, problem.status


def action2state_feasibility_fast(state_action_feasibility_lo, state_action_feasibility_hi):

    # get no. of actions k and dimension d from the shape of state_action_feasibility_lo:
    k, d = state_action_feasibility_lo.shape
    rd = range(d)

    # list of index tuples of the 2**d many corners of a hypercube, 0 for lower, 1 for upper bound:
    corner_indices = list(product([0,1], repeat=d))  # d-th cartesian power of {0,1}

    # all box corners:
    action_corners = [
        [state_action_feasibility_lo[a, i] if ind[i] == 0 else state_action_feasibility_hi[a, i] for i in range(d)]
        for ind in corner_indices
        for a in range(k)
    ]

    # find the convex hull U of the union of the k boxes:
    U = ConvexHull(np.array(action_corners))  # ! bottleneck !

    # vertices, center (avg. of vertices), bounding box, dimensions, and inequalities of U:
    Uvertices = U.points[U.vertices]
    Ucenter = np.mean(Uvertices, axis=0)
    Ulo = np.min(Uvertices, axis=0)
    Uhi = np.max(Uvertices, axis=0)
    Uwidths = Uhi - Ulo
    Uineqs = U.equations.tolist()

    # main task: find a large hyperrectangle that is contained in U...

    # begin by finding the largest hyperrectangle that is centered at Ucenter and has the same aspect ratio as the bounding box of U:
    # for each ray starting at Ucenter and moving in the direction dx of a main diagonal of the hypercube,
    # find the point where it first hits the boundary of U.
    #   the equation for the ray is x = Ucenter + t * dx, t >= 0.
    #   the equation for the boundary of U is a dot x + b <= 0.
    #   the intersection point thus has a dot (Ucenter + t * dx) + b = 0, i.e., t = - (a dot Ucenter + b) / (a dot dx).
    # then fix all adjacent faces of that corner and grow the hyperrectangle further 
    # until some other corner hits the boundary.
    # repeat until all faces are fixed.

    # initialize flexibility and corner positions:
    face_flexible = np.ones((2, d))
    corners = np.repeat(Ucenter.reshape((1,-1)), 2**d, axis=0)

    # while there are still flexible corners, find the next hit and freeze adjacent faces:
    for it in range(d + 1):
        if np.sum(face_flexible) == 0:
            break
        # directions in which corners move:
        dxs = np.array([[(2*ind[i]-1) * face_flexible[ind[i],i] * Uwidths[i] for i in rd] for ind in corner_indices])
        allinvts = []
        for j, dx in enumerate(dxs):
            # find the inverse time at which this corner hits each face of U:
            invts = [ 
                - np.dot(coeffs[:-1], dx) / (np.dot(coeffs[:-1], corners[j]) + coeffs[-1]) 
                for coeffs in Uineqs 
            ]
            # only consider positive times (negative times mean the corner is moving away from the face):
            invts_nonneg = [invt if invt > 0 else 1e-10 for invt in invts]
            # register the inverse time of the earliest hit of this corner with any face:
            allinvts.append(max(invts_nonneg))
        # find the corner and time of next hit:
        j = np.argmax(allinvts)
        ind = corner_indices[j]
        t = 1 / allinvts[j]
        # propagate all corners to that time:
        corners += t * dxs
        # freeze all faces adjacent to the corner that hit the boundary:
        for i in rd: 
            face_flexible[ind[i],i] = 0

    # compute limits of the hyperrectangle:
    blo = corners[0]
    bhi = corners[-1]

    return U, Uvertices, Ucenter, blo, bhi


# test:

import time
import matplotlib.pyplot as plt

## parameters

d = 4  # 2  # dimension = no. of criteria i  (larger is more difficult to solve, up to 4 seems to work fine)
k = 5  # 5  # no. of actions a  (smaller is more difficult to approximate)

nits = 100

# estimate the avg. time it takes to compute the hyperrectangle:
t0 = time.time()
for i in range(nits):
    # draw k random d-dimensional state-action feasibility boxes [blo[a], bhi[a]] from the unit hypercube:
    state_action_feasibility_lo = np.random.rand(k, d)
    state_action_feasibility_hi = np.random.rand(k, d)
    U, Uvertices, Ucenter, blo, bhi = action2state_feasibility_fast(state_action_feasibility_lo, state_action_feasibility_hi)
t1 = time.time()
avg_time_fast = (t1-t0)/nits
print('time per iteration (fast): ', avg_time_fast)
t0 = time.time()
for i in range(nits):
    # draw k random d-dimensional state-action feasibility boxes [blo[a], bhi[a]] from the unit hypercube:
    state_action_feasibility_lo = np.random.rand(k, d)
    state_action_feasibility_hi = np.random.rand(k, d)
    U, Uvertices, Ucenter, blo, bhi, status = action2state_feasibility_opt(state_action_feasibility_lo, state_action_feasibility_hi)
t1 = time.time()
avg_time_opt = (t1-t0)/nits
print('time per iteration (opt): ', avg_time_opt)

# compare the fast with the opt result in one example:
ratios = []
for i in range(nits):
    state_action_feasibility_lo = np.random.rand(k, d)
    state_action_feasibility_hi = np.random.rand(k, d)
    U, Uvertices, Ucenter, blo, bhi = action2state_feasibility_fast(state_action_feasibility_lo, state_action_feasibility_hi)
    Uopt, Uverticesopt, Ucenteropt, bloopt, bhiopt, status = action2state_feasibility_opt(state_action_feasibility_lo, state_action_feasibility_hi)
    if status != 'optimal':
        print('optimal solution not found!')
        continue
    ratios.append(np.prod(bhi - blo) / np.prod(bhiopt - bloopt))

ratios = np.array(ratios)

print('avg optimality ratio of fast solution', np.mean(ratios[np.where(ratios < 1e100)]))  # strange...
print('worst-case optimality ratio of fast solution', np.min(ratios))
print('speedup of fast solution', avg_time_opt / avg_time_fast)

# plot last example:

if d==2:
    plt.figure()

    # plot the original boxes in green:
    for a in range(k):
        plt.plot([state_action_feasibility_lo[a, 0], state_action_feasibility_hi[a, 0], state_action_feasibility_hi[a, 0], state_action_feasibility_lo[a, 0], state_action_feasibility_lo[a, 0]],
                [state_action_feasibility_lo[a, 1], state_action_feasibility_lo[a, 1], state_action_feasibility_hi[a, 1], state_action_feasibility_hi[a, 1], state_action_feasibility_lo[a, 1]],
                'g-')

    # plot U in green dashed lines and its center as a blue dot:
    plt.plot(U.points[U.vertices,0], U.points[U.vertices,1], 'g--')
    plt.plot(Uvertices[[0,-1]][:,0], Uvertices[[0,-1]][:,1], 'g--')
    plt.plot(Ucenter[0], Ucenter[1], 'bo')

    # plot box [blo, bhi] in blue:
    plt.plot([blo[0], bhi[0], bhi[0], blo[0], blo[0]],
            [blo[1], blo[1], bhi[1], bhi[1], blo[1]],
            'b-',lw=2)
    
    # plot box [bloopt, bhiopt] in red:
    plt.plot([bloopt[0], bhiopt[0], bhiopt[0], bloopt[0], bloopt[0]],
            [bloopt[1], bloopt[1], bhiopt[1], bhiopt[1], bloopt[1]],
            'r-',lw=2)  

    plt.show()  
    