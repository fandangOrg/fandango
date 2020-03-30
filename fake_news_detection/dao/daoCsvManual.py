'''
Created on Mar 30, 2020

@author: camila
'''

import pandas as pd
from pandas import ExcelWriter

source = '/home/camila/Downloads/Article Annotation.xlsx'
output = '/home/camila/Downloads/Articles_classified.xlsx'

writer = ExcelWriter(output)

def write_report(source, format_options):
    excel_df = pd.ExcelFile(source)
    for sheet_name in excel_df.sheet_names:
        df = pd.read_excel(source, sheet_name=sheet_name)
        n_articles = count_articles(df)
        av_lenght = average_lenght(df)
        n_yes = count_trustworthy(df)
        dict_lang = {'Number of Articles':n_articles, 'Average Lenght':av_lenght, 'Number of Trustworthy':n_yes}
        df = pd.DataFrame(dict_lang, index =[0])
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        if format_options['format']:
            format_report(df, writer, sheet_name, format_options)
    writer.save()

def format_report(df, writer, sheet_name, options:dict):
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    fmt = workbook.add_format({'align': 'right',
                               'bold': True, 'bottom': 5, 'border':1, 'border_color':'black'})
    unit = 1.5
    background_color = options['header_color'] if 'header_color' in options else 'cyan'
    header_fmt = workbook.add_format({'font_size': 20, 'align': 'right', 'bg_color': background_color})
    for row in range(len(df.index) + 1):
        if row == 0:
            worksheet.set_row(row, height=30)
            continue
        worksheet.set_row(row, height=25)
    worksheet.conditional_format('A1:Z200', {'type': 'no_blanks', 'format': fmt})
    worksheet.conditional_format('A1:Z1', {'type': 'no_blanks', 'format': header_fmt})
    worksheet.set_column('A:A', unit * len(df.columns[0]))
    worksheet.set_column('B:B', unit * len(df.columns[1]))
    worksheet.set_column('C:C', unit * len(df.columns[2]))

def count_articles(df):
    count =0
    for index in range(len(list(df.iterrows()))):
        if isinstance(df['Body'][index], str) or isinstance(df['Article URL'][index], str)\
                or isinstance(df['Headline'][index], str):
            count +=1
    return count


def average_lenght(df):
    count = list()
    for row in df['Body']:
        if not isinstance(row, str):
            continue
        n_words = len(str(row).split(' '))
        count.append(n_words)
    return int(sum(count)/len(count))


def count_trustworthy(df):
    n_yes = 0
    for row in df['Trustworthy? (yes or no)']:
        if row.casefold() == 'yes':
            n_yes +=1
    return n_yes


if __name__ == '__main__':

    options= {'format':True}
    write_report(source, options)
