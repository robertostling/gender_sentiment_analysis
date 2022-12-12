import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, JsCode,DataReturnMode,GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import re, os
from glob import glob
sns.set(font_scale=0.5)
sns.set(rc = {'figure.figsize':(5,5)})

def filter_df(field):
  if len(st.session_state[field])>0:
    st.session_state.df = st.session_state.df[st.session_state.df[field].isin(st.session_state[field])]
    generate_plots()

def plot_stacked_barchart_bk(df, x, y, color, title=False):
  if title:
    fig=px.bar(df,x=x,y=y, color=color, title=title)
  else:
     fig=px.bar(df,x=x,y=y, color=color)
  return fig
  #st.write(fig)

def plot_stacked_barchart(df, x, y, color, title=False):
  if title:
    fig=px.histogram(df,x=x, color=color, title=title, barnorm = "percent", text_auto= '.2f', nbins=35)
  else:
     fig=px.histogram(df,x=x, color=color, barnorm = "percent", text_auto= '.2f', nbins=35)
  return fig

def plot_barchart(df, x, y, orient="v"):
    fig=px.bar(df,x=x,y=y, orientation=orient)
    return fig
  #st.write(fig)

def plot_histogram(df, x, bins=20):
    fig=px.histogram(df,x=x, nbins=bins)
    return fig


def plot_timeline(df, x, y, color, title):
  fig = px.line(
      df,x=x, y=y, title=title,
      color=color)
  return fig



def plot_heatmap(df):
  fig = px.imshow(df, text_auto='.3f', aspect='auto') #width=800, 
  return fig

def plot_heatmap_bk(df, x, y,facet):
  fig = px.imshow(
      df,x=x, y=y, facet_col=facet) # , text_auto='.2f'
  return fig

def load_data_synthesis():
  st.header("Lexical Concurrency Exploration : synthesis")
  if 'init' not in st.session_state:
    st.session_state.init=True
  #print(st.session_state.word)
  if st.session_state.word not in filespath:
    st.write('No filepath for this word : ' + st.session_state.word + ". Check filespath variable in code.")
    return False
  if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(filespath[st.session_state.word])
    columns = st.session_state.df.columns
    columns = [col for col in columns if re.search('lemma',col)]
    #print(st.session_state.df["r1lemma"].value_counts().head(20))
    for col in columns:
      colforme = re.sub('lemma','forme',col)
      print(col, colforme)
      st.session_state.df[col] = np.where(st.session_state.df[col].str.contains("unknown"), st.session_state.df[colforme], st.session_state.df[col])
      #st.session_state.df.loc[st.session_state.df[col] =='unknown', col] = st.session_state.df[colforme]
    #exit()
    #print(st.session_state.df["r1lemma"].value_counts().head(20))
    st.session_state.df['date'] = pd.to_datetime(st.session_state.df['date'])
    st.session_state.df['year-month'] = st.session_state.df['date'].dt.strftime('%Y-%m')
    st.session_state.country = st.session_state.df.country.unique()
    st.session_state.journal = st.session_state.df.journal.unique()
    st.session_state.subject = st.session_state.df.subject.unique()
  generate_plots_synthesis()

