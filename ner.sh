#!/bin/bash
set -eux
#python simple_fe.py
crfsuite learn -m mymodel -a l2sgd -p c2=0.000001 train.feats 
#crfsuite learn -m mymodel -a lbfgs -p c1=0.01 -p c2=0.00001 train.feats
crfsuite tag -m mymodel test_nolabels2.feats > predtags
python tageval.py test_withlabels.txt predtags
python pred2kaggle.py predtags > for_kaggle
paste predtags test_nolabels2.txt > all_results.txt
