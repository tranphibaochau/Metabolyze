import warnings
import pandas as pd
import itertools
import scipy
import scipy.stats
import numpy as np
from functools import reduce
import re
import numpy 
import subprocess as sp
import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

#warnings.filterwarnings("ignore")

#import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument('-rn', "--rowname", nargs='?', help="Rownames for heatmaps // True or False", const=1, type=str, default='True')
# args = parser.parse_args()


class Analysis:

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    def __init__(self, data, sample_sheet, blank_threshold_value, method):
        
        self.data = 'inputs/'+data
        self.sample_sheet = 'inputs/'+sample_sheet
        self.blank_threshold_value = blank_threshold_value
        self.method = method

    def input_check(self):
        id_dict = self.get_ids('ID')
        print("Number of Samples:", len(id_dict))
        
        for x, y in id_dict.items():
            print(x, ':', y)
        sample_id = self.get_ids('All')
        if len(sample_id) != len(set(sample_id)):
            raise Exception('Error: Check unique Sample IDs in: Groups.csv for error')
        
        skeleton_input = pd.read_table(self.data)
        # metabolite_list = skeleton_input['Metabolite']
        # if len(metabolite_list) != len(set(metabolite_list)):
#             raise Exception('Error: Check Metabolite column for duplicates in : Skeleton_input.tsv')
        
        if self.get_matrix(self.get_ids('All')).isnull().values.any():
            raise Exception('Error: Check for Missing Values in Sample intensities: Skeleton_input.csv')
        
        if len(sample_id) != len(self.get_matrix(self.get_ids('All')).columns):
            raise Exception('Error: Check if Number of Samples in Groups.csv matches Skeleton_input.tsv')
    
        skeleton = self.get_ids('All')
        groups = pd.read_csv(self.sample_sheet)['File'].tolist()
        
        if set(groups).issubset(skeleton) is False:
            print(groups)
            print(skeleton)
            raise Exception('sample_sheet: Sample Names Incorrectly Match Skeleton File Names')
    

        
    def dir_create(self):

        groups = pd.read_csv(self.sample_sheet)
        results_folder = ""

        if self.method == 'flux':
            results_folder = 'Flux-DME-results-'+str(len(self.get_ids('True'))) + '-Samples/'
        if self.method == 'sum':
            results_folder = 'Sum-DME-results-'+str(len(self.get_ids('True'))) + '-Samples/'
        if self.method == 'median':
            results_folder = 'Median-DME-results-'+str(len(self.get_ids('True'))) + '-Samples/'
        if self.method == 'default':
            results_folder = 'DME-results-'+str(len(self.get_ids('True'))) + '-Samples/'

        sub_directories = [results_folder + subdir for subdir in ['Volcano', 'Heatmap', 'Tables', 'PCA', 'Inputs', 'Pathway', 'Impacts']]
        sub_directories.append(results_folder)
        
        for subdir in sub_directories:
            if not os.path.exists(subdir):
                os.makedirs(subdir)

    def get_groups(self):
    # Get corresponding IDs for each group in Groups.csv

        project = pd.read_csv('inputs/Groups.tsv', sep='\t')
        grouped_samples = {}

        for condition in (project.Group.unique()):
            if condition != 'Blank':
                test = [x.split('.')[0] for x in project.loc[project['Group'] == condition, 'File'].tolist()]
                grouped_samples[condition] = test
        return grouped_samples

    def get_ids(self, selection):
        
        # Return sample IDS for all samples including blanks
        if selection == 'All':
            skeleton = pd.read_table(self.data)
            
            spike_cols = [col for col in skeleton.columns if 'S' in col]
            spike_cols.pop(0)
            return list(spike_cols)
        
        # Get all sequence IDS (xml ids) from Groups.csv
        if selection == 'True':
            project = pd.read_table('inputs/Groups.tsv', sep='\t')
            project = project.loc[project['Group'] != 'Blank']
            all_samples = [x.split('.')[0] for x in project['File'].tolist()]
            return all_samples
        
        if selection == 'Sample':
            project = pd.read_csv('inputs/Groups.tsv', sep='\t')
            project = project.loc[project['Group'] != 'Blank']
            all_samples = [x.split('.')[0] for x in project['id'].tolist()]
            return all_samples
        
        # Get all blank IDS from skeleton output matrix
        if selection == 'Blank':
            project = pd.read_csv('inputs/Groups.tsv', sep='\t')
            project = project.loc[project['Group'] == 'Blank']
            all_samples = [x.split('.')[0] for x in project['File'].tolist()]
            return list(all_samples)
        if selection == 'ID':
            project = pd.read_csv('inputs/Groups.tsv',sep='\t')
            grouped_samples = {}
            
            for condition in (project.id.unique()):

                test = [x.split('.')[0] for x in project.loc[project['id'] == condition, 'File'].tolist()]
                test = ''.join(test)
                grouped_samples[test] = condition
            return grouped_samples
    
    def sequence2id(self, result):
        
        ids = self.get_ids('ID')
    
        for x, y in ids.items():
            result.rename(columns={x: y}, inplace=True)
            # Returns matrix based on inputted IDS
        return result
    
    def get_matrix(self,ids):
        
        skeleton_outbut_hybrid = pd.read_table(self.data)
        skeleton_outbut_hybrid = skeleton_outbut_hybrid.set_index('Metabolite')
        
        matrix = (skeleton_outbut_hybrid[skeleton_outbut_hybrid.columns.intersection(ids)])
        return matrix
    
    def get_imputed_full_matrix(self, full_matrix, param):
        
        blank_matrix = pd.DataFrame(self.get_matrix(self.get_ids('Blank')))
        
        blank_threshold = pd.DataFrame(blank_matrix.mean(axis=1)*3)+ self.blank_threshold_value
        blank_threshold['Metabolite'] = blank_threshold.index
        blank_threshold.columns = ['blank_threshold','Metabolite']
        test_dictionary = {}
        #print(full_matrix)
        for index, row in full_matrix.iterrows():
            test_list = []
    #print(index)
            for val in row:
                blankthresh = blank_threshold.loc[index, ['blank_threshold']][0]
                if val < blankthresh:
                    if param == 'detected':
                        test_list.append(blankthresh)
                    if param == 'corrected':
                        test_list.append(0)
                else:
                    test_list.append(val)
            test_dictionary[index] = test_list

        df_test = (pd.DataFrame.from_dict(test_dictionary))
        final = df_test.transpose()
        final.columns = list(full_matrix)
        return final

    def compile_tests(self, results_folder, full_matrix):

        test_compile = {}

        blank_matrix = pd.DataFrame(self.get_matrix(self.get_ids('Blank')))
        blank_threshold = pd.DataFrame(blank_matrix.mean(axis=1)*3)+self.blank_threshold_value
        blank_threshold['Metabolite'] = blank_threshold.index
        blank_threshold.columns = ['blank_threshold', 'Metabolite']
            
        for file in os.listdir(results_folder):
            if file.endswith('corrected.csv'):
                #path = os.path.abspath(results_folder+file)
                test = pd.read_csv(results_folder+file,keep_default_na=True)
                test = test.fillna('NA')
                test.index = test['Metabolite']
                columns = ['ttest_pval', 'Log2FoldChange','impact_score']
                changed_names = [file +'_'+ x for x in columns]
                changed_names = [x.replace('.corrected.csv','') for x in changed_names]
                
                df1 = pd.DataFrame(test, columns=columns)
                df1.columns  = changed_names
                test_compile[file] = df1
        
        merged_df = pd.concat(test_compile, axis =1)
        merged_df.columns = [col[1] for col in merged_df.columns]
        
        
        test_dictionary = {}
        for index, row in full_matrix.iterrows():
            test_list = []
        #print(index)
            for val in row:
                blankthresh = blank_threshold.loc[index, ['blank_threshold']][0]
                if val < blankthresh:
                    test_list.append(blankthresh)
                else:
                    test_list.append(val)
            test_dictionary[index] = test_list
            
        df_test = (pd.DataFrame.from_dict(test_dictionary))
        final = df_test.transpose()
        final.columns = list(full_matrix)

        detection_dict = {}

        for index, row in final.iterrows():
            test_list = []
            row_intensity = (pd.DataFrame(row))
            blankthresh = blank_threshold.loc[index, ['blank_threshold']][0]
            detected = (row_intensity[row_intensity > float(blankthresh)].count())
            detected = (detected[0])
            detection_dict[index] = detected

        test_dictionary = {}
        for index, row in full_matrix.iterrows():
            test_list = []
        #print(index)
            for val in row:
                blankthresh = blank_threshold.loc[index, ['blank_threshold']][0]
                if val < blankthresh:
                    test_list.append('-')
                else:
                    test_list.append(val)
            test_dictionary[index] = test_list
            
        df_test = (pd.DataFrame.from_dict(test_dictionary))
        new_final = df_test.transpose()
        new_final.columns = list(full_matrix)

        detection_df = pd.DataFrame(list(detection_dict.items()))
        detection_df.columns = ['Metabolite', 'Detection']
        detection_df.index = detection_df['Metabolite']

        compiled = new_final.join(merged_df, how='outer')
        compiled_final = compiled.join(detection_df, how='outer')

        return(compiled_final, final)

    def print_blank_threshold(self):
        print(self.blank_threshold_value)
        
    def dme_comparisons(self):
        
        sample_groups = self.get_groups()
        groups = pd.read_csv(self.sample_sheet)
        unique_groups = [x for x in groups.Group.unique() if x != 'Blank']
        unique_comparisons = []
        
        for L in range(0, len(unique_groups)+1):
            for subset in itertools.combinations(unique_groups, L):
                if len(subset) == 2:
                    unique_comparisons.append(subset)

        reversed_groups = []
        for comparison in unique_comparisons:
            reversed_comparison = tuple(reversed(comparison))
            reversed_groups.append(reversed_comparison)

        unique_comparisons = unique_comparisons + reversed_groups
        return unique_comparisons

    
    def t_test(self):
        print("\n")
        print("============================================")
        print("Pipeline executed:")

        # Create samplesheet
        sample_sheet = pd.read_csv("inputs/Groups.tsv",sep='\t')
        sample_sheet['Color'] = 'NA'
        colors = ['#FF0000', '#0000FF', '#000000', '#008000', '#FFFF00', '#800080', '#FFC0CB', "#c0feff", "#5b2d8c",
                  "#7f8c2d", "#F1948A", "#BB8FCE", "#AED6F1", "#A3E4D7", "#F7DC6F", "#DC7633", "#5D6D7E", "#7B7D7D"]
        zipped_up = zip(colors,list(self.get_groups().keys()))
        for x, y in zipped_up:
            sample_sheet.loc[sample_sheet.Group == y, 'Color'] = x

        sample_sheet.to_csv('inputs/Groups.csv',index = False)
        

        # Create skeleton_input
        skeleton = pd.read_csv(self.data,sep='\t')

        if 'Skeleton_Metabolite' in skeleton:
            skeleton.to_csv(self.data,sep='\t',index=False)
        else:
            skeleton['numbers'] = pd.Series(np.arange(1,len(skeleton)+1,1))
            skeleton['New_Metabolite'] = skeleton['numbers'].astype(str) +'         '+ skeleton['Metabolite']
            skeleton['Skeleton_Metabolite'] = skeleton['Metabolite']
            skeleton['Metabolite'] = skeleton['New_Metabolite']
            del skeleton['New_Metabolite']
            del skeleton['numbers']

            col_name = "Skeleton_Metabolite"
            first_col = skeleton.pop(col_name)
            skeleton.insert(0, col_name, first_col)

            skeleton.to_csv(self.data,sep='\t',index=False)


        self.input_check()
        print("\n")
        print("Creating Directories...")
        print("\n")
        # Create all necessary directories
        self.dir_create()
        
        groups = pd.read_csv(self.sample_sheet)
        unique_groups = [x for x in groups.Group.unique()]
               
        # get all unique comparisons from Groups.csv
        unique_comparisons = self.dme_comparisons()

        #Meta Data on Metabolites
        standard = pd.read_csv(self.data,sep='\t')
        detection_column_index = standard.columns.get_loc("detections")
        standard = standard.iloc[:, 0:detection_column_index]


        # Set directory for results folder 
        if self.method == 'flux':
            results_folder = 'Flux-DME-results-' + str(len(self.get_ids('True'))) + '-Samples/'
        elif self.method == 'sum':
            results_folder = 'Sum-DME-results-' + str(len(self.get_ids('True'))) + '-Samples/'
        elif self.method == 'median':
            results_folder = 'Median-DME-results-' + str(len(self.get_ids('True'))) + '-Samples/'
        elif self.method == 'default':
            results_folder = 'DME-results-' + str(len(self.get_ids('True'))) + '-Samples/'

        sample_sheet.to_csv(results_folder + 'Inputs/Groups.tsv', sep='\t', index=False)
        

        # Get all sample matrix

        all_matrix = self.get_matrix(self.get_ids(selection='All'))
        all_matrix = self.sequence2id(all_matrix)
        all_matrix.to_csv(results_folder+'Tables/Intensity.values.all.csv')
        # Get full matrix of intensity values with Sequence IDS replaced with ID from Groups.csv


        full_matrix = self.get_matrix(self.get_ids(selection='True'))
        full_matrix = self.sequence2id(full_matrix)
        full_matrix_name = results_folder+'Tables/'+'Intensity.values.csv'
        detected_matrix_name = results_folder+'Tables/'+'Intensity.detected.values.csv'
        full_matrix.to_csv(full_matrix_name)
        
        corrected_matrix = self.sequence2id(self.get_imputed_full_matrix(self.get_matrix(ids=self.get_ids('True')),param        ='corrected'))
        corrected_matrix.index.name = 'Metabolite'
        corrected_matrix.to_csv(results_folder+'Tables/'+'Intensity.corrected.values.csv')
        
        
        for comparison in unique_comparisons:
            matrices = []    
            sample_groups = self.get_groups()
            #print (comparison[0])
            
            comparison_ids = []
            for condition in comparison:   
                if condition in sample_groups:
                    ids = (sample_groups[condition]) 
                    #print (ids)
                    matrices.append((self.get_imputed_full_matrix(self.get_matrix(ids=ids),param='detected')))
                    comparison_ids.append(ids)
            
            
            sample_ids = [item for sublist in comparison_ids for item in sublist]
            #generate samplesheet just for comparison
            
            

            samplesheet_comparison = sample_sheet.loc[sample_sheet['File'].isin(sample_ids)]
            
            samplesheet_comparison_name = results_folder+'PCA/samplesheet.csv'
            samplesheet_comparison.to_csv(samplesheet_comparison_name)
            
            #print ((matrices.shape())
            group_sample_number =  int((matrices[0].shape)[1])
            group_sample_number_2 = int(group_sample_number+ ((matrices[1].shape)[1]))
            
            #print(comparison_ids)
            
            pca_matrix = reduce(lambda left,right: pd.merge(left,right,left_index=True, right_index=True), matrices)
            #pca_matrix = pd.DataFrame(pca_matrix).set_index('Metabolite')
            pca_matrix.index.name = 'Metabolite'

            pca_matrix = self.sequence2id(pca_matrix)
            comparison_pca_name = (results_folder+'PCA/'+comparison[0]+'_vs_'+comparison[1]+'_PCA.html').replace(" ", "")
            comparison_pca = results_folder+'PCA/PCA_matrix.csv'
            
            
            pca_matrix.to_csv(comparison_pca)
            
            
            proc = sp.Popen(['python3','-W ignore','pca.py',comparison_pca,samplesheet_comparison_name,comparison_pca_name])
            
            #samplesheet_comparison_name.to_csv(samplesheet_comparison_name)
            
            matrices.append(pd.DataFrame(self.get_matrix(self.get_ids(selection='Blank'))))
            df_m = reduce(lambda left,right: pd.merge(left,right,left_index=True, right_index=True), matrices)
