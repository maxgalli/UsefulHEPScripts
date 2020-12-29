import numpy as np

def random_array(n):
    """
    Create 2x2 random array and return it after performing useless
    operations
    """
    arr = np.random.rand(n, n)
    arr_up = 1 + arr
    arr_down = 1 - arr
    mean = arr.mean()
    return arr

def random_array_for_loop(n, loops):
    """
    Return a list containing *loops* random_arrays created calling
    random_array(n)
    """
    lst = [random_array(n) for loop in range(loops)]
    return lst
