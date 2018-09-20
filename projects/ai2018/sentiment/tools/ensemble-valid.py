#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# ==============================================================================
#          \file   ensemble.py
#        \author   chenghuige  
#          \date   2018-09-15 19:04:21.026718
#   \Description  
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys 
import os

import glob
import pandas as pd
import numpy as np 
from sklearn.metrics import f1_score
import gezi

idir = sys.argv[1]

num_attrs = 20
scores = np.zeros([num_attrs])

def parse(l):
  return np.array([float(x.strip()) for x in l[1:-1].split(',')])

def calc_f1(labels, predicts):
  f1_list = []
  for i in range(num_attrs):
    f1 = f1_score(labels[:,i], predicts[:, i], average='macro')
    f1_list.append(f1)
  f1 = np.mean(f1_list)
  return f1 

def to_predict(logits, need_softmax=True):
  if need_softmax:
    logits = np.reshape(logits, [-1, num_attrs, 4])
    probs = gezi.softmax(logits, -1)
  else:
    probs = logits
  probs = np.reshape(probs, [-1, 4])
  result = np.zeros([len(probs)])
  for i, prob in enumerate(probs):
    # TODO try to calibrate to 0.5 ?
    if prob[0] >= 0.6:
      result[i] = -2
    else:
      result[i] = np.argmax(prob[1:]) - 1
  
  result = np.reshape(result, [-1, num_attrs])

  return result

idx = 2
results = None
results2 = None
for file_ in glob.glob('%s/*.valid.csv' % idir):
  df = pd.read_csv(file_)
  labels = df.iloc[:,idx:idx+num_attrs].values
  predicts = df.iloc[:,idx+num_attrs:idx+2*num_attrs].values
  scores = df['score']
  scores = [parse(score) for score in scores]
  print(file_, calc_f1(labels, predicts), calc_f1(labels, to_predict(scores)))
  if results is None:
    results = np.zeros([len(df), num_attrs * 4])
    results2 = np.zeros([len(df), num_attrs * 4])
  for i, score in enumerate(scores):
    results[i] += score 
    score = gezi.softmax(np.reshape(score, [num_attrs, 4]), -1)
    score = np.reshape(score, [-1])
    results2[i] += score

adjusted_f1 = calc_f1(labels, to_predict(results))
results = np.reshape(results, [-1, num_attrs, 4]) 
predicts = np.argmax(results, -1) - 2
f1 = calc_f1(labels, predicts)

print('f1:', f1)
print('adjusted f1:', adjusted_f1)

adjusted_f1_prob = calc_f1(labels, to_predict(results2, need_softmax=False))
results2 = np.reshape(results2, [-1, num_attrs, 4]) 
predicts2 = np.argmax(results2, -1) - 2
f1_prob = calc_f1(labels, predicts2)

#print(labels)
#print(predicts2)

print('f1_prob:', f1_prob)
print('adjusted f1_prob:', adjusted_f1_prob)