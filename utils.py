from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Lock

def parallelize_with_param(method, param_list):
    lock = Lock()
    num_done_wrapper = [0] # TODO: switch to python 3 and use non-local
    total = len(param_list)

    # closure to track of how many network calls we've completed
    def _method(param):
        result = method(param)
        with lock:
            num_done_wrapper[0] = num_done_wrapper[0] + 1
            num_done = num_done_wrapper[0]
            if num_done % 20 == 0:
                print "Finished {}/{}".format(num_done, total)
        return result

    pool = ThreadPool(100)
    results = pool.map(_method, param_list)
    pool.close()
    pool.join()
    return results
