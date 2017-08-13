
# coding: utf-8

# In[10]:

import glob,os,re,math
import matplotlib.pyplot as plt
import numpy as np
get_ipython().magic(u'matplotlib inline')


# In[2]:

def tokenize(text):
    l=text.split()
    punctuations=",.?!\"\':;-"
    l=[s.strip(punctuations).lower() for s in l]
    return l


# In[3]:

def chunk(text, length, overlap=False):
    if overlap==False:
        overlap=length
    starts=range(0,len(text),overlap)
    ans=[text[i:i+n] for i in starts]
    return ans


# In[4]:

def text_freq(path):
    #Create a corpus
    filenames=glob.glob(path)
    corpus=[tokenize(open(f,'r').read()) for f in filenames]
    #Build a dictionary of tokens
    tf={}
    for text in corpus:
        for token in text:
            if token in tf:
                tf[token]+=1
            else:
                tf[token]=1
    return tf


# In[5]:

def doc_freq(path):
    
    ## build corpus
    filenames=glob.glob(path)
    corpus=[tokenize(open(f,'r').read()) for f in filenames]
    
    ## create dictionary with document frequency: unique word in a text
    doc_freq={}
    for text in corpus:
        text=set(text) 
        for wd in text:
            if wd in doc_freq.keys():
                doc_freq[wd]+=1
            else:
                doc_freq[wd]=1
                    
    return doc_freq


# In[ ]:

def vectorize(features, text):
    ##text: A list of string
    ## feature: list
    f_counts = []
    for f in features:
        count=len([wd for wd in text if wd==f])
        f_counts.append(count/float(len(text)))
    return f_counts
        


# In[9]:

def tf_idf(filepath,corpuspath):
    #tf_idf score dict
        tf_dict =tf(filepath)
        df_dict = df(corpuspath)
        n=0
        for i in glob.glob(corpuspath):
            n+=1
        score={}
        for token in tf_dict.keys():
            score[token]=round(tf_dict[token]
                                 *math.log(float(n)/df_dict[token]))
        return tf_dict


# In[12]:

def distance(c1,c2):
    ans=0
    for i, v in enumerate(c1):
        ans+=(v-c2[i])**2
        ans=ans**0.5
    return ans


# In[13]:

def type_token(text):
    ans=len(set(text))/(float)(len(text))
    return ans


# In[ ]:

def count_words(path,top_words):
    corpus = []
    for f in glob.glob(path):
        text = open(f, 'r').read()
        text = tokenize(text)
        corpus.append(text)
    print corpus[:2][:10]
    tokens = {}
    for t in corpus:
        for word in t:
            if word in tokens: 
                tokens[word] +=1
            else:
                tokens[word]=1
    tupple_tokens =tokens.items()
    sort(tupple_tokens, lambda x: [1])[:top_words]
    


# In[15]:

def feature_extraction(tf_dict,topn):
    #use top n words of a corpus as feature
    top_n= sorted(tf_dict.item(),
                  reverse=True,key=lambda x:x[1])[:topn]
    features,counts=zip(*top_n)
    return features,counts