#             print(df_m.head())                  
#              df_blankless = df_m.copy()
            
            #print(group_sample_number,group_sample_number_2)
           # print(df_blankless.head())
            
            #return(df_blankless)
            
            ### Calculate Pearson Correlation 


            def get_correlation(matrix,group):

                temp_pearson_dict ={}
                cov = sample_sheet.loc[sample_sheet['Group'] == group]['Covariate']

                for row in matrix.iterrows():
                    index, data = row

                    pearson_correl = np.corrcoef(data, cov)[0, 1]
                    temp_pearson_dict[index] = pearson_correl

                pearson_df = pd.DataFrame([temp_pearson_dict]).T
                pearson_df.columns = [group]
                return(pearson_df)
            
            blank_matrix = pd.DataFrame(self.get_matrix(self.get_ids('Blank')))
            blank_matrix.to_csv(results_folder+'Tables/'+'blank_intensity.csv')
            blank_threshold = pd.DataFrame(blank_matrix.mean(axis=1)*3)+self.blank_threshold_value
            blank_threshold['Metabolite'] = blank_threshold.index
            blank_threshold.columns = ['blank_threshold','Metabolite']

            
            df_m['ttest_pval'] = ((scipy.stats.ttest_ind(df_m.iloc[:, :group_sample_number], df_m.iloc[:, group_sample_number:group_sample_number_2], axis=1))[1])
            df_m['1/pvalue'] = float(1)/df_m['ttest_pval']      
            group_1_df = (pd.DataFrame(df_m.iloc[:, :group_sample_number]))
            group_2_df = (pd.DataFrame(df_m.iloc[:, group_sample_number:group_sample_number_2]))
            
            
            
            
            df_m[comparison[0]+'_Mean'] = (group_1_df.mean(axis=1))
            df_m[comparison[1]+'_Mean'] = (group_2_df.mean(axis=1))
            
            df_m['Log2FoldChange'] =  np.log2(((group_1_df.mean(axis=1)))/((group_2_df.mean(axis=1))))
            df_m['LogFoldChange'] =  (((group_1_df.mean(axis=1)))/((group_2_df.mean(axis=1))))
            
            final_df_m = pd.merge(standard, df_m, on='Metabolite')
            final_df_m = pd.merge(final_df_m,blank_threshold,on='Metabolite')
            # Add detection column

            for col in blank_matrix.columns:

                final_df_m[col] = blank_matrix[col].values
          
            comparison_name = (results_folder+'Tables/'+comparison[0]+'_vs_'+comparison[1]+'.corrected.csv').replace(" ", "")
            
            
            
            
            final_df_m = self.sequence2id(final_df_m)
            
            final_df_m['combined_mean'] = (final_df_m[s[0]+'_Mean']+final_df_m[comparison[1]+'_Mean'])/2
            final_df_m['impact_score'] = (((2**abs(final_df_m['Log2FoldChange']))*final_df_m['combined_mean'])/final_df_m['ttest_pval'])/1000000
            final_df_m.impact_score = final_df_m.impact_score.round()
            final_df_m['impact_score'] = final_df_m['impact_score'].fillna(0)

            
            
            ####Calculate Detection
            

            detection_dict = {}
            
            comparison_matrix = group_1_df.join(group_2_df, how='outer')
            
            
            for index, row in comparison_matrix.iterrows():
                test_list = []
                #print (row)
                #print(index)
                row_intensity = (pd.DataFrame(row))
                blankthresh = blank_threshold.loc[index, ['blank_threshold']][0]
                detected = (row_intensity[row_intensity > float(blankthresh)].count())
                detected = (detected[0])
                detection_dict[index] = detected

            detection_df = pd.DataFrame(list(detection_dict.items()))
            detection_df.columns = ['Metabolite','Detection']
            detection_df.index = detection_df['Metabolite']

            final_df_m = pd.merge(final_df_m, detection_df, on='Metabolite')
            
            # Add impact score
            
            
            print("\n")
            print("\n")
            print("\n")
            print("===========================================================================================")
            
            print('\033[1m' + "Analysis",":",comparison[0]+'_vs_'+comparison[1])
            print('\n')
            print('Results Generated: %s'%comparison_name)
            final_df_m = final_df_m.fillna('NA')
            