def generate_plots_synthesis():
  # forme
  df_gr1 = st.session_state.df.groupby(['year-month','forme'])['coreforme'].count().reset_index(name='count')
  df_gr2 = df_gr1.groupby(['year-month'])['count'].sum().reset_index(name="total")
  df_grouped = pd.merge(df_gr1, df_gr2, on="year-month")
  df_grouped['percent'] = df_grouped['count'] / df_grouped['total']
  # metadata
  # subject
  df_subj = st.session_state.df.groupby(['subject','forme'])['coreforme'].count().reset_index(name='count')
  df_subj2 = df_subj.groupby(['subject'])['count'].sum().reset_index(name="total")
  df_group_subj = pd.merge(df_subj, df_subj2, on="subject")
  df_group_subj['percent'] = df_group_subj['count'] / df_group_subj['total']

  # country
  df_cnt = st.session_state.df.groupby(['country','forme'])['coreforme'].count().reset_index(name='count')
  df_cnt2 = df_cnt.groupby(['country'])['count'].sum().reset_index(name="total")
  df_group_cnt = pd.merge(df_cnt, df_cnt2, on="country")
  df_group_cnt['percent'] = df_group_cnt['count'] / df_group_cnt['total']
  # journal
  df_jnrl = st.session_state.df.groupby(['journal','forme'])['coreforme'].count().reset_index(name='count')
  df_jnrl2 = df_jnrl.groupby(['journal'])['count'].sum().reset_index(name="total")
  df_group_jnrl = pd.merge(df_jnrl, df_jnrl2, on="journal")
  df_group_jnrl['percent'] = df_group_jnrl['count'] / df_group_jnrl['total']
  #print("displaying plots")
  with st.expander("Distribution / Evolution des formes (relative weight of words per period)"):
    dftmp = st.session_state.df.groupby('forme')['coreforme'].count().reset_index(name='count')
    fig = px.pie(dftmp, names='forme',values='count')
    st.plotly_chart(fig,use_container_width = True)
    fig = plot_stacked_barchart(df_grouped,x='year-month',y='percent',color="forme")
    st.plotly_chart(fig,use_container_width = True)
  #with st.expander("Evolution des formes (absolute weight of words per period)"):
  #  fig=plot_stacked_barchart(df_gr1,x='year-month',y='count',color="forme")
  #  st.plotly_chart(fig,use_container_width = True)
  with st.expander("Distribution / Evolution par métadonnées : subject"):
    dftmp = st.session_state.df.groupby('subject')['coreforme'].count().reset_index(name='count')
    fig = px.pie(dftmp, names='subject',values='count')
    st.plotly_chart(fig,use_container_width = True)
    fig=plot_stacked_barchart(df_group_subj,x='subject',y='percent',color="forme")
    st.plotly_chart(fig,use_container_width = True)
    wordlist = st.session_state.df.forme.unique()
    for w in wordlist:
      df_subj_evol = st.session_state.df[st.session_state.df.forme==w].groupby(['year-month','subject'])['coreforme'].count().reset_index(name='count')
      fig=plot_stacked_barchart(df_subj_evol,x='year-month',y='count',color="subject", title=w)
      st.plotly_chart(fig,use_container_width = True)

  with st.expander("Distribution / Evolution par métadonnées : country"):
    dftmp = st.session_state.df.groupby('country')['coreforme'].count().reset_index(name='count')
    fig = px.pie(dftmp, names='country',values='count')
    st.plotly_chart(fig,use_container_width = True)
    fig=plot_stacked_barchart(df_group_cnt,x='country',y='percent',color="forme")
    st.plotly_chart(fig,use_container_width = True)
    wordlist = st.session_state.df.forme.unique()
    for w in wordlist:
      df_subj_evol = st.session_state.df[st.session_state.df.forme==w].groupby(['year-month','country'])['coreforme'].count().reset_index(name='count')
      fig=plot_stacked_barchart(df_subj_evol,x='year-month',y='count',color="country", title=w)
      st.plotly_chart(fig,use_container_width = True)

  with st.expander("Distribution / Evolution par métadonnées : journal"):
    dftmp = st.session_state.df.groupby('journal')['coreforme'].count().reset_index(name='count')
    fig = px.pie(dftmp, names='journal',values='count')
    st.plotly_chart(fig,use_container_width = True)
    fig=plot_stacked_barchart(df_group_jnrl,x='journal',y='percent',color="forme")
    st.plotly_chart(fig,use_container_width = True)
    wordlist = st.session_state.df.forme.unique()
    for w in wordlist:
      df_subj_evol = st.session_state.df[st.session_state.df.forme==w].groupby(['year-month','journal'])['coreforme'].count().reset_index(name='count')
      fig=plot_stacked_barchart(df_subj_evol,x='year-month',y='count',color="journal", title=w)
      st.plotly_chart(fig,use_container_width = True)

  with st.expander("Raw data"):
    st.dataframe(st.session_state.df)

