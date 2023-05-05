import pandas as pd
import requests

def downloadImages(imageList,targetFolder="IMG_Download/"):
    import requests
    import os.path

    for imageUrl in imageList:
        try:
            filename=imageUrl.split("/")[-1]
            print(imageUrl, end=", ")

            if os.path.exists(targetFolder+filename)!=True:
                r = requests.get(imageUrl, allow_redirects=True)
                with open (targetFolder+filename, "wb") as f:
                    f.write(r.content)
        except:
            print("error: ", imageUrl)
    return



def displayImage(df,n=1,targetFolder="IMG_Download/"):
    df=df.reset_index()
    text=df.text[n]
    username=df.username[n]
    date=df.created_at[n]
    print(f"{username} ({date}):\n{text}")
    
    for imageUrl in df.media_url[n]: 
        filename=imageUrl.split("/")[-1]
        
        from IPython.display import Image
        filename=targetFolder+filename
        print("file: ",filename)
        return filename