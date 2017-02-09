import feedparser
import discord
import logging
import asyncio
import time
import re


#Logging Capability
logging.basicConfig(filename="gurubot-log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s [+]%(message)s")
log = logging.getLogger()

# Client
client = discord.Client()

# Bot Responses
author = "**Learning Penetration Testing\n\nThe Penetration Testing Community**"
Help = "**!!author\n!!joinredteam5**"

# Feed Sources
newslist = open("newslist.txt", "r").readlines()
cve_feed = "http://www.cvedetails.com/vulnerability-feed.php?vendor_id=0&product_id=0&version_id=0&orderby=2&cvssscoremin=0"
ctf_upcoming_feed = "https://ctftime.org/event/list/upcoming/rss/"

# Channel IDs
news_channel = "278244337752735744"
vulnerability_channel = "278244156759867392"
ctf_channel = "274925767924776960"

# timers
FEED_UPDATE_DELTA = 3600

@client.event
# After Client Connection
async def on_ready():
    log.info("Initialzation Complete..")
    log.info("Guru! Guru!.")
    await update_all_feeds()

# Updates Feeds
async def update_all_feeds():
    while True:
        await post_feeds(ctf_upcoming_feed, ctf_channel)
        await post_feeds(cve_feed, vulnerability_channel)
        await post_feeds(newslist, news_channel)
        asyncio.sleep(FEED_UPDATE_DELTA)

# Posts Feeds
async def post_feeds(feed, channel):
    if not feed == str:
        for feed_source in feed:
            feeder = feedparser.parse(feed_source.strip())
            await feed_procedure(feeder, channel)
    else:
        feeder = feedparser.parse((log.info(feed_source.strip())))
        await feed_procedure(feeder, channel)

# Feed Handler
async def feed_procedure(feeder, channel):
    entry = feeder.entries[0]
    args = [entry.title, entry.summary, entry.link]
    msg = "**---New Post!---\n{}\n\n{}\n{}**".format(*args)
    await client.send_message(client.get_channel(channel), re.sub("<.*?>", "", msg))

# Bot Capabilities Upon Sent Message
@client.event
async def on_message(message):
    log.info("{} Sent:".format(message.author))
    log.info("Message: {}".format(message.content))

    if message.content.startswith("!!author"):
        await client.send_message(message.channel, author)

    if message.content.startswith("!!help"):
        await client.send_message(message.channel, Help)

    if message.content.startswith("!!joinredteam5"):
        redteam5_about_page = open("RedTeam5.txt", "r").read()
        with open("malware-image.jpg", "rb") as community_logo:
            await client.send_message(message.channel, redteam5_about_page)
            await client.send_file(message.channel, community_logo)

# Grabs Token For Authentication
with open("_secret.token.txt", 'r') as fh:
    token = fh.read().strip()
client.run(token)