def load_data_linguistic():
  st.header("Lexical Concurrency Exploration : lexico-syntactic patterns")
  #if 'init' not in st.session_state:
  #  st.session_state.init=True
  #if st.session_state.word not in filespath:
  #  st.write('No filepath for this word : ' + st.session_state.word + ". Check filespath variable in code.")
  #  return False
  st.session_state.df = pd.read_csv(filespath[st.session_state.word])
  st.session_state.df['date'] = pd.to_datetime(st.session_state.df['date'])
  st.session_state.df['year-month'] = st.session_state.df['date'].dt.strftime('%Y-%m')
  st.session_state.country = st.session_state.df.country.unique()
  st.session_state.journal = st.session_state.df.journal.unique()
  st.session_state.subject = st.session_state.df.subject.unique()
  generate_plots_patterns(cat="N")

def generate_plots_patterns(cat="N"):
  # for category Noun
  st.session_state.df = st.session_state.df[st.session_state.df.corepos.str.contains(cat)]
  print(st.session_state.df.shape)
  print(st.session_state.df.r1pos.value_counts())
  with st.expander("Noun : pattern X ADJ"): 
    # distribution
    dftmp = st.session_state.df[st.session_state.df.r1pos=='Adj'].groupby(['forme','r1lemma'])['coreforme'].count().reset_index(name='count')
    df_gr2 = dftmp.groupby(['forme'])['count'].sum().reset_index(name="total")
    df_grouped = pd.merge(dftmp, df_gr2, on="forme")
    df_grouped['percent'] = df_grouped['count'] / df_grouped['total']
    print(df_grouped)
    words = dftmp.forme.value_counts().index
    #print(words)
    #st.write("Adjectives distribution by lexeme (X Adj)")
    fig=plot_stacked_barchart(df_grouped,x='forme',y='percent',color="r1lemma", title="Adjectives distribution by lexeme (X Adj)") #
    st.plotly_chart(fig,use_container_width = True)

    # timeline of observations / events
    dftmp_time = st.session_state.df[st.session_state.df.r1pos=='Adj'].groupby(['year-month','forme'])['coreforme'].count().reset_index(name='count')
    df_gr2_time = dftmp_time.groupby(['forme'])['count'].sum().reset_index(name="total")
    df_grouped_time = pd.merge(dftmp_time, df_gr2_time, on="forme")
    df_grouped_time['percent'] = df_grouped_time['count'] / df_grouped_time['total']
    fig = plot_stacked_barchart(dftmp_time,x='year-month',y='count',color="forme", title="Evolution (absolute frequency)")
    st.plotly_chart(fig,use_container_width = True)
    fig = plot_stacked_barchart(df_grouped_time,x='year-month',y='percent',color="forme", title="Evolution (inner percentage per year-month)")
    st.plotly_chart(fig,use_container_width = True)

    # details
    print(df_grouped_time.columns)
    for w in words:
      dftmp2 = df_grouped_time[df_grouped_time['forme']==w][['r1lemma','percent','count']].fillna(0.00)
      nb = dftmp2.shape[0]
      fig = px.histogram(dftmp2.sort_values(by="count", ascending=False).head(30), x='r1lemma',y='percent',text_auto=True, title= w + '('+str(nb) + ')')
      #fig = px.pie(df_grouped[df_grouped['forme']== w].sort_values(by="count", ascending=False).head(30), names='r1lemma',values='percent')
      st.plotly_chart(fig,use_container_width = True)

  with st.expander("Noun : pattern V X (Object)"):
    dftmp = st.session_state.df[st.session_state.df.l2pos=='Verb'].groupby(['forme','l2lemma'])['coreforme'].count().reset_index(name='count')
    print(dftmp)
    words = dftmp.forme.value_counts().index
    print(words)
    # synthesis
    st.subheader('Synthesis : distribution of Verbs per lexeme and Evolution')
    fig = plot_stacked_barchart(dftmp,y='forme',x='count',color="l2lemma")
    fig.update_layout(autosize=True)
    st.plotly_chart(fig,use_container_width = True)

    # details
    st.subheader("Details per word")
    for w in words:
      fig = px.bar(dftmp[dftmp.forme==w].sort_values(by='count', ascending=False).head(30), y='l2lemma',x='count', orientation='h', title=w + '(' + str(dftmp[dftmp.forme==w].shape[0]) + ' verbs)')
      st.plotly_chart(fig,use_container_width = False)

