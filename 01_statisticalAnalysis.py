#!/usr/bin/env python
# coding: utf-8

# In[1]:


#%reset -f
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.options.mode.use_inf_as_na = False
pd.option_context('mode.use_inf_as_na', True)

import statistics as stats

import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')

import math
from math import(e)

from sklearn.metrics import roc_curve, roc_auc_score, auc, precision_recall_curve

from scipy.interpolate import interp1d
from collections import defaultdict

from matplotlib_venn import venn3, venn3_circles


# In[2]:


listIndex = ['RWI', 'MNDWI', 'NDWI', 'AWEInsh', 'AWEIsh']
listIndexB = ['RWI', 'MNDWI', 'NDWI']
listCity = ['Sao Paulo', 'Curitiba', 'Florianopolis', 'Porto Alegre', 'Buenos Aires', 'Vina del Mar']


# In[3]:


import os
path = 'C:\\Users\\eduju\\OneDrive\\Documentos\\Doutorado\\artigos\\ÍndiceÁgua\\ArcGis\\exportFromGEE'
#os.listdir(path)
os.chdir(path)

df_SR = pd.read_csv('samplePointsCities_20240811_harmonized.csv', sep=',', decimal='.')
df_SR.replace([np.inf, -np.inf], np.nan, inplace=True)

def reclassify(value):
    if value == 'water':
        return 1
    if value != 'water':
        return 0

df_SR['surfClass'] = df_SR['surface'].apply(reclassify)

print('Sample points: ',len(df_SR))
print()
print(df_SR.head(1))


# ### Indices calc

# In[4]:


def powe(number):
    return number ** (1 / e)


# In[5]:


df_SR['B3Pow']     = df_SR['B3'].apply(powe)

df_SR['RWI'] = 0
df_SR['NDWI']    = (df_SR['B3'] - df_SR['B8'])         / (df_SR['B3'] + df_SR['B8'])
df_SR['MNDWI']   = (df_SR['B3'] - df_SR['B11'])        / (df_SR['B3'] + df_SR['B11'])
#df_SR['RWI']  = (df_SR['B3Pow'] - df_SR['B11'])     / (df_SR['B3Pow'] + df_SR['B11'])

 # AWEIsh =            blue     + 2.5 x    green    - 1.5 x (   Nir      +     Swir1   ) - 0.25 x   Swir2
df_SR['AWEIsh']   = df_SR['B2'] + 2.5 * df_SR['B3'] - 1.5 * (df_SR['B8'] + df_SR['B11']) - 0.25 * df_SR['B12']
 # AWEInsh        = 4 x (   green    -    Swir1    ) - (0.25 x      Nir    + 2.75 x    Swir2    )
df_SR['AWEInsh']  = 4 * (df_SR['B3'] - df_SR['B11']) - (0.25 * df_SR['B8'] + 2.75 * df_SR['B12'])
df_SR['code'] = range(1, len(df_SR) + 1)

print(df_SR.head(1))


# In[6]:


cityValue = {}

for city in listCity:
    cityValue[city] = df_SR[df_SR['city'] == city]['B3Pow'].median() / df_SR[df_SR['city'] == city]['B3'].median()

print(cityValue)

df_SR['divider'] = df_SR['city'].map(cityValue)
df_SR['B3powDiv']  = df_SR['B3Pow'] / df_SR['divider']

df_SR['RWI'] = (df_SR['B3powDiv'] - df_SR['B11']) / (df_SR['B3powDiv'] + df_SR['B11'])

print('____________________')

#df_SR.to_excel('df_SR.xlsx') 

unique_cities = df_SR['divider'].unique()
print(df_SR.head(1))


# #### range of index value

# In[7]:


print('RWI: from ',round(df_SR['RWI'].min(), 4),' to ',round(df_SR['RWI'].max(), 4))
print('MNDWI: from ',round(df_SR['MNDWI'].min(), 4),' to ',round(df_SR['MNDWI'].max(), 4))
print('NDWI: from ',round(df_SR['NDWI'].min(), 4),' to ',round(df_SR['NDWI'].max(), 4))
print('AWEIsh: from ',round(df_SR['AWEIsh'].min(), 4),' to ',round(df_SR['AWEIsh'].max(), 4))
print('AWEInsh: from ',round(df_SR['AWEInsh'].min(), 4),' to ',round(df_SR['AWEInsh'].max(), 4))


