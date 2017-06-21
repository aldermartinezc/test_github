#build a function for percentage and raw graph:
def graph_counts(dataframe, column, graphType, isPercentage, numShow):
    '''dataframe: input the dataframe you want to visualize
       column: input the specific column(s) you want to visualize
       graphType: type of graph(bar, pie, hist, area...)
       isPercentage: indicate raw value counts or percentage(boolean)
       numShow: number of categories to show, input 'all' for all categories '''
    col = dataframe.loc[:,str(column)]
    
    if isPercentage:
        value_count = col.value_counts()/sum(col.value_counts())
        plt_title = 'Percentage of ' + str(column)

    else:
        value_count = col.value_counts()
        plt_title = 'Raw Count of ' + str(column)
        
    if str(numShow) != 'all':
        value_count = value_count.head(numShow)

    '''below is the type of graph to choose'''        
    if str(graphType) == 'bar':
        value_count.plot.bar(title = plt_title)
        
    elif str(graphType) == 'pie':
        value_count.plot.pie()
        
    elif str(graphType) == 'hist':
        value_count.plot(kind = 'hist')
        
    elif str(graphType) == 'area':
        value_count.plot.area()
        
    plt.title(plt_title)