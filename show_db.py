#!/bin/env python3

import pickle

if __name__ == '__main__':
    with open('facedb.db', 'rb') as f:
        face_database_all = pickle.loads(f.read())

    for p in face_database_all:
        print(p.pinfo, len(p.feature_list))
