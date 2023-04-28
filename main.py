import ast
import csv
import datetime
import os
import shutil
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import schedule
import tweepy as tw
from PIL import Image
from konlpy.tag import Okt
from tqdm import tqdm
from wordcloud import WordCloud

file = "data.csv"
to_pull = 1500  # amount of tweets to pull for each run

# Twitter API credentials
# For more information, visit https://docs.tweepy.org/en/stable/authentication.html?highlight=OAuth1UserHandler#tweepy.OAuth1UserHandler
auth = tw.OAuth1UserHandler(
    "consumer_key", "consumer_secret",
    "access_token", "access_token_secret"
)
api = tw.API(auth, wait_on_rate_limit=True)


# open csv file
def save_to_csv():
    global id, name, screen_name, text, created_at, retweet_count, favorite_count, hashtags, file
    fields = [id, name, screen_name, text, created_at, retweet_count, favorite_count, hashtags]
    with open(file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


# function that pulls tweets
def get_data():
    print("Started collecting data.")
    global id, name, screen_name, text, created_at, retweet_count, favorite_count, hashtags, file
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["id", "name", "screen_name", "text", "created_at", "retweet_count", "favorite_count", "hashtags"])
    i = 0
    tweets = tw.Cursor(api.search_tweets, q="한복", lang="ko").items(to_pull)

    try:
        for tweet in tqdm(tweets, total=to_pull):
            i = i + 1
            id = tweet.id
            created_at = tweet.created_at
            screen_name = tweet.user.screen_name
            name = tweet.user.name
            text = tweet.text
            retweet_count = tweet.retweet_count
            favorite_count = tweet.favorite_count
            hashtags = tweet.entities['hashtags']
            save_to_csv()
            # print(f"Pulled tweet {id}. {i}/{to_pull} ({round(i / to_pull * 100, 3)})%")
        print("Completed collecting data.\n")
    except:
        print("Failed collecting data. Trying again in 3 seconds.")
        time.sleep(3)
        get_data()


