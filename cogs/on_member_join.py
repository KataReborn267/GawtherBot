import disnake
import sqlite3 as sql
import json
import random

from disnake.ext import commands
from Paginator import CreatePaginator
from helpers import get_guild_id


class OnMemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = disnake.Embed(
            color=disnake.Colour.random(),
            title="Welcome To Gawther!",
            description=f"Hi, {member.display_name}! Welcome to Gawther! Please Read Below To Find Out More About Us!"
        ).set_thumbnail(
            url = self.bot.user.avatar
        )

        all_embeds = []
        all_embeds.insert(0,embed)

        with open('./json_files/new_member_info.json', 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

            for i in data["information"].keys():
                item_name = data["information"][i]["name"]
                item_value = data["information"][i]["value"]

                all_embeds.append(disnake.Embed(color=disnake.Colour.random(),title=item_name,description=item_value).set_thumbnail(url=self.bot.user.avatar))

            all_embeds.insert(
                len(all_embeds)+1, 
                disnake.Embed(
                    color = disnake.Colour.random(),
                    title="In Addition. . .",
                    description="In Addition to those values above, we also would like to go over some rules for the community with you",
                ).set_thumbnail(
                    url = self.bot.user.avatar
                )
            )

        with open('./json_files/rules.json','r',encoding='utf-8-sig') as f:
            data = json.load(f)

            for line in data["rules"]:
                title = data["rules"][line]["title"]
                rule = data["rules"][line]["rule"]

                all_embeds.append(disnake.Embed(color=disnake.Colour.random(),title=title,description=rule).set_thumbnail(url=self.bot.user.avatar))

        all_embeds.insert(
            len(all_embeds)+1, 
            disnake.Embed(
                color = disnake.Colour.random(),
                title="What Do I Do Now?",
                description="If you agree to the rules, then please respond with Confirm. Otherwise, respond with Deny"
            ).set_thumbnail(
                url = self.bot.user.avatar
            ).set_footer(
                text="If you cannot access the discord after you've responded with Confirm, please type `/reconfirm`."
            )
        )

        await member.send(embed=all_embeds[0],view=CreatePaginator(all_embeds,member.id,None))
        choice = await self.bot.wait_for('message')

        welcome_channel = disnake.utils.get(
            member.guild.text_channels, name="welcome_members")

        all_quotes = []

        with sql.connect('./databases/quotes.db') as quotesDb:
            cur = quotesDb.cursor()

            all_items = cur.execute(
                'SELECT quote, author FROM quotes').fetchall()

        for line in all_items:
            all_quotes.append(f"{line[0]} --{line[1]}")

        quote = random.choice(all_quotes) if all_quotes else "Welcome Aboard! We're Happy To Have You!"

        if choice.content.lower() == "confirm":
            member_role = disnake.utils.get(
                member.guild.roles, name="Member")
            await member.add_roles(member_role)

            with sql.connect('./databases/members.db') as mdb:
                cur = mdb.cursor()

                current_members = cur.execute(
                    'SELECT id FROM profile').fetchall()

                if member.id not in current_members:
                    srch = 'INSERT INTO profile(id,quote,mutes,bans,warnings,kicks,dob,color,bank) VALUES (?,?,?,?,?,?,?,?,?)'
                    val = (member.id, "None", 0, 0, 0, 0, "None", "None", 1500)

                    cur.execute(srch, val)

                    await member.send("You Have Been Successfully Made A Member! Please Enjoy Your $1500.00GB (Gawther Bucks) Welcome Bonus!")

                    embed = disnake.Embed(
                        color=disnake.Colour.green(),
                        title=f"Welcome {member.display_name}",
                        description="We're Pleased To Have You Aboard! Please Enjoy Your Stay! Remember: If you have any problems, please get in touch with Support!"
                    ).set_footer(text=quote).set_thumbnail(url=member.avatar)

                    await welcome_channel.send(embed=embed)
                else:
                    await member.send("There was an issue with adding you to the database. Please get in touch with support!")
        else:
            await member.send("Are you sure you want to deny the rules? Y/N")
            choice = await self.bot.wait_for('message')

            if choice.content.lower() == "y":
                await member.guild.kick(member, "Denied Confirmation To Rules")
            else:
                await self.on_member_join(member)

    @commands.slash_command(name="reconfirm",description="ONLY USABLE IN DM'S -- allows a member to restart the on_join event for new members")
    async def reconfirm(self,inter):
        await self.on_member_join(inter.author)
        return await inter.response.send_message("Check your DM's",delete_after=10)


def setup(bot):
    bot.add_cog(OnMemberJoin(bot))
