#This code has been written for aiXai, "www.getaixai.com". This code has been modified for aiXai from the tutorial provided 
#by "The Lazy Programmer" at Udemy.com

from __future__ import print_function, division
from builtins import range


import os
import requests
import zipfile
import numpy as np
import pandas as pd
from scipy.misc import imread, imsave, imresize
from scipy.misc import *
from glob import glob
from tqdm import tqdm
import imageio
import PIL
from PIL import Image


def get_mnist(limit=None):
  if not os.path.exists('../large_files'):
    print("You must create a folder called large_files adjacent to the class folder first.")
  if not os.path.exists('../large_files/train.csv'):
    print("Looks like you haven't downloaded the data or it's not in the right spot.")
    print("Please get train.csv from https://www.kaggle.com/c/digit-recognizer")
    print("and place it in the large_files folder.")

  print("Reading in and transforming data...")
  df = pd.read_csv('../large_files/train.csv')
  data = df.as_matrix()
  np.random.shuffle(data)
  X = data[:, 1:] / 255.0 # data is from 0..255
  Y = data[:, 0]
  if limit is not None:
    X, Y = X[:limit], Y[:limit]
  return X, Y


def get_celeb(limit=None):

  if not os.path.exists('../DCGAN/large_files'):
    os.mkdir('../DCGAN/large_files')

  # eventual place where our final data will reside
  if not os.path.exists('../DCGAN/large_files/img_align_celeba-cropped/img_align_celeba'):

    # check for original data
    if not os.path.exists('../DCGAN/large_files/img_align_celeba'):
      # download the file and place it here
      if not os.path.exists('../DCGAN/large_files/img_align_celeba.zip'):
        print("Downloading img_align_celeba.zip...")
        download_file(
          '0B7EVK8r0v71pZjFTYXZWM3FlRnM',
          '../DCGAN/large_files/img_align_celeba.zip'
        )

      # unzip the file
      print("Extracting img_align_celeba.zip...")
      with zipfile.ZipFile('../DCGAN/large_files/img_align_celeba.zip') as zf:
        zip_dir = zf.namelist()[0]
        zf.extractall('../DCGAN/large_files')


  # load in the original images
  filenames = glob("../DCGAN/large_files/img_align_celeba/*.jpg")
  N = len(filenames)
  print("Found %d files!" % N)



  # crop the images to 64x64
  if not os.path.exists('../DCGAN/large_files/img_align_celeba-cropped'):
    os.mkdir('../DCGAN/large_files/img_align_celeba-cropped')
    os.mkdir('../DCGAN/large_files/img_align_celeba-cropped/img_align_celeba')

  print("Cropping images, please wait...")

  for i in range(N):
      crop_and_resave(filenames[i], '../DCGAN/large_files/img_align_celeba-cropped')
      if i % 1000 == 0:
          print("%d/%d" % (i, N))


  # make sure to return the cropped version
  filenames = glob("../DCGAN/large_files/img_align_celeba-cropped/img_align_celeba/*.jpg")
  return filenames




# functions for altering/editing images
def crop_and_resave(inputfile, outputdir):
  # # theoretically, we could try to find the face
  # # but let's be lazy
  # # we assume that the middle 108 pixels will contain the face

  filename = inputfile.split('/')[-1]

  image = Image.open(inputfile)
  box = (35, 35, 185, 185)
  cropped_image = image.crop(box)
  resized_image = cropped_image.resize((64,64))
  resized_image.save('/'.join([outputdir, filename]))


def scale_image(im):
  # scale to (-1, +1)
  return (im / 255.0)*2 - 1


def files2images_theano(filenames):
  # theano wants images to be of shape (C, D, D)
  # tensorflow wants (D, D, C) which is what scipy imread
  # uses by default
  return [scale_image(imread(fn).transpose((2, 0, 1))) for fn in filenames]




def files2images(filenames):
  return [scale_image(imageio.imread(fn)) for fn in filenames]





# functions for downloading file from google drive
def save_response_content(r, dest):
  # unfortunately content-length is not provided in header
  total_iters = 1409659 # in KB
  print("Note: units are in KB, e.g. KKB = MB")
  # because we are reading 1024 bytes at a time, hence
  # 1KB == 1 "unit" for tqdm
  with open(dest, 'wb') as f:
    for chunk in tqdm(
      r.iter_content(1024),
      total=total_iters,
      unit='KB',
      unit_scale=True):
      if chunk: # filter out keep-alive new chunks
        f.write(chunk)


def get_confirm_token(response):
  for key, value in response.cookies.items():
    if key.startswith('download_warning'):
      return value
  return None


def download_file(file_id, dest):
  drive_url = "https://docs.google.com/uc?export=download"
  session = requests.Session()
  response = session.get(drive_url, params={'id': file_id}, stream=True)
  token = get_confirm_token(response)

  if token:
    params = {'id': file_id, 'confirm': token}
    response = session.get(drive_url, params=params, stream=True)

  save_response_content(response, dest)


