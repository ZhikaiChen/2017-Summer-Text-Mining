
# coding: utf-8

# In[1]:

import re
import pandas as pd
import matplotlib.pyplot as plt
import os


# In[2]:

os.chdir('/Users/chenzhikai/hdw_2017/printer_metadata/Relational database/')


# In[6]:

'''
@Path=csv with standard names as columns, and their
variations as rows,
@nonstd=a series of unstandardized people names
return a series of standardized people names'''
def regNm(path,nonstd=None):
    df=pd.read_csv(path)
    std_dict=pd.melt(df).dropna().set_index('value').to_dict()['variable']
    #Standardize names in a given series
    #a filter than modified varied names who exist in the dictionary
    def standardize_names(person):
        if person in std_dict:
            return std_dict[person]
        else:
            return person
    res=nonstd.map(standardize_names)
    return res


# In[15]:

#apply on a string, return a list of strings (info after signalling words)
def applysplitters(splitters, s):
    val = s
    for (find,replace) in splitters:
        val = re.sub(find, "|"+replace+r"\1", val)
    return [phrase for phrase in val.split("|") if phrase != '']


# In[53]:

'''Split original publisher fields into printer, publisher, seller, based on keywords, by, for, sold by
and create new columns for their locations and institutional affiliations'''
def preproccess():
    
    df=pd.read_csv('printers.csv',index_col=0).fillna('')
    df.replace(':','',regex=True,inplace=True)
    #get rid of ... and strip trialing punctunations

    df.publisher=df.publisher.replace(r'\.\.\.','')
    df.publisher=df.publisher.str.strip(': ;?')
    # {m,n}? captures matched patterns from length m to length n, as few as possible
    # re.findall("regex()()") returns [($1,$2),($1,$2),...]
    #Preprocess to change "printed and sold by J. Bradford" into "printed by J. Bradford and sold by J. Bradford"
    df.publisher=df.publisher.str.replace('^(?:[EeIij][mn])?[Pp][ir][iye]nt[ye]d and [Ssh]?ou?lde? by ([A-Z](?:\.|[a-z]+\.?) ?)([A-Z](?:\.|[a-z]+\.?)),?',
                             r'printed by '+r'\g<1>'+r'\g<2>'+' and sold by '+r'\g<1>'+r'\g<2>')                             
    
    # use key words 'printed', 'for', 'are sold to' to create three fields
    splitters = [["((\\b[EeIij][mn])?[Pp][ir][iye]nt[ye]d\\b)", "printer:"],
                 ["(\\bfor\\b)", "publisher:"],
                 ["(( are)?( to)?( bee?)? [Ssh]ou?lde?)", "seller:"]]
    # list of list of strings of splitted fields
    l=map(lambda x:applysplitters(splitters,x),df.publisher)
    #create a list of dictionaries 
    output=[]
    for sublist in l:
        d ={}
        for item in sublist:
            if ':' in item:
                (k,v)=item.split(':')
            else:
                k,v = 'printer',item
            if k in d.keys():
                d[k]+=v
            else:
                d[k]=v
        output.append(d)
    Three_field=pd.DataFrame(output)
    Three_field['key']=df['dlps']
    
    #start to clean up the printer field
    Three_field.printer=Three_field.printer.str.replace(r'\.\.\.','')
    Three_field.printer=Three_field.printer.str.strip(': ;')
    # split printer field along location printer info and keyword 'by'

    df_new=Three_field.printer.str.extract(
    r'(?P<printer_location>^(?:\b[Ii]n\b|\b[Aa]t\b|\b[Ww]ithin\b|\b[Nn]eare?\b|\b[Dd]w[ey]ll[iy]nge?\b|\b[Aa]gainst\b|\b[Oo]ver\b|\b[Uu]nder\b).*)(?P<printer_y> ?\b[Bb]y\b,?.*)'
    ,expand=True)
    df_gesamt = pd.concat([Three_field,df_new], axis=1,
                      join ='outer')
    mask = df_gesamt['printer_y'].notnull()
    df_gesamt['printer'][mask] = df_gesamt['printer_y'][mask]
    df_gesamt.drop('printer_y',axis=1, inplace=True)
    
    # separate  printer from location based on location keywords
    df_new=df_gesamt.printer.str.extract(
        r'(?P<printer_y>.*?)(?P<printer_location_y>(?:\b[Ii]n\b|\b[Aa]t\b|\b[Ww]ithin\b|\b[Nn]eare?\b|\b[Dd]w[ey]ll[iy]nge?\b|\b[Aa]gainst\b|\b[Oo]ver\b|\b[Uu]nder\b).*)'
    ,expand=True) 
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                      join ='outer')

    mask = df_gesamt['printer_y'].notnull()
    df_gesamt['printer'][mask] = df_gesamt['printer_y'][mask]
    mask = df_gesamt['printer_location_y'].notnull()
    df_gesamt['printer_location'][mask] = df_gesamt['printer_location_y'][mask]
    df_gesamt.drop(['printer_y','printer_location_y'],axis=1, inplace=True)
    
    #extract printer enclosed by location info in printer_location field 
    #'In London, xx, dwelling at xx'
    df_new=df_gesamt.printer_location.str.extract(r'(?P<printer_location_y>^(?:.*))(?P<printer_y> ?\b[Bb]y\b,? .*)')
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                      join ='outer')

    mask = df_gesamt['printer_location_y'].notnull()
    df_gesamt['printer'][mask] = df_gesamt['printer'][mask]+df_gesamt['printer_y'][mask]
    df_gesamt['printer_location'][mask] = df_gesamt['printer_location_y'][mask]
    df_gesamt.drop(['printer_y','printer_location_y'],axis=1, inplace=True)

    
    #for cases like in London, by xx, dwelling at
    #put by xx in printer field, concat in London and dwelling at and put them into loc field
    df_new=df_gesamt.printer.str.extract(
        r'(?P<printer_y>.*?)(?P<printer_location_y>(?:\b[Ii]n\b|\b[Aa]t\b|\b[Ww]ithin\b|\b[Nn]eare?\b|\b[Dd]w[ey]ll[iy]nge?\b|\b[Aa]gainst\b|\b[Oo]ver\b|\b[Uu]nder\b).*)'
    ,expand=True)
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                      join ='outer')

    mask = df_gesamt['printer_location_y'].notnull()
    df_gesamt['printer'][mask] = df_gesamt['printer_y'][mask]
    df_gesamt['printer_location'][mask] = df_gesamt['printer_location_y'][mask]+df_gesamt['printer_location'][mask]
    df_gesamt.drop(['printer_y','printer_location_y'],axis=1, inplace=True)
    
    #Put stuffs in printer field started with "For" into publisher field
    df_new=df_gesamt.printer.str.extract('(?P<publisher_y> ?For .*)',expand=True)
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                     join ='outer')

    mask = df_gesamt['publisher_y'].notnull()
    df_gesamt['publisher'][mask] = df_gesamt['publisher_y'][mask]
    df_gesamt['printer'][mask]=''
    df_gesamt.drop('publisher_y', inplace=True,axis=1)
    
    #Put stuff in printer begins with word 'Sold' into seller field

    df_new=df_gesamt.printer.str.extract('(?P<seller_y> ?[Ssh]ou?lde?.*)',expand=True)
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                     join ='outer')
    mask = df_gesamt['seller_y'].notnull()
    df_gesamt['seller'][mask] = df_gesamt['seller_y'][mask]
    df_gesamt['printer'][mask]=''
    df_gesamt.drop('seller_y', inplace=True,axis=1)
    
    # Create new col printer to- for institutional affiliations
    df_new=df_gesamt.printer.str.extract(
    '(?P<printer_y>.*?)(?P<printer_to>(?:,? [Pp][ir][iye]nters? to).*)'
    ,expand=True)
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                     join ='outer')
    mask = df_gesamt['printer_y'].notnull()
    df_gesamt['printer'][mask] = df_gesamt['printer_y'][mask]
    df_gesamt.drop('printer_y', inplace=True,axis=1)
    
    #split publisher field along location infos
    df_new=df_gesamt.publisher.str.extract(
    r'(?P<publisher_y>.*?)(?P<publisher_location>(?:\b[Ii]n\b|\b[Aa]t\b|\b[Ww]ithin\b|\b[Nn]eare?\b|\b[Dd]w[ey]ll[iy]nge?\b|\b[Aa]gainst\b|\b[Oo]ver\b|\b[Uu]nder\b).*)'
    ,expand=True)
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                      join ='outer')

    mask = df_gesamt['publisher_y'].notnull()
    df_gesamt['publisher'][mask] = df_gesamt['publisher_y'][mask]
    #mask = ~(df_gesamt['publisher_location_y'].isnull())
    #df_gesamt['publisher_location'][mask] = df_gesamt['printer_location_y'][mask]
    df_gesamt.drop(['publisher_y'],axis=1, inplace=True)
    
    #split stuffs in seller field based on location info
    df_new=df_gesamt.seller.str.extract(
    r'(?P<seller_y>.*?)(?P<seller_location>(?:\b[Ii]n\b|\b[Aa]t\b|\b[Ww]ithin\b|\b[Nn]e[ea]re?\b|\b[Dd]w[ey]ll[iy]nge?\b|\b[Aa]gainst\b|\b[Oo]ver\b|\b[Uu]nder\b).*)'
    ,expand=True)
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                      join ='outer')
    mask = df_gesamt['seller_y'].notnull()
    df_gesamt['seller'][mask] = df_gesamt['seller_y'][mask]
    df_gesamt.drop(['seller_y'],axis=1, inplace=True)
    
    #put stuff in seller_location after by into seller col
    probs=df_gesamt[df_gesamt.seller_location.fillna('').str.contains(' by 'or' by ')&~(df_gesamt.seller.fillna('').str.contains(' by 'or' by '))]
    df_new=probs.seller_location.str.extract(r'(?P<seller_location_y>^(?:.*))(?P<seller_y> ?\b[Bb]y\b,?.*)')
    df_gesamt = pd.concat([df_gesamt,df_new], axis=1,
                      join ='outer')
    mask = df_gesamt['seller_location_y'].notnull()
    df_gesamt['seller'][mask] = df_gesamt['seller'][mask]+df_gesamt['seller_y'][mask]
    df_gesamt['seller_location'][mask] = df_gesamt['seller_location_y'][mask]
    df_gesamt.drop(['seller_y','seller_location_y'],axis=1, inplace=True)
    
    #replace By, printed by with empty string
    df_gesamt.printer=df_gesamt.printer.str.replace('By ?','')
    df_gesamt.printer=df_gesamt.printer.str.replace('([EeIij][mn])?[Pp][ir][iye]nt[ye]d (by )?','')
    df_gesamt.to_csv('df_gesamt.csv')
    return 


