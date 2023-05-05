import pandas as pd

from datetime import datetime
Today=datetime.now().strftime('%Y-%m-%d')


def load_data(file):
    from json import load
    with open (file, "r", encoding="utf-8") as f:
        data = load(f) 
    return (data)

def FileImport(DataName):
    from glob import glob
    
    dataList=glob("*"+DataName+"*"+"_data.json")
    print(", ".join(dataList))
    combined_results = []
    combined_media=[]
    combined_users=[]
    #combined_userDict={}
    for file in dataList:
        
        ## Combine Data
        data=load_data(file)["data"]
        combined_results.extend(data)
        
        ## Combine Media
        try:
            media=load_data(file)["includes"]["media"]
            combined_media.extend(media)
        except: 
            print("no_Media")        
            
            
        ## Combine User Infos    
        try:
            users=load_data(file)["includes"]["users"]
            combined_users.extend(users)
        except: 
            print("no_users")        
            

        #UserDict = {item['id']:item["username"] for item in data['includes']['users']}
        #combined_userDict = {**combined_userDict, **UserDict}
    print(f"Tweets: {len(combined_results)}, Media:{len(combined_media)}, Users: {len(combined_users)}")
    return combined_results, combined_media, combined_users


def generateTweeturl(x):
    s=x['id'] 
    a=x['author_id']
    url=f"https://twitter.com/{a}/status/{s}"
    return url

def ImgageDownload(media_url_list,directory="/content/drive/MyDrive/Maastricht_Workshop_Jupyter/"):
    import requests
    filenames=[]
    if type(media_url_list)==list:
        for url in media_url_list:
            try:
                filename="IMG_Download/"+url.split("/")[-1]
                filenames+=[filename]
                print(filename)
                r = requests.get(url, allow_redirects=True)
                with open (directory+filename, "wb") as f:
                    f.write(r.content)

            except:
                print("error with: ", url)
                return filenames

    if type(media_url_list)==str:
        url=media_url_list
        try:
            filename="IMG_Download/"+url.split("/")[-1]
            filenames+=[filename]
            print(filename)
            r = requests.get(url, allow_redirects=True)
            with open (directory+filename, "wb") as f:
                f.write(r.content)

        except:
            print("error with: ", url)
            return filenames

#df['author_name']=df.author_id.apply(lambda x: combined_userDict[x])

def url_expand(i):
    if type(i)==list:
        i=[x['expanded_url'] for x in i]
    return i

def hashtags_expand(i):
    if type(i)==list:
        i=[x['tag'] for x in i]
    return i

def attachments_expand(i):
    if type(i)==dict:
        if "media_keys" in i:
            i=i['media_keys']
    return i

def mentioned_username(mentioned):
    usernames=[]
    if type(mentioned)==list:
        usernames=[i["username"] for i in mentioned if "username" in i]
    return usernames
        
        
def TextCleaner(text):
    #remove UserNames
    text=" ".join([word for word in text.split() if word[0]!="@" if word[:4]!="http"])
    text=text.replace("&amp","&")
    return text


def expand_df(df): 
    df=df.join(pd.json_normalize(df.public_metrics))
    df=df.join(pd.json_normalize(df.attachments))
    df=df.join(pd.json_normalize(df.entities))
    df.created_at=df.created_at.apply(pd.to_datetime)
    df.urls=df.urls.apply(url_expand)
    df.attachments=df.attachments.apply(attachments_expand)
    df.hashtags=df.hashtags.apply(hashtags_expand)
    df.mentions=df.mentions.apply(mentioned_username)

    df["text_clean"]=df["text"].apply(TextCleaner)
    df["word_count"]=df.text_clean.apply(lambda x: len(x.split()))
    df["Tweet_url"]=df.apply(generateTweeturl,axis=1)
    return df

def simplify_df(df): 
    return df[["text","text_clean","created_at","id","author_id","retweet_count","reply_count","like_count","quote_count","impression_count","word_count","attachments","urls","hashtags","mentions"]]


def replace_mediakey(KeyList, import_dict={}):
    return_values=[]
    if type(KeyList)==list:
        for i in KeyList:
            if i in import_dict:
                return_values+=[import_dict[i]]
    return return_values


def prepare_df(combined_results,combined_media=False,combined_user=False, Simplify=True):
    df=pd.DataFrame(combined_results)
    df=expand_df(df) ## Applies functions to convert the imported Twitter data into a one level DataFrame 
    
    
    if Simplify==True: # remove some columns
        df=simplify_df(df)
    
    #add some columns from Data
    
    if combined_media!=False: ### Add a column with the image URL
        media_dict = {item['media_key']:item["url"] for item in combined_media if "url" in item}
        df["media_url"]=df.attachments.apply(replace_mediakey, import_dict=media_dict)

    if combined_user!=False:
        for field in ["username","name","description",'location']:
            user_dict = {item['id']:item[field] for item in combined_user if field in item} # generate different dictionaries
            
            df[field]=df.author_id.map(user_dict) # map them on the dataframe

    return df


def make_wordcloud(flat_list,filename,Mostcommon=100):
    from collections import Counter
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    
    a_counter = Counter(flat_list)
    most_common = a_counter.most_common(Mostcommon)
    wordcloud=WordCloud(background_color="white", width=1200, height=1200).generate_from_frequencies(dict(most_common))
    
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(filename,dpi=300)
    plt.show()
    
    
def FindTweetByMediaKey(x, mediaKey="3_1250417374660100096"):

    if type(x)==list:
        for i in x:
            if mediaKey in i:
                return True
        
    return False


def Keyword_context(text,search_word="sustainable",context=(4,4)):

    PreWords,AfterWords=context
    list_of_words = text.split()
    WordbeginLetters=4
    try:
        similars=[word for word in list_of_words if word[:WordbeginLetters].lower()==search_word[:WordbeginLetters]][0].lower()
        
        pos=list_of_words.index(similars)
     #   print(similars + ":   ")
        
        if pos>WordbeginLetters and pos+AfterWords<len(list_of_words):
            
           # next_word =" ".join(list_of_words[pos-PreWord : pos+AfterWords])
            next_word =" ".join(list_of_words[pos-PreWords : pos+AfterWords])
        else:
            next_word =" ".join(list_of_words[0: pos+AfterWords])
            
        print(next_word)
        #results=" ".join(search_word, next_word)
    except:
        results=""
    results=""

    return results

## User_Analyse Functions:

def most_popular_users(df, by_value='like_count',n=20,plot=True):

    Piv_table = pd.pivot_table(df, values='like_count', index=["username"], aggfunc=sum)

    if plot==True:
        import matplotlib.pyplot as plt
        MostLikedAuthors=Piv_table.sort_values('like_count', ascending=False)[:n]
        MostLikedAuthors.plot.barh(title=f'Most popular {n} users on Twitter by{by_value}')
        plt.savefig(Today+DataName+"MostLiked_"+str(N)+"_Authors-Barh.pdf",dpi=300,bbox_inches="tight")
        plt.show()
    
    return MostLikedAuthors