#             final_df_m = pd.merge(final_df_m,merged_pearson,on='Metabolite',how='outer')
            final_df_m.to_csv(comparison_name)  
            
            
            test = pd.read_csv(comparison_name)
            
            print("Significant Metabolites P-value < 0.05:",len(test.loc[test['ttest_pval'] < 0.05]))
        
            #Generate Volcano
            print("Generating Volcano Plot: %s" % comparison_name)
            
            if self.method == 'default':
                proc = sp.Popen(['Rscript','scripts/volcano.plot.R',comparison_name,'True'])
            else:
                proc = sp.Popen(['Rscript','scripts/volcano.plot.R',comparison_name,'False'])
            
            # Generate heatmaps
            pvalues = [str(0.05)]
            print("Generating Pvalue < 0.05 Heatmap: %s"%comparison_name)
            for pvalue in pvalues:    
            
                proc = sp.Popen(['Rscript','scripts/heatmap.R',comparison_name,pvalue,'TRUE'])
             
            # Generate heatmap with all expressed metabolites


            print("\n")
        
            # Generate 3-D PCA
            
        print("Compiling Comparison - Results - output: dme.compiled.csv")
        
        compiled, imputed_intensities = self.compile_tests(results_folder+'Tables/',full_matrix)
        compiled = compiled.fillna('-')
        
        
        def change_column_order(df, col_name, index):
            cols = df.columns.tolist()
            cols.remove(col_name)
            cols.insert(index, col_name)
            return df[cols]
            
        compiled.to_csv(results_folder+'Tables/'+'dme.compiled.csv')
        
        if "FDR" in standard:
            dme_meta_data = standard[['Metabolite', 'Formula', 'FDR', 'Ion Type','mz','ppm','RT','RT_range','Skeleton_Metabolite']]
        else:
            dme_meta_data = standard[['Metabolite', 'Formula', 'Ion Type','mz','ppm','RT','RT_range','Skeleton_Metabolite']]
        
        dme_meta_data.index = dme_meta_data['Metabolite']
        compiled = pd.merge(dme_meta_data,compiled, on='Metabolite')
        compiled = change_column_order(compiled, 'Detection', 7)
        
        compiled.to_csv(results_folder+'Tables/'+'dme.compiled.csv')
        
        imputed_intensities.index.name = "Metabolite"
        #imputed_intensities = imputed_intensities.rename(columns={ imputed_intensities.columns[0]: "Metabolite" })
    
        imputed_intensities.to_csv(results_folder+'Tables/'+'Intensity.detected.values.csv')
        print("Generating Full Heatmap")
        proc = sp.Popen(['Rscript','scripts/heatmap.full.R',full_matrix_name,'nonimputed'])
        proc = sp.Popen(['Rscript','scripts/heatmap.full.R',detected_matrix_name,'imputed'])
        proc = sp.Popen(['python3','-W ignore','pca.py',detected_matrix_name,self.sample_sheet,(results_folder+'PCA/'+'PCA.full.html')])

        os.remove(comparison_pca)
        os.remove(samplesheet_comparison_name)
        
        from shutil import copyfile
        
        
        copyfile(self.data, results_folder+'Inputs/'+self.data.split('/')[1])

        table_directory = results_folder+'Tables'
        

        print('#######')
