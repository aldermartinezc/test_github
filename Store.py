# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 01:13:27 2017

@author: abhishek.shetty
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import requests
from joblib import Parallel , delayed
from sklearn.metrics.pairwise import cosine_similarity , euclidean_distances
import csv


def _haversine(loc ,  R):
    
        '''
    
        Calculates haversine distance between two points
    
        
        Parameters
        ----------
        loc : a numpy array from the data consisting of two columns - LATITUDE AND LONGITUDE
    
    
        Returns
        ----------
        lon_dif : A matrix consisting of distances for each store against each store
    
        '''
    
        
        loc1 = loc
        loc2 = loc
        
        earth_radius = R

        locs_1 = np.deg2rad(loc1)
        locs_2 = np.deg2rad(loc2)

        lat_dif = (locs_1[:,0][:,None]/2 - locs_2[:,0]/2)
        lon_dif = (locs_1[:,1][:,None]/2 - locs_2[:,1]/2)

        np.sin(lat_dif, out=lat_dif)
        np.sin(lon_dif, out=lon_dif)

        np.power(lat_dif, 2, out=lat_dif)
        np.power(lon_dif, 2, out=lon_dif)

        lon_dif *= ( np.cos(locs_1[:,0])[:,None] * np.cos(locs_2[:,0]) )
        lon_dif += lat_dif

        np.arctan2(np.power(lon_dif,.5), np.power(1-lon_dif,.5), out = lon_dif)
        lon_dif *= ( 2 * earth_radius )
        
        #JN: Set this to None and test
        lon_dif[np.diag_indices_from(lon_dif)] = None

        return lon_dif
    
    

def _closest_store(data , dist_matrix , split_column , split_by , thres):

    
    '''
    Takes user input on what value the data must be split on to calculate closest store , 
    number of stores within a certain distance and minimum distance
    
    Parameters
    ----------
    data : Takes a dataframe as input. Store data
    
    dist_matrix : A matrix consisting of distances for each store against each store
    
    split_column: takes a column name as input in string format. 
    
    split_by: takes either a string element or a list as input.The input can either be 'ALL' or one or more values 
    of the column specified in split_column. When split_by is equal to 'ALL' , it calculates haversine distance for 
    a given store against all stores. When split_by is equal to one or more values of a given column , it calculates 
    haversine distance for all stores against only those stores whose split_column value is equivalent to that present 
    in split_by parameter
    
    thres : takes a integer as input. 
    
   
    Returns
    -------
    
    index: returns the index of the closest store for each store
    
    min_value : returns the distance of the closest store for each store
    
    count: returns the number of stores within a given distance threshold for each store
    
    
    '''
    #JN: Do split_column instead
    if split_column != 'ALL':
        
        split_ind = np.where(data[split_column] == split_by)[0]
        
        #JN: Change this condition to zero
        if len(split_ind) == 1:
            
            index_min , min_value , count = None , None , None
            
        else:
            
            split_dist_mat = dist_matrix[:,split_ind]
            #JN: After convertining diagonal of distance to Nan, changes the functions below to the nan equivalent
            #JN: Fixed closest store issue
            #index_min = np.nanargmin(split_dist_mat,axis = 1)
            min_index_split = np.nanargmin(split_dist_mat,axis = 1)
            index_min = [split_ind[min_index_split[i]]for i in range(min_index_split.shape[0])]
            min_value = np.nanmin(split_dist_mat,axis=1)
            count = np.nansum((split_dist_mat>0) & (split_dist_mat<thres),axis=1)

        
    else: 
        index_min = np.nanargmin(dist_matrix , axis = 1)
        min_value = np.nanmin(dist_matrix,axis=1)
        count = np.nansum((dist_matrix>0) & (dist_matrix<thres),axis=1)
        
        
    return index_min , min_value , count    
   
   