#    fig = plt.figure()
#    dftmp2 = st.session_state.df[st.session_state.df.l2pos=='Verb'].groupby(['l2lemma','forme'])['coreforme'].count().reset_index(name='count')
#    l2lemma_crosstab = pd.crosstab(dftmp2.l2lemma,dftmp2.forme,values=dftmp['count'], normalize="columns", aggfunc=np.sum, dropna=True)#normalize="cols", , aggfunc='count',values=dftmp.count, dropna=True, margins=True
    #l2lemma_crosstab = pd.pivot_table(dftmp2, columns='l2lemma',index='forme',values='count', dropna=True, fill_value=0, aggfunc=np.sum).apply(lambda x: x / float(x.sum())).round(2)#normalize="cols", , aggfunc='count',values=dftmp.count, dropna=True, margins=True
#    print(l2lemma_crosstab)

#    sns.set(font_scale = 0.2)
#    sns.heatmap(l2lemma_crosstab.T,  annot=True, fmt='.02f', # linewidths=.2,  
#                  yticklabels=True, xticklabels=True,cmap="Blues")
#    st.pyplot(fig)#,use_container_width = True
    #formes = st.session_state.df.forme.unique()
    #for f in formes:
    #      crosstab = pd.crosstab(st.session_state.df.subject,
    #                st.session_state.df['year-month'],aggfunc='count', values=st.session_state.df.coreforme, normalize="columns", dropna=True,) # , margins=True
    #      fig = plt.figure()
    #      sns.heatmap(crosstab,  annot=True, fmt='.2f', linewidths=.2,  
    #              yticklabels=True, xticklabels=True,cmap="Blues", title=f)
    #      st.pyplot(fig)#,use_container_width = True

  with st.expander("Raw data"):
    st.dataframe(st.session_state.df)

############# specific to sentiment
def load_data(filepath):
    try :
        #print(filepath)
        df = pd.read_csv(filepath)
        df["year"]=df["year"].values.astype('str')
        df['year'] = df.year.str.replace("\.0$",'', regex=True)
        df['year'] = pd.to_datetime(df['year'], format="%Y")
        return df
    except Exception as e :
        st.write("error : " + str(e))
        return False

def get_most_correlated_columns(df):
    corr_matrix = df.corr().abs()
    #the matrix is symmetric so we need to extract upper triangle matrix without diagonal (k = 1)
    sol = (corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
                  .stack()
                  .sort_values(ascending=False))
    return sol

def countPlot(x,data,figsize=(10,4), title=False):
    fig = plt.figure(figsize=figsize)
    if title:
        sns.countplot(x = x, data = data).set_title(title)
    else:
        sns.countplot(x = x, data = data)
    st.pyplot(fig)

def distPlot(data, col, figsize=(4,4), kde=False, bins=10, title=False):
    fig = plt.figure(figsize=figsize)
    if title:
        sns.histplot(data=data, x=col, kde=kde,  bins=bins).set_title(title)
    else:
        fig = sns.histplot(data=data, x=col, kde=kde,  bins=bins)
    st.pyplot(fig)
#first element of sol series is the pair with the biggest correlation    
########################################### main
sns.set(font_scale=0.5)

url_renderer =  JsCode("""
function(params) {return `<a href=${params.value} target="_blank">Source</a>`}
""")

html_renderer =  JsCode("""
function(params) {return `<div>${params.value}</div>`}
""")

