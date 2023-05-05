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
    combined_extTweets=[]
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
            
            
            
        ## Combine extendedTweets
        try:
            extTweets=load_data(file)["includes"]["tweets"]
            combined_extTweets.extend(extTweets)
        except: 
            print("no_Extended_tweets")      
            
            
        ## Combine User Infos    
        try:
            users=load_data(file)["includes"]["users"]
            combined_users.extend(users)
        except: 
            print("no_users")        
            

        #UserDict = {item['id']:item["username"] for item in data['includes']['users']}
        #combined_userDict = {**combined_userDict, **UserDict}
    print(f"Tweets: {len(combined_results)}, Media:{len(combined_media)}, Users: {len(combined_users)}")
    return combined_results, combined_media, combined_users, combined_extTweets


def generateTweeturl(x):
    s=x['id'] 
    a=x['author_id']
    url=f"https://twitter.com/{a}/status/{s}"
    return url

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
    text=text.lstrip("RT ")
    return text

def Sequence_Hashtag_remove(text,NsequenceHashtags=5):
    simpl="-".join([w[0] for w in text.split()])
    
    if simpl.count("#-#")>NsequenceHashtags:
        text=" ".join([w for w in text.split() if w[0]!="#"]) 
        
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


def prepare_df(combined_results,combined_media=False,combined_user=False,combined_extTweets=False, Simplify=True):
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
            
    df["RT"]=df.text.apply(lambda x: x[:2]=="RT")
        
    return df


# SCHMARRRN
            
   # if combined_extTweets!=False:
        
        
        
        ###############
        # extend Tweet: ###NOT NEEDED ... only useful for retweets 
        
        
       #extTweet_dict={item['id']:item["text"] for item in combined_extTweets if "text" in item}
        
        
       # df["extended_tweet"]=df.id.map(extTweet_dict)
        

        #mentioned Users:
 
        #Mentioned_dict={item['id']:[mention['username'] for mention in item['entities']['mentions']] for item in combined_extTweets if "entities" in item and 'mentions' in item["entities"]}

      
       # df["mentioned_users"]=df.id.map(Mentioned_dict)
        #############