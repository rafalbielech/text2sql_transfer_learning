#!/bin/sh


export CUR_PATH=$(pwd)
export PATH_TRAIN=$CUR_PATH/models/sqlnet
echo $CUR_PATH
echo $PATH_TRAIN
#call train.py
python $PATH_TRAIN/train.py --dataset=$CUR_PATH/spider_dataset/ --no_gpu --epochs=100
#call retrain.py
#call eval/test