credits='''
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">                                                                                                    
<hr/>
<b>Credits</b><ul>
<li>PyABSA python module : <a href="https://github.com/yangheng95/PyABSA" target="new"><i class="fa-solid fa-arrow-up-right-from-square"></i></a> </li>                                                                                                                                                                                                          
<li>Project members : Emmanuel Cartier, Natalia Levshina, Maria Koptjevskaja Tamm, Robert Mikael Östling </li>                                                                                                                                                                                          
<li>Project github repository : <a href="https://github.com/ecartierlipn/gender_sentiment_analysis" target="new"><i class="fa-solid fa-arrow-up-right-from-square"></i></a> </li>                                                                                                                                                                                                          
</ul>
'''


path = '../corpora/'
cworkdir = os.getcwd()
wordspairs= {'French':['femme,femmes-homme,hommes','fille,filles-garçon,garçons', 'épouse,femme,épouses-mari,époux','mère,mères-père,pères','fille,filles-fils','soeur,soeurs-frère,frères','tante, tantes-oncle, oncles'], 'English':[]}
langcorpora={'French':{'FICTION': '', 'NEWS': 'lemonde_1945_2020'}, 'English':{'FICTION':'English_fiction_woman_forR.txt','NEWS':''}}
langs=[k for k in langcorpora]
if len(langs)>1:
    langs.insert(0,'Choose a language')
genres = ['FICTION','NEWS']
polarity = ['NEGATIVE', 'NEUTRAL', 'POSITIVE']

