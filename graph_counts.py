#build a function for percentage and raw graph:
#ask for raw input
import matplotlib.pyplot as plt
def graph_counts(dataframe, column, hasSubset, graphType, isPercentage, numShow):
    '''dataframe: input the dataframe you want to visualize
       column: input the specific column(s) you want to visualize
       hasSubset: indicate if you want to have a subset of data
       graphType: type of graph(bar, pie, hist, area...)
       isPercentage: indicate raw value counts or percentage(boolean)
       numShow: number of categories to show, input 'all' for all categories '''
    
    cusColor = 'b'
    if len(set(dataframe.loc[:,'BEERTYPE'])) == 1:
        for each in set(dataframe.loc[:,'BEERTYPE']):
            if each == 'NonLowPoint':
                cusColor = 'blue'
            elif each == 'LowPoint':
                cusColor = 'orange'

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
    
    
    if isPercentage:
        value_count = col.value_counts()/sum(col.value_counts())
        plt_title = 'Percentage of Each by ' + str(column)

    else:
        value_count = col.value_counts()
        plt_title = 'Raw Count of Each by' + str(column)
        
    if str(numShow) != 'all':
        value_count = value_count.head(numShow)

    '''below is the type of graph to choose'''        
    if str(graphType) == 'bar':
        value_count.plot.bar(title = plt_title, color = cusColor)
        
    elif str(graphType) == 'pie':
        value_count.plot.pie(autopct='%1.1f%%')
        
    elif str(graphType) == 'hist':
        value_count.plot(kind = 'hist', color = cusColor)
        
    elif str(graphType) == 'area':
        value_count.plot.area(color = cusColor)
        
    plt.title(plt_title)