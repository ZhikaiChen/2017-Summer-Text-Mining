
# coding: utf-8

# In[1]:

import TextAnalysisLibrary
import glob,os
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


# In[ ]:

corpus_path='/Users/chenzhikai/AnacondaProjects/2017 Summer Research/novels/*txt'
austen_path="/Users/chenzhikai/AnacondaProjects/2017 Summer Research/stylometric/Austen/*.txt"
alcott_path="/Users/chenzhikai/AnacondaProjects/2017 Summer Research/stylometric/Alcott/*.txt"


# In[ ]:

filenames=glob.glob(corpus_path)
corpus=[TextAnalysisLibrary.tokenize(open(f,'r').read()) for f in filenames]


# In[ ]:

tf_dict=TextAnalysisLibrary.tf_dict(corpus_path)
features,counts=TextAnalysisLibrary.feature_extraction(tf_dict,100)


# In[ ]:

# extract samples by chunking Austen' & Alcott' texts
austen_alcott=glob.glob(austen_path) + glob.glob(alcott_path)
samples=[]
for f in austen_alcott:
    text=TextAnalysisLibrary.tokenize(open(f,'r').read())
    text_chunks=TextAnalysisLibrary.chunk(text,5000)
    samples.extend(text_chunks)


# In[ ]:

#count fq of features in a sample
X=[]
for chunk in samples:
    vector=MyLibrary.vectorize(features, chunk)
    X.append(vector)


# In[ ]:

# clustering
cluster=KMeans(n_clusters=2).fit(X)
cluster.labels_


# In[ ]:

#Visualization using PCA
pca=PCA(n_components=2).fit(X)
x,y=zip(*pca.transform(X))

colors=['r' if boo else 'b' for boo in cluster.labels_]

plt.figure(figsize=(15,10))
plt.scatter(x,y,s=100,alpha=0.5,c=colors)
plt.scatter(x,y)
plt.show()