# function that renders wordcloud using data from csv file (for words)
def render_words():
    print("Started rendering")
    global id, name, screen_name, text, created_at, retweet_count, favorite_count, hashtags, file, app, apperernc, words
    df = pd.read_csv(file, encoding='utf-8', header=0)
    # wc = df.set_index("text").to_dict()["text"]

    content_all = ''
    for i in range(len(df["text"])):
        content_all = content_all + " " + df["text"].loc[i]
    content_all = str(content_all)

    print("Completed reading csv.")

    okt = Okt()
    nouns_txt = okt.nouns(content_all)
    print("Completed extracting nouns.")

    # remove 1-letter words
    nouns_txt = [noun for noun in nouns_txt if len(noun) > 1]

    stopword = ["가", "가까스로", "가령", "각", "각각", "각자", "각종", "갖고말하자면", "같다", "같이", "개의치않고", "거니와", "거바", "거의", "것",
                "것과 같이",
                "것들", "게다가", "게우다", "겨우", "견지에서", "결과에 이르다", "결국", "결론을 낼 수 있다", "겸사겸사", "고려하면", "고로", "곧", "공동으로", "과",
                "과연", "관계가 있다", "관계없이", "관련이 있다", "관하여", "관한", "관해서는", "구", "구체적으로", "구토하다", "그", "그들", "그때", "그래",
                "그래도",
                "그래서", "그러나", "그러니", "그러니까", "그러면", "그러므로", "그러한즉", "그런 까닭에", "그런데", "그런즉", "그럼", "그럼에도 불구하고",
                "그렇게 함으로써",
                "그렇지", "그렇지 않다면", "그렇지 않으면", "그렇지만", "그렇지않으면", "그리고", "그리하여", "그만이다", "그에 따르는", "그위에", "그저", "그중에서",
                "그치지 않다", "근거로", "근거하여", "기대여", "기점으로", "기준으로", "기타", "까닭으로", "까악", "까지", "까지 미치다", "까지도", "꽈당", "끙끙",
                "끼익", "나", "나머지는", "남들", "남짓", "너", "너희", "너희들", "네", "넷", "년", "논하지 않다", "놀라다", "누가 알겠는가", "누구", "다른",
                "다른 방면으로", "다만", "다섯", "다소", "다수", "다시 말하자면", "다시말하면", "다음", "다음에", "다음으로", "단지", "답다", "당신", "당장",
                "대로 하다", "대하면", "대하여", "대해 말하자면", "대해서", "댕그", "더구나", "더군다나", "더라도", "더불어", "더욱더", "더욱이는", "도달하다",
                "도착하다",
                "동시에", "동안", "된바에야", "된이상", "두번째로", "둘", "둥둥", "뒤따라", "뒤이어", "든간에", "들", "등", "등등", "딩동", "따라", "따라서",
                "따위", "따지지 않다", "딱", "때", "때가 되어", "때문에", "또", "또한", "뚝뚝", "라 해도", "령", "로", "로 인하여", "로부터", "로써", "륙",
                "를", "마음대로", "마저", "마저도", "마치", "막론하고", "만 못하다", "만약", "만약에", "만은 아니다", "만이 아니다", "만일", "만큼", "말하자면",
                "말할것도 없고", "매", "매번", "메쓰겁다", "몇", "모", "모두", "무렵", "무릎쓰고", "무슨", "무엇", "무엇때문에", "물론", "및", "바꾸어말하면",
                "바꾸어말하자면", "바꾸어서 말하면", "바꾸어서 한다면", "바꿔 말하면", "바로", "바와같이", "밖에 안된다", "반대로", "반대로 말하자면", "반드시", "버금",
                "보는데서", "보다더", "보드득", "본대로", "봐", "봐라", "부류의 사람들", "부터", "불구하고", "불문하고", "붕붕", "비걱거리다", "비교적", "비길수 없다",
                "비로소", "비록", "비슷하다", "비추어 보아", "비하면", "뿐만 아니라", "뿐만아니라", "뿐이다", "삐걱", "삐걱거리다", "사", "삼", "상대적으로 말하자면",
                "생각한대로", "설령", "설마", "설사", "셋", "소생", "소인", "솨", "쉿", "습니까", "습니다", "시각", "시간", "시작하여", "시초에", "시키다",
                "실로",
                "심지어", "아", "아니", "아니나다를가", "아니라면", "아니면", "아니었다면", "아래윗", "아무거나", "아무도", "아야", "아울러", "아이", "아이고",
                "아이구",
                "아이야", "아이쿠", "아하", "아홉", "안 그러면", "않기 위하여", "않기 위해서", "알 수 있다", "알았어", "앗", "앞에서", "앞의것", "야", "약간",
                "양자",
                "어", "어기여차", "어느", "어느 년도", "어느것", "어느곳", "어느때", "어느쪽", "어느해", "어디", "어때", "어떠한", "어떤", "어떤것", "어떤것들",
                "어떻게", "어떻해", "어이", "어째서", "어쨋든", "어쩔수 없다", "어찌", "어찌됏든", "어찌됏어", "어찌하든지", "어찌하여", "언제", "언젠가", "얼마",
                "얼마 안 되는 것", "얼마간", "얼마나", "얼마든지", "얼마만큼", "얼마큼", "엉엉", "에", "에 가서", "에 달려 있다", "에 대해", "에 있다", "에 한하다",
                "에게", "에서", "여", "여기", "여덟", "여러분", "여보시오", "여부", "여섯", "여전히", "여차", "연관되다", "연이서", "영", "영차", "옆사람",
                "예",
                "예를 들면", "예를 들자면", "예컨대", "예하면", "오", "오로지", "오르다", "오자마자", "오직", "오호", "오히려", "와", "와 같은 사람들", "와르르",
                "와아", "왜", "왜냐하면", "외에도", "요만큼", "요만한 것", "요만한걸", "요컨대", "우르르", "우리", "우리들", "우선", "우에 종합한것과같이", "운운",
                "월",
                "위에서 서술한바와같이", "위하여", "위해서", "윙윙", "육", "으로", "으로 인하여", "으로서", "으로써", "을", "응", "응당", "의", "의거하여",
                "의지하여",
                "의해", "의해되다", "의해서", "이", "이 되다", "이 때문에", "이 밖에", "이 외에", "이 정도의", "이것", "이곳", "이때", "이라면", "이래",
                "이러이러하다", "이러한", "이런", "이럴정도로", "이렇게 많은 것", "이렇게되면", "이렇게말하자면", "이렇구나", "이로 인하여", "이르기까지", "이리하여",
                "이만큼",
                "이번", "이봐", "이상", "이어서", "이었다", "이와 같다", "이와 같은", "이와 반대로", "이와같다면", "이외에도", "이용하여", "이유만으로", "이젠",
                "이지만",
                "이쪽", "이천구", "이천육", "이천칠", "이천팔", "인 듯하다", "인젠", "일", "일것이다", "일곱", "일단", "일때", "일반적으로", "일지라도",
                "임에 틀림없다",
                "입각하여", "입장에서", "잇따라", "있다", "자", "자기", "자기집", "자마자", "자신", "잠깐", "잠시", "저", "저것", "저것만큼", "저기", "저쪽",
                "저희", "전부", "전자", "전후", "점에서 보아", "정도에 이르다", "제", "제각기", "제외하고", "조금", "조차", "조차도", "졸졸", "좀", "좋아",
                "좍좍",
                "주룩주룩", "주저하지 않고", "줄은 몰랏다", "줄은모른다", "중에서", "중의하나", "즈음하여", "즉", "즉시", "지든지", "지만", "지말고", "진짜로",
                "쪽으로",
                "차라리", "참", "참나", "첫번째로", "쳇", "총적으로", "총적으로 말하면", "총적으로 보면", "칠", "콸콸", "쾅쾅", "쿵", "타다", "타인", "탕탕",
                "토하다", "통하여", "툭", "퉤", "틈타", "팍", "팔", "퍽", "펄렁", "하", "하게될것이다", "하게하다", "하겠는가", "하고 있다", "하고있었다",
                "하곤하였다", "하구나", "하기 때문에", "하기 위하여", "하기는한데", "하기만 하면", "하기보다는", "하기에", "하나", "하느니", "하는 김에", "하는 편이 낫다",
                "하는것도", "하는것만 못하다", "하는것이 낫다", "하는바", "하더라도", "하도다", "하도록시키다", "하도록하다", "하든지", "하려고하다", "하마터면",
                "하면 할수록",
                "하면된다", "하면서", "하물며", "하여금", "하여야", "하자마자", "하지 않는다면", "하지 않도록", "하지마", "하지마라", "하지만", "하하", "한 까닭에",
                "한 이유는", "한 후", "한다면", "한다면 몰라도", "한데", "한마디", "한적이있다", "한켠으로는", "한항목", "할 따름이다", "할 생각이다", "할 줄 안다",
                "할 지경이다", "할 힘이 있다", "할때", "할만하다", "할망정", "할뿐", "할수있다", "할수있어", "할줄알다", "할지라도", "할지언정", "함께", "해도된다",
                "해도좋다", "해봐요", "해서는 안된다", "해야한다", "해요", "했어요", "향하다", "향하여", "향해서", "허", "허걱", "허허", "헉", "헉헉", "헐떡헐떡",
                "형식으로 쓰여", "혹시", "혹은", "혼자", "훨씬", "휘익", "휴", "흐흐", "흥", "힘입어", "그거", "진짜", "정말", "이미", "제대로", "제발",
                "니" "기", "이제", "그냥"]

    fonts = "NotoSansKR-Bold.otf"

    # remove stopwords from the nouns_list
    nouns_txt = [nouns_txt[i] for i in range(len(nouns_txt)) if nouns_txt[i] not in stopword]

    print("Completed removing stopwords.")

    icon = Image.open("mask.png")
    icon.putalpha(255)
    mask = Image.new("RGB", icon.size, (255, 255, 255))
    mask.paste(icon, icon)
    mask = np.array(mask)

    unique_string = (" ").join(nouns_txt)

    wordcloud = WordCloud(width=2048, height=1024, colormap='bwr', background_color="black", font_path=fonts,
                          max_words=500, collocations=False).generate(unique_string)
    plt.figure(figsize=(15, 8))
    plt.axis("off")

    # save the wordcloud image
    wordcloud.to_file("result.png")

    # sort the nouns_list by frequency
    apperernc = []
    words = []
    for i in range(len(nouns_txt)):
        if nouns_txt[i] not in words:
            words.append(nouns_txt[i])
            apperernc.append(1)
        else:
            apperernc[words.index(nouns_txt[i])] += 1

    # sort the words list by frequency
    apperernc, words = (list(t) for t in zip(*sorted(zip(apperernc, words))))
    # inverse the list
    apperernc = apperernc[::-1]
    words = words[::-1]

    print("Completed drawing wordcloud.\n")


