import matplotlib.pyplot as plt
def graph_counts(dataframe, column, hasSubset, graphType, isPercentage, numShow):
    
    '''
        Visualize particular columns in dataframe. 
    
    
       Parameters:
       ----------
       
           dataframe: takes a dataframe as input
           
           column: takes a column of the dataframe as input
           
           hasSubset: takes a boolean as input. Whether to take a subset of the dataframe
           
           graphType: takes a string as input.Type of graph(bar, pie, hist, area...)
           
           isPercentage: takes a boolean as input. Show the graph in raw counts or percentage
           
           numShow: takes both integer and the string 'all' as input. The number of categories to show; 'all' for all categories
      
      Return:
      -------
      
          None
          
      '''
    
    #assigin color
    cusColor = 'b'
    if len(set(dataframe.loc[:,'BEERTYPE'])) == 1:
        for each in set(dataframe.loc[:,'BEERTYPE']):
            if each == 'NonLowPoint':
                cusColor = 'blue'
            elif each == 'LowPoint':
                cusColor = 'orange'
               
    else:
        pass

    if hasSubset is False:
        col = dataframe.loc[:,str(column)]
    else:
        print('please input the subset Column')
        subsetCol = input()
        print('please input the subset Value')
        subsetValue = input()
        col = dataframe.loc[dataframe[str(subsetCol)]==str(subsetValue), str(column)]
        
        if subsetValue == 'NonLowPoint':
            cusColor = 'blue'
        elif subsetValue == 'LowPoint':
            cusColor = 'orange'    
    
    #show percentage or raw value
    if isPercentage:
        value_count = col.value_counts()/sum(col.value_counts())
        plt_title = 'Percentage of Each by ' + str(column)

    else:
        value_count = col.value_counts()
        plt_title = 'Raw Count of Each by' + str(column)
        
    if str(numShow) != 'all':
        value_count = value_count.head(numShow)

        
    #type of graph   
    if str(graphType) == 'bar':
        value_count.plot.bar(title = plt_title, color = cusColor)
        
    elif str(graphType) == 'pie':
        value_count.plot.pie(autopct='%1.1f%%')
        
    elif str(graphType) == 'hist':
        value_count.plot(kind = 'hist', color = cusColor)
        
    elif str(graphType) == 'area':
        value_count.plot.area(color = cusColor)
        
    plt.title(plt_title)