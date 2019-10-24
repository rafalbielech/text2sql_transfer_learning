#!/bin/sh


export CUR_PATH=$(pwd)
export PATH_TRAIN=$CUR_PATH/models/sqlnet
export PATH_DATA=../..
echo $CUR_PATH
echo $PATH_TRAIN
echo $PATH_DATA
#call train.py
python $CUR_PATH/train.py --dataset=$PATH_DATA/spider_dataset/ --no_gpu --epochs=100
#call retrain.py
#call eval/test