# ## Surface reflectance histogram

# In[8]:


water_SR = df_SR[df_SR['surfClass'] == 1]

B3_SR = water_SR['B3']
B3_SR_exp = water_SR['B3Pow']
B3_SR_expDiv = water_SR['B3powDiv']

plt.figure(figsize=(12,4))
plt.hist(B3_SR, bins=30, alpha=0.5, label='B3', color='blue')
plt.hist(B3_SR_exp, bins=30, alpha=0.5, label='B3 Pot', color='red')
plt.hist(B3_SR_expDiv, bins=30, alpha=0.5, label='B3 Pot Div', color='green')

plt.title('Green and green potentiation band histogram of water surface sample points')
plt.xlabel('Value')
plt.ylabel('Freq')
#plt.xlim([0, 0.5])
plt.legend()
#plt.savefig('Histogram_1_exp', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.show()


# ## Surface reflectance KDE

# In[9]:


def kdePlot(water, nonWater, index):
    plt.figure(figsize=(6,3))
    sns.kdeplot(nonWater,   label = 'non-water', color='red')#, bw_adjust=0.25, cut=0)
    sns.kdeplot(water,      label = 'water'    , color='blue')#  , bw_adjust=0.25, cut=0)

    plt.title(index, fontsize=18)
    plt.xlabel('Value', fontsize=14)
    plt.ylabel('Freq', fontsize=14)
    
    plt.xlim([-1.2, 1.2])
    plt.ylim([0, 9])
    plt.legend()
    plt.savefig('KDE_'+index, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.show()


# In[10]:


water = df_SR[df_SR['surfClass'] == 1]
nonWater = df_SR[df_SR['surfClass'] != 1]

for index in listIndex:
    waterIndex = water[index]
    nonWaterIndex = nonWater[index]
    kde = kdePlot(waterIndex, nonWaterIndex, index)


# ### Partial ROC curve

# In[11]:


surfClass = df_SR['surfClass'].tolist()
RWI       = df_SR['RWI'].tolist()
MNDWI     = df_SR['MNDWI'].tolist()
NDWI      = df_SR['NDWI'].tolist()
AWEInsh   = df_SR['AWEInsh'].tolist()
AWEIsh    = df_SR['AWEIsh'].tolist()


# In[12]:


plt.rcParams['figure.figsize'] = [2, 6]
plt.rcParams['figure.dpi'] = 72
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12  # Font size for x-axis ticks
plt.rcParams['ytick.labelsize'] = 12  # Font size for y-axis ticks

fprThreshold = 0.02
tprThreshold = 0.0

def partial_AUC(Y_true, Y_scores, index, munic):
    if len(Y_true) == 0 or len(Y_scores) == 0:
        raise ValueError("Y_true and Y_scores must not be empty")

    fpr, tpr, thresholds = roc_curve(Y_true, Y_scores)

    # Combinar valores de TPR para o mesmo FPR usando a média
    fpr_tpr_dict = defaultdict(list)
    for f, t in zip(fpr, tpr):
        fpr_tpr_dict[f].append(t)
    
    unique_fpr = np.array(list(fpr_tpr_dict.keys()))
    unique_tpr = np.array([np.mean(tprs) for tprs in fpr_tpr_dict.values()])

    # Adicionar ponto 0.02 se necessário
    if np.max(unique_fpr) < 0.02:
        unique_fpr = np.append(unique_fpr, 0.02)
        unique_tpr = np.append(unique_tpr, interp1d(unique_fpr, unique_tpr, fill_value="extrapolate")(0.02))

    fpr_interval = np.linspace(0, 0.02, num=1000)

    interpolator = interp1d(unique_fpr, unique_tpr, kind='linear', fill_value="extrapolate")
    tpr_interpolated = interpolator(fpr_interval)

    # Replace NaN values by 0
    tpr_interpolated = np.nan_to_num(tpr_interpolated)

    auc_partial = auc(fpr_interval, tpr_interpolated)
    auc_value = auc_partial

    plt.plot(unique_fpr, unique_tpr, label='Curva ROC Original')
    #plt.plot(fpr_interval, tpr_interpolated, label='Curva ROC Interpolada (FPR 0-0.02)', linestyle='--')
    #plt.fill_between(fpr_interval, tpr_interpolated, alpha=0.2, color='b')

    plt.xlabel(f"FPR <= {fprThreshold}", fontsize=16)
    plt.ylabel("TPR", fontsize=16)
    plt.xlim([0.0, fprThreshold])
    plt.xticks([0, fprThreshold/2, fprThreshold])
    plt.ylim([tprThreshold, 1])
    plt.yticks([tprThreshold, (1-tprThreshold)/4*1, (1-tprThreshold)/4*2, (1-tprThreshold)/4*3, 1])
    plt.title('pAUC: ' + str(round(auc_value, 5)), fontsize=18)
    #plt.legend(loc="lower right")
    #plt.savefig('Partial_' + munic + '_' + index, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.show()

    return auc_value


# #### Partial ROC curve for all the cities

# In[13]:


print()
munic = ''
index = ''
print('Partial Area Under Curve up to',fprThreshold,' of FPR - all the cities')

partial_auc_RWI     = partial_AUC(surfClass, RWI,     'RWI',     'allTheCities')
partial_auc_MNDWI   = partial_AUC(surfClass, MNDWI,   'MNDWI',   'allTheCities')
partial_auc_NDWI    = partial_AUC(surfClass, NDWI,    'NDWI',    'allTheCities')
partial_auc_AWEInsh = partial_AUC(surfClass, AWEInsh, 'AWEInsh', 'allTheCities')
partial_auc_AWEIsh  = partial_AUC(surfClass, AWEIsh,  'AWEIsh',  'allTheCities')
print()
print('partial auc_RWI:',     round(partial_auc_RWI,5))
print('partial auc_MNDWI:',   round(partial_auc_MNDWI,5))
print('partial auc_NDWI:',    round(partial_auc_NDWI,5))
print('partial auc_AWEInsh:', round(partial_auc_AWEInsh,5))
print('partial auc_AWEIsh:',  round(partial_auc_AWEIsh,5))


# #### Partial ROC curve for each city

# In[14]:


for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]
    
    surfClass_city = df_SR_city['surfClass'].tolist()
    RWI_city       = df_SR_city['RWI'].tolist()
    MNDWI_city     = df_SR_city['MNDWI'].tolist()
    NDWI_city      = df_SR_city['NDWI'].tolist()
    AWEInsh_city   = df_SR_city['AWEInsh'].tolist()
    AWEIsh_city    = df_SR_city['AWEIsh'].tolist()

    print()
    print('Partial Area Under Curve up to',fprThreshold,' for',munic)
    partial_auc_RWI_city     = partial_AUC(surfClass_city, RWI_city, 'RWI', munic)
    partial_auc_MNDWI_city   = partial_AUC(surfClass_city, MNDWI_city, 'MNDWI', munic)
    partial_auc_NDWI_city    = partial_AUC(surfClass_city, NDWI_city, 'NDWI', munic)
    partial_auc_AWEInsh_city = partial_AUC(surfClass_city, AWEInsh_city, 'AWEInsh', munic)
    partial_auc_AWEIsh_city  = partial_AUC(surfClass_city, AWEIsh_city, 'AWEIsh', munic)
    print()
    print(munic,'partial auc_RWI:',     round(partial_auc_RWI_city,5))
    print(munic,'partial auc_MNDWI:',   round(partial_auc_MNDWI_city,5))
    print(munic,'partial auc_NDWI:',    round(partial_auc_NDWI_city,5))
    print(munic,'partial auc_AWEInsh:', round(partial_auc_AWEInsh_city,5))
    print(munic,'partial auc_AWEIsh:',  round(partial_auc_AWEIsh_city,5))


