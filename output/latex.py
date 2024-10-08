import pandas as pd

# Load the CSV file
file_path = 'combined_avg_output.csv'  # Update this with the actual path to your CSV file
data = pd.read_csv(file_path)
data['method'] = data['method'].apply(lambda x: ''.join(x.replace('Entities', '').replace('_', ' ')))

# Function to filter data by a specific dataset
def filter_data_by_dataset(data, dataset_name):
    if dataset_name:
        return data[data['dataset'] == dataset_name]
    return data

# Function to filter data by a specific method name pattern
def filter_data_by_method(data, method_pattern):
    if method_pattern:
        return data[data['method'].str.startswith(method_pattern)]
    return data

# Prepare the data for each table
def prepare_tables(data):
    table_one = data.pivot(index='method', columns='dataset', values=['Precision', 'Recall', 'F1-score', 'F@5', 'F@10']).round(3)
    table_two = data.pivot(index='method', columns='dataset', values=['P@5', 'R@5', 'F@5']).round(3)
    table_three = data.pivot(index='method', columns='dataset', values=['P@10', 'R@10', 'F@10']).round(3)
    table_four = data.pivot(index='method', columns='dataset', values=['P@15', 'R@15', 'F@15']).round(3)
    table_five = data.pivot(index='method', columns='dataset', values=['NDCG', 'MAP']).round(3)
    table_six = data.pivot(index='method', columns='dataset', values=['avg_n_gt_keywords', 'avg_n_extraced_leywords', 'training seconds', 'prediction seconds']).round(3)
    return table_one, table_two, table_three, table_four, table_five, table_six

# Function to convert DataFrame to LaTeX table with multirow and multicolumn, and bold the maximum values
def dataframe_to_latex(df, caption, label, metrics, new_header):
    datasets = df.columns.levels[1]
    methods = df.index
    rows = []
    
    # Header
    header = '\\begin{table}\n\\centering\n'
    header += f'\\caption{{{caption}}}\n'
    header += f'\\label{{{label}}}\n'
    header += '\\begin{tabular}{l' + 'c' * len(datasets) * len(metrics) + '}\n\\toprule\n'
    header += '& ' + ' & '.join([f'\\multicolumn{{{len(metrics)}}}{{c}}{{{dataset}}}' for dataset in datasets]) + ' \\\\\n'
    header += '& ' + ' & '.join(new_header * len(datasets)) + ' \\\\\n\\midrule\n'
    rows.append(header)
    
    # Data
    for method in methods:
        row = [method]
        for dataset in datasets:
            for metric in metrics:
                value = df.loc[method, (metric, dataset)]
                if value == df[(metric, dataset)].max():
                    row.append(f'\\textbf{{{value}}}')
                else:
                    row.append(value)
        rows.append(' & '.join(map(str, row)) + ' \\\\\n')
    
    footer = '\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    rows.append(footer)
    
    return ''.join(rows)

# Main function to generate LaTeX tables
def generate_latex_tables(data, dataset_name=None, method_pattern=None):
    if dataset_name:
        data = filter_data_by_dataset(data, dataset_name)
    if method_pattern:
        data = filter_data_by_method(data, method_pattern)
    
    table_one, table_two, table_three, table_four, table_five, table_six = prepare_tables(data)
    
    new_header_one = ['P', 'R', '$F_1$', '$F_1$@5', '$F_1$@10']
    new_header_two = ['P@5', 'R@5', '$F_1$@5']
    new_header_three = ['P@10', 'R@10', '$F_1$@10']
    new_header_four = ['P@15', 'R@15', '$F_1$@15']
    new_header_five = ['NDCG', 'MAP', 'Ts', 'Ps']
    new_header_six = ['GT', 'EX', 'Ts', 'Ps']

    latex_table_one = dataframe_to_latex(table_one, 'Precision, Recall, $F_1$, $F_1$@5, $F_1$@10 score for each dataset', 'tab:table_one', ['Precision', 'Recall', 'F1-score', 'F@5', 'F@10'], new_header_one)
    latex_table_two = dataframe_to_latex(table_two, 'P@5, R@5, $F_1$@5 for each dataset', 'tab:table_two', ['P@5', 'R@5', 'F@5'], new_header_two)
    latex_table_three = dataframe_to_latex(table_three, 'P@10, R@10, $F_1$@10 for each dataset', 'tab:table_three', ['P@10', 'R@10', 'F@10'], new_header_three)
    latex_table_four = dataframe_to_latex(table_four, 'P@15, R@15, $F_1$@15 for each dataset', 'tab:table_four', ['P@15', 'R@15', 'F@15'], new_header_four)
    latex_table_five = dataframe_to_latex(table_five, 'NDCG, MAP for each dataset', 'tab:table_five', ['NDCG', 'MAP'], new_header_five)
    latex_table_six = dataframe_to_latex(table_six, 'Average Number of Ground Truth Keyphrases, Average Number of Extracted Keyphrases, training seconds, prediction seconds for each dataset', 'tab:table_six', ['avg_n_gt_keywords', 'avg_n_extraced_leywords', 'training seconds', 'prediction seconds'], new_header_six)

    # Save LaTeX tables to files
    with open('prf_combined.tex', 'w') as f:
        f.write(latex_table_one)

    with open('prf5_combined.tex', 'w') as f:
        f.write(latex_table_two)

    with open('prf10_combined.tex', 'w') as f:
        f.write(latex_table_three)

    with open('prf15_combined.tex', 'w') as f:
        f.write(latex_table_four)

    with open('others_combined.tex', 'w') as f:
        f.write(latex_table_five)

    with open('others2_combined.tex', 'w') as f:
        f.write(latex_table_six)

    print("LaTeX tables generated and saved to files.")

# Call the function to generate LaTeX tables with the option to filter by dataset and method name pattern
generate_latex_tables(data, dataset_name='inspec', method_pattern='LLMBaseModel-simple')  # Specify dataset name and method pattern or leave as None to use all
