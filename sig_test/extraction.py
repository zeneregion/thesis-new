from numpy import uintp, array, zeros, sum, linalg, uint8
from cv2 import getRotationMatrix2D, warpAffine, flip, setUseOptimized, imwrite, rectangle, cvtColor, COLOR_GRAY2BGR
from bitarray import bitarray
import gc
from ctypes import *
import ctypes
from numpy.ctypeslib import ndpointer
#from multiprocessing.pool import Pool, Process, Value
import threading
import subprocess
import Queue
from threading import Thread

libextraction = cdll.LoadLibrary("./C_Libraries/libextractionv2.so")
libextraction.sum.restype = ctypes.c_double
_doublepp = ndpointer(dtype = uintp, ndim = 1, flags = 'C')
libextraction.sum.argtypes = [_doublepp, ctypes.c_int]
#libextraction.calculateSD.argtypes = [ctypes.c_int]
libextraction.calculateSD.restype = ctypes.c_double
setUseOptimized(True)
##gc.enable()
N = 0
M = 0
L = 0
image = array([])
width = 0
height = 0
number_of_block = 0
rot0 = array([], uint8)
#rot90 = array([], uint8)
#rot180 = array([], uint8)
#rot270 = array([], uint8)
lum_array = 0
def set_initials(N_f, M_f, L_f, image_f):
    global N, M, L, image, number_of_blocks
    N = N_f
    M = M_f 
    L = L_f
#    print N,M,L
    image = image_f
    number_of_blocks = ((L - N) / M) + 1

def get_total_energy_of_block(block):
    block = block.flatten()
    total_energy = 0
    for element in block:
        total_energy += element ** 2

    return total_energy

#@profile    
def get_average_luminance_of_block(block):
    return sum(block) / (64.0)


def get_second_singular(block):
    U, s, V = linalg.svd(block)
    #print s[1] ** 2
    return s[1] ** 2

def get_singular_energy(block):
    total_energy = get_total_energy_of_block(block)
    if total_energy == 0:
        return 0
    else:
        return get_second_singular(block) / get_total_energy_of_block(block)



#@profile
def get_blocks():
    global counter
    '''Dividing cropped image N x N blocks by M overlapping'''
    I_vis_blur_y = zeros((number_of_blocks * N, number_of_blocks * N), uint8)
    I_vis_blur_x = zeros((number_of_blocks * N, L), uint8)
    for x in xrange(0, L - M, M):
        I_vis_blur_x[x * 2:x * 2 + N, :] = image[x:x + N, :]

    for y in xrange(0, L - M, M):
        I_vis_blur_y[:, y * 2:y * 2 + N] = I_vis_blur_x[:, y:y + N]

    #imwrite("blocked_example.jpg", I_vis_blur_y)
    return I_vis_blur_y

# #@profile
# def basic_rotations(rot0):
#     center = (N * number_of_blocks) / 2
#     rot_matrix = getRotationMatrix2D((center, center), 90, 1)
#     rot90 = warpAffine(rot0, rot_matrix, (center * 2, center * 2))
#     rot180 = warpAffine(rot90, rot_matrix, (center * 2, center * 2))
#     rot270 = warpAffine(rot180, rot_matrix, (center * 2, center * 2))
#     vertical = flip(rot0, 0)
#     horizontal = flip(rot0, 1)
#     rot0_c = cvtColor(rot0, COLOR_GRAY2BGR)
#     rot90_c = cvtColor(rot90, COLOR_GRAY2BGR)
#     rot180_c = cvtColor(rot180, COLOR_GRAY2BGR)
#     rot270_c = cvtColor(rot270, COLOR_GRAY2BGR)
#     vertical_c = cvtColor(vertical, COLOR_GRAY2BGR)
#     horizontal_c = cvtColor(horizontal, COLOR_GRAY2BGR)
#     for y in range(0,16):
#         print range(y,16)
#         for x in range(y,16):
#            rot0_c = rectangle(rot0_c, (x * 8, y * 8), (x * 8 + 8 , y * 8 + 8), (255,0,0), 1)
#            rot90_c = rectangle(rot90_c, (x * 8, y* 8), (x * 8 + 8,y * 8 + 8), (255,0,0), 1)
#            rot180_c = rectangle(rot180_c, (x * 8,y * 8), (x * 8+8,y * 8+8), (255,0,0), 1)
#            rot270_c = rectangle(rot270_c, (x * 8,y *8), (x * 8+8,y * 8+8), (255,0,0), 1)
#            vertical_c = rectangle(vertical_c, (x * 8,y * 8), (x * 8+8,y * 8+8), (255,0,0), 1)
#            horizontal_c = rectangle(horizontal_c, (x * 8,y * 8), (x * 8+8,y *8+8), (255,0,0), 1)
#     imwrite("rot90_quadrant.jpg",rot90_c)
#     imwrite("rot180_quadrant.jpg",rot180_c)
#     imwrite("rot270_quadrant.jpg", rot270_c)
#     imwrite("rot0_quadrant.jpg", rot0_c)
#     imwrite("horizontal_quadrant.jpg", horizontal_c)
#     imwrite("vertical_quadrant.jpg", vertical_c)
    
