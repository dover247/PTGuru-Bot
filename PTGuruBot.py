"""Learning Penetration Testing Community Bot."""
import logging
import asyncio
import re
import json
import hashlib
import datetime
import time
import discord
import aiohttp
import feedparser

# Logging Capability
logging.basicConfig(filename="gurubot-log.txt",
                    level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s [+]%(message)s")
LOGGER = logging.getLogger()

# Client
CLIENT = discord.Client()

# Bot Responses
AUTHOR = """**Learning Penetration Testing

The Penetration Testing Community**"""

# Feed Sources
FEEDS_FILE = open("feedlist.json", "r+")
FEED_LIST = json.load(FEEDS_FILE)
# timers
FEED_UPDATE_DELTA = 60

def get_datetime(var):
    """Get """
    if isinstance(var, datetime.datetime):
        publish_date = var
    elif isinstance(var, time.struct_time):
        publish_date = datetime.datetime(*var[:6])
    return publish_date

async def get_feed_content(url):
    """Get Feed Content"""
    async with aiohttp.get(url) as resp:
        if resp.status == 200:
            return await resp.text()

def get_channel(channel):
    """Get the discord channel object from channel name"""
    if channel == "news":
        channel_id = 288834230618816516 #278244337752735744
    elif channel == "ctf":
        channel_id = 288834230618816516 #274925767924776960
    return discord.Object(id=str(channel_id))

# Updates Feeds
async def update_all_feeds():
    """Update feeds."""
    await CLIENT.wait_until_ready()
    feed_types = FEED_LIST.items()
    while not CLIENT.is_closed:
        for i in feed_types:
            await post_feeds(i[1])
        FEEDS_FILE.seek(0)
        json.dump(FEED_LIST, FEEDS_FILE, indent="\t")
        FEEDS_FILE.truncate()
        await asyncio.sleep(FEED_UPDATE_DELTA)


# Posts Feeds
async def post_feeds(feeds_dict):
    """Post All Feeds."""
    try:
        channel = get_channel(feeds_dict["postChannel"])
        feed_color = int(feeds_dict["color"], 0)
        for feed in feeds_dict["feeds"]:
            content = await get_feed_content(feed["url"])
            if not content:
                continue
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            if "hash" in feed:
                current_hash = feed["hash"]
                if current_hash == content_hash:
                    continue
            feed["hash"] = content_hash
            feeder = feedparser.parse(content)
            items = feeder.entries
            if "items" not in feed:
                feed["items"] = {}
            for item in reversed(items):
                item_id_node = item[feed["idNode"]]
                if "idPattern" in feed and feed["idPattern"]:
                    matches = re.search(feed["idPattern"], item_id_node)
                    item_id = matches.group(1)
                else:
                    item_id = item_id_node
                if not item_id.isdigit():
                    item_id = hashlib.md5(item_id.encode('utf-8')).hexdigest()
                if item_id not in feed["items"]:
                    if 'published_parsed' in item:
                        publish_date = get_datetime(item.published_parsed)
                    elif 'updated_parsed' in item:
                        publish_date = get_datetime(item.updated_parsed)
                    elif 'published_parsed' in feeder.feed:
                        publish_date = get_datetime(feeder.feed.published_parsed)
                    elif 'updated_parsed' in feeder.feed:
                        publish_date = get_datetime(feeder.feed.updated_parsed)
                    try:
                        publish_date
                    except NameError:
                        publish_date = datetime.datetime.now()
                    feed["items"][item_id] = publish_date.isoformat()
                    await feed_procedure(item, channel, feed["prefix"]+item_id,
                                         publish_date, feed_color)
    except Exception as ex:
        LOGGER.error("Feed Posting Failed.\n%s", ex)

# Feed Handler
async def feed_procedure(item, channel, item_id, publish_date, feed_color):
    """Action taken upon receiving a feed."""
    embed = discord.Embed(title=item.title,
                          description=re.sub(r'(&lt;|<).*?(&gt;|>)', '', item.summary),
                          url=item.link, colour=feed_color,
                          timestamp=publish_date)
    embed.set_footer(text=item_id)
    await CLIENT.send_message(channel, embed=embed)


# After Client Connection
@CLIENT.event
async def on_ready():
    """After Initialzation."""
    LOGGER.info("Initialzation Complete..")
    LOGGER.info("Guru! Guru!.")


# Bot Capabilities Upon Sent Message
@CLIENT.event
async def on_message(message):
    """Action Taken Upon Messenge Sent."""
    LOGGER.info("%s Sent:", message.author)
    LOGGER.info("Message: %s", message.content)

    if message.content.startswith("!!author"):
        await CLIENT.send_message(message.channel, AUTHOR)

    if message.content.startswith("!!help"):
        await CLIENT.send_message(message.channel, "Help")

    if message.content.startswith("!!joinredteam5"):
        redteam5_about_page = open("RedTeam5.txt", "r").read()
        with open("malware-image.jpg", "rb") as community_logo:
            await CLIENT.send_message(message.channel, redteam5_about_page)
            await CLIENT.send_file(message.channel, community_logo)


CLIENT.loop.create_task(update_all_feeds())
# Grabs Token For Authentication
with open("_secret.token.txt", 'r') as fh:
    TOKEN = fh.read().strip()
CLIENT.run(TOKEN)
