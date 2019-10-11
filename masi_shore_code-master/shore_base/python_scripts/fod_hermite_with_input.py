from dipy.reconst.shore import ShoreModel
#from dipy.viz import window, actor
#from dipy.data import fetch_isbi2013_2shell, read_isbi2013_2shell, get_sphere
from scipy.io import loadmat,savemat
from dipy.io.gradients import read_bvals_bvecs
from dipy.core.gradients import gradient_table
import os
import numpy as np
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Define Paths for the data and bvals and bvecs
data_path = r'D:\Users\Vishwesh\PycharmProjects\shore_mapmri\multi_shell_data_b0.mat'
bval_path = r'D:\Users\Vishwesh\PycharmProjects\shore_mapmri\ms_bvals_b0.bval'
bvec_path = r'D:\Users\Vishwesh\PycharmProjects\shore_mapmri\ms_bvecs_b0.bvec'

data_path = os.path.normpath(data_path)
bval_path = os.path.normpath(bval_path)
bvec_path = os.path.normpath(bvec_path)

bvals, bvecs = read_bvals_bvecs(bval_path, bvec_path)
gtab = gradient_table(bvals, bvecs)

print('Gradient Table Loaded and Ready for use')

data = loadmat(data_path)
actual_data = data['ms_data']

print('Input Data all loaded and ready for use ...')

# Define Paths for FOD Data
fod_data_path = r'D:\Users\Vishwesh\PycharmProjects\shore_mapmri\fod_qspace.mat'
fod_bval_path = r'D:\Users\Vishwesh\PycharmProjects\shore_mapmri\fod_bvals.bval'
fod_bvec_path = r'D:\Users\Vishwesh\PycharmProjects\shore_mapmri\fod_bvecs.bvec'

fod_data_path = os.path.normpath(fod_data_path)
fod_bval_path = os.path.normpath(fod_bval_path)
fod_bvec_path = os.path.normpath(fod_bvec_path)

fod_bvals, fod_bvecs = read_bvals_bvecs(fod_bval_path, fod_bvec_path)
fod_gtab = gradient_table(fod_bvals, fod_bvecs)

print('FOD Gradient Table Loaded and Ready for use')

fod_data = loadmat(fod_data_path)
fod_actual_data = fod_data['new_q_fod']

print('Output Data all loaded and ready for use ...')

print('Fitting Shore to both models')

radial_order = 6
zeta = 700
lambdaN = 1e-8
lambdaL = 1e-8
asm = ShoreModel(gtab, radial_order=radial_order,
                 zeta=zeta, lambdaN=lambdaN, lambdaL=lambdaL)

asmfit = asm.fit(actual_data)

print('Shore Model Coeffs Generated ...')

print('Transforming object shape to save to a .mat file')

shore_input_matrix = np.zeros((57267,50))

for i in range(0,57267):

    temp_shore_coeffs = asmfit.fit_array[i]._shore_coef
    shore_input_matrix[i,:] = temp_shore_coeffs

    if (i%1000 == 0):
        print(i)

savemat('shore_coeffs_r6_v2.mat',mdict={'input_shore': shore_input_matrix})

print('Shore Coefficients Fitted for Input Data and Saved as well !!')

radial_order = 6
zeta = 700
lambdaN = 1e-8
lambdaL = 1e-8
asm_fod = ShoreModel(fod_gtab, radial_order=radial_order,
                 zeta=zeta, lambdaN=lambdaN, lambdaL=lambdaL)

asm_fod_fit = asm_fod.fit(fod_actual_data)

print('Shore Model Coeffs Generated for FOD ...')

print('Transforming object shape to save to a .mat file')

shore_output_matrix = np.zeros((57267,50))

for i in range(0,57267):

    temp_shore_coeffs = asm_fod_fit.fit_array[i]._shore_coef
    shore_output_matrix[i,:] = temp_shore_coeffs

    if (i%1000 == 0):
        print(i)

savemat('shore_coeffs_fod_r6_v2.mat',mdict={'output_shore': shore_output_matrix})

print('Shore Coefficients Fitted for Output Data and Saved as well!!')

signal_recon = asm_fod_fit.fitted_signal()
print('Signal Reconstructed from shore FOD coefficients')

mse_vector = np.zeros((57267,1))

for i in range(0,57267):

    orig_sig = fod_actual_data[i,:]
    recon_sig = signal_recon[i,:]

    temp_mse = np.mean((orig_sig - recon_sig)**2)
    mse_vector[i] = temp_mse


n, bins, patches = plt.hist(x=mse_vector, bins=100, color='#0504aa',
                            alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Mean Squared Error')
plt.ylabel('Number of Voxels - Total 57000')
plt.title('Signal Representation using 3D-Shore')
maxfreq = n.max()
plt.show()

print('Debug and save the Shore basis matrix for the FOD part')