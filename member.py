import pandas as pd
import numpy as np

df = pd.read_csv('.use_baby.csv',index_col=['updated'])
df.index = pd.to_datetime(df.index)

df = df[(df['days'] < 1800) & (df['days'] > 0)]
df = df[(df['sex'] == 0) | (df['sex'] == 1)]
df = df[(df['temperature'] >= 20) & (df['temperature'] <= 45)]

from sklearn.cluster import AgglomerativeClustering

cluster = AgglomerativeClustering(n_clusters=2, affinity='euclidean', linkage='ward')
pred = cluster.fit_predict(df)

df['cluster'] = pred

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

X = df

# 데이터 scatterplot
ax.scatter(  X.iloc[:,0]
           , X.iloc[:,1]
           , X.iloc[:,2]
           , c = X.clust
           , s = 10
           , cmap = "rainbow"
           , alpha = 1
          )

# 시각화 각도 설정
ax.view_init(elev=30, azim=90)

# 축 레이블 추가
ax.set_xlabel('days')
ax.set_ylabel('sex')
ax.set_zlabel('temperature')

plt.savefig('img.png')

