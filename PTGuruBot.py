import feedparser
import discord
import logging
import asyncio
import feedparser
import time
import re

#Logging Capability
logging.basicConfig(filename="gurubot-log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s [+]%(message)s")
log = logging.getLogger()

# Client
client = discord.Client()

# Bot Responses
author_name = """**Learning Penetration Testing

The Penetration Testing Community**"""

# Feed Sources
with open("newslist.txt", "r") as fh:
    newslist = [line for line in fh]
cve_feed = "http://www.cvedetails.com/vulnerability-feed.php?vendor_id=0&product_id=0&version_id=0&orderby=2&cvssscoremin=0"
ctf_upcoming = "https://ctftime.org/event/list/upcoming/rss/"

# Channel IDs
news_channel = "278244337752735744"
vulnerability_channel = "278244156759867392"
ctf_channel = "274925767924776960"


# timers
FEED_UPDATE_DELTA = 60

# Single Feeders


async def updatefeeds():
    while True:
        cve_feeder = feedparser.parse(cve_feed)
        ctf_feeder = feedparser.parse(ctf_upcoming)
        for feed_source in newslist:
            news_feeder = feedparser.parse(feed_source)
            await post_feeds(news_feeder)
        await post_feeds(ctf_feeder)
        await post_feeds(cve_feeder)
        await asyncio.sleep(FEED_UPDATE_DELTA)

@client.event
# After Client Connection
async def on_ready():
    log.info("Initialzation Complete..")
    log.info("Guru! Guru!.")
    await updatefeeds()

# InfoSec Feeds
async def post_feeds(feed):
    entry = feed.entries[0]
    args = [entry.title, entry.link]
    msg = "**{}**\n\n{}".format(*args)
    await client.send_message(client.get_channel(news_channel), msg)

# CVE Vulnerability Feed
async def post_vulnerabilities():
    entry = cve_feeder.entries[0]
    args = [entry.title, entry.summary, entry.link]
    msg = "**Newly Posted Vulnerability!!\n{}\n\n{}\n{}**".format(*args)
    await client.send_message(client.get_channel(vulnerability_channel), msg)

# Upcoming CTFs Feed "CTFtime.org"
async def post_upcoming_ctfs():
    entry = ctf_feeder.entries[0]
    args = [entry.title, re.sub("<.*?>", "", entry.summary)]
    msg = "**Newly Posted CTF!!\n\n{}\n\n{}**".format(*args)
    await client.send_message(client.get_channel(ctf_channel), msg)


@client.event
# Bot Capabilities Upon Sent Message
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


with open("_secret.token.txt", 'r') as fh:
    token = [line for line in fh][0]
client.run(token)
