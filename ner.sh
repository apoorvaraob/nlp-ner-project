#!/bin/bash
set -eux
python simple_fe.py
crfsuite learn -m mymodel -a lbfgs -p c2=0.01 train.feats 
#crfsuite learn -m mymodel train.feats > train.log
crfsuite tag -m mymodel test_nolabels.feats > predtags
python tageval.py test_withlabels.txt predtags
python pred2kaggle.py predtags > for_kaggle
paste predtags test_nolabels.txt > all_results.txt
