import numpy as np

def func_to_test1(z: np.ndarray):
  return z

def func_to_test2(z: np.ndarray):
  return z ** 2

def func_to_test3(z: np.ndarray):
  return (3*z+5)/(-4*z+1)

def func_to_test4(z: np.ndarray):
  return (3*z+1)/(3*z-1)

def func_to_test5(z: np.ndarray):
  return np.where(z != 0, 1/z, 0)

def func_to_test6(z: np.ndarray):
  return np.cos(1j * np.conj(z)) + np.sin(z)

def func_to_test7(z: np.ndarray):
  return np.where(z != 0, np.log(z), 0)

def func_to_test8(z: np.ndarray):
  return np.cosh(z) + np.tanh(z)