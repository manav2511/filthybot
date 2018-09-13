import discord
from discord.ext import commands
from osuapi import OsuApi, ReqConnector
import requests
import os
import sys

apicode="92a4871f7a42d7015d58a9acf3dda2f662ba28db"
api = OsuApi(apicode, connector=ReqConnector())



def display(param):
	profile=api.get_user(param)
	print(profile)
	tit="Osu Profile for "+profile[0].username
	desc="Username: "+profile[0].username+"\n"+"PP: "+str(profile[0].pp_raw)+"\n"+"Rank: "+str(profile[0].pp_rank)+"\n"+"Playcount: "+str(profile[0].playcount)
	em = discord.Embed(title= tit, description=desc, colour=0xDEADBF)
	return em
	
def scoredisp(user,scores,amt):
	tit = "Top "+str(amt)+" scores for "+user
	desc=""
	count = 1
	for i in scores:
		bmp = api.get_beatmaps(beatmap_id=i.beatmap_id)
		desc = desc + str(count) + ".) " + bmp[0].title + "[" + bmp[0].version + "] " + str(i.enabled_mods) + " -- PP : " + str(i.pp) +  " Played on " + str(i.date) + "\n"   
		count+=1

	em = discord.Embed(title= tit, description=desc, colour=0xDEADBF)
	return em

def recentdisp(user,scores,amt):
	tit = "Recent "+str(amt)+" scores for "+user
	desc=""
	count = 1
	for i in scores:
		bmp = api.get_beatmaps(beatmap_id=i.beatmap_id)
		desc = desc + str(count) + ".) " + bmp[0].title + "[" + bmp[0].version + "] " + str(i.enabled_mods) + " Played on " + str(i.date) + "\n" 
		count+=1

	em = discord.Embed(title= tit, description=desc, colour=0xDEADBF)
	return em


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

