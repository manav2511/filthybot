from datetime import datetime

import discord
from discord.ext import commands

from osuapi import OsuApi, ReqConnector

from dateutil.relativedelta import relativedelta

class OsuModule:
    def __init__(self, client):
        self.client     = client
        self.database   = self.client.database
        self.api        = OsuApi(self.database.get_osu_api_key(), connector=ReqConnector())

    # Completed with Rich embed.
    @commands.command(name='osu')
    async def osu(self, ctx, *params, member: discord.Member = None):
        if member is None and len(params) == 0:
            discord_id = ctx.message.author.id

            self.database.cursor.execute("SELECT `osu_id` FROM `users` WHERE `discord_id` = ?",
                                         (discord_id,))
            osu_id = self.database.cursor.fetchone()[0]

            embed = self.display_profile(osu_id)
            await ctx.send(embed=embed)

        elif len(params) > 0:
            for osu_id in params:
                embed = self.display_profile(osu_id)
                await ctx.send(embed=embed)

        if member is not None:
            print(member.id)
            self.database.cursor.execute("SELECT `osu_id` FROM `users` WHERE `discord_id` = ?", (member.id,))

            osu_id = self.database.cursor.fetchone()[0]

            embed = self.display_profile(osu_id)
            await ctx.send(embed=embed)

    @commands.command(name='top')
    async def top(self, ctx, *params):
        (user, amt) = self.params_seperator(ctx, *params)
        embed = self.top_scores(user, amt)
        await ctx.send(embed=embed)

    @commands.command(name='recent')  # Completed With Rich Embed.
    async def recent(self, ctx, *params):
        (user, amt) = self.params_seperator(ctx, *params)
        embed = self.recent_scores(user, amt)
        await ctx.send(embed=embed)

    @commands.command(name='set')
    async def set(self, ctx, param):
        discord_id = ctx.message.author.id
        osu_id = self.api.get_user(param)[0].user_id
        self.database.cursor.execute("SELECT `osu_id` FROM `users` WHERE `discord_id` = ?", (discord_id,))
        data = self.database.cursor.fetchone()
        if data is None:
            self.database.cursor.execute("INSERT INTO `users`(`discord_id`, `osu_id`, `days`, `total`) VALUES (?, ?, 0, 0)", (discord_id, osu_id))
            self.database.db.commit()
            title = 'Succesfully set {} IGN as {}'.format(ctx.message.author, param)
            embed = discord.Embed(title=title, colour=0xDEADBF)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Record Already Exists")

    @commands.command(name='compare')
    async def compare(self, ctx, user1, user2):
        embed = self.check(user1, user2)
        await ctx.send(embed=embed)

    @commands.command(name='topr')
    async def topr(self, ctx, *params):
        (user, amt) = self.params_seperator(ctx, *params)
        embed = self.recent_top(user, amt)
        await ctx.send(embed=embed)

    def display_profile(self, param):
        # Obtaining Profile from Paramerter.
        profile = self.api.get_user(param)

        # Local Stuff
        title = "osu! Profile for " + profile[0].username
        thumbnail = "https://a.ppy.sh/" + str(profile[0].user_id)
        user_url = "https://osu.ppy.sh/users/" + str(profile[0].user_id)

        # Embed Creation.
        embed = discord.Embed(title=title, timestamp=datetime.utcnow(),
                              url=user_url,
                              color=0xFF0418,
                              footer="Osu India bot v.1.0"
                              )

        # thumbnails
        embed.set_thumbnail(url=thumbnail)
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
        embed.add_field(name="Country Rank", value='#' + str(
            profile[0].pp_country_rank), inline=True)
        return embed

    def top_scores(self, user, amt):
        # Api Call
        scores = self.api.get_user_best(user, limit=amt)

        # Local Stuff.
        title = "Top {} Scores for {}".format(amt, user)
        count = 1

        # Embed
        embed = discord.Embed(title=title, timestamp=datetime.utcnow(),
                              color=0xFF0418,
                              footer="Osu India bot v.1.0"
                              )
        # Fields.
        for score in scores:
            beatmap = self.api.get_beatmaps(beatmap_id=score.beatmap_id)
            Title = "#{}. {}[{}] +**{}**".format(count, beatmap[0].title,
                                                 beatmap[0].version, score.enabled_mods)
            Value = "PP:{}\n Played {}".format(score.pp, self.time_elapsed(str(score.date)))
            embed.add_field(name=Title, value=Value, inline=False)
            count += 1
        return embed

    def recent_scores(self, user, amt):
        scores = self.api.get_user_recent(user, limit=amt)
        title = "Recent {} scores for {}".format(amt, user)
        count = 1

        # Discord Embed Creation.
        embed = discord.Embed(title=title, timestamp=datetime.utcnow(),
                              color=0xFF0418,
                              footer="Osu India bot v0.2.0"
                              )

        # Looping over all Scores and adding fields.
        for score in scores:
            beatmap = self.api.get_beatmaps(beatmap_id=score.beatmap_id)
            name = "#{}. {}[{}] +**{}**".format(count, beatmap[0].title,
                                                 beatmap[0].version, score.enabled_mods)

            time_delta = str(score.date)

            value = "*Played {}\n SR: {}".format(
                self.time_elapsed(time_delta), str(beatmap[0].difficultyrating)[:5])

            embed.add_field(name=name, value=value, inline=False)
            count += 1

        return embed

    # Hacked this together using 3 lists, modifications needed
    def recent_top(self, user, amt):
        scores_list = []
        scores = self.api.get_user_best(user, limit=100)

        for i in range(100):
            scores_list.append((i + 1, scores[i]))

        # sort according to date
        scores_sorted = sorted(scores_list, key=lambda score: score[1].date, reverse=True)

        title = "Recent {} top scores for {}".format(amt, user)
        count = 1

        # Embed
        embed = discord.Embed(title=title, timestamp=datetime.utcnow(),
                              color=0xFF0418,
                              footer="Osu India bot v0.2.0"
                              )
        # Fields.
        for score in scores_sorted:
            if count > amt:
                break

            beatmap = self.api.get_beatmaps(beatmap_id=score[1].beatmap_id)
            name = "#{}. {}[{}] +**{}**".format(score[0], beatmap[0].title,
                                                 beatmap[0].version, score[1].enabled_mods)

            value = "PP:{}\n Played {}".format(score[1].pp, self.time_elapsed(str(score[1].date)))

            embed.add_field(name=name, value=value, inline=False)
            count += 1

        return embed

    def check(self, user1, user2):
        # major formatting required
        # to add avatar pic no clue how to
        p1 = self.api.get_user(user1)
        p2 = self.api.get_user(user2)

        title = "Comparing stats for " + user1 + " and " + user2

        desc = "\t\t" + user1 + "  |  " + user2 + "\t\t\n"  # \t or multiple spaces not working
        desc += "**Rank :**\t " + str(p1[0].pp_rank) + "  |  " + str(p2[0].pp_rank) + "\n"
        desc += "**Country Rank :**\t " + str(p1[0].pp_country_rank) + "  |  " + str(p2[0].pp_country_rank) + "\n"
        desc += "**PP :**\t " + str(p1[0].pp_raw) + "  |  " + str(p2[0].pp_raw) + "\n"
        desc += "**Accuracy :**\t " + str(p1[0].accuracy)[:5] + "  |  " + str(p2[0].accuracy)[:5] + "\n"

        score1 = self.api.get_user_best(user1, limit=1)
        score2 = self.api.get_user_best(user2, limit=1)

        desc += "**Top Play :**\t " + str(score1[0].pp) + "  |  " + str(score2[0].pp) + "\n"
        desc += "**Playcount :**\t " + str(p1[0].playcount) + "  |  " + str(p2[0].playcount) + "\n"

        embed = discord.Embed(title=title, description=desc, colour=0xDEADBF)

        return embed

    def time_elapsed(self, datestr):
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
            time_elapsed += "{} year{}, ".format(years, "s" if years != 1 else "")
        if (months > 0):
            time_elapsed += "{} month{}, ".format(months, "s" if months != 1 else "")
        if (days > 0):
            time_elapsed += "{} day{}, ".format(days, "s" if days != 1 else "")
        if (hours > 0):
            time_elapsed += "{} hour{}, ".format(hours, "s" if hours != 1 else "")
        if (minutes > 0):
            time_elapsed += "{} minute{}, ".format(minutes, "s" if minutes != 1 else "")
        if (seconds > 0):
            time_elapsed += "{} second{} ago".format(seconds, "s" if seconds != 1 else "")

        return time_elapsed

    def params_seperator(self, ctx, *params):
        # Default user AND default amount
        if len(params) == 0:
            self.database.cursor.execute("SELECT `osu_id` FROM `users` WHERE `discord_id` = ?",
                                         (ctx.message.author.id,))
            osu_id = self.database.cursor.fetchone()[0]
            if osu_id is None:
                return (None, None)
            user = self.api.get_user(osu_id)[0].username
            amt = 5
        # Only default amount
        elif len(params) == 1:
            user = self.tag_to_id(ctx)
            if user is False:
                return (None, None)
            if user is None:
                user = params[0]
            amt = 5
        # No defaults
        else:
            user = self.tag_to_id(ctx)
            if user is False:
                return (None, None)
            if user is None:
                user = params[0]
            amt = params[1]
        return (user, amt)

    def tag_to_id(self, ctx):
        user_list = ctx.message.mentions
        if len(user_list) == 0:
            return None
        else:
            user_id = user_list[0].id
            self.database.cursor.execute("SELECT `osu_id` FROM `users` WHERE `discord_id` = ?", (user_id,))
            osu_id = self.database.cursor.fetchone()[0]
            if osu_id is None:
                return False
            return self.api.get_user(osu_id)[0].username

    def new_recent(self, user_id):
        scores = self.api.get_user_best(user_id, limit=50)
        new_scores = []
        last_checked = datetime.now()  # need to save the last checked to a file
        scores_sorted = sorted(scores, key=lambda s: s.date, reverse=True)  # sort according to date
        for score in scores_sorted:
            if score.date > last_checked:
                new_scores.append(score)
            else:
                break
        print("New Recent was executed")
        return new_scores

    # def track(self):
    #     c.execute("SELECT OSU_ID FROM USERS")
    #     data = c.fetchall()
    #     scores_to_be_printed = []
    #     for x in data:
    #         new_scores = new_recent(x[0])
    #         if len(new_scores) == 0:
    #             continue
    #         else:
    #             scores_to_be_printed.append(new_scores)
    #     print("track was executed")
    #     return scores_to_be_printed

def setup(client):
    client.add_cog(OsuModule(client))
