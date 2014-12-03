import string
import re

def read_file(filename):
    r"""Assume the file is the format
    word \t tag
    word \t tag
    [[blank line separates sentences]]
    
    This function reads the file and returns a list of sentences.  each
    sentence is a pair (tokens, tags), each of which is a list of strings of
    the same length.
    """
    sentences = open(filename).read().strip().split("\n\n")
    ret = []
    for sent in sentences:
        lines = sent.split("\n")
        pairs = [L.split("\t") for L in lines]
        tokens = [tok for tok,tag in pairs]
        tags = [tag for tok,tag in pairs]
        ret.append( (tokens,tags) )
    return ret

def clean_str(s):
    """Clean a word string so it doesn't contain special crfsuite characters"""
    return s.replace(":","_COLON_").replace("\\", "_BACKSLASH_")

def extract_features_for_sentence1(tokens):
    N = len(tokens)
    feats_per_position = [set() for i in range(N)]
    for t in range(N):
        w = clean_str(tokens[t])
        digitre = re.compile('.*[\d].*')
        feats_per_position[t].add("word=%(word)s\tcap=%(isupper)i\tdigits=%(containsDigit)i\tstripOut=%(stripOut)s\tlowercased=%(lowercased)s\tshape=%(shape)s"%{"word":w, "isupper":w[0].isupper(), "containsDigit":bool(digitre.search(w)), "stripOut":strip_feature(w), "lowercased":w.lower(), "shape":shape_feature(w)})
    return feats_per_position

extract_features_for_sentence = extract_features_for_sentence1

#Anything that is definitely not an NE
def strip_feature(t): 
    if re.match('#.*',t): #Hashtag
        return True
    elif re.match('@.*',t): #mention
        return True
    elif re.match('RT|Retweet',t): #Retweet
        return True
    elif re.match('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)',t): #url
        return True
    elif re.match("[<>.?!$@!%^;&*_\-=+():|,'\"\\/\[\]pPD3]+", t): #Emoticons and symbols
        return True
    elif re.match("'s", t): #Emoticons and symbols
        return True
    elif re.match("^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$",t): #dates
        return True
    return False


def shape_feature(t):
    #reduce uppercase
    shape = re.sub(r'[A-Z]+','A',t)
    #reduce lowercase
    shape = re.sub(r'[a-z]+','a',shape)
    #reduce numbers
    shape = re.sub(r'[0-9]+','0',shape)
    #reduce punctuations
    shape = re.sub(r'[^A-Za-z0-9]+','$',shape)
    return shape

def extract_features_for_file(input_file, output_file):
    """This runs the feature extractor on input_file, and saves the output to
    output_file."""
    sents = read_file(input_file)
    with open(output_file,'w') as output_fileobj:
        for tokens,goldtags in sents:
            feats = extract_features_for_sentence(tokens)
            for t in range(len(tokens)):
                feats_tabsep = "\t".join(feats[t])
                print>>output_fileobj, "%s\t%s" % (goldtags[t], feats_tabsep)
            print>>output_fileobj, ""

extract_features_for_file("train.txt", "train.feats")
extract_features_for_file("dev.txt", "dev.feats")
