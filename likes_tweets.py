import requests
import os
import json
import urllib.request as req

tokenfile = "token.json"
savefile = "save.json"

# To set your enviornment variables in your terminal run the following line:
# export "BEARER_TOKEN"="<your_bearer_token>"
# bearer_token = os.environ.get("BEARER_TOKEN")

with open(tokenfile) as f:
    token_dict = json.load(f)
    
bearer_token = token_dict["BEARER_TOKEN"]
max_results = 5

def get_userid_by_username(username:str) -> str:
    if "USER_ID" not in token_dict:
        usernames = "usernames=" + username        
        user_fields = "user.fields=description,created_at"
        url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
        response = requests.request("GET", url, auth=bearer_oauth,)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        json_response = response.json()
        with open(tokenfile, "w") as f:
            token_dict["USER_ID"] = str(json_response["data"][0]["id"])
            json.dump(token_dict, f, indent=4)
    
    return token_dict["USER_ID"]

def create_url():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    # tweet_fields = "media.fields=url"
    
    if not os.path.isfile(savefile):
        save = {"next_token": ""}
        with open(savefile, "w+") as f:
            json.dump(save, f, indent=4)
    
    with open(savefile) as f:
        save_data = json.load(f)
        next_token = save_data["next_token"]

    print("next_token :" + next_token)
    tweet_fields = {
        "expansions":"author_id,attachments.media_keys",
        "user.fields" :"username",
        "tweet.fields": "text,entities",
        "media.fields" : "url",
        "max_results" : max_results
    }
    
    if len(next_token) != 0:
        tweet_fields["pagination_token"] = next_token
    
    id = get_userid_by_username(token_dict["USER_NAME"])
    
    # tweet_fields = "tweet.fields=lang,author_id"
    # Be sure to replace your-user-id with your own user ID or one of an authenticating user
    # You can find a user ID by using the user lookup endpoint
    # id = "your-user-id"
    # id = "romsenorange"
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs
    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    return url, tweet_fields


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2LikedTweetsPython"
    return r

def connect_to_endpoint(url, fields):
    response = requests.request(
        "GET", url, auth=bearer_oauth, params=fields)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def save_img(tweet_json, save_dir) -> bool:
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    media_key_dict = {}
    media_key_text_dict = {}
    if tweet_json["meta"]["result_count"] == 0:
        print("no data")
        save = {"next_token": ""}
        with open(savefile, "w+") as f:
            json.dump(save, f, indent=4)
        return True

    save = {"next_token": tweet_json["meta"]["next_token"]}
    with open(savefile, "w+") as f:
        json.dump(save, f, indent=4)

    try:
        for data in tweet_json["data"]:
            if "attachments" in data:             
                for i, media_keys in enumerate(data["attachments"]["media_keys"]): 
                    media_key_dict[media_keys] = data["author_id"]
                    media_key_text_dict[media_keys] = data["text"].replace("https://", "") + "-" + str(i)
        
        userid_dict = {}
        for user in tweet_json["includes"]["users"]:
            userid_dict[user["id"]] = user["username"]
        
        media_key_username_dict = {}
        for media_key in media_key_dict.items():
            for userid in userid_dict.items():
                if media_key[1] == userid[0]:
                    media_key_username_dict[media_key[0]] = "@" + userid[1]
        
        ret:bool = False
        for tweet in tweet_json["includes"]["media"]:
            save_name:str = media_key_username_dict[tweet["media_key"]] + " " + media_key_text_dict[tweet["media_key"]]
            save_name = save_name.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\\", "_").replace("/", "_").replace(":", "：").replace("*", "＊").replace("?", "？").replace("\"", "_").replace("<", "＜").replace(">", "＞").replace("|", "｜")
            url = tweet["url"]
            filepath = save_dir + save_name + url[-4:]
            
            if os.path.isfile(filepath):
                ret = True
            else:
                ret = False
            
            try:
                req.urlretrieve(url, filepath)
            except Exception as e:
                print(" !=== failed to save picture. ===!")
            print("text: " + save_name)
            print("    --> url: " + url)
    except Exception as e:
        ret = False
        assert 0

    if ret == True:
        save = {"next_token": ""}
        with open(savefile, "w+") as f:
            json.dump(save, f, indent=4)
        print("reached the already exists.")
        print("    --> " + "\"" + filepath + "\"")

    return ret

def main():
    isDone = False
    while  not isDone:
        url, tweet_fields = create_url()
        json_response = connect_to_endpoint(url, tweet_fields)
        # print(json.dumps(json_response, indent=4, sort_keys=True))
        isDone = save_img(json_response, "./downloads/")

if __name__ == "__main__":
    main()