# function that renders wordcloud using data from csv file (for hashtags)
def render_hashtag():
    global words, apperernc
    print("Started rendering")
    df = pd.read_csv('data.csv')

    hashtags = []

    for i in range(len(df["hashtags"])):
        tags = df["hashtags"].loc[i]

        tags = ast.literal_eval(tags)
        # Create a list of hashtags

        for i in range(len(tags)):
            hashtags.append(tags[i]["text"])

    print("Completed reading data.csv")

    stopwords = ["팔로우", "RT", "이벤트", "RT및", "섹트", "RT이벤트", "섹스"]
    hashtags = [hashtags[i] for i in range(len(hashtags)) if hashtags[i] not in stopwords]
    fonts = "NotoSansKR-Bold.otf"

    print("Completed filtering hashtags.")

    unique_string = (" ").join(hashtags)
    wordcloud = WordCloud(width=2048, height=1024, colormap='summer', background_color="black", font_path=fonts,
                          max_words=500, collocations=False).generate(unique_string)
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")

    # save image to a file
    wordcloud.to_file("hashtag.png")

    # sort the nouns_list by frequency
    apperernc = []
    words = []
    for i in range(len(hashtags)):
        if hashtags[i] not in words:
            words.append(hashtags[i])
            apperernc.append(1)
        else:
            apperernc[words.index(hashtags[i])] += 1

    # sort the hashtag list by frequency
    apperernc, words = (list(t) for t in zip(*sorted(zip(apperernc, words))))
    # inverse the list
    apperernc = apperernc[::-1]
    words = words[::-1]
    print("Completed drawing wordcloud.\n")