def _missing_store(data , dist_matrix , missing_col):
        
        
        '''
        Imputes demographics or distributor code values for those stores which have missing values in these columns 
        based on the demographics or distributor code of the nearest store. The nearest store is calculated by using 
        haversine distance        
        
        Parameters
        ----------

        data : Takes a dataframe as input. Store data

        dist_matrix : A matrix consisting of distances for each store against each store

        missing_col : Takes a string as input. The column name of the data whose missing values need to be imputed
        
        Returns
        -------
        
        miss_index : The index of the missing store
        
        index_min : The index of the nearest store for each store with missing demographics
                   
        '''
        
        miss_index = list(np.where(np.isnan(data[missing_col]))[0])
        include_index = list(np.where(data[missing_col].notnull() ==  True)[0])

        split_dist_mat = dist_matrix[np.ix_(miss_index , include_index)] 
        min_index_split = np.nanargmin(split_dist_mat,axis = 1)
        index_min = [include_index[min_index_split[i]] for i in range(min_index_split.shape[0])]
        
        return miss_index , index_min  


    
def _censusBlock(data,row , url):
        
    
        '''
        
        Uses FCC API to find the Census Block ID given a longitude and latitude. Adds a column to the data which contains the
        Census Block ID. If an ID is not found, then a None value is used
        
        Parameters
        ----------
        
        data : takes a dataframe as input. This dataset should latitude and longitude columns for
                the given set of stores
                
        row : takes an integer as input. This parameter will be used to iterate over rows of given data

        url : takes string as input. Contains the url from which data must be scraped


        Returns

        out : Returns the BlockId for each store         
        
        
        '''        
        
        
        #url = 'http://data.fcc.gov/api/block/find?format=json'
    
        lat_str = '&latitude='+str(data.iloc[row]['LATITUDE'])
        long_str = '&longitude='+str(data.iloc[row]['LONGITUDE'])
            
        try:
            r = requests.get(url+lat_str+long_str)
            out = r.json()['Block']['FIPS']
        except:
            out = None
            
        return out 
    
    

#JN: Look into joblib and following sklearn coding structure and style