#     rot90 = rot90[0:120, 0:120]
#     rot180 = rot180[0:120, 0:120]
#     rot270 = rot270[0:120, 0:120]
    
# ##        fVertical0 = flip(image, 0)
# ##        fHorizontal0 = flip(image, 1)
# ##        fVertical90 = flip(rot90, 0)
# ##        fHorizontal90 = flip(rot90, 1)
# ##        fVertical180 = flip(rot180, 0)
# ##        fHorizontal180 = flip(rot180, 1)
# ##        fVertical270 = flip(rot270, 0)
# ##        fHorizontal270 = flip(rot270, 1)

#     return rot90, rot180, rot270
# ##    fVertical0, fHorizontal0, fVertical90, fHorizontal90, fVertical180, fHorizontal180, \
# ##         fVertical270, fHorizontal270

#@profile

def get_luminances():
    x = 0
    y = 0
    lumin_array = zeros((31,31))

    while x<31 or y<31:
        lumin_array[x][y] = get_average_luminance_of_block(rot0[x*N:x*N+N, y*N:y*N+N])
        #print lumin
        if x==30 and y==30:
            break
        if x == 30:
            y += 1
            x= 0
        else:
            x = x + 1
    #print lumin_array
    return lumin_array

def get_fragment(x, y, only_rotate):
    global lum_array
    if only_rotate == 2:
        avg_lum = (lum_array[x][y] + lum_array[y][x] + lum_array[x][30 - y] + lum_array[y][30 - x] + \
            lum_array[30 - x][30 - y] + lum_array[30 - y][30 - x] + lum_array[30 - x][y] + lum_array[30 - y][x]) / 8
        std_lum = libextraction.calculateSD(array([lum_array[x][y], lum_array[y][x], lum_array[x][30 - y], lum_array[y][30 - x] + \
            lum_array[30 - x][30 - y], lum_array[30 - y][30 - x], lum_array[30 - x][y], lum_array[30 - y][x]]).ctypes.data_as(c_void_p))
    
        rot0_copy = rot0.copy()
        rot0_copy = cvtColor(rot0_copy, COLOR_GRAY2BGR)
        rot0_copy = rectangle(rot0_copy, (x * 8, y * 8), (x * 8 + 8 , y * 8 + 8), (x*15,y*15,0), 1)
        rot0_copy = rectangle(rot0_copy, (y * 8, x * 8), (y* 8 + 8 , x * 8 + 8), (x*15,y*15,0), 1) 
        rot0_copy = rectangle(rot0_copy, (x * 8, (30 - y) * 8), (x  * 8 + 8 , (30 - y) * 8 + 8), (x*15,y*15,0), 1)
        rot0_copy = rectangle(rot0_copy, (y * 8, (30 - x) * 8), (y * 8 + 8 , (30 - x) * 8 + 8), (x*15,y*15,0), 1)
        rot0_copy = rectangle(rot0_copy, ((30 - x) * 8, (30 - y) * 8), ((30 - x) * 8 + 8 , (30 - y) * 8 + 8), (x*15,y*15,0), 1)
        rot0_copy = rectangle(rot0_copy, ((30 - y) * 8, (30 - x) * 8), ((30 - y) * 8 + 8 , (30 - x) * 8 + 8), (x*15,y*15,0), 1)
        rot0_copy = rectangle(rot0_copy, ((30 - x) * 8, y * 8), ((30 - x) * 8 + 8 , y  * 8 + 8), (x*15,y*15,0), 1)
        rot0_copy = rectangle(rot0_copy, ((30 - y) * 8, x * 8), ((30 - y) * 8 + 8 , x * 8 + 8), (x*15,y*15,0), 1)
        imwrite("rot0_rectangle.jpg" , rot0_copy)
        return avg_lum, std_lum

    elif only_rotate == -1:
        avg_lum = (lum_array[x][y] + lum_array[30 - y][x] + lum_array[x][30 - y] + lum_array[y][30 - x]) / 4
        #std_lum = libextraction.calculateSD(array([lum_array[x][y], lum_array[x][30 - y], lum_array[30 - x][30 - y], lum_array[30 - x][y]]).ctypes.data_as(c_void_p))
        std_lum = libextraction.calculateSD(array([lum_array[x][y], lum_array[30 - y][x], lum_array[x][30 - y], lum_array[y][30 -x]]).ctypes.data_as(c_void_p))
        #print std_lum
        return avg_lum, std_lum

    elif only_rotate == 0:
        avg_lum = lum_array[x][y]
        std_lum = lum_array[x][y]

        return avg_lum, std_lum

    elif only_rotate == 1:
        avg_lum = (lum_array[x][y] + lum_array[x][30 - y] + lum_array[30 -x][y] + lum_array[30 - x][30 - y]) / 4
        #print avg_lum
        #std_lum = libextraction.calculateSD(array([lum_array[x][y], lum_array[x][30 - y], lum_array[30 - x][30 - y], lum_array[30 - x][y]]).ctypes.data_as(c_void_p))
        std_lum = libextraction.calculateSD(array([lum_array[x][y], lum_array[x][30 - y], lum_array[30 - x][y], lum_array[30 - x][30 -y]]).ctypes.data_as(c_void_p))
        #print std_lum
        #print avg_lum, std_lum
        return avg_lum, std_lum

    # if only_rotate == 1:
    #     results = map(get_average_luminance_of_block, [rot0[y * N:y * N + N, x * N:x * N + N], rot0[(y + 1)* N:(y + 1) * N + N, (x - 1) * N:(x - 1) * N + N], \
    #         rot0[(30 - y - 1)* N:(30 - y - 1) * N + N, (x - 1) * N:(x - 1) * N + N], rot0[(30 - y)* N:(30 - y) * N + N, x  * N:x * N + N], \
    #         rot0[(30 - y)* N:(30 - y) * N + N, (30 - x) * N:(30 - x) * N + N], rot0[(30 - y - 1)* N:(30 - y - 1) * N + N, (30 - x + 1) * N:(30 - x + 1) * N + N], \
    #         rot0[(y + 1)* N:(y + 1) * N + N, (30 - x + 1) * N:(30 - x + 1) * N + N], rot0[y* N:y * N + N, (30 - x) * N:(30 - x) * N + N]]
    #     avg_lum = (results[0] + results[1] + results[2] + results[3] + results[4] + results[5] + results[6] + results[7]) / 8
    #     #std_lum = np.std(np.array([lum1, lum2, lum3, lum4]))
    #     std_lum = libextraction.calculateSD(array([results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7]]).ctypes.data_as(c_void_p))

    #     #singular energy part
    #     # singular_energies = map(get_singular_energy, [rot0[y * N:y * N + N, x * N:x * N + N], rot90[y * N:y * N + N, x * N:x * N + N], \
    #     #     rot180[y * N:y * N + N, x * N:x * N + N], rot270[y * N:y * N + N, x * N:x * N + N]])
    #     # avg_sing = (singular_energies[0] + singular_energies[1] + singular_energies[2] + singular_energies[3]) / 4
    #     # std_sing = libextraction.calculateSD(array([singular_energies[0], singular_energies[1], singular_energies[2], singular_energies[3]]). \
    #     #     ctypes.data_as(c_void_p))
    #     return avg_lum, std_lum

    # elif only_rotate == 0:
    #     lum1 = get_average_luminance_of_block(rot0[y * N:y * N + N, x * N:x * N + N])
    #     avg_lum = lum1
    #     std_lum = 0
    #     # avg_sing = get_singular_energy(rot0[y * N:y * N + N, x * N:x * N + N])
    #     # std_sing = 0
        
    #     return avg_lum, std_lum

    # elif only_rotate == -1:
    #     results = map(get_average_luminance_of_block, [rot0[y * N:y * N + N, x * N:x * N + N],rot90[y * N:y * N + N, x * N:x * N + N]]
    #     avg_lum = (results[0] + results[1] + results[2] + results[3] + results[4] + results[5] + results[6] + results[7]) / 8
    #     #std_lum = np.std(np.array([lum1, lum2, lum3, lum4]))
    #     std_lum = libextraction.calculateSD(array([results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7]]).ctypes.data_as(c_void_p))


  #  else:
  #      results = map(get_average_luminance_of_block, [rot0[y * 8:y * 8 + N, x * 8:x * 8 + N], rot90[y * 8:y * 8 + N, x * 8:x * 8 + N], \
  #          rot180[y * 8:y * 8 + N, x * 8:x * 8 + N], rot270[y * 8:y * 8 + N, x * 8:x * 8 + N]])
  #      #lum1 = get_average_luminance_of_block(rot0[y * 8:y * 8 + N, x * 8:x * 8 + N])
  #      #lum2 = get_average_luminance_of_block(rot90[y * 8:y * 8 + N, x * 8:x * 8 + N])
  #      #lum3 = get_average_luminance_of_block(rot180[y * 8:y * 8 + N, x * 8:x * 8 + N])
        #lum4 = get_average_luminance_of_block(rot270[y * 8:y * 8 + N, x * 8:x * 8 + N])