# ### Sample point classification errors by threshold

# In[15]:


waterSample = df_SR[df_SR['surfClass'] == 1]
nonWaterSample = df_SR[df_SR['surfClass'] == 0]


# ##### True positives and true negatives for all the cities (FPR=0)

# In[16]:


for index in listIndex:
    threshold = max(nonWaterSample[index])
    print(index+' threshold: '+str(threshold))
    waterList    = df_SR[df_SR['surfClass'] == 1][index]
    nonWaterList = df_SR[df_SR['surfClass'] == 0][index]
    countWater = sum(1 for i in waterList if i > threshold)
    print('Correct '+index+' water classified points in all the cities',countWater,
          '(',round(countWater/len(waterList),5),' - ',round(countWater/len(waterList)*100,2),'%)')
    countNonWater = sum(1 for i in nonWaterList if i <= threshold)
    print('Correct '+index+' non-water classified points in all the cities',countNonWater, '(',round(countNonWater/len(nonWaterList)*100,2), '%)')
    if countWater == 0:
        print(index+' Misclassification points in all the cities:',round(((len(waterList)-countWater+len(nonWaterList)-countNonWater))/(len(waterList)+len(nonWaterList)),4))
        print(index+' Water misclassification points in all the cities (%):',round(100,2))
    elif countWater != 0:
        print(index+' Water misclassification points in all the cities (%):',round((((len(waterList)-countWater))/len(waterList)*100),2))
    print()


