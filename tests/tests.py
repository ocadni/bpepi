import sys
import os
import pickle
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__),".."), "bpepi")))
from st import SparseTensor
from fg import FactorGraph

def test(type='t'):
    """Function to check agreement with SIB

    Args:
    type (str): Which test to perform. Current options are {'t', 'i'}. 't' checks if marginals agree on tree graphs. 'i' checks if marginals from informed and random initializations in bpepi agree in regimes where they do not in SIB.
    """ 
    passed = []
    if type=='t':
        num_dir = 0
        count_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data/tree'))
        for root, dirs, files in os.walk(count_path):
            for name in dirs:
                num_dir += 1
        for i in range(0, num_dir):
            path = os.path.join(count_path, str(i))
            with open(path+'/contacts', 'rb') as f:
                contacts = pickle.load(f)
            with open(path+'/list_obs', 'rb') as f:
                list_obs = pickle.load(f)
            with open(path+'/params', 'rb') as f:
                params = pickle.load(f)
            sib_marginals = np.load(path+'/sib_marginals.npz')['arr_0']
            code_fg = FactorGraph(params[0], params[1], contacts, list_obs, params[2])
            code_fg.update()
            code_marginals = code_fg.marginals()
            if np.allclose(np.sum(code_marginals - sib_marginals, axis=1), np.zeros(params[0]), atol=1e-14) == True:
                passed.append(1)
            else:
                passed.append(0)
        print(sum(passed), 'tests passed out of', len(passed))
    if type=='i':
        save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
        num_dir=0
        count_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_data/initialization'))
        for root, dirs, files in os.walk(count_path):
            for name in dirs:
                print(name)
                num_dir += 1
        print(num_dir)
        for i in range(0, num_dir):
            path = os.path.join(count_path, str(i))
            with open(path+'/contacts', 'rb') as f:
                contacts = pickle.load(f)
            with open(path+'/list_obs', 'rb') as f:
                list_obs = pickle.load(f)
            with open(path+'/list_obs_all', 'rb') as f:
                list_obs_all = pickle.load(f)
            with open(path+'/params', 'rb') as f:
                params = pickle.load(f)
            sib_marginals_rnd = np.load(path+'/sib_marginals_rnd.npz')['arr_0']
            sib_marginals_inf = np.load(path+'/sib_marginals_inf.npz')['arr_0']
            code_f_rnd = FactorGraph(params[0], params[1], contacts, [], params[2])
            code_f_rnd.update(tol=1e-9)
            code_f_rnd.reset_obs(list_obs)
            code_f_rnd.update(tol=1e-9)
            code_marginals_rnd = code_f_rnd.marginals()
            np.savez(save_path+'/bpepi_marginals_rnd.npz', code_marginals_rnd)
            code_f_inf = FactorGraph(params[0], params[1], contacts, list_obs_all, params[2])
            code_f_inf.update(tol=1e-9)
            code_f_inf.reset_obs(list_obs)
            code_f_inf.update(tol=1e-9)
            code_marginals_inf = code_f_inf.marginals()
            np.savez(save_path+'/bpepi_marginals_inf.npz', code_marginals_inf)
            tolerances = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
            distance_1 = '> 1'
            for tol in tolerances:
                if np.allclose(np.sum(np.abs(code_marginals_rnd - sib_marginals_rnd), axis=1), np.zeros(params[0]), atol=tol):
                    distance_1 = '<'+str(tol)
                    break
            distance_2 = '> 1'
            for tol in tolerances:
                if np.allclose(np.sum(np.abs(code_marginals_inf - sib_marginals_rnd), axis=1), np.zeros(params[0]), atol=tol):
                    distance_2 = '<'+str(tol)
                    break
            distance_3 = '> 1'
            for tol in tolerances:
                if np.allclose(np.sum(np.abs(sib_marginals_rnd - sib_marginals_inf), axis=1), np.zeros(params[0]), atol=tol):
                    distance_3 = '<'+str(tol)
                    break
        print('bpepi rnd marginals and sib rnd marginals distance', distance_1)
        print('bpepi inf marginals and sib rnd marginals distance', distance_2)
        print('sib inf marginals and sib rnd marginals distance', distance_3)


test(type='i')