# function that sends a tweet with the wordcloud image
def post_words():
    print("Started posting.")
    global apperernc, words, to_pull
    # get time in kst time zone with pytz
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))
    year = now.year
    month = now.month
    day = now.day

    status = f"""📌 {year}년 {month}월 {day}일 한복 관련 단어 트렌드 입니다.

🏆 한복 관련 단어 랭킹:
🥇 {words[1]} - {apperernc[1]}회
🥈 {words[2]} - {apperernc[2]}회
🥉 {words[3]} - {apperernc[3]}회

트윗 {to_pull}개로 분석된 결과입니다."""

    update_status(status, "result.png")


def post_hashtag():
    print("Started posting.")
    global apperernc, words, to_pull
    # get time in kst time zone with pytz
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))
    year = now.year
    month = now.month
    day = now.day

    status = f"""📌 {year}년 {month}월 {day}일 한복 관련 해시테그 트렌드 입니다.

🏆 한복 해시테그 단어 랭킹:
🥇 #{words[1]} - {apperernc[1]}회
🥈 #{words[2]} - {apperernc[2]}회
🥉 #{words[3]} - {apperernc[3]}회

    트윗 {to_pull}개로 분석된 결과입니다."""

    update_status(status=status, filename="hashtag.png")


def update_status(status, filename):
    try:
        api.update_status_with_media(status=status, filename=filename)
        print("Completed posting.\n")
    except:
        print("Failed posting. Trying again in 2 seconds.")
        time.sleep(2)
        update_status(status, filename)


# function that archives the wordcloud image and the csv file
def archive():
    print("Started archiving.")
    # rename the file
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second

    os.rename("result.png", f"{year}-{month}-{day}-{hour}-{minute}-{second}-result.png")
    os.rename("hashtag.png", f"{year}-{month}-{day}-{hour}-{minute}-{second}-hashtag.png")
    os.rename("data.csv", f"{year}-{month}-{day}-{hour}-{minute}-{second}.csv")
    # move the file to the archive folder
    shutil.move(f"{year}-{month}-{day}-{hour}-{minute}-{second}-result.png", "archive/words")
    shutil.move(f"{year}-{month}-{day}-{hour}-{minute}-{second}-hashtag.png", "archive/tags")
    shutil.move(f"{year}-{month}-{day}-{hour}-{minute}-{second}.csv", "archive/csv")
    print("Completed archiving.\n")


def start():
    print("""============================================
Timed Bot Activation
============================================""")
    get_data()
    render_words()
    post_words()
    render_hashtag()
    post_hashtag()
    archive()
    print("""============================================
Finished Loop.
============================================""")


# start the bot
schedule.every().day.at("00:00").do(start)

print("Bot Loaded!")
while True:
    schedule.run_pending()
    time.sleep(1)
