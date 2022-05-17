import matplotlib.pyplot as plt
import numpy as np
from numpy import asarray
from numpy import exp
from numpy.random import randn
from numpy.random import rand
from numpy.random import randint
from numpy.random import seed

def eggholder(x):
    return (-(x[1] + 47) * np.sin(np.sqrt(abs(x[0]/2 + (x[1]  + 47)))) -x[0] * np.sin(np.sqrt(abs(x[0] - (x[1]  + 47)))))


def schubert(x):
    x1, x2 = x[0], x[1]
    sum1, sum2 = 0, 0
    for i in range(1, 6):
        sum1 = sum1 + (i * np.cos(((i + 1) * x1) + i))
        sum2 = sum2 + (i * np.cos(((i + 1) * x2) + i))
    y = sum1 * sum2
    return y * (-1)


x = np.arange(-512, 513)
y = np.arange(-512, 513)
xgrid, ygrid = np.meshgrid(x, y)
xy = np.stack([xgrid, ygrid])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.view_init(45, -45)
ax.plot_surface(xgrid, ygrid, eggholder(xy), cmap='terrain')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('eggholder(x, y)')
plt.show()


# check if a point is within the bounds of the search
def in_bounds(point, bounds):
    # enumerate all dimensions of the point
    for d in range(len(bounds)):
        # check if out of bounds for this dimension
        if point[d] < bounds[d, 0] or point[d] > bounds[d, 1]:
            return False
    return True

# hill climbing local search algorithm
def hillclimbing(objective, bounds, n_iterations, step_size, start_pt):
    # store the initial point
    solution = start_pt
    # evaluate the initial point
    solution_eval = objective(solution)
    # run the hill climb
    for i in range(n_iterations):
        # take a step
        candidate = None
        while candidate is None or not in_bounds(candidate, bounds):
            candidate = solution + randn(len(bounds)) * step_size
        # evaluate candidate point
        candidte_eval = objective(candidate)
        # check if we should keep the new point
        if candidte_eval <= solution_eval:
            # store the new point
            solution, solution_eval = candidate, candidte_eval
    return [solution, solution_eval]

# simulated annealing algorithm
def simulated_annealing(objective, bounds, n_iterations, step_size, temp):
    # generate an initial point
    best = bounds[:, 0] + rand(len(bounds)) * (bounds[:, 1] - bounds[:, 0])
    # evaluate the initial point
    best_eval = objective(best)
    # current working solution
    curr, curr_eval = best, best_eval
    # run the algorithm
    for i in range(n_iterations):
        # take a step
        candidate = curr + randn(len(bounds)) * step_size
        # evaluate candidate point
        candidate_eval = objective(candidate)
        # check for new best solution
        if candidate_eval < best_eval:
            # store new best point
            best, best_eval = candidate, candidate_eval
            # report progress
            #print('>%d f(%s) = %.5f' % (i, best, best_eval))
            # difference between candidate and current point evaluation
            diff = candidate_eval - curr_eval
        # calculate temperature for current epoch
        t = temp / float(i + 1)
        # calculate metropolis acceptance criterion
        metropolis = exp(-diff / t)
        # check if we should keep the new point
        if diff < 0 or rand() < metropolis:
            # store the new current point
            curr, curr_eval = candidate, candidate_eval
    return [best, best_eval]


# iterated local search algorithm
def iterated_local_search(objective, bounds, n_iter, step_size, n_restarts, p_size, temp, algorithm, sequence):
    # define starting point
    best = None
    while best is None or not in_bounds(best, bounds):
        best = bounds[:, 0] + rand(len(bounds)) * (bounds[:, 1] - bounds[:, 0])
    # evaluate current best point
    best_eval = objective(best)
    # enumerate restarts
    for n in range(n_restarts):
        seed(sequence[n])
        # generate an initial point as a perturbed version of the last best
        start_pt = None
        while start_pt is None or not in_bounds(start_pt, bounds):
            start_pt = best + randn(len(bounds)) * p_size
        # perform a stochastic hill climbing search
        if algorithm:
            solution, solution_eval = hillclimbing(objective, bounds, n_iter, step_size, start_pt)
        else:
            solution, solution_eval = simulated_annealing(objective, bounds, n_iter, step_size, temp)
        # check for new best
        if solution_eval < best_eval:
            best, best_eval = solution, solution_eval
            print('Restart %d, best: f(%s) = %.5f' % (n, best, best_eval))
    return [best, best_eval]



def main():
    # seed the pseudorandom number generator
    seed(4567)
    # define range for input
    bounds = asarray([[-512.0, 513.0], [-512.0, 513.0]])
    # define the total iterations
    n_iterations = 2000
    # define the maximum step size
    step_size = 0.2
    # total number of random restarts
    n_restarts = 30
    # prepare a sequence
    sequence = [randint(100000) for i in range(n_restarts)]
    # perturbation step size
    p_size = 100.0
    # initial temperature
    temp = 2
    # perform the hill climbing search
    print('Hill Climbing search')
    best, score = iterated_local_search(eggholder, bounds, n_iterations, step_size, n_restarts, p_size, temp, 1, sequence)
    print('Done!')
    print('f(%s) = %f' % (best, score))
    print('Simulated Annealing search search')
    # perform the simulated annealing search
    best, score = iterated_local_search(eggholder, bounds, n_iterations, step_size, n_restarts, p_size, temp, 2, sequence)
    print('Done!')
    print('f(%s) = %f' % (best, score))

if __name__ == '__main__':
    main()