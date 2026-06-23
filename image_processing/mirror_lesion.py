"""
Functions to mirror lesion to other hemisphere.

Several functions are available according to case. For example, if you just wanted to flip hemispheres, the function will flip about the x-axis.
"""

"""
Flip about x-axis: when your image is in a symmetric template, you can just flip the lesion across the x-axis.

For now (June 10, 2026 @ 3:20pm), we will just be using a cerebellar template.

Note that this works best if x=0 corresponds to midsaggital line (if cerebral cortex flipping).

An improvement on this function would be to have an input where you can enter the coordinates for the midsaggital line.

An even greater improvement would be if it could find said line.
"""

# imports
import nibabel as nib

def FlipLR(image):
    """
    Simple flip: flips image along x-axis (L-R flip)

    Input: image (Nifti or string)

    Output: Nifti image
    """
    if type(image) == str:
        image = nib.load(image)
    
    img_arr = image.get_fdata()

    flip_LR = img_arr[::-1, :,:]

    flipped_img = nib.Nifti1Image(flip_LR, image.affine)
    
    return flipped_img