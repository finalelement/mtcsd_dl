import numpy as np
import nibabel as nib
import random

def load_nifty(path_to_file, data_type):
    nifti_data = nib.load(path_to_file)
    nifti_img = nifti_data.get_fdata(dtype=data_type)
    nifti_data.uncache()
    return nifti_img


def nifti_image_generator_patch(inputPath, bs, patch_size):
    # open the CSV file for reading
    #f = open(inputPath, "r")
    n_retrievals = 250000
    n_classes = 45
    # loop indefinitely
    while True:

        for vol_index, each_vol in enumerate(inputPath):

            # Load Nifti Volumes of Input, Output and Mask
            input_vol = load_nifty(each_vol['input_image'], data_type='float32')
            output_vol = load_nifty(each_vol['output_image'], data_type='float32')
            mask_vol = load_nifty(each_vol['mask'], data_type='float32')

            # Convert mask_vol to int to save space
            mask_vol = np.int16(mask_vol)

            # Extract Voxel Indices
            true_vox_inds = np.where(mask_vol == 1)
            true_vox_inds = np.asarray(true_vox_inds)
            true_vox_inds = np.transpose(true_vox_inds)
            len_true_vox = len(true_vox_inds)

            current_retrieval = 0
            while current_retrieval < n_retrievals:
                # initialize our batches of images and labels
                images = np.empty((bs, patch_size[0], patch_size[1], patch_size[2], n_classes))
                labels = np.empty((bs, n_classes))

                # X = np.empty((self.batch_size, self.n_classes))
                # y = np.empty((self.batch_size, self.n_classes))

                # Generate Random Inds for usage
                rand_inds = random.sample(range(len_true_vox - 1), bs)

                # Generate data
                for each_ind, each in enumerate(rand_inds):
                    # Retrieve indices
                    vox_inds = true_vox_inds[each, :]
                    images[each_ind, :] = np.squeeze(input_vol[vox_inds[0]-1:vox_inds[0]+2,
                                                               vox_inds[1]-1:vox_inds[1]+2,
                                                               vox_inds[2]-1:vox_inds[2]+2, :])

                    labels[each_ind, :] = np.squeeze(output_vol[vox_inds[0], vox_inds[1], vox_inds[2], :])

                current_retrieval = current_retrieval + bs
                yield (images, labels)