# ##### True positives by water class and water index (FPR=0)

# In[23]:


## Correct by water class
classWater = df_SR['classWat'].unique().tolist()
#print(classWater)
for index in listIndexB:
    print()
    threshold = max(nonWaterSample[index])
    print(index+' threshold: '+str(threshold))
    waterDF = df_SR[df_SR['surfClass'] == 1][[index, 'classWat']]
    for classWat2 in classWater:
        classWaterDF = waterDF[waterDF['classWat'] == classWat2]
        countWater = sum(1 for i in classWaterDF[index] if i > threshold)
        if len(classWaterDF) != 0:
            #print(classWat2)
            print(index+' - '+classWat2+' - points: ',countWater,' of ',len(classWaterDF), 
                  ' (',round(countWater/len(classWaterDF)*100,2),'%)')


# #### threshold for each city

# In[24]:


for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]
    print('______________________________________________')
    print(munic)

    for index in listIndex:
        df_SR_CityNonWater = df_SR_city[df_SR_city['surfClass'] == 0]
        threshold = max(df_SR_CityNonWater[index])
        print()
#        print(index+' threshold: '+str(round(threshold, 4)))
        print(index+' threshold: '+str(threshold))
        waterList = df_SR_city[df_SR_city['surfClass'] == 1][index]
        print(len(waterList))
        nonWaterList = df_SR_city[df_SR_city['surfClass'] == 0][index]
        countWater = sum(1 for i in waterList if i > threshold)
        print('Correct '+index+' water classified points in '+munic+': ',countWater,
          '(',round(countWater/len(waterList),5),' - ',round(countWater/len(waterList)*100,2),'%)')
        countNonWater = sum(1 for i in nonWaterList if i <= threshold)
        print('Correct '+index+' non-water classified points in '+munic+':',countNonWater, '(',round(countNonWater/len(nonWaterList)*100,1), '%)')
        if countWater == 0:
            print(index+' Misclassification points in '+munic+':',round(((len(waterList)-countWater+len(nonWaterList)-countNonWater))/(len(waterList)+len(nonWaterList)),4))
            print(index+'Water misclassification points in '+munic+'(%):',round(100,2))
        elif countWater != 0:
            print(index+' Water misclassification points in '+munic+'(%):',round((((len(waterList)-countWater))/len(waterList)*100),2))
        print()
        print()


# ##### True positives by water class, water index, and city (FPR=0)

# In[28]:


## Correct by water class
for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]
    print('______________________________________________')
    print(munic)
    watPoints = len(df_SR_city[df_SR_city['surfClass'] == 1])
    print(watPoints, 'water points')

    classWater = df_SR_city['classWat'].unique().tolist()
    #print(classWater)
    for index in listIndexB:
        print()
        waterDF = df_SR_city[df_SR_city['surfClass'] == 1][[index, 'classWat']]
        nonWaterList = df_SR_city[df_SR_city['surfClass'] == 0][[index, 'classWat']]
        threshold = max(nonWaterList[index])
        print(index+' threshold: '+str(threshold))
        for classWat2 in classWater:
            classWaterDF = waterDF[waterDF['classWat'] == classWat2]
            countWater = sum(1 for i in classWaterDF[index] if i > threshold)
            if len(classWaterDF) != 0:
                #print(classWat2)
                print(index+' - '+classWat2+' - points: ',countWater,' of ',len(classWaterDF), 
                      '(',round(countWater/len(classWaterDF)*100,2),'%)')


# #### Shadow and other elements influence

# In[29]:


nonWater_dictCity = {}
water_dictCity = {}

