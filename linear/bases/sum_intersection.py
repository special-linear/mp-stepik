from linear.matrix import Matrix, kernel_basis


# input is two matrices of the same height separated by a blank line
# return two matrices whose columns form bases for the sum and intersection of the images
# output is two matrices separated by a blank line


def generate():
    pass


def check(reply, clue):
    pass


def solve(dataset):
    matrices_strs = dataset.split('\n\n')
    entries = ((map(int, row.split()) for row in entries_strs.splitlines()) for entries_strs in matrices_strs)
    a1, a2 = map(Matrix, entries)
    a = Matrix.hstack(a1, a2)
    a_ker_basis, pivots = kernel_basis(a, output_pivots=True)
    sum_basis = Matrix.hstack(*[a[:, i] for i in pivots])
    intersection_basis = a1 @ a_ker_basis[:a1.shape()[1], :]
    return '{}\n\n{}'.format(sum_basis, intersection_basis)

