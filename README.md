(code was modified from [here](https://github.com/taoyds/spider/tree/master/baselines/sqlnet))

## Setup the environment
Run ```python unpack.py``` to unpack the datasets

## Training the models
```
cd models/sqlnet
python train.py --dataset=../../spider_dataset/ --no_gpu --epochs=100
```

Of course, you can use different flags; run ```python train.py --help``` for help w/the flags.