for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]
    dictName = f"{munic.replace(' ', ' ')}"

    nonWater_dictCity[dictName] = {}
    water_dictCity[dictName] = {}

    for index in listIndex:
        df_SR_CityNonWater = df_SR_city[df_SR_city['surfClass'] == 0]
        df_SR_CityWater    = df_SR_city[df_SR_city['surfClass'] == 1]
        nonWaterThreshold  = max(df_SR_CityNonWater[index])
        waterThreshold     = min(df_SR_CityWater[index])

        nonWater_dictCity[dictName][index] = {
            'threshold': nonWaterThreshold,
        }

        water_dictCity[dictName][index] = {
            'threshold': waterThreshold,
        }


# In[30]:


for munic in listCity:
    print('_________________________________')
    print(munic)
    df_SR_city = df_SR[df_SR['city'] == munic]

    for index in listIndex:
        df_SR_CityNonWater = df_SR_city[df_SR_city['surfClass'] == 0]
        df_SR_CityWater    = df_SR_city[df_SR_city['surfClass'] == 1]
#        print(df_SR_CityNonWater[index])

        nonWater_threshold = nonWater_dictCity[munic][index]['threshold']
        #print(nonWater_threshold)
        water_threshold    = water_dictCity[munic][index]['threshold']
        #print(water_threshold)
        #print('Non-water - '+munic+' - '+index+': '+str(nonWater_threshold))
        #print('Water     - '+munic+' - '+index+': '+str(water_threshold))
        nonWaterList = df_SR_CityNonWater[index].tolist()
#        print(nonWaterList)
        countList = sum(value <= nonWater_threshold and value > water_threshold for value in nonWaterList)
        
        print(index+': water minimum: '+str(round(water_threshold,3))+', non-water maximum: '+str(round(nonWater_threshold,3))+
              ', non-water points in interval: '+str(countList)+' ('+str(round(countList/len(df_SR_CityNonWater)*100,1))+'%)')


# #### Twenty comission points

# ##### All the cities

# In[31]:


for index in listIndex:
    indexValue = nonWaterSample[index].tolist()
    threshold = 0
    def get_tenth_highest_value(indexValue):
        sorted_list = sorted(indexValue, reverse=True)
        return sorted_list[19]
    
    threshold = get_tenth_highest_value(indexValue)
    
    print(index+' threshold: '+str(round(threshold, 16)))
    waterList    = df_SR[df_SR['surfClass'] == 1][index]
    nonWaterList = df_SR[df_SR['surfClass'] == 0][index]
    countWater = sum(1 for i in waterList if i > threshold)
    #print('Correct '+index+' water classified points in all the cities',countWater, '(',round(countWater/len(waterList)*100,2), '%)')
    countNonWater = sum(1 for i in nonWaterList if i <= threshold)
    #print('Correct '+index+' non-water classified points in all the cities',countNonWater, '(',round(countNonWater/len(nonWaterList)*100,2), '%)')
    #print(index+' Misclassification points in all the cities:',(len(waterList)-countWater+len(nonWaterList)-countNonWater))
    if countWater == 0:
        print(index+' Water misclassification points in all the cities(%):',round(100,2))
    elif countWater != 0:
        print(index+' Water misclassification points in all the cities (%):',round((((len(waterList)-countWater))/len(waterList)*100),2))
    print()


# ##### By city

# In[32]:


for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]
    print('______________________________________________')
    print(munic)

    for index in listIndex:
        df_SR_CityNonWater = df_SR_city[df_SR_city['surfClass'] == 0]
        def get_tenth_highest_value(indexValue):
            sorted_list = sorted(indexValue, reverse=True)
            return sorted_list[19]

        threshold = get_tenth_highest_value(df_SR_CityNonWater[index].tolist())

        print(index+' threshold: '+str(round(threshold, 16)))
        waterList = df_SR_city[df_SR_city['surfClass'] == 1][index]
        nonWaterList = df_SR_city[df_SR_city['surfClass'] == 0][index]
        countWater = sum(1 for i in waterList if i > threshold)
        #print('Correct '+index+' water classified points in '+munic+':',countWater, '(',round(countWater/len(waterList)*100,1), '%)')
        countNonWater = sum(1 for i in nonWaterList if i <= threshold)
        #print('Correct '+index+' non-water classified points in '+munic+':',countNonWater, '(',round(countNonWater/len(nonWaterList)*100,1), '%)')
        if countWater == 0:
            #print(index+' Misclassification points in '+munic+':',round(((len(waterList)-countWater+len(nonWaterList)-countNonWater))/(len(waterList)+len(nonWaterList)),4))
            print(index+' Water misclassification points in '+munic+'(%):',round(100,2))
        elif countWater != 0:
            print(index+' Water misclassification points in '+munic+'(%):',round((((len(waterList)-countWater))/len(waterList))*100,2))
        print()


