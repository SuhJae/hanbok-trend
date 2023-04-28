import time
from datetime import datetime, timedelta

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import redis
import schedule
import tweepy
from tqdm import tqdm

# Redis password (Leave blank if not set)
redis_pass = ''

# Twitter API credentials
# For more information, visit https://docs.tweepy.org/en/stable/authentication.html?highlight=OAuth1UserHandler#tweepy.OAuth1UserHandler
auth = tw.OAuth1UserHandler(
    "consumer_key", "consumer_secret",
    "access_token", "access_token_secret"
)
api = tweepy.API(auth)

# variables
r = redis.Redis(host='localhost', port=6379, db=1, password=redis_pass)
days = 7


def number_format(number):
    return ("{:,}".format(number))


def render():
    global days, r
    print("Collecting data...")

    count = []
    time = []

    # count keys generated in the last 7 days with 1 hour interval
    for i in tqdm(range(days * 24)):
        today = datetime.now()
        # subtract i hours from today
        hour = today - timedelta(hours=i)

        # get keys generated on that day
        key = hour.strftime("%Y%m%d_%H")

        # try to get cached value
        if r.exists(f'cached:{key}'):
            counting = int(r.get(f'cached:{key}'))
        else:
            counting = len(r.keys(key + "*"))
            r.set(f'cached:{key}', counting)
        count.append(counting)
        time.append(hour.strftime('%d일 %H시'))

    # invert the list
    count.reverse()
    time.reverse()

    print("Rendering graph...")

    # draw line chart

    plt.figure(figsize=(15, 5), facecolor='black')

    # set font to IBMPlexSansKR-Bold.ttf
    font_path = 'IBMPlexSansKR-Bold.ttf'
    font_manager.fontManager.addfont(font_path)
    prop = font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = prop.get_name()

    # set background color to black
    ax = plt.axes()
    ax.set_facecolor('#080808')

    # only show x axis labels every 0:00 of the day
    plt.xticks(range(0, len(time), 24), time[::24], color='#9598A1', fontsize=20)
    plt.yticks(color='#9598A1', fontsize=15)

    plt.plot(time, count, color='#2A62FF', linewidth=1)

    # add grid
    plt.grid(color='#2A2E39', linestyle='-', linewidth=0.5)

    # fill the area under the line with alpha value gradient
    background_color = '#2A62FF'

    plt.fill_between(time, count, color=background_color, alpha=0.2)

    plt.title('한복 트윗 수', color='white', fontsize=20)

    # save the image
    plt.savefig('graph.png')
    # reset the plot
    plt.clf()
    update_header()


def update_header():
    print("Updating profile...")
    # update header image
    description = f"""매일 한복 관련 단어들의 트렌드를 전합니다.
지금까지 분석된 트윗: {number_format(r.dbsize())}개"""
    api.update_profile_banner('graph.png')

    # update bio
    api.update_profile(description=description, location="마지막 업데이트: " + datetime.now().strftime("%d일 %H시 %M분"))

    now = datetime.now()
    next_update = now + timedelta(hours=1)
    print(f"Done!")


render()

# run every hour at 0 minute
schedule.every().hour.at(":00").do(render)

while True:
    schedule.run_pending()
    time.sleep(5)