# In[54]:

pd.set_option('max_colwidth',150)


# In[56]:
'''Separate extract multiple printers,publishers and sellers 

from each columns, and relate these actors via keys(the unique works they are invovled in)'''
def to_relational_database():
    df=pd.read_csv('df_gesamt.csv',index_col=0)  
    printer = pd.DataFrame(df[['key','printer']])
    
    #clean up the dataset
    printer=printer.fillna('')
    printer.replace('^by ','',regex=True,inplace=True)
    printer.replace(r'([EeIij][mn])?[Pp][ir][iye]nt[ye]d, and','',regex=True,inplace=True)
    printer.replace(r'([EeIij][mn])?[Pp][ir][iye]nt[ye]d, by ','',regex=True,inplace=True)
    printer.replace(r'^[Mm]e ','',regex=True,inplace=True)
    printer.replace(r',? and$','',regex=True,inplace=True)
    printer.replace(r'&amp','and',regex=True,inplace=True)
    printer.replace(r'^and$','',regex=True,inplace=True)
    printer.replace(r'and are$','',regex=True,inplace=True)
    printer.replace(r'\.\.\.','',regex=True,inplace=True)
    printer.replace(r'and;','and',regex=True,inplace=True)
    printer.replace(r'and,','and',regex=True,inplace=True)
    printer.printer=printer.printer.str.strip(',: ;?')
    printer.replace(r'[Rr]e-','',regex=True,inplace=True)
    printer.replace('\. ?$|, ?$','',regex=True,inplace=True)
    printer.replace('^by ?|[Cc]hez |[Bb]e |^[Pp]ar |^[Pp]er |sic ','',regex=True,inplace=True)
    printer.printer=printer.printer.replace('^([A-Z](?:\.|[a-z]+\.?)) and ([A-Z](?:\.|[a-z]+\.?) )([A-Z][a-z]+),?',                                
      r'\g<1>'+r' \g<3>'+' and '+r'\g<2>'+r'\g<3>')
    
    #Inspect the word count of pritner field to devise a strategy to clean up further
    printer['printer_wc'] =map(lambda x:len(x.split()),printer.printer)
    #after = printer.groupby('printer_wc')['printer'].count()
    
    # separate two names based according to 'pattern name 1 and name 2'
    df_new=printer.printer.str.extract(
    '(?P<printer_1>(?: ?[A-Z][a-z,.]+ ?,?| ?[A-Z]\.?,? ?)+)(?:and )(?P<printer_2>(?: ?[A-Z][a-z,.]+ ?,?| ?[A-Z]\.?,? ?)+)',
    expand=True)
    printer = pd.concat([printer,df_new], axis=1,
                  join ='outer')
    
    #trim comma after previous split
    printer=printer.replace(', ?$','',regex=True)
    
    #update word count
    printer['printer_wc'] =map(lambda x:len(x.split()),printer.printer)
    
    #If printer field has only two word put it into printer_1 field
    mask = (printer.printer_1.isnull()) & (printer.printer_wc ==2)
    printer.printer_1[mask] = printer.printer[mask]
    
    #Put the expression like the heirs of Andrew Anderson (an important printer)
    df_new=printer.printer.str.extract(
    '(?P<printer_1y>(?:the)? [Hh]eirs?(?: and [Ss]uccessors of) Andrew Anderson,?)(?P<stuff>(?:.*))',
    expand=True)
    printer = pd.concat([printer,df_new], axis=1,
                    join ='outer')
    mask = printer['printer_1y'].notnull()
    printer.printer_1[mask]=printer.printer_1y[mask]
    printer.drop(['printer_1y','stuff'], inplace=True,axis=1)
    
    #hand_clean
    #hand_clean=printer[~printer.printer_1.notnull()&~(printer.printer_wc<=2)]
    
    #put all the names into printer_1 field separated by comma
    printer.printer_1.replace(' $','',regex= True,inplace=True)
    mask=printer.printer_2.notnull()
    printer.printer_1[mask]=printer.printer_1[mask]+', '+printer.printer_2[mask]
    #extract all the printer names and put them into a column
    #multiple level 0s are place holders for books, making printers related by keys possible
    merged=printer.printer_1.str.extractall("([^,]+)").reset_index().merge(printer,left_on='level_0',right_index=True)
    printer_key=merged[['key', 0]]
    printer_key.columns=['key','actor']
    printer_key['role']='printer'
    
    #start to clean publisher fields
    publisher = pd.DataFrame(df[['key','publisher']])
    
    #data clean up
    publisher.publisher=publisher.publisher.fillna('')
    publisher.publisher=publisher.publisher.str.strip(',: ;?. ')
    publisher.replace(r'\.\.\.','',regex=True,inplace=True)
    publisher.replace(r'&amp;','and',regex=True,inplace=True)
    publisher.publisher=publisher.publisher.str.strip(',: ;?.')
    publisher.publisher.replace('^ ?[Ff]or,? |,? and ?$| ?sic|^\t ?[Mm]e |. And$','',regex=True,inplace=True)
    publisher.replace('^([A-Z](?:\.|[a-z]+\.?)) and ([A-Z](?:\.|[a-z]+\.?) )([A-Z][a-z]+),?',                                
      r'\g<1>'+r' \g<3>'+' and '+r'\g<2>'+r'\g<3>',regex=True,inplace=True)
    publisher.replace('^ ?[Bb]y ','',regex=True,inplace=True)
    
    #Separate and extract multiple printers
    df_new=publisher.publisher.str.extract(
    '(?P<publisher_1>(?: ?[A-Z][a-z,.]+ ?,?| ?[A-Z]\.?,? ?)+)(?:and )(?P<publisher_2>(?: ?[A-Z][a-z,.]+ ?,?| ?[A-Z]\.?,? ?)+)',
    expand=True)
    publisher = pd.concat([publisher,df_new], axis=1,
                    join ='outer')
    #replace 'and' in one word field with nothing
    publisher.publisher.replace('^and ?','',regex=True,inplace=True)
    
    #update word count
    publisher['publisher_wc'] =map(lambda x:len(x.split()),publisher.publisher)
    #If printer field has only two or one word, put it into printer_1 field
    mask = (publisher.publisher_1.isnull()) & ((publisher.publisher_wc ==2) |(publisher.publisher_wc ==1))
    publisher.publisher_1[mask] = publisher.publisher[mask]
    
    #hand clean
    #hand_clean2=publisher[publisher.publisher_1.isnull()]
    
    #put names into publisher_1 field separated by comma
    publisher.publisher_1.replace(' $','',regex= True,inplace=True)
    mask=publisher.publisher_2.notnull()
    publisher.publisher_1[mask]=publisher.publisher_1[mask]+', '+publisher.publisher_2[mask]
    
    merged=publisher.publisher_1.str.extractall("([^,]+)").reset_index().merge(publisher,left_on='level_0',right_index=True)
    publisher_key=merged[['key', 0]]
    publisher_key.columns=['key','actor']
    publisher_key['role']='publisher'
    
    #start cleaning up seller
    seller = pd.DataFrame(df[['key','seller']])
    seller.seller=seller.seller.fillna('')
    seller.seller=seller.seller.map(lambda x: x.strip(',: ;?. '))
    seller.replace(r'\.\.\.','',regex=True,inplace=True)
    seller.replace(r'&amp;','and',regex=True,inplace=True)
    seller.seller=seller.seller.map(lambda x: x.strip(',: ;?.'))
    seller.replace(r'(are )?(to )?(bee? )?[Ss]ou?lde?','',regex=True,inplace=True)
    seller.replace('^([A-Z](?:\.|[a-z]+\.?)) and ([A-Z](?:\.|[a-z]+\.?) )([A-Z][a-z]+),?',                                
      r'\g<1>'+r' \g<3>'+' and '+r'\g<2>'+r'\g<3>',regex=True,inplace=True)
    seller.replace('^ ?[Bb]y ','',regex=True,inplace=True)
    seller.replace(', ?$','',regex=True,inplace=True)
    seller['seller_wc']= map(lambda x:len(str(x).split()),seller.seller)
    
    #put stuff after by into seller_1 col
    df_new=seller.seller.str.extract(
    '(?P<seller_1>(?: ?[A-Z][a-z.,]+ ?,?| ?[A-Z]\.?,? ?)+)(?:and )(?P<seller_2>(?: ?[A-Z][a-z,.]+ ?,?| ?[A-Z]\.?,? ?)+)',
    expand=True)
    seller = pd.concat([seller,df_new], axis=1,
                     join ='outer')
    
    #update word count by wc==2 into seller_1 field
    seller['seller_wc']= map(lambda x:len(str(x).split()),seller.seller)
    mask=seller.seller_wc==2
    seller.seller_1[mask]=seller.seller[mask]
    #put names into seller_1 field separated by comma
    seller.seller_1=seller.seller_1.replace(' $','',regex= True)
    mask=seller.seller_2.notnull()
    seller.seller_1[mask]=seller.seller_1[mask]+', '+seller.seller_2[mask]

    #merging
    merged=seller.seller_1.str.extractall("([^,]+)").reset_index().merge(seller,left_on='level_0',right_index=True)
    seller_key=merged[['key', 0]]
    seller_key.columns=['key','actor']
    seller_key['role']='seller'
    
    #Create final relational datase of printers, publishers, sellers
    database=printer_key.append([publisher_key,seller_key],ignore_index=True)
    database.to_csv('database.csv')
    return database







# In[ ]:



