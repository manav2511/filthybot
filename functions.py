import discord
from discord.ext import commands
from osuapi import OsuApi, ReqConnector
import requests
import os
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

api_read = open("osuapikey.txt")
apicode = api_read.readline().strip()
api = OsuApi(apicode, connector=ReqConnector())


def display_profile(param):
        # Obtaining Profile from Paramerter.
    profile = api.get_user(param)

    # Local Stuff
    Usertitle = "Osu Profile for " + profile[0].username
    thum = "https://a.ppy.sh/"+str(profile[0].user_id)+"?1528809158.jpeg"
    user_url = "https://osu.ppy.sh/users/"+str(profile[0].user_id)

    # Embed Creation.
    embed = discord.Embed(title=Usertitle, timestamp=datetime.utcnow(),
                          url=user_url,
                          color=0xFF0418,
                          footer="Osu India bot v.1.0"
                          )

    # thumbnails
    embed.set_thumbnail(url=thum)
    # PP
    embed.add_field(name="PP", value=str(profile[0].pp_raw), inline=True)
    # Rank
    embed.add_field(name="Rank", value='#' +
                    str(profile[0].pp_rank), inline=True)
    # Playcount
    embed.add_field(name="Playcount", value=str(
        profile[0].playcount), inline=True)
    # Accuracy
    embed.add_field(name="Accuracy", value=str(
        profile[0].accuracy)[:6], inline=True)
    # Country Indentification.
    embed.add_field(name="Country", value=str(profile[0].country), inline=True)
    # Country Rank.
    embed.add_field(name="Country Rank", value='#'+str(
        profile[0].pp_country_rank), inline=True)
    return embed


def Top_Scores(context, user, amt):
	#Api Call
    Scores = api.get_user_best(user, limit=amt)
	#Local Stuff.
    Usertitle = "Top {} Scores for {}".format(amt, user)
    count = 1
	#Embed
    embed = discord.Embed(title=Usertitle, timestamp=datetime.utcnow(),
                          color=0xFF0418,
                          footer="Osu India bot v.1.0"
                          )
	#Feilds.
    for var in Scores:
        beatmap = api.get_beatmaps(beatmap_id=var.beatmap_id)
        Title = "{}. {}[{}] +**{}**".format(count, beatmap[0].title,
                                       beatmap[0].version, var.enabled_mods)
        Value = "PP:{}\n Played {}".format(var.pp, time_elapsed(var.date))
        embed.add_field(name=Title, value=Value, inline=False)
        count += 1
    return embed


def recent_Scores(param, amt):
    scores = api.get_user_recent(param, limit=amt)
    Usertitle = "Recent {} scores for {}".format(amt, param)
    count = 1
    # Discord Embed Creation.
    embed = discord.Embed(title=Usertitle, timestamp=datetime.utcnow(),
                          color=0xFF0418,
                          footer="Osu India bot v.1.0"
                          )
    # Looping over All Scores and adding feilds.
    for var in scores:
        beatmap = api.get_beatmaps(beatmap_id=var.beatmap_id)
        Title = "{}. {}[{}] +**{}**".format(count, beatmap[0].title,
                                           beatmap[0].version, var.enabled_mods)

        Time_del = var.date
        Value = "*Played {}\n SR: {}".format(
            time_elapsed(Time_del), str(beatmap[0].difficultyrating)[:5])
        embed.add_field(name=Title, value=Value, inline=False)
        count += 1
    return embed

def check(user1,user2):
	#major formatting required
	#to add avatar pic no clue how to
	p1 = api.get_user(user1)
	p2 = api.get_user(user2)
	tit = "Comparing stats for " + user1 + " and " + user2	
	desc = "\t\t"+user1+"  |  "+user2+"\t\t\n"		#\t or multiple spaces not working
	desc = desc+"**Rank :**\t " + str(p1[0].pp_rank) + "  |  " + str(p2[0].pp_rank)+"\n"
	desc = desc+"**Country Rank :**\t " + str(p1[0].pp_country_rank) + "  |  " + str(p2[0].pp_country_rank)+"\n"
	desc = desc+"**PP :**\t " + str(p1[0].pp_raw) + "  |  " + str(p2[0].pp_raw)+"\n"
	desc = desc+"**Accuracy :**\t " + str(p1[0].accuracy)[:5] + "  |  " + str(p2[0].accuracy)[:5]+"\n"
	score1 = api.get_user_best(user1,limit=1)
	score2 = api.get_user_best(user2,limit=1)
	desc = desc+"**Top Play :**\t " + str(score1[0].pp) + "  |  " + str(score2[0].pp)+"\n"
	desc = desc+"**Playcount :**\t " + str(p1[0].playcount) + "  |  " + str(p2[0].playcount)+"\n"
	em = discord.Embed(title= tit, description=desc, colour=0xDEADBF)
	return em


def time_elapsed(datestr):
    parsed_date = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    today = datetime.utcnow()

    time_delta = relativedelta(today, parsed_date)

    years = abs(time_delta.years)
    months = abs(time_delta.months)
    days = abs(time_delta.days)
    hours = abs(time_delta.hours)
    minutes = abs(time_delta.minutes)
    seconds = abs(time_delta.seconds)

    time_elapsed = ""

    if (years > 0):
        time_elapsed.append("{} year{}, ".format(years, "s" if years!=1 else ""))
    if (months > 0):
        time_elapsed.append("{} month{}, ".format(months, "s" if months!=1 else ""))
    if (days > 0):
        time_elapsed.append("{} day{}, ".format(days, "s" if days!=1 else ""))
    if (hours > 0):
        time_elapsed.append("{} hour{}, ".format(hours, "s" if hours!=1 else ""))
    if (minutes > 0):
        time_elapsed.append("{} minute{}, ".format(minutes, "s" if minutes!=1 else ""))
    if (seconds > 0):
        time_elapsed.append("{} second{} ago".format(seconds, "s" if seconds!=1 else ""))

    return time_elapsed