#         for file in os.listdir(results_folder+'Tables'):
#             if file.endswith('corrected.csv'):
        path = os.path.abspath(results_folder+'Tables')
        output_path = os.path.abspath(results_folder+'Pathway')

        
#        if 'Feature' in str(final_df_m['Metabolite'].tolist()[2]):
#            print('Unsuitable Metabolite Names for Pathway Analysis')
#        else:
#            proc = sp.Popen(['Rscript','scripts/pathway.R',path,output_path])
#      time.sleep(2)
        impact_folder = results_folder + 'Tables/dme.compiled.csv'
        proc = sp.Popen(['python3','scripts/impact.correlation.py', impact_folder])


        proc = sp.Popen(['python3', 'scripts/sig.genes.py', path])
        proc = sp.Popen(['python3', 'scripts/plot.qc.py', results_folder])


        print(" ========== Pipeline Finished ========== ")
            
            
        print("\n")
        print("\n")
        print("\n")
        print("===============================================")
        print("\n")
        print("\n")
        print("\n")



if __name__ == "__main__":
    try:
        print('\n')
        print('\n')
        print('\n')
        print('\n')
        print('\n')

        print('\033[1m' + '============== Pipeline Executed ==============')
        skeleton_name = [x for x in os.listdir('inputs') if x.endswith('.quantified')][0]
        result = Analysis(data=skeleton_name,sample_sheet='Groups.csv',blank_threshold_value=10000,method='default')
        result.t_test()
    except IndexError:

        print('\n')
        print('\n')
        print('\n')
        print('=== .quantified input not detected ===')
        print('=== Checking for output.tsv input ===')
        skeleton_name = [x for x in os.listdir('inputs') if x.endswith('output.tsv')][0]
        result = Analysis(data=skeleton_name,sample_sheet='Groups.csv',blank_threshold_value=10000,method='default')
        result.t_test()