# #### Fifty comission points

# ##### All the cities

# In[34]:


for index in listIndex:
    indexValue = nonWaterSample[index].tolist()
    threshold = 0
    def get_tenth_highest_value(indexValue):
        sorted_list = sorted(indexValue, reverse=True)
        return sorted_list[49]
    
    threshold = get_tenth_highest_value(indexValue)
    
    print(index+' threshold: '+str(round(threshold, 16)))
    waterList    = df_SR[df_SR['surfClass'] == 1][index]
    nonWaterList = df_SR[df_SR['surfClass'] == 0][index]
    countWater = sum(1 for i in waterList if i > threshold)
    #print('Correct '+index+' water classified points in all the cities',countWater, '(',round(countWater/len(waterList)*100,2), '%)')
    countNonWater = sum(1 for i in nonWaterList if i <= threshold)
    #print('Correct '+index+' non-water classified points in all the cities',countNonWater, '(',round(countNonWater/len(nonWaterList)*100,2), '%)')
    #print(index+' Misclassification points in all the cities:',(len(waterList)-countWater+len(nonWaterList)-countNonWater))
    if countWater == 0:
        print(index+' Water misclassification points in all the cities(%):',round(100,2))
    elif countWater != 0:
        print(index+' Water misclassification points in all the cities (%):',round((((len(waterList)-countWater))/len(waterList)*100),2))
    print()


# ##### By city

# In[36]:


for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]
    print('______________________________________________')
    print(munic)

    for index in listIndex:
        df_SR_CityNonWater = df_SR_city[df_SR_city['surfClass'] == 0]
        def get_tenth_highest_value(indexValue):
            sorted_list = sorted(indexValue, reverse=True)
            return sorted_list[99]

        threshold = get_tenth_highest_value(df_SR_CityNonWater[index].tolist())

        print(index+' threshold: '+str(round(threshold, 16)))
        waterList = df_SR_city[df_SR_city['surfClass'] == 1][index]
        nonWaterList = df_SR_city[df_SR_city['surfClass'] == 0][index]
        countWater = sum(1 for i in waterList if i > threshold)
        #print('Correct '+index+' water classified points in '+munic+':',countWater, '(',round(countWater/len(waterList)*100,1), '%)')
        countNonWater = sum(1 for i in nonWaterList if i <= threshold)
        #print('Correct '+index+' non-water classified points in '+munic+':',countNonWater, '(',round(countNonWater/len(nonWaterList)*100,1), '%)')
        if countWater == 0:
            #print(index+' Misclassification points in '+munic+':',round(((len(waterList)-countWater+len(nonWaterList)-countNonWater))/(len(waterList)+len(nonWaterList)),4))
            print(index+' Water misclassification points in '+munic+'(%):',round(100,2))
        elif countWater != 0:
            print(index+' Water misclassification points in '+munic+'(%):',round((((len(waterList)-countWater))/len(waterList))*100,2))
        print()
        print()


# ### Venn diagram

# In[38]:


listIndex2 = ['RWI', 'MNDWI', 'NDWI']

def printVenn3(onlyRWI, onlyMNDWI, onlyNDWI, RWI_MNDWI, RWI_NDWI, MNDWI_NDWI, 
               indexesIntersection, outside, munic):
    percentages = {
        '100': onlyRWI,                                    # RWIe
        '110': round(RWI_MNDWI - indexesIntersection,2),   # RWIe and MNDWI intersection
        '101': round(RWI_NDWI  - indexesIntersection,2),   # RWIe and NDWI intesection
        '011': round(MNDWI_NDWI  - indexesIntersection,2), # MNDWI and NDWI intersection
        '010': onlyMNDWI,                                  # only MNDWI
        '001': onlyNDWI,                                   # only NDWY
        '111': indexesIntersection                         # all the indexes intersection
    }

    print('Only RWI: ', onlyRWI) 
    print('Only MNDWI: ', onlyMNDWI) 
    print('Only NDWI: ', onlyNDWI)
    print('RWI ∩ MNDWI - NDWI :', round(RWI_MNDWI  - indexesIntersection,2))
    print('RWI ∩ NDWI - MNDWI :', round(RWI_NDWI   - indexesIntersection,2))
    print('MNDWI ∩ NDWI - RWI :', round(MNDWI_NDWI - indexesIntersection,2))
    print('RWI ∩ MNDWI ∩ NDWI :', indexesIntersection)
    print('outside: ', round(outside,2))
    # Calcular tamaños de grupos
    sizes = {}
    for key, value in percentages.items():
        sizes[key] = value
    
    # Calcular percentual fora dos conjuntos
    total_percent = 100
    for key, value in percentages.items():
        total_percent -= value
        
    sizes['outside'] = total_percent
    # Criar o diagrama de Venn
    plt.figure(figsize=(6, 6))
