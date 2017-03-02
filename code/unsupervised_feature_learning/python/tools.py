# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 17:28:07 2017

@author: Thomas PESNEAU
TOOL FUNCTIONS FOR FEATURE EXTRACTION
"""
import numpy as np
import random
import time

def extract_random_patches(X,nb_patches,rfSize,dim):
    """
    Crop random patches from a set of images
    -----------------
    Parameters:
        X: set of images, numpy array nb_images x nb_elements
        nb_patches: number of patches to extract, int
        rfSize: size of the patches to extract, int
        dim: dimension of the images in the set, list
    """
    N = rfSize * rfSize * 3
    nb_images = X.shape[0]
    patches = np.zeros((nb_patches,N))
    for i in range(nb_patches):
        im_no = i % nb_images
        if(i % 10000 == 0):
            print("Patch extraction: {} / {}".format(i,nb_patches))
        # Draw two random integers
        row = random.randint(0,dim[0] - rfSize)
        col = random.randint(0,dim[1] - rfSize)
        # Crop random patch
        image = X[im_no,:].reshape(tuple(dim))
        patch = image[row:row+rfSize, col:col+rfSize,:]
        patches[i,:] = patch.reshape((1,N))
    return patches
    
def pre_process(patches,eps):
    """
    Pre-process the patches by substracting the mean and dividing by the variance
    --------------
    Parameters:
        patches: collection of patches, numpy array nb_patches x dim_patch
        eps: constant to avoid division by 0
    """
    mean_patches = np.mean(patches, axis=1)
    mean_patches = mean_patches.reshape((len(mean_patches),1))
    #print("size mean: {}".format(mean_patches.shape))
    var_patches = np.var(patches, axis=1)
    var_patches = var_patches.reshape((len(var_patches),1))
    #print("size var: {}".format(var_patches.shape))
    patches = patches - mean_patches
    patches = np.divide(patches,np.sqrt(var_patches + eps))
    return patches
    

def whiten(patches,eps_zca):
    """
    Performs whitening of the patches
    -------------
    Parameters:
        patches: collection of patches, numpy array nb_patches x dim_patch
        eps_zca: zca whitening constant
    """
    C = np.cov(patches,rowvar=False)
    M = np.mean(patches,axis=0)
    M = M.reshape((len(M),1))
    D,V = np.linalg.eig(C)
    D = D.reshape((len(D),1))
    D_zca = np.sqrt(1 / (D + eps_zca))
    D_zca = D_zca.reshape(len(D_zca))
    D_zca = np.diag(D_zca)
    P = np.dot(V,np.dot(D_zca,V.transpose()))
    patches = np.dot((patches.transpose() - M).transpose(),P)
    return patches,M,P
    
def Kmeans(patches,nb_centroids,nb_iter):
    x2 = patches**2
    x2 = np.sum(x2,axis=1)
    x2 = x2.reshape((len(x2),1))
    centroids = np.random.normal(size=(nb_centroids,patches.shape[1])) * 0.1## initialize the centroids at random
    sbatch = 1000
    
    for i in range(nb_iter):
        print("K-means: {} / {} iterations".format(i,nb_iter))
        c2 = 0.5 * np.sum(centroids**2,axis=1)
        c2 = c2.reshape((len(c2),1))
        sum_k = np.zeros((nb_centroids,patches.shape[1]))## dictionnary of patches
        compt = np.zeros(nb_centroids)## number of samples per clusters
        compt = compt.reshape((len(compt),1))
        loss = 0
        ## Batch update
        for j in range(0,sbatch,patches.shape[0]):
            last = min(j+sbatch,patches.shape[0])
            m = last - j
            diff = np.dot(centroids,patches[j:last,:].transpose()) - c2## difference of distances
            labels = np.argmax(diff,axis=0)## index of the centroid for each sample
            max_value = np.max(diff,axis=0)## maximum value for each sample
            loss += np.sum(0.5*x2[j:last,:] - max_value)
            S = np.zeros((m,nb_centroids))
            ## Put the label of each sample in a sparse indicator matrix
            ## S(i,labels(i)) = 1, 0 elsewhere
            for ind in range(m):
                S[ind,labels[ind]] = 1    
            sum_k += np.dot(S.transpose(),patches[j:last,:])## update the dictionnary
            sumS = np.sum(S,axis=0)
            sumS = sumS.reshape((len(sumS),1))
            compt += sumS## update the number of samples per centroid in the batch
            
        centroids = np.divide(sum_k,compt)## Normalise the dictionnary, will raise a RunTimeWarning if compt has zeros
                                          ## this situation is dealt with in the two following lines  
        badCentroids = np.where(compt == 0)## Find the indices of empty clusters
        centroids[tuple(badCentroids),:] = 0## in the case where a cluster is empty, set the centroid to 0 to avoid NaNs
    return centroids
                

def extract_features(X,centroids,rfSize,dim,*args):
    ## Check number of inputs
    if(args):
        print("Optional arguments received")
    else:
        print("No optional arguments")
    
    
def standard():
    raise NotImplementedError
    


