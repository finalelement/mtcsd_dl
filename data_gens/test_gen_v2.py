import os
import nibabel as nib
import numpy as np
import time

def load_nifty(path_to_file, data_type):
    nifti_data = nib.load(path_to_file)
    nifti_img = nifti_data.get_fdata(dtype=data_type)
    nifti_data.uncache()
    return nifti_img

def save_nifti(predicted_vol, path_to_nifti_header, saver_path):

    nib_img = nib.Nifti1Image(predicted_vol, nib.load(path_to_nifti_header).affine, nib.load(path_to_nifti_header).header)

    # Grab ID from path to header
    f_name = path_to_nifti_header.split('\\')
    f_path = os.path.join(saver_path, f_name[-2] + '.nii.gz')
    nib.save(nib_img, f_path)

def test_predictor(dl_model, test_data, save_path):

    vol_saver_path = os.path.join(save_path, 'predicted_volumes')
    if os.path.exists(vol_saver_path) is False:
        os.mkdir(vol_saver_path)

    for vol_index, each_vol in enumerate(test_data):

        start_time = time.time()

        # Load Nifti Volumes of Input, Output and Mask
        input_vol = load_nifty(each_vol['input_image'], data_type='float32')
        output_vol = load_nifty(each_vol['output_image'], data_type='float32')
        mask_vol = load_nifty(each_vol['mask'], data_type='float32')

        # Convert mask_vol to int to save space
        mask_vol = np.int16(mask_vol)

        vol_dims = mask_vol.shape
        pred_vol = np.zeros((vol_dims[0], vol_dims[1], vol_dims[2], 45))
        for x in range(vol_dims[0]):
            print(x)
            for y in range(vol_dims[1]):
                for z in range(vol_dims[2]):
                    if mask_vol[x, y, z] == 1:
                        ip_voxel = np.squeeze(input_vol[x, y, z, :])
                        ip_voxel = np.reshape(ip_voxel, [1, 45])
                        t_pred = dl_model.predict(ip_voxel)
                        pred_vol[x, y, z, :] = np.squeeze(t_pred)

        end_time = time.time()
        time_taken = end_time - start_time
        print('Predictions Completed for Vol {} & Time Taken was {} \n'.format(vol_index, time_taken))
        print('Saving predicted volume')

        save_nifti(pred_vol, each_vol['output_image'], vol_saver_path)




