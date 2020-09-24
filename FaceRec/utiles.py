#!/bin/python

import numpy as np  # 数据处理的库numpy


def eu_dis(feature_1, feature_2): 
    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)
    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    return dist
