import numpy as np
import matplotlib.pyplot as plt

# parameters:

nits = 10000
ks = [2, 5, 10, 20, 50, 100]  # no. of goods
etas = [0, 0.5, 1, 1.5, 2.0, 2.5]  # heterogeneity of the true log-coefficients
sigmas = [0, 0.1, 0.2, 0.3, 0.4]  # variance of the log-coefficient misspecification
linestyles = ['-', '--', '-.', '-.', ':', ':']

def sample_L(eta, k, sigma):

    # draw true log coefficients from a normal distribution:
    c = np.exp(np.random.randn(k) * eta)
    C = np.sum(c)

    # draw misspecified log coefficients from a normal distribution:
    c_hat = c * np.exp(np.random.randn(k) * sigma)
    C_hat = np.sum(c_hat)

    # compute the loss in true utility from optimizing with misspecified coefficients:
    L = C * np.log(C_hat/C) + np.sum(c * np.log(c/c_hat))

    return L

# estimate and plot the avg. loss:
means = np.zeros((len(etas),len(sigmas),len(ks)))
for l,eta in enumerate(etas):
    print('eta = {}'.format(eta))
    for j,sigma in enumerate(sigmas):
        for i,k in enumerate(ks):
            means[l,j,i] = np.mean([sample_L(eta, k, sigma) for it in range(nits)])

# dependence on k:
plt.figure()
for l,eta in enumerate(etas):
    for j,sigma in enumerate(sigmas):
        plt.plot(ks, means[l,j,:], label='eta = {}, sigma = {}'.format(eta,sigma), linestyle=linestyles[j], lw=1+eta)
plt.legend()
plt.xlabel('k')
plt.ylabel('avg. loss')
plt.show()

# dependence on eta:
plt.figure()
for i,k in enumerate(ks):
    for j,sigma in enumerate(sigmas):
        plt.semilogy(etas, means[:,j,i], label='k = {}, sigma = {}'.format(k,sigma), linestyle=linestyles[j], lw=1+np.log(k))
plt.legend()
plt.xlabel('eta')
plt.ylabel('avg. loss')
plt.show()

# dependence on sigma:
plt.figure()
for i,k in enumerate(ks):
    for l,eta in enumerate(etas):
        plt.plot(np.array(sigmas)**2, means[l,:,i], label='k = {}, eta = {}'.format(k,eta), linestyle=linestyles[l], lw=1+np.log(k))
plt.legend()
plt.xlabel('sigma²')
plt.ylabel('avg. loss')
plt.show()

