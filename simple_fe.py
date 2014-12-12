import string
import re
import nltk
#import codecs
#import sys

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

        #for context features
        if t > 0:
            w_before = clean_str(tokens[t-1])
        else:
            w_before = "none"
        if t+1 < N:
            w_after = clean_str(tokens[t+1])
        else:
            w_after = "none"
        
        
        if t > 1:
            w_before_before = clean_str(tokens[t-2])
        else:
            w_before_before = "none"
        if t+2 < N:
            w_after_after = clean_str(tokens[t+2])
        else:
            w_after_after = "none"



        w = w.decode('utf-8')
        w_before = w_before.decode('utf-8')
        w_after = w_after.decode('utf-8')
        w_before_before = w_before_before.decode('utf-8')
        w_after_after = w_after_after.decode('utf-8')

        digitre = re.compile('.*[\d].*')
        
        
        stripstring = ""
        for featureType in ["hashtag", "mention", "retweet","url","symoticon", "apossuffix", "date"]:
            stripstring += "\t" + featureType + "=" + str(strip_feature(featureType, w))
        
        feats_per_position[t].add("word=%(word)s\tcap=%(isupper)i\tdigits=%(containsDigit)i"+stripstring+"\tlowercased=%(lowercased)s\taffix1=%(affix1)s\tsuffix1=%(suffix1)s\taffix2=%(affix2)s\tsuffix2=%(suffix2)s\taffix3=%(affix3)s\tsuffix3=%(suffix3)s\tshape=%(shape)s\tpostag=%(postag)s\tpostag_context=%(postag_context)s\tprev_word=%(prev_word)s\tnext_word=%(next_word)s\tprev_prev_word=%(prev_prev_word)s\tnext_next_word=%(next_next_word)s\tclusterid=%(clusterid)s"%{"word":w, "isupper":w[0].isupper(), "containsDigit":bool(digitre.search(w)), "lowercased":w.lower(), "affix1":char_affix(w,1), "suffix1":char_suffix(w,1), "affix2":char_affix(w,2), "suffix2":char_suffix(w,2), "affix3":char_affix(w,3), "suffix3":char_suffix(w,3), "shape":shape_feature(w), "postag":pos_tag(w), "postag_context":pos_tag_context(w_before,w,w_after),"prev_word":prev_word(w_before,w),"next_word":next_word(w,w_after),"prev_prev_word":prev_word(w_before_before,w_before),"next_next_word":next_word(w_after,w_after_after),"clusterid":clusterid(w)})

    return feats_per_position

extract_features_for_sentence = extract_features_for_sentence1

#Anything that is definitely not an NE
#character affixes and some wordform features
def strip_feature(mode, t):
    if mode == "hashtag" and re.match('#.*',t): #Hashtag
        return True
    elif mode == "mention" and re.match('@.*',t): #mention
        return True
    elif mode == "retweet" and re.match('RT|Retweet',t): #Retweet
        return True
    elif mode == "url" and re.match('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)',t): #url
        return True
    elif mode == "symoticon" and re.match("[<>.?!$@!%^;&*_\-=+():|,'\"\\/\[\]pPD3]+", t): #Emoticons and symbols
        return True
    elif mode == "apossuffix" and re.match("'s", t): #Emoticons and symbols
        return True
    elif mode == "date" and re.match("^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$",t): #dates
        return True
    
    return False

#shape feature
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


#additional pos tagging features
def is_pos_tag_noun(t):
    word = nltk.word_tokenize(t)
    tag = nltk.pos_tag(word)
    if tag in ['NNP','NNPS','NN','NNS']:
        return True
    else:
        return False


def pos_tag(t):
    word = nltk.word_tokenize(t)
    tag = nltk.pos_tag(word)
    return tag[0][1]


#positional offset feature - pos context
def pos_tag_context(t_before, t, t_after):
    word = nltk.word_tokenize(t)
    before = nltk.word_tokenize(t_before)
    after = nltk.word_tokenize(t_after)
    tag = nltk.pos_tag(word)
    tag_before = nltk.pos_tag(before)
    tag_after = nltk.pos_tag(after)
    tag_context = tag_before + tag + tag_after
    tags = []
    tags += [x[1] for x in tag_context]
    tagsfeat = '-'.join(tags)
    return tagsfeat

#positional offset feature -  context - previous
def prev_word(t_before, t):
    #t = unicode(t)
    #t = t.encode('utf-8', errors='ignore')
    #t_before = unicode(t_before)
    #t_before = t_before.encode('utf-8', errors='ignore')
    prev_this = t_before+"-"+t
    return prev_this


#positional offset feature -  context - next
def next_word(t, t_after):
    #t = unicode(t)
    #t = t.encode('utf-8', errors='ignore')
    #t_after = unicode(t_after)
    #t_after = t_after.encode('utf-8', errors='ignore')
    this_next = t+"-"+t_after
    return this_next

def char_affix(t,x):
    return t[0:x]

def char_suffix(t,x):
    length = len(t)
    last = length-x
    return t[last:]

def clusterid(w):
    print w
    f = open('50mpaths2.txt', 'r')
    if w.isalnum():
        w.strip()
        clusterid = re.findall(r'([0-1]+)(\s+)(%s)(\s+)([0-9]+)(\s+)' % w, f.read(),flags=re.IGNORECASE)
        try:
            clusterid = clusterid[0][0]
        except IndexError:
            clusterid = 0
    else:
        clusterid = 1000110
    print clusterid
    return clusterid


def extract_features_for_file(input_file, output_file):
    """This runs the feature extractor on input_file, and saves the output to
    output_file."""
    #UTF8Writer = codecs.getwriter('utf8')
    #sys.stdout = UTF8Writer(sys.stdout)
    sents = read_file(input_file)
    with open(output_file,'w') as output_fileobj:
        for tokens,goldtags in sents:
            feats = extract_features_for_sentence(tokens)
            for t in range(len(tokens)):
                feats_tabsep = "\t".join(feats[t])
                feats_tabsep = unicode(feats_tabsep)
                #print feats_tabsep
                feats_tabsep = feats_tabsep.encode('utf-8', errors='ignore')
                print>>output_fileobj, "%s\t%s" % (goldtags[t], feats_tabsep)
            print>>output_fileobj, ""

extract_features_for_file("train.txt", "train.feats")
#extract_features_for_file("dev.txt", "dev.feats")
extract_features_for_file("test_nolabels.txt", "test_nolabels.feats")

