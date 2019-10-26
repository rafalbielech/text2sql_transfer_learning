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

```python datasplitter.py --orig_dataset=spider_dataset --new_dataset_dir=my_new_dataset_for_db_42 --database_num=42 --print_db_nums --split=0.7```

Run below for help
```python datasplitter.py --help```


Example of the python interface:
```python
from datasplitter import DataSplitter
p = DataSplitter(path_to_original_dataset='./spider_dataset', split=0.6)
p.create_dataset_folder("test_dir")
p.merge_data_files()
p.split_based_on_database(some_database_to_split_on, p.combined_data)
p.delete_dataset_folder()
```
For some reason, DEV_PATH and TEST_PATH right now are expecting a dev.json file thus one is created, however, it is properly split up into test and validate json files using a designated split.
