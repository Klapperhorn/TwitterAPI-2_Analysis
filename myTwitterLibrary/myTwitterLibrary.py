import requests
import datetime as dt
import time
import json
import pandas as pd
import glob

Today=dt.datetime.now().strftime('%Y-%m-%d')

def load_data(file):
    with open (file, "r", encoding="utf-8") as f:
        data = json.load(f) 
    return (data)

def write_data(file, data):
    with open (file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def dtC(Time):
    return dt.datetime.strptime(Time,'%Y-%m-%d').strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def create_headers(BToken):
    headers = {"Authorization": "Bearer {}".format(BToken)}
    return headers


def connect_to_endpoint(search_url, headers, params,filename="2023-02-06_Twitter_API_key.json"):
    
    BToken=load_data(filename)['Bearer_Token']
    headers=create_headers(BToken)
    response = requests.request("GET", search_url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main(query_params,filename="2023-02-06_Twitter_API_key.json"):
    BToken=load_data(filename)['Bearer_Token']
    headers = create_headers(BToken)
    search_url = "https://api.twitter.com/2/tweets/search/all"
    json_response = connect_to_endpoint(search_url, headers, query_params)
    #print(query_params)
    for i in range(5):
        try:
            print(json_response["data"][i]['created_at'])
            print(json_response["data"][i]['text'])
            print("\n")
        except:
            print(f'bad response - I am waiting 2 seconds, then try again.')
            time.sleep(2)
            print("next token: ",json_response['meta']['next_token'])
    return json_response


def mainCount(query_params,filename="2023-02-06_Twitter_API_key.json"):
    BToken=load_data(filename)['Bearer_Token']
    headers = create_headers(BToken)
    search_url = "https://api.twitter.com/2/tweets/counts/all"
    json_response = connect_to_endpoint(search_url, headers, query_params)
    try:
        toDo=json_response['meta']['total_tweet_count']
        print(json_response["data"][0])
    except:
        "huch"
    return json_response



def GetTweets(query_params,max_results,i,Today,DataName):
    print(i,i*max_results)
    json_response=main(query_params)
    time.sleep(3)  
    NextToken=json_response['meta']['next_token']
    query_params["next_token"]=NextToken

    with open(Today+"_"+DataName+"_"+str(i)+'_data'+'.json', 'w', encoding='utf-8') as f:
        json.dump(json_response, f, ensure_ascii=False, indent=4)
    return query_params



        
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