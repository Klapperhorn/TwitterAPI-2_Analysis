import requests
import yaml
import datetime as dt
import time
import json
import pandas as pd
import glob

from datetime import datetime.now datetime.strftime

Heute=dt.datetime.now().strftime('%Y-%m-%d')

with open("210615_key.yaml") as file:
    keys = yaml.load(file, Loader=yaml.FullLoader)
keys.keys()

BToken=keys['search_tweets_dipro']
search_url = BToken['endpoint']

def dtC(Time):
    return dt.datetime.strptime(Time,'%Y-%m-%d').strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(BToken['bearer_token'])}
    return headers

headers=create_headers(BToken)

def connect_to_endpoint(search_url, headers, params):
    response = requests.request("GET", search_url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main(query_params):
    headers = create_headers(BToken)
    json_response = connect_to_endpoint(search_url, headers, query_params)
    #print(query_params)
    for i in range(5):
        try:
            print(json_response["data"][i]['created_at'])
            print(json_response["data"][i]['text'])
            print("\n")
        except:
            print('huch?')
    return json_response


def mainCount(query_params):
    search_url = "https://api.twitter.com/2/tweets/counts/all"
    json_response = connect_to_endpoint(search_url, headers, query_params)
    try:
        toDo=json_response['meta']['total_tweet_count']
        print(json_response["data"][0])
    except:
        "huch"
    return json_response



def GetTweets(query_params,max_results,i,Heute,DataName):
    print(i,i*max_results)
    json_response=main(query_params)
    time.sleep(3)  
    NextToken=json_response['meta']['next_token']
    query_params["next_token"]=NextToken

    with open(Heute+"_"+DataName+"_"+str(i)+'_data'+'.json', 'w', encoding='utf-8') as f:
        json.dump(json_response, f, ensure_ascii=False, indent=4)
    return query_params


def load_data(file):
    with open (file, "r", encoding="utf-8") as f:
        data = json.load(f) 
    return (data)

def write_data(file, data):
    with open (file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
def FileImport(DataName):
    import glob
    
    dataList=glob.glob("*"+DataName+"*"+"_data.json")
    print(", ".join(dataList))
    combined_results = []
    combined_media=[]
    #combined_userDict={}
    for file in dataList:
        try:
            media=load_data(file)["includes"]["media"]
            combined_media.extend(media)
        except: 
            print("no_Media")        
        data=load_data(file)["data"]
        #UserDict = {item['id']:item["username"] for item in data['includes']['users']}
        combined_results.extend(data)
        #combined_userDict = {**combined_userDict, **UserDict}
    print(len(combined_results),len(combined_media))
    return combined_results, combined_media


def ImgDownload(c):
    import requests
    key=c["media_key"]
    url=c["url"]
    try:
        filename=key+"."+url.split(".")[-1]
    #print(filename)
        r = requests.get(url, allow_redirects=True)
    
        with open ("IMG_Download/"+filename, "wb") as f:
            f.write(r.content)
    except:
        print("error: ", url)
    
    return key,url