class store(object):
    
    def __init__(self , data , storeCol = 'TDLINX_STORE_CD',earth_radius = 'miles' , distance_threshold = 0.5 , num_cores = -3):
        
     self.storeCol = storeCol
     self.data = data
     self.store = list(data[storeCol])
     self.num_cores = num_cores
    
     list_stores = [x for x in self.store if len(x) < 7]
     if len(list_stores) > 0:
         print(str(len(list_stores)) + ' stores had leading zeros dropped')
         print('Writing down these store_cd to Store_List.csv')
         with open('Store_List.csv','wb') as resultFile:
             wr = csv.writer(resultFile,dialect = 'excel')
             wr.writerows(list_stores)
          
         self.data[storeCol] = self.data[self.storeCol].map(lambda x : '0'*(7 - len(x)) + x if len(x) < 7 else x)
     if earth_radius == 'miles':
            self.R = 3958.75 # miles
     else:
            self.R = 6397 #kms
     self.threshold = distance_threshold
     self.latlon = np.array(data[['LATITUDE','LONGITUDE']])
     self.dist_matrix = _haversine(self.latlon , self.R)
      
     
        
    
    
    def closest_store(self , split_col_dict = {'PREMISE_TYPE_CD' : ['O'] , 'CHANNEL_DSC': ['CONVENIENCE STORE','GROCERY']}):
          
    
         '''
         Adds columns corresponding to minimum distance , count of stores within a user-specifed threshold and closest store code
         based on the split column-condition given by the user
         
         Parameters
         ----------
         
         split_col_dict: Takes a dictionary as input with column name as keys and column values as value. Closest store , minimum distance and 
         count of stores are calculated for each column present as keys in the dictionary and the data is split based on the value given for a 
         given key. If no such split is required , the user needs to specify 'TYPE' as key and 'ALL' as value.
         
         Returns
         -------
         
         adds minimum distance , count of stores and closest store code column for each key specified to the data
        
         '''
         #JN: remove loc2 because the haversine will calculate for all stores
         #JN: Move this to init and make it a self.variable
        
         keys = [k for k in list(split_col_dict.keys())]               
        
         for key in keys:

             vals = split_col_dict[key]      

             for val in vals:
                 
                 if key == 'ALL' and val != 'ALL':
                     
                     raise ValueError("Invalid value for key 'ALL' ... Use 'ALL' as value")
                                    
                
                 if val == 'ALL' and key != 'ALL':
                    
                     levels = list(self.data[key].unique())
                    
                     for lev in levels:
                     
                        index_min , min_value , count = _closest_store(data = self.data,dist_matrix = self.dist_matrix,
                                                                       split_column = key , 
                                                                       split_by = lev , thres = self.threshold)
                    
                        if index_min is None:
                            
                            self.data[key+"_"+lev+"_DIST"] = None
                            self.data[key+"_"+lev+"_NUM_STORES"] = None
                            self.data[key+"_"+lev+"_CLOSEST_STORE"] = None
    
                        
                        else:                                
                            self.data[key+"_"+lev+"_DIST"] = min_value
                            self.data[key+"_"+lev+"_NUM_STORES"] = count
                            self.data[key+"_"+lev+"_CLOSEST_STORE"] = self.storeCol[index_min].values
                        
                    
                 else:
                    
                    index_min , min_value , count = _closest_store(data = self.data,dist_matrix = self.dist_matrix,
                                                                   split_column = key , split_by = val , thres = self.threshold)
                    
                    if index_min is None:
                        
                        self.data[key+"_"+val+"_DIST"] = None
                        self.data[key+"_"+val+"_NUM_STORES"] = None
                        self.data[key+"_"+val+"_CLOSEST_STORE"] = None
                        
                    else:
                        
                        self.data[key+"_"+val+"_DIST"] = min_value
                        self.data[key+"_"+val+"_NUM_STORES"] = count
                        #JN: Removed line below, causing issues with chagnes to fix when leading zeros are dropped in init
                        #self.data[key+"_"+val+"_CLOSEST_STORE"] = self.storeCol[index_min].values
                        self.data[key+"_"+val+"_CLOSEST_STORE"] = self.data[self.storeCol][index_min].values
                        
                
        
            
      
    def missing_value_imputation(self , missing_column = ['BLACK_POP_PCT','WHITE_POP_PCT']):
    
        '''
        
        Imputes demographics or distributor code values for those stores which have missing values in these columns 
        based on the demographics or distributor code of the nearest store. The nearest store is calculated by using 
        haversine distance        
    
        Parameters
        ----------
    
        missing_column : Takes a list an input. A list of column names for which missing values needs to be imputed based on closest store
    
        Returns
        -------
    
        For the columns in missing_column , if there any missing values , imputes them from the closest store
        

        '''    
    
        for col in missing_column:
        
            miss_index , index_min = _missing_store(data = self.data , dist_matrix = self.dist_matrix , missing_col = col)
            
            self.data.ix[miss_index , col] = self.data.ix[index_min, col].values
        
        
    def binarize(self , column):
        
        '''
        Creates dummy columns of 1-0 for each level in a specified columns
    
        Parameters
        ----------
        column: takes a string or a list of string as input. The input must be a column name present in the data
    
        Returns
        ----------
        for each level in the specified column , creates a new column containing 1-0's and adds them back to the data
    
    
        '''
        self.data = pd.concat([self.data ,pd.get_dummies(self.data[column] , prefix = ['B_'+c for c in column])] , axis = 1)
        
    
    def normalize(self , columns , n_type = 'Minmax' , feature_range = (0,1) , threshold = 0.5):
    
        '''
        Transforms features by scaling a given feature to a given range
        Does minmax normalization by default. If minmax is set as False , then does a z-score normalization
    
        Parameters
        ----------
    
        column: takes a string or a list of string as input. The input must be a column name present in the data
    
        n_type: takes a string as input. By default , the value for this parameter is 'Minmax'
    
        feature_range: tuple (min, max), default=(0, 1) . Desired range of transformed data.
    
        threshold : takes a number as input ; applies only when n_type = Binarize
    
        **update
        --------
    
        normalize function can now be used to do log , square root , inverse square root , binarize columns
            
        Returns
        -------
        If n_type is Minmax , does a minmax normalization on the specified column based on the feature_range. 
    
        If n_type is Z-score,then does a z-score normalization (subtract by mean and divide by sd) 
        on the specified column
    
        If n_type is Log , does a log transformation on the specified column
    
        If n_type is Sqr-Root , does a square root transformation on the specified column
    
        If n_type is Inv-Sqr-Root , does a inverse square root transformation on the specified column
    
        If n_type is Binarize , values greater than the threshold map to 1, while values less than
        or equal to the threshold map to 0
    
    
        Creates new normalized columns and then adds them back to the data
    
        TODO
        Consider in the future to pass dictionary with normalization technique as key and parameters as the value (e.g {'Minmax':[0,1]})
    

    
        '''             
        
        
        for col in columns:
            
            if n_type == 'Minmax':
        
                x_std = (self.data.loc[:,col] - np.nanmin(self.data.loc[:,col])) / (np.nanmax(self.data.loc[:,col]) - np.nanmin(self.data.loc[:,col]))
            
                self.data['N_'+col+'_M'] = x_std * (feature_range[1] - feature_range[0]) + feature_range[0]

            elif n_type == 'Z-score':
            
                self.data['N_'+col+'_Z'] = (self.data.loc[:,col] - np.mean(self.data.loc[:,col])) / np.std(self.data.loc[:,col])    
                
            elif n_type == 'Log':
                
               
                if sum(self.data.loc[:,col] <=0 ) > 0:
                    
                    #find minimum value
                    m = min(i for i in self.data.loc[:,col] if i > 0)
                    log_df = np.array(self.data.loc[:,col].values)
                    log_df[log_df < m] = m                        
                    self.data['N_'+col+'_L'] = np.log(log_df)
                    
                else:
                    self.data['N_'+col+'_L'] = np.log(self.data.loc[:,col])
                    
                    
            elif n_type == 'Sqr-Root':
                
                self.data['N_'+col+'_SR'] = np.sqrt(self.data.loc[:,col])
                
            elif n_type == 'Inv-Sqr-Root':
                
                self.data['N_'+col+'_ISR'] = self.data.loc[:,col].apply(lambda x : x ** -1/2) 
                
            elif n_type == 'Binarize':
                
                cond = self.data.loc[:,col] >= threshold
                
                self.data['N_'+col+'_B'] = 0
                self.data.loc[cond , 'N_'+col+'_B'] = 1
               

    
    
    def similarity(self , method , columns , exclude_nulls = False):

        '''
        Takes three values as input for method - cosine , euclidean and pearson correlation
        for a matrix of m x n dimensions , returns a matrix of m x m dimensions
        
        Also need to specify a list of columns on which these metrics will be calculated
        
        Treat Nan , infinity values before using this method
        
        Parameters
        ----------
        method: takes a string as input. This input can either be 'cosine' or 'euclidean' or 'pearson'
        
        columns: takes a string or list of strings as input. Must be column names present in the data
        
        exclude_nulls : takes a boolean value as input. If True, then all the null valued rows are removed before creating the
        similarity matrix. If False ,  then all the nulls values are converted to zero and then the similarity matrix is created
                    
    
        Returns
        ----------
    
        for a matrix of m x n dimensions , returns a matrix of m x m dimensions which contains similarities based on the 
        method specified
    
        TODO
        ----------
    
        JN: Need to check if we'll run into performance issues with this. May need to convert to a sparse matrix


    
        ''' 
    
        #JN: We do not want to drop the entire column.
        if exclude_nulls:   
            
            #data_for_sim = self.data[columns].dropna()
            raise Exception("TODO: NEED TO FIX")
            
        else:
            
            data_for_sim = self.data[columns].fillna(0) 
            
    
        if method == 'cosine':
            return cosine_similarity(data_for_sim)
            
        if method == 'euclidean':
            return 1 / (1 + euclidean_distances(data_for_sim))
            
        if method == 'pearson':
            return np.array(data_for_sim.T.corr(method = 'pearson')  ) 
        
        
        self.sim_matrix = data_for_sim
        
        
    def censusBlock(self , url):
       
        
        '''
        
        Calls _censusBlock function and parallelizes it
        
        
        Parameters
        ---------
        
        
        url : takes string as input. Contains the url from which data must be scraped
        
        
        Returns
        -------
        
        censusBlock_df : A list of censusBlock Id's for each store. This is added to the data
        
        
        '''        
        
            
        censusBlock_df = Parallel(n_jobs = self.num_cores)(delayed(_censusBlock)(
                              data = self.data,
                              row = row,
                              url = url)
                              for row in range(self.data.shape[0])
                              )            

        self.data['CENSUS_BLOCK_ID'] = censusBlock_df   
        