st.set_page_config(layout = "wide")
st.header("Aspect-based Sentiment Analysis applied to gender lexemes in 5 languages, 2 genres, from 1950 to now")
lang = st.sidebar.selectbox('Language',langs)
if lang != 'Choose a language':
    # display available corpora
    corpora = [k + ':' + v for k,v in langcorpora[lang].items() if len(v)>0]
    if len(corpora)>1:
        corpora.insert(0,'Choose a corpus')
    corpus = st.sidebar.selectbox('Corpus',corpora)    
    
    if corpus != 'Choose a corpus':
        # get list of files and words (from word files)
        #files = glob(path + corpus.split(':')[1] + ".*.sentiment.csv")
        #print(files)
        #words = [data.split('.')[-3] for data in files]
        #words.insert(0,'Choose a word')
        #word = st.sidebar.selectbox('Word',words)

        # get list of files and words (from word pairs)
        #files = glob(path + corpus.split(':')[1] + ".*.sentiment.csv")
        #print(files)
        words = wordspairs[lang]
       # words = [data.split('.')[-3] for data in files]
        words.insert(0,'Choose a word pair')
        word = st.sidebar.selectbox('Word Pairs',words)

        # last step : generate visualization and data
        if word != 'Choose a word pair':
            st.sidebar.write(credits, unsafe_allow_html=True)
            #print(words.index(word)-1)
            wordlist = re.split(r"[,-]", word.strip())
            print(wordlist)
            dflist=[]
            with st.expander("Distribution and Evolution of Sentiment Polarity"):
                for w in wordlist:
                    # depends if we are on streamlit cloud
                    if cworkdir =='/app/gender_sentiment_analysis':
                        wordpath = cworkdir + '/'+ path[2:] + corpus.split(':')[1] + "." + w + ".sentiment.csv"
                    else:
                        wordpath = path + corpus.split(':')[1] + "." + w + ".sentiment.csv"
                    if os.path.isfile(wordpath) is False:
                        st.write("Error loading file : [" + wordpath + "]. Skipping this word")
                        continue
                    else:
                        df = load_data(wordpath)
                        print(df.info())
                        # clean data
                        df['aspect']= w
                        df['sentiment']= df['sentiment'].str.replace(r"\W+","", regex=True, flags=re.I)
                        df['sentiment']= df['sentiment'].str.replace(r"(Negative)+","Negative", regex=True, flags=re.I)
                        df['sentiment']= df['sentiment'].str.replace(r"(Positive)+","Positive", regex=True, flags=re.I)
                        df['sentiment']= df['sentiment'].str.replace(r"(Neutral)+","Neutral", regex=True, flags=re.I)
                        df['year']= df['year'].dt.year
                        df['Text']= df['Text'].str.replace(r"\b" + w + r"\b",r"<mark>" + w + r"</mark>", regex=True, flags=re.I)
                        columns = list(df.columns)
                        print(columns)
                        dflist.append(df)
                        #columns.remove('aspect')
                        col1, col2 = st.columns([3,5])
                        color_discrete_map = {'Negative': 'red', 'Neutral': 'blue', 'Positive': 'green'}
                        with col1:
                            #fig = px.bar(df.sentiment.value_counts(), orientation="v")
                            fig = px.pie(df, values=df.sentiment.value_counts().values, color=df.sentiment.value_counts().index, title="<b>Distribution</b>", color_discrete_map=color_discrete_map)
                            fig.update_layout(font_size=8,bargap=0.1, title_x=0.5, title_y=0.9, title_font_size=14,title_font_color="black")
                            st.plotly_chart(fig,use_container_width = True)

                        with col2:
                            fig = px.histogram(df,x='year', color='sentiment', barnorm = "percent", text_auto= '.2f', nbins=35, title="<b>Evolution : " + w + ' (' + str(df.shape[0]) + ' sentences)</b>', color_discrete_map=color_discrete_map)
                            #fig = plot_stacked_barchart(df, 'year', 'sentiment', 'sentiment', title="<b>Evolution : " + w + ' (' + str(df.shape[0]) + ' sentences)</b>', color_discrete_map=color_discrete_map)
                            fig.update_layout(font_size=8,bargap=0.1,title_x=0.5, title_y=0.9, title_font_size=14,title_font_color="black")
                            st.plotly_chart(fig,use_container_width = True)

            dftotal = pd.concat(dflist)
            print(dftotal.info())


            #fig = px.histogram(dftotal, x="year", y="sentiment", color="sentiment", facet_row="aspect")
            #fig = px.histogram(dftotal, x="year", y="sentiment", color="sentiment", facet_row="aspect", barnorm = "percent", text_auto= '.2f', nbins=35)
            #fig = px.bar(dftotal, x="year", y="sentiment", color="sentiment", facet_row="aspect")
            #fig.update_layout(font_size=8,bargap=0.1)
            #st.plotly_chart(fig,use_container_width = True)


            with st.expander("Dataframe"):
                        #columns.insert(0,'tweet')

                        gbint = GridOptionsBuilder.from_dataframe(dftotal[columns])
                        return_mode_value = DataReturnMode.__members__['FILTERED']
                        update_mode_value = GridUpdateMode.__members__['MODEL_CHANGED']            
                        gbint.configure_pagination()
                        #gbint.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='count', editable=False)
                        gbint.configure_column('Text', wrapText=True, cellRenderer=html_renderer, autoHeight=True, flex=5, minWidth=350)
                        gbint.configure_column("link",cellRenderer=url_renderer, width=50)
                        gbint.configure_column("year",width=50)
                        gbint.configure_column("aspect",width=50)
                        gbint.configure_column("sentiment",width=50)
                        gbint.configure_column("prob", type=['numericColumn'], valueGetter='Number(data.prob).toFixed(3)', width=50)
                        
                        #for colname in columns[1:]:
                        #    gbint.configure_column(colname,flex=1,  type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=3) # type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2
                        #gbint.configure_column("id_sent", wrapText=True, flex=2, cellRenderer=html_jscode, autoHeight=True, width=700) # , cellStyle=cellstyle_jscode , , cellStyle={"resizable": True,"autoHeight": True,"wrapText": True}
                        gbint.configure_side_bar()
                        #gbint.configure_selection("single")
                        gridOptions = gbint.build()
                        ag_grid = AgGrid(
                                            dftotal[columns], 
                                            data_return_mode=return_mode_value, 
                                            update_mode=update_mode_value,
                                            fit_columns_on_grid_load=True,                
                                            gridOptions=gridOptions, 
                                            allow_unsafe_jscode=True,
                                            height=500,
                                            enable_enterprise_modules=True
                                            )#, enable_enterprise_modules=True
                    
