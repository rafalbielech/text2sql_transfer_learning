(code was modified from [here](https://github.com/taoyds/spider/tree/master/baselines/sqlnet))

## Setup the environment
Run ```python unpack.py``` to unpack the datasets

## Training the models
```
cd models/sqlnet
python train.py --dataset=../../spider_dataset/ --no_gpu --epochs=100
```

Of course, you can use different flags; run ```python train.py --help``` for help w/the flags.

## Data Split
All of our data is found in the {train, train_other, dev}.json files in the original spider dataset. The data split module creates a new folder in this project that contains the files that the modules is expecting in the train and test.

Load_dataset function loads below tables from dataset folder:
TABLE_PATH = "tables.json"
TRAIN_PATH = "train.json"
DEV_PATH = "dev.json"
TEST_PATH = "dev.json"

There are two available interfaces, a command line interface as well as a python interface.

Example of command line interface:

```python datasplitter.py --orig_dataset=spider_dataset --new_dataset_dir=my_new_dataset_for_db_42 --database_num=42 --print_db_nums --train_split=0.7```

Run below for help
```python datasplitter.py --help```


Example of the python interface:
```python
from datasplitter import DataSplitter
p = DataSplitter(path_to_original_dataset='./spider_dataset', train_split=0.6)
p.create_dataset_folder("test_dir")
p.merge_data_files()
p.split_based_on_database_v1(some_database_to_split_on, p.combined_data)
# ex: p.split_based_on_database_v1("yelp", p.combined_data)
# if you would like to create further splits in train and retrain then use v2
# ex:  p.split_based_on_database_v2("yelp", p.combined_data)
p.delete_dataset_folder()
```
For some reason, DEV_PATH and TEST_PATH right now are expecting a dev.json file thus one is created, however, it is properly split up into test and validate json files using a designated split.


## Experiment Driver

The experiment driver integrates the modules(datasplitter.py, train.py, retrain.py and test.py). The configurations can be modified in the config.json in the root folder before executing the file. This was the python script used to conduct our experiments and parellize our train, retrain and test procedure on gypsum. If running on local machine with no gpus, make sure to set the --no_gpu flag as true in the config.json, else set the no_gpu flag as false.

The experiment driver expects two arguments --start and --end to indicate the range of database numbers that we want to perform the experiment on. 

Command line interface:

```python experimentDriver.py --start 1 --end 10```