# normal quotas
    venn3(subsets=sizes, set_labels=('RWI', 'MNDWI', 'NDWI'), set_colors=("magenta", "yellow", "cyan"), alpha=0.6)
    venn3_circles(subsets=sizes, linewidth=0.5)
# end normal quotas
    
# small quotas
    
#    out = venn3(subsets=sizes, set_labels=('RWI', 'MNDWI', 'NDWI'), set_colors=("magenta", "yellow", "cyan"), alpha=0.6)
#    for text in out.set_labels:
#        text.set_fontsize(1)
#    for x in range(len(out.subset_labels)):
#        if out.subset_labels[x] is not None:
#            out.subset_labels[x].set_fontsize(1)    
            
# end small quotas
    
    plt.title(munic+' Venn diagram', fontsize=12)
    #plt.savefig('VennDiagram_'+munic+'.jpg', dpi=1200)
    plt.show()


# ##### Set theory for zero false positive for all the cities

# In[39]:


## corrigir ou utilizar o tudoJunto_d
munic = 'All the cities'

waterSample    = df_SR[df_SR['surfClass'] == 1]
nonWaterSample = df_SR[df_SR['surfClass'] == 0]

def threshold(index):
    return max(nonWaterSample[index])

RWI_T = threshold('RWI')
MNDWI_T = threshold('MNDWI')
NDWI_T = threshold('NDWI')

waterList = df_SR[df_SR['surfClass'] == 1]
countWater = round(sum(1 for x, y, z in zip(waterList['RWI'], waterList['MNDWI'], waterList['NDWI']) 
                       if x >= RWI_T or y >= MNDWI_T or z >= NDWI_T)/len(waterSample)*100,2)
outside = round(100-countWater, 2)

indexesIntersection = round(sum(1 for x, y, z in zip(waterList['RWI'], waterList['MNDWI'], waterList['NDWI']) 
                         if x >= RWI_T and y >= MNDWI_T and z >= NDWI_T)/len(waterSample)*100,2)
RWI_MNDWI  = round(sum(1 for x, y in zip(waterList['RWI'], waterList['MNDWI']) 
                        if x > RWI_T and y >= MNDWI_T)/len(waterSample)*100,2)
RWI_NDWI  = round(sum(1 for x, z in zip(waterList['RWI'], waterList['NDWI'])  
                        if x > RWI_T and z >= NDWI_T)/len(waterSample)*100,2)
MNDWI_NDWI  = round(sum(1 for y, z in zip(waterList['MNDWI'],    waterList['NDWI'])  
                        if y > MNDWI_T    and z >= NDWI_T)/len(waterSample)*100,2)

print('Thresholds')
print('RWI: ',RWI_T)
print('MNDWI: ',MNDWI_T)
print('NDWI: ', NDWI_T)
print()

RWI = round(sum(1 for i in waterList['RWI'] if i > RWI_T)/len(waterSample)*100,2)
print('RWI', RWI,'%')
MNDWI = round(sum(1 for i in waterList['MNDWI'] if i > MNDWI_T)/len(waterSample)*100,2)
print('MNDWI', MNDWI,'%')
NDWI = round(sum(1 for i in waterList['NDWI'] if i > NDWI_T)/len(waterSample)*100,2)
print('NDWI', NDWI,'%')