##            lum5 = self.get_average_luminance_of_block(fVertical0[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum6 = self.get_average_luminance_of_block(fHorizontal0[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum7 = self.get_average_luminance_of_block(fVertical90[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum8 = self.get_average_luminance_of_block(fHorizontal90[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum9 = self.get_average_luminance_of_block(fVertical180[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum10 = self.get_average_luminance_of_block(fHorizontal180[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum11 = self.get_average_luminance_of_block(fVertical270[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])
##            lum12 = self.get_average_luminance_of_block(fHorizontal270[y * 8:y * 8 + self.N, x * 8:x * 8 + self.N])

       # avg_lum = (lum1 + lum2 + lum3 + lum4) / 4
#        avg_lum = (results[0] + results[1] + results[2] + results[3]) / 4

        #std_lum = np.std(np.array([lum1, lum2, lum3, lum4, lum5, lum6, lum7, lum8, lum9, lum10, lum11, lum12]))
        #std_lum = libextraction.calculateSD(array([lum1, lum2, lum3, lum4]).ctypes.data_as(c_void_p))
 #       std_lum = libextraction.calculateSD(array([results[0], results[1], results[2], results[3]]).ctypes.data_as(c_void_p))


#        return avg_lum, std_lum
#@profile
def get_all_fragments():
    global rot0, lum_array
    fragments_list = [[],[], [], []]
    rot0 = get_blocks()
    #print rot0
    lum_array = get_luminances()
    #print lum_array
    #rot90, rot180, rot270 = basic_rotations(rot0)
    counter_x = 0
    counter_y = 0
    #append_fragment = fragments_list.append
    append_avg_lum = fragments_list[0].append
    append_std_lum = fragments_list[1].append
    # append_avg_sing = fragments_list[2].append
    # append_std_sing = fragments_list[3].append
    while(counter_x < 15 or counter_y < 15):
        if counter_x == 16:
            counter_y += 1
            counter_x = counter_y
        if counter_x == counter_y or counter_x == 15:
            if counter_x == 15 and counter_y == 15:
                avg_lum, std_lum = get_fragment(counter_x, counter_y, 0)
                append_avg_lum(avg_lum)
                append_std_lum(std_lum)
                # append_avg_sing(avg_sing)
                # append_std_sing(std_sing)                
            elif counter_x == 15:
                avg_lum, std_lum = get_fragment(counter_x, counter_y, -1)
                append_avg_lum(avg_lum)
                append_std_lum(std_lum)
                # append_avg_sing(avg_sing)
                # append_std_sing(std_sing)
            elif counter_x == counter_y:
                avg_lum, std_lum = get_fragment(counter_x, counter_y, 1)  
                append_avg_lum(avg_lum)
                append_std_lum(std_lum)
        else:
            avg_lum, std_lum = get_fragment(counter_x, counter_y, 2)
            append_avg_lum(avg_lum)
            append_std_lum(std_lum)
            # append_avg_sing(avg_sing)
            # append_std_sing(std_sing)   
        counter_x += 1
    return fragments_list

#@profile
def get_signature():
    signature = bitarray()
    counter_list = 0
    counter_fragment = 0
    sig_append = signature.append
    fragments = get_all_fragments()
    for features in fragments:
        for x in range(0, len(features) -1):
            if features[x] < features[x + 1]:
                sig_append(True)
            else:
                sig_append(False)

    sig_append(False)
    sig_append(False)
    #print len(signature)
    #print len(signature)
    #print("Generated signature length:%d",len(signature))
    #print signature
    return signature




