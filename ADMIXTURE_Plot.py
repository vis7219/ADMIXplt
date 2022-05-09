#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:50:04 2022

@author: vishak
"""

import getopt
import sys
import pandas as pd
import matplotlib.pyplot as plt

def parseopts(opts):
    params = {}

    for opt, arg in opts:

        if opt in ["-K"]:
            params['K'] = int(arg)

        elif opt in ["--input"]:
            params['input'] = arg

        elif opt in ["--output"]:
            params['output'] = arg

        elif opt in ["--pop"]:
            params['pop'] = arg
        
        elif opt in ["--output_type"]:
            params['output_type'] = arg

    return params

def read_metadata(meta_file):
    meta_file = pd.read_excel(meta_file, header = None)
    if len(meta_file.columns) == 3:
        meta_file.rename(columns = {0 : 'Sample_ID',
                               1 : 'Population',
                               2 : 'Sub-Population'},
                        inplace = True)
    else:
        meta_file.rename(columns = {0 : 'Sample_ID',
                                    1 : 'Population'},
                         inplace = True)
        meta_file['Sub-Population'] = '.'
    
    return(meta_file)

def refine_df(combined_df , df):
    
    # Remove rows having a '.' as Sub-Population
    main_subpop_df = combined_df[~combined_df['Sub-Population'].isin(['.'])]
    
    # DF to concatenate the Main DF with
    ordered_main_subpop_df = pd.DataFrame(columns = main_subpop_df.columns)
    
    # For loop to get all unique Sub-Population IDs. Using list(set(df['Sub-Population'])) was not
    # Preservin order. So this is solution
    subpop = []
    for subpop_id in main_subpop_df['Sub-Population'].tolist():
        if subpop_id in subpop:
            continue
        
        else:
            subpop.append(subpop_id)
    
    # Creating new DF with sorted Values
    for subpop_id in subpop:
        temp_df = main_subpop_df[main_subpop_df['Sub-Population'].isin([subpop_id])]

        scores = {}
        for i in list(df.columns):
            scores[int(i)] = sum(temp_df[i])
            
        keymax = max(zip(scores.values() , scores.keys()))[1]
        
        temp_df.sort_values(by = int(keymax) , inplace = True)
        
        ordered_main_subpop_df = pd.concat([ordered_main_subpop_df , temp_df])
        
    
    # Keep rows having '.' as Sub-Population
    dot_df = combined_df[combined_df['Sub-Population'].isin(['.'])]
    
    ordered_dot_df = pd.DataFrame(columns = dot_df.columns)
    
    # For loop to get all Population IDs
    pop = []
    for pop_id in dot_df['Population'].tolist():
        if pop_id in pop:
            continue
        
        else:
            pop.append(pop_id)
            
    # Creating new DF with sorted Values
    for pop_id in pop:
        temp_df = dot_df[dot_df['Population'].isin([pop_id])]
        
        scores = {}
        for i in list(df.columns):
            scores[int(i)] = sum(temp_df[i])
            
        keymax = max(zip(scores.values() , scores.keys()))[1]
        
        temp_df.sort_values(by = int(keymax) , inplace = True)
        
        ordered_dot_df = pd.concat([ordered_dot_df , temp_df])
        
    final_df = pd.concat([ordered_main_subpop_df , ordered_dot_df]).reset_index(drop = True)
    
    #final_df['index'] = final_df['index'].astype('int')
    
    return(final_df)

def pop_divider(combined_df):
    pop_grp = combined_df.groupby(('Population'))
    last_pop_sample_no = list(pop_grp.last()['index'])
    
    for i in last_pop_sample_no:
        ax.plot([i,i],
                [0,1],
                color = 'black',
                linewidth = 0.5)
    
    return(last_pop_sample_no)
        
def subpop_divider(combined_df , last_pop_sample_no):
    temp_df = combined_df[combined_df['Sub-Population'] != '.']
    subpop_grp = temp_df.groupby('Sub-Population')
    last_subpop_sample_no = list(subpop_grp.last()['index'])
    
    for i in last_subpop_sample_no:
        
        if i in last_pop_sample_no:
            continue
        
        else:
            ax.plot([i,i],
                    [0,1],
                    color = 'w',
                    linewidth = 0.5)

def pop_xticks(combined_df , count):
    if count == K-1:
        pop_grp = combined_df.groupby(('Population'))
        ax2 = ax.secondary_xaxis('bottom')
        ax2.spines['bottom'].set_visible(False)
        
        pop_list = list(set(combined_df['Population']))
        try:
            pop_list.remove('.')
        except ValueError:
            pass
        
        final_pop = []
        final_pos = []
        for i in pop_list:
            temp_df = pop_grp.get_group(i).reset_index(drop = True)
            # Getting the middle location of X-tick
            pop_pos = int(((temp_df['index'][len(temp_df) - 1] - temp_df['index'][0]) / 2) + temp_df['index'][0])
            
            final_pop.append(i)
            final_pos.append(pop_pos)
        
        ax2.set_xticks(final_pos , final_pop , fontsize = 15)
        
def subpop_xticks(combined_df , count):
    if count == 1:
        temp_df = combined_df[combined_df['Sub-Population'] != '.']
        subpop_grp = temp_df.groupby('Sub-Population')
        
        subpop_list = list(set(combined_df['Sub-Population']))
        subpop_list.remove('.')
        
        final_subpop = []
        final_pos = []
        for i in subpop_list:
            temp_df = subpop_grp.get_group(i).reset_index(drop = True)
            # Getting the middle location of X-tick
            subpop_pos = int((( temp_df['index'][len(temp_df)-1] - temp_df['index'][0]) / 2) + temp_df['index'][0])
            
            final_subpop.append(i)
            final_pos.append(subpop_pos)
        
        ax.set_xticks(final_pos, final_subpop, rotation = 30 , fontsize = 8)
        ax.xaxis.tick_top()

def howto_use():
    print("\n********************")
    print("This is how to use the script\n")
    print("[REQUIRED]\t -K=<int>")
    print("[REQUIRED]\t --input=<file> (The file prefix)\t")
    print("[REQUIRED]\t --output=<file> (Output file prefix)\t")
    print("[REQUIRED]\t --pop=<excel file> (MetaData of the samples)\t")
    print("[REQUIRED]\t --output_type=<str> (pdf / jpeg / png)\t")
    print("\t \t \t Column1 = Sample ID (Order should be the same as the one in admixture file")
    print("\t \t \t Column2 = Population")
    print("\t \t \t Column3 = Sub-Population (If not known for particular group, fill with '.') [NOT REQUIRED]\n")
    print("********************\n")
    


if __name__=="__main__":

    # parse command-line options
    argv = sys.argv[1:]
    smallflags = "K:"
    bigflags = ["input=", "output=", "pop=" , "output_type="]
    try:
        opts, args = getopt.getopt(argv, smallflags, bigflags)
        if not opts:
            howto_use()
            sys.exit(2)
    except getopt.GetoptError:
        print("Incorrect options passed")
        howto_use()
        sys.exit(2)

    params = parseopts(opts)
    
    # The main part of the script
    # Creating the Fig object
    fig = plt.figure(figsize=(22, 15))
    fig.subplots_adjust(wspace=0, hspace=0.14)
    
    K = params['K']
    
    count = 1 # Used for proper placement of the x-axis ticks
    # List of colors to be used
    colors = ['indianred' , 'saddlebrown' , 'darkorange' , 'khaki' , 'limegreen' , 'aqua' , 'cornflowerblue' ,
              'indigo' , 'purple' , 'gray']

    # Looping through K number of ADMIXTURE files
    for j in range(2,K+1):
        
        # Read the ADMIXTURE files
        df = pd.read_table(params['input'] + "." + str(j) +".Q" , header = None, sep = ' ')
        anc_no = len(df.columns)
        
        # Read the Sample METADATA File
        meta = read_metadata(params['pop'])
        
        # Merging the ADMIXTURE & METADATA dataframes
        combined_df = pd.concat([meta , df], axis = 1)
        
        combined_df = refine_df(combined_df , df)
        combined_df.reset_index(inplace = True)
        
        # Position of the ADMIXTURE Subplot
        graph_no = int(str(K) + '1' + str(j))
        
        # Create an Axes object
        ax = fig.add_subplot(graph_no)
        
        # Creating dividers between Populations
        last_pop_sample_no = pop_divider(combined_df)
        
        # Creating dividers between Sub-Populations
        subpop_divider(combined_df , last_pop_sample_no)
            
        # Beautifying the ADMIXTURE Graph
        ax.set_yticks([])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # Setting Sub-Population X-ticks
        subpop_xticks(combined_df , count)
        
        if count > 1:
            ax.set_xticks([])
        
        # Setting Population X-ticks
        pop_xticks(combined_df , count)
    
        # Looping through the Ancesteries columns
        bottom_df = combined_df[0] # Important for making STACKED Bar Plots
        for i in range(anc_no):
            if i == 0:
                ax.bar(combined_df['Sample_ID'],
                       combined_df[i],
                       width = 1.0,
                       color = colors[i])
                
            else:
                ax.bar(combined_df['Sample_ID'],
                       combined_df[i],
                       width = 1.0,
                       bottom = bottom_df,
                       color = colors[i])
                
                bottom_df = bottom_df + combined_df[i]
        
        count += 1
        
    fig.savefig(params['output'] + '.' + params['output_type'] , format = params['output_type'])

    