print()
print()
print('Correct classified', countWater,'%')                 
print('False negative rate:',outside,'%')
print()
onlyRWI   = round(RWI   - RWI_MNDWI - RWI_NDWI + indexesIntersection,2)
onlyMNDWI = round(MNDWI - RWI_MNDWI - MNDWI_NDWI + indexesIntersection,2)
onlyNDWI  = round(NDWI  - RWI_NDWI  - MNDWI_NDWI + indexesIntersection,2)

vennDiagram = printVenn3(onlyRWI, onlyMNDWI, onlyNDWI, RWI_MNDWI, RWI_NDWI, 
                         MNDWI_NDWI, indexesIntersection, outside, munic)


# ##### Set theory for zero false positive for each city

# In[40]:


for munic in listCity:
    df_SR_city = df_SR[df_SR['city'] == munic]

    waterSample    = df_SR_city[df_SR_city['surfClass'] == 1]
    nonWaterSample = df_SR_city[df_SR_city['surfClass'] == 0]
    
    def threshold(index):
        return max(nonWaterSample[index])
    
    RWI_T   = nonWater_dictCity[munic]['RWI']['threshold']
    MNDWI_T    = nonWater_dictCity[munic]['MNDWI']['threshold']
    NDWI_T     = nonWater_dictCity[munic]['NDWI']['threshold']
    
    waterList = df_SR_city[df_SR_city['surfClass'] == 1]
    countWater = round(sum(1 for x, y, z in zip(waterList['RWI'], waterList['MNDWI'], waterList['NDWI']) 
                           if x >= RWI_T or y >= MNDWI_T or z >= NDWI_T)/len(waterSample)*100,2)
    outside = round(100-countWater, 2)
    
    indexesIntersection = round(sum(1 for x, y, z in zip(waterList['RWI'], waterList['MNDWI'], waterList['NDWI']) 
                             if x >= RWI_T and y >= MNDWI_T and z >= NDWI_T)/len(waterSample)*100,2)
    RWI_MNDWI  = round(sum(1 for x, y in zip(waterList['RWI'], waterList['MNDWI']) 
                            if x > RWI_T and y >= MNDWI_T)/len(waterSample)*100,2)
    RWI_NDWI  = round(sum(1 for x, z in zip(waterList['RWI'], waterList['NDWI'])  
                            if x > RWI_T and z >= NDWI_T)/len(waterSample)*100,2)
    MNDWI_NDWI  = round(sum(1 for y, z in zip(waterList['MNDWI'],    waterList['NDWI'])  
                            if y > MNDWI_T    and z >= NDWI_T)/len(waterSample)*100,2)
    
    print(munic)
    print('Thresholds')
    print('RWI: ',RWI_T)
    print('MNDWI: ',MNDWI_T)
    print('NDWI: ', NDWI_T)
    print()
    
    RWI = round(sum(1 for i in waterList['RWI'] if i > RWI_T)/len(waterSample)*100,2)
    print('RWI', RWI,'%')
    MNDWI = round(sum(1 for i in waterList['MNDWI'] if i > MNDWI_T)/len(waterSample)*100,2)
    print('MNDWI', MNDWI,'%')
    NDWI = round(sum(1 for i in waterList['NDWI'] if i > NDWI_T)/len(waterSample)*100,2)
    print('NDWI', NDWI,'%')
    
    print()
    #print('Intersections')
    #print('All the index', indexesIntersection,'%')
    #print('RWI and MNDWI', RWI_MNDWI,'%')
    #print('RWI and NDWI', RWI_NDWI,'%')
    #print('MNDWI and NDWI', MNDWI_NDWI,'%')
    print()
    print('Correct classified', countWater,'%')                 
    print('False negative rate:',outside,'%')
    print()
    onlyRWI   = round(RWI   - RWI_MNDWI - RWI_NDWI + indexesIntersection,2)
    onlyMNDWI = round(MNDWI - RWI_MNDWI - MNDWI_NDWI + indexesIntersection,2)
    onlyNDWI  = round(NDWI  - RWI_NDWI  - MNDWI_NDWI + indexesIntersection,2)
    #print('only RWI', onlyRWI)
    #print('only MNDWI', onlyMNDWI)
    #print('only NDWI', onlyNDWI)
    
    vennDiagram = printVenn3(onlyRWI, onlyMNDWI, onlyNDWI, RWI_MNDWI, RWI_NDWI, 
                             MNDWI_NDWI, indexesIntersection, outside, munic)
    


# In[ ]:





# In[ ]:





# In[ ]:




