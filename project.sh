#!/bin/bash
python simple_fe.py
rm mymodel
crfsuite learn -m mymodel $1
crfsuite tag -m mymodel dev.feats > predtags
python tageval.py dev.txt predtags
