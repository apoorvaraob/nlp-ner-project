#!/bin/sh
set -eux
python simple_fe.py
crfsuite learn -m mymodel train.feats > train.log
#crfsuite learn -m mymodel -a lbfgs -p c2=1 train.txt
crfsuite tag -m mymodel test_nolabels.feats > predtags
python tageval.py test_nolabels.txt predtags
#append dev.txt to train.txt
