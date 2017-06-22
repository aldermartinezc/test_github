import matplotlib.pyplot as plt
def graph_counts(state, dataframe, column, hasSubset, subset_Col, subset_Value, graphType, isPercentage, numShow, savePDF, savePNG):
    
    '''
        Visualize particular columns in dataframe. 
    
    
       Parameters:
       ----------
           
           state: takes a string. The name of the state
       
           dataframe: takes a dataframe as input
           
           column: takes a column of the dataframe as input
           
           hasSubset: takes a boolean as input. Whether to take a subset of the dataframe
           
           subsetCol: takes both a string and 'None'. String for the column name; 'None' if hasSubset is False
           
           subsetValue: takes string, integer and 'None'. String and integer for the subset criteria; 'None' if hasSubset is False
           
           graphType: takes a string as input.Type of graph(bar, pie, hist, area...)
           
           isPercentage: takes a boolean as input. Show the graph in raw counts or percentage
           
           numShow: takes both integer and the string 'all' as input. The number of categories to show; 'all' for all categories
           
           savePDF: takes boolean as input. Whether to save image as a pdf
           
           savePNG: takes boolean as input. Whether to save image as a PNG
      
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

    graph_subset_name = ''
    #subset 
    if hasSubset is False:
        col = dataframe.loc[:,str(column)]
    else: 
        subsetCol = str(subset_Col) 
        subsetValue = str(subset_Value)
        
        col = dataframe.loc[dataframe[subsetCol]==subsetValue, str(column)]
        
        if subsetValue == 'NonLowPoint':
            cusColor = 'blue'
        elif subsetValue == 'LowPoint':
            cusColor = 'orange'    
        
        graph_subset_name = 'with subset '+str(subset_Col) +'where value is '+str(subset_Value)
    
    #show percentage or raw value
    if isPercentage:
        value_count = col.value_counts()/sum(col.value_counts())
        plt_title = 'Percentage of Each by ' + str(column)

    else:
        value_count = col.value_counts()
        plt_title = 'Raw Count of Each by' + str(column)
    
    #number of categories
    if str(numShow) != 'all':
        value_count = value_count.head(numShow)

 
    #type of graph  

    if str(graphType) == 'bar':
        ax = value_count.plot.bar(title = plt_title, color = cusColor)
 
    elif str(graphType) == 'pie':
        ax = value_count.plot.pie(autopct='%1.1f%%')
        
    elif str(graphType) == 'hist':
        ax = value_count.plot(kind = 'hist', color = cusColor)
        
    elif str(graphType) == 'area':
        ax = value_count.plot.area(color = cusColor)
    plt.title(plt_title)
    
    #save as PDF
    fig = ax.get_figure()  
    
    fig_name = str(graphType) + ' plot of '+ str(plt_title) + graph_subset_name + ' -'+str(state)
    fig_name_pdf = fig_name+'.pdf'
    fig_name_png = fig_name+'.png'
    
    if savePDF and savePNG:
        fig.savefig(fig_name_pdf)
        fig.savefig(fig_name_png)
    else:
        if savePNG:
            fig.savefig(fig_name_png)
            
        elif savePDF:
            fig.savefig(fig_name_pdf)
