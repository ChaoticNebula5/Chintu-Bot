import html
import json
from datetime import datetime, timedelta

import numpy as np
import requests
from cogs.utils.db_utils import db_utils
from cogs.utils.db_utils import create_dict
from main_resources.item_use import *


class Currency(commands.Cog):
    """🤑 Everything related to da money 🤑"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.collection = database["currency"]
        self.utils = currency_utils(self.collection)
        self.db_utils = db_utils(self.collection,
                                 wallet=0,
                                 bank=0,
                                 bank_limit=0,
                                 commands=0,
                                 inventory=None,
                                 t_daily=0,
                                 t_weekly=0,
                                 t_monthly=0
                                 )
        self.defined_currencies = json.loads(
            open('./main_resources/Assets/currency_values.json', encoding='utf-8').read())
        self.items_by_id = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_id"]
        self.id_by_name = json.loads(
            open('./main_resources/Assets/shop_items.json', encoding='utf-8').read())["by_name"]
        self.paged_shop, self.pages = create_paged_shop(self.items_by_id)
        self.houses = {
            1: "5 of a kind",
            2: "4 of a kind",
            3: "3 of a kind and a pair",
            4: "2 pairs",
            5: "1 pair",
            6: "None of the accepted combinations"
        }
        self.prizes = {
            5: 2,
            4: 1.5,
            3: 1.3,
            2: 1.2,
            1: 1
        }
        self.quiz_categories = {
            "gk": 9,
            "books": 10,
            "film": 11,
            "music": 12,
            "theatre": 13,
            "tv": 14,
            "games": 15,
            "bgames": 16,
            "sci": 17,
            "cs": 18,
            "math": 19,
            "myth": 20,
            "sports": 21,
            "geography": 22,
            "history": 23,
            "pol": 24,
            "art": 25,
            "celeb": 26,
            "animals": 27
        }
        self.quiz_help_dict = {
            "gk": "General Knowldege",
            "books": "Books",
            "film": "Films",
            "music": "Music",
            "theatre": "Musicals and Theatre",
            "tv": "Television",
            "games": "Video Games",
            "bgames": "Board Games",
            "sci": "Science and Nature",
            "cs": "Computer Science",
            "math": "Mathematics",
            "myth": "Mythology",
            "sports": "Sports",
            "geography": "Geography",
            "history": "History",
            "pol": "Politics",
            "art": "Art",
            "celeb": "Celebrities",
            "animals": "Animals"
        }

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        await on_message(self.bot, message)

    @commands.command(name="daily")
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        """Daily dose of sweet cash 💰💰💰"""
        daily_time = self.collection.find_one({"_id": ctx.author.id}, {"t_daily": 1})

        if daily_time is None \
                or daily_time['t_daily'] == 0 \
                or (datetime.utcnow() - daily_time['t_daily']) >= timedelta(days=1):

            self.db_utils.initialize_template().add_operators(
                inc=create_dict(wallet=self.defined_currencies['daily']),
                set=create_dict(t_daily=datetime.utcnow())
            ).upsert_from_template(create_dict(_id=ctx.author.id), wallet=0, t_daily=0)

            emb = discord.Embed(title="Enjoy your daily cold hard cash 🤑",
                                description=f"{self.defined_currencies['daily']} coins were placed in your wallet!",
                                color=discord.Colour.green())
            emb.add_field(name="You can claim your daily again in:", value="24 hours")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(title="You have already claimed your daily coins", color=discord.Colour.red())
            del_time = (daily_time['t_daily'] + timedelta(days=1)) - datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            emb.add_field(name="You can claim your daily again in:",
                          value=f"{hours} hours, {minutes} minutes and {seconds} seconds")
            await ctx.send(embed=emb)
            raise CommandError

    @commands.command(name="weekly")
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def weekly(self, ctx: commands.Context):
        """Weekly dose of sweet cash 💰💰💰"""
        weekly_time = self.collection.find_one({"_id": ctx.author.id}, {"t_weekly": 1})

        if weekly_time is None \
                or weekly_time['t_weekly'] == 0 \
                or (datetime.utcnow() - weekly_time['t_weekly']) >= timedelta(days=7):
            self.db_utils.initialize_template().add_operators(
                inc=create_dict(wallet=self.defined_currencies['weekly']),
                set=create_dict(t_weekly=datetime.utcnow())
            ).upsert_from_template(create_dict(_id=ctx.author.id), wallet=0, t_weekly=0)
            emb = discord.Embed(title="Enjoy your weekly cold hard cash 🤑",
                                description=f"{self.defined_currencies['weekly']} coins were placed in your wallet!",
                                color=discord.Colour.green())
            emb.add_field(name="You can claim your weekly again in:", value="7 days")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(title="You have already claimed your weekly coins", color=discord.Colour.red())
            del_time = (weekly_time['t_weekly'] + timedelta(days=7)) - datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = (days * 24 + seconds // 3600) % 24
            minutes = (seconds % 3600) // 60
            # seconds = seconds % 60
            emb.add_field(name="You can claim your weekly again in:",
                          value=f"{days} days, {hours} hours and {minutes} minutes")
            await ctx.send(embed=emb)
            raise CommandError

    @commands.command(name="monthly")
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def monthly(self, ctx: commands.Context):
        """Monthly dose of sweet cash 💰💰💰"""
        monthly_time = self.collection.find_one({"_id": ctx.author.id}, {"t_monthly": 1})

        if monthly_time is None \
                or monthly_time['t_monthly'] == 0 \
                or (datetime.utcnow() - monthly_time['t_monthly']) >= timedelta(days=30):
            self.db_utils.initialize_template().add_operators(
                inc=create_dict(wallet=self.defined_currencies['monthly']),
                set=create_dict(t_monthly=datetime.utcnow())
            ).upsert_from_template(create_dict(_id=ctx.author.id), wallet=0, t_monthly=0)
            emb = discord.Embed(title="Enjoy your monthly cold hard cash 🤑",
                                description=f"{self.defined_currencies['monthly']} coins were placed in your wallet!",
                                color=discord.Colour.green())
            emb.add_field(name="You can claim your monthly again in:", value="30 days")
            await ctx.send(embed=emb)

        else:
            emb = discord.Embed(title="You have already claimed your monthly coins", color=discord.Colour.red())
            del_time = (monthly_time['t_monthly'] + timedelta(days=30)) - datetime.utcnow()
            days, seconds = del_time.days, del_time.seconds
            hours = (days * 24 + seconds // 3600) % 24
            minutes = (seconds % 3600) // 60
            # seconds = seconds % 60
            emb.add_field(name="You can claim your monthly again in:",
                          value=f"{days} days, {hours} hours and {minutes} minutes")
            await ctx.send(embed=emb)
            raise CommandError

    @commands.command(name="balance", aliases=['bal'])
    @commands.cooldown(rate=1, per=1.0, type=commands.BucketType.user)
    async def balance(self, ctx: commands.Context, targeted_user: discord.Member = None):
        """Check the balance of those pesky scrubs"""
        if targeted_user is None:
            targeted_user = ctx.author
        wallet_coins, bank_coins = self.utils.get_balance(targeted_user.id)
        desc_str = f"**Wallet: **" \
                   f"<a:chintucoin:839401482184163358>{wallet_coins}\n**Bank: **" \
                   f"<a:chintucoin:839401482184163358>{bank_coins}"
        emb = discord.Embed(title=f"**{targeted_user.display_name}'s Account details**", description=desc_str,
                            color=discord.Colour.green())
        if wallet_coins + bank_coins == 0:
            emb.set_footer(text="Poor much?")
        await ctx.send(embed=emb)

    @commands.command(name="withdraw", aliases=['with'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def withdraw(self, ctx: commands.Context, amount: str):
        wallet_coins, bank_coins = self.utils.get_balance(ctx.author.id)
        if bank_coins == 0:
            await ctx.send(f"{ctx.author.mention} Your bank account is empty lmfao")
            raise CommandError
        if amount.lower() == "max" or amount.lower() == "all":
            amount = bank_coins
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send(f"{ctx.author.mention} Enter a valid amount or max/all")
                raise CommandError
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} Enter a valid amount or max/all")
            raise CommandError
        if amount > bank_coins:
            await ctx.send(f"{ctx.author.mention} You do not have {amount} coins in your bank account")
            raise CommandError
        self.db_utils.initialize().add_operators(
            inc=create_dict(wallet=amount, bank=-amount)
        ).update_one(create_dict(_id=ctx.author.id))
        emb = discord.Embed(title=f"{ctx.author.display_name} Withdrew {amount} coins",
                            description=f"**Wallet: **<a:chintucoin:839401482184163358>"
                                        f"{wallet_coins + amount}\n**Bank: **<a:chintucoin:839401482184163358>"
                                        f"{bank_coins - amount}",
                            color=discord.Colour.green())
        await ctx.send(embed=emb)

    @commands.command(name="deposit", aliases=['dep'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def deposit(self, ctx: commands.Context, amount: str):
        wallet_coins, bank_coins = self.utils.get_balance(ctx.author.id)
        if wallet_coins == 0:
            await ctx.send(f"{ctx.author.mention} Your wallet is empty lmfao")
            raise CommandError
        if amount.lower() == "max" or amount.lower() == "all":
            amount = wallet_coins
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send(f"{ctx.author.mention} Enter a valid amount or max/all")
                raise CommandError
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} Enter a valid amount or max/all")
            raise CommandError
        if amount > wallet_coins:
            await ctx.send(f"{ctx.author.mention} You do not have {amount} coins in your wallet")
            raise CommandError
        self.db_utils.initialize().add_operators(
            inc=create_dict(wallet=-amount, bank=amount)
        ).update_one(create_dict(_id=ctx.author.id))
        emb = discord.Embed(title=f"{ctx.author.display_name} Deposited {amount} coins",
                            description=f"**Wallet: **"
                                        f"<a:chintucoin:839401482184163358>{wallet_coins - amount}\n**Bank: **"
                                        f"<a:chintucoin:839401482184163358>{bank_coins + amount}",
                            color=discord.Colour.green())
        await ctx.send(embed=emb)

    @commands.command(name="give", aliases=['pay'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def give(self, ctx: commands.Context, targeted_user: discord.Member, amount: int):
        """Give away your hard earned cash 🎁"""
        if ctx.author.id == targeted_user.id:
            await ctx.send(f"{ctx.author.mention}, you can't give coins to yourself. 😡")
            raise CommandError
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention}, enter a value greater than 0. You can't fool me. 😡")
            raise CommandError
        wallet_coins, bank_coins = self.utils.get_balance(ctx.author.id)
        if wallet_coins < amount or wallet_coins == 0:
            await ctx.send(f"{ctx.author.mention} You don't have enough coins lmao, get a job.")
            raise CommandError
        else:
            self.db_utils.initialize().add_operators(
                inc=create_dict(wallet=-amount)
            ).update_one(create_dict(_id=ctx.author.id))
            self.db_utils.initialize_template().add_operators(
                inc=create_dict(wallet=amount)
            ).upsert_from_template(create_dict(_id=targeted_user.id), wallet=0)
            await ctx.send(
                f"** {ctx.author.mention} gave {amount} coins to {targeted_user.display_name}  "
                f"<a:chintucoin:839401482184163358>**")

    @commands.command(name="shop")
    @commands.cooldown(rate=1, per=1.0, type=commands.BucketType.user)
    async def shop(self, ctx: commands.Context, page: int = 1):
        """See what treasures await your purchase"""
        if self.pages >= page >= 1:
            embed = self.paged_shop[page - 1].set_footer(text=f"Page {page} of {self.pages}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention} Enter a valid page number")
            raise CommandError

    @commands.command(name="gift")
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def gift(self, ctx: commands.Context, target_user: discord.Member, item: str, amount: int = 1):
        """Give away your precious items 🎁"""
        item_dict = None
        item_id = None
        item = item.lower()
        if item in self.items_by_id:
            item_dict = self.items_by_id[item]
            item_id = item
        elif item in self.id_by_name:
            item_dict = self.items_by_id[str(self.id_by_name[item])]
            item_id = str(self.id_by_name[item])

        if item_dict is not None and item_id is not None:
            if amount > 0:
                inventory = self.collection.find_one({"_id": ctx.author.id}, {"inventory": 1})
                if inventory is not None:
                    inventory = inventory["inventory"]
                    if item_id in inventory and inventory[item_id] >= amount:
                        embed = discord.Embed(
                            title=f"Do you want to gift {amount} {item_dict['name']} to {target_user.name}?",
                            description="React with 👍 within 15 seconds to confirm", color=discord.Colour.green())
                        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                        message = await ctx.send(embed=embed)
                        await message.add_reaction("👍")

                        def check(reaction, user):
                            return user.id == ctx.author.id and str(
                                reaction.emoji) == '👍' and reaction.message.id == message.id

                        try:
                            await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                            self.db_utils.initialize().add_operators(
                                inc={f"inventory.{item_id}": -amount}
                            ).update_one(create_dict(_id=ctx.author.id))
                            self.db_utils.initialize_template().add_operators(
                                inc={f"inventory.{item_id}": amount}
                            ).upsert_from_template(create_dict(_id=target_user.id), inventory=0)
                            await ctx.send(
                                f"{ctx.author.mention} You have successfully "
                                f"gifted {amount} {item_dict['name']} to {target_user.name}")
                        except asyncio.TimeoutError:
                            embed = discord.Embed(
                                title=f"Do you want to gift {amount} {item_dict['name']} to {target_user.name}?",
                                description="Gift failed. Please try again", color=discord.Colour.red())
                            embed.set_footer(text=f"Requested by {ctx.author.display_name}",
                                             icon_url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()
                            raise CommandError
                    else:
                        await ctx.send(f"{ctx.author.mention} Lmao you don't have {amount} {item_dict['name']} to"
                                       f" gift.")
                        raise CommandError
                else:
                    self.db_utils.initialize_template().insert_from_template(_id=ctx.author.id)
                    await ctx.send(f"{ctx.author.mention} Lmao you don't have {amount} {item_dict['name']} to gift.")
                    raise CommandError
            else:
                await ctx.send(f"{ctx.author.mention} Enter a valid amount")
                raise CommandError
        else:
            await ctx.send(f"{ctx.author.mention} Enter a valid item ID or name")
            raise CommandError

    @commands.command(name="buy")
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def buy(self, ctx: commands.Context, item, amount: int = 1):
        """Buy the items of your dreams from the shop <a:chintucoin:839401482184163358>"""
        item_dict = None
        item = item.lower()
        try:
            item = int(item)
            if str(item) in self.items_by_id:
                item_dict = self.items_by_id[str(item)]
        except Exception:
            if item in self.id_by_name:
                item_dict = self.items_by_id[str(self.id_by_name[item])]
                item = self.id_by_name[item]
        if item_dict is None:
            await ctx.send(f"{ctx.author.mention} Enter a valid item ID or name")
            raise CommandError
        if amount < 0:
            await ctx.send(f"{ctx.author.mention} Enter a valid amount")
            raise CommandError
        wallet_coins, bank_coins = self.utils.get_balance(ctx.author.id)
        if wallet_coins <= 0 or wallet_coins < self.items_by_id[str(item)]["value"] * amount:
            await ctx.send(
                f"{ctx.author.mention} You don't have enough money" +
                f" for buying {self.items_by_id[str(item)]['name']}. Get a job lmao.")
            raise CommandError

        embed = discord.Embed(
            title=f"Do you want to purchase {amount} {item_dict['name']} for {item_dict['value'] * amount}?",
            description="React with 👍 within 15 seconds to purchase", color=discord.Colour.green())
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")

        def check(reaction, user):
            return user.id == ctx.author.id and str(
                reaction.emoji) == '👍' and reaction.message.id == message.id

        try:
            await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            self.db_utils.initialize().add_operators(
                inc={"wallet": -item_dict["value"] * amount,
                     f"inventory.{str(item)}": amount}
            ).update_one(create_dict(_id=ctx.author.id))
            await ctx.send(
                f"{ctx.author.mention} You have successfully "
                f"purchased {amount} {item_dict['name']} for {item_dict['value'] * amount}")
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title=f"Do you want to purchase {amount} {item_dict['name']} for {item_dict['value'] * amount}?",
                description="Purchase failed. Please try again", color=discord.Colour.red())
            embed.set_footer(text=f"Requested by {ctx.author.display_name}",
                             icon_url=ctx.author.avatar_url)
            await message.edit(embed=embed)
            await message.clear_reactions()
            raise CommandError

    @commands.command(name="bet")
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def bet(self, ctx: commands.Context, amount: str):
        """Join in on some gambling action, similar to Klondike dice game"""
        wallet_coins, bank_coins = self.utils.get_balance(ctx.author.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount.lower() == "max" or amount.lower() == "all":
                if wallet_coins <= 0:
                    await ctx.send(f"{ctx.author.mention} Lmao you don't have enough coins to bet.")
                    raise CommandError
                if wallet_coins >= 250000:
                    amount = 250000
                else:
                    amount = wallet_coins
            else:
                await ctx.send(f"{ctx.author.mention} Enter a proper amount or max/all.")
                raise CommandError

        if 250000 >= amount >= 50:
            if wallet_coins >= amount and wallet_coins > 0:
                bot_pair, user_pair = find_pairs(np.random.randint(1, 6, 5)), find_pairs(np.random.randint(1, 6, 5))
                if bot_pair <= user_pair:
                    embed = discord.Embed(title=f"{ctx.author.display_name}'s losing bet",
                                          description=f"You lost {amount} coins",
                                          color=discord.Colour.red())
                    embed.add_field(name="Chintu rolled:", value=self.houses[bot_pair])
                    embed.add_field(name="You rolled:", value=self.houses[user_pair])
                    self.db_utils.initialize().add_operators(
                        inc=create_dict(wallet=-amount)
                    ).update_one(create_dict(_id=ctx.author.id))
                else:
                    embed = discord.Embed(title=f"{ctx.author.display_name}'s winning bet",
                                          description=f"You won {int(amount * self.prizes[bot_pair - user_pair] + amount)} coins",
                                          color=discord.Colour.green())
                    embed.add_field(name="Chintu rolled:", value=self.houses[bot_pair])
                    embed.add_field(name="You rolled:", value=self.houses[user_pair])
                    self.db_utils.initialize().add_operators(
                        inc=create_dict(wallet=int(amount * self.prizes[bot_pair - user_pair]))
                    ).update_one(create_dict(_id=ctx.author.id))
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{ctx.author.mention} Lmao you don't have enough coins to bet.")
                raise CommandError
        elif amount >= 250000:
            await ctx.send(f"{ctx.author.mention} If I let you bet more than 50,000 coins, you'd be broke in no time.")
            raise CommandError
        else:
            await ctx.send(f"{ctx.author.mention} Enter an amount greater than 50 coins")
            raise CommandError

    @commands.command(name="use")
    @commands.cooldown(rate=1, per=8.0, type=commands.BucketType.user)
    async def use(self, ctx: commands.Context, item):
        """Use the items you got there in your inventory"""
        item_dict = None
        item = item.lower()
        try:
            item = int(item)
            if str(item) in self.items_by_id:
                item_dict = self.items_by_id[str(item)]
        except Exception:
            if item in self.id_by_name:
                item_dict = self.items_by_id[str(self.id_by_name[item])]
                item = self.id_by_name[item]
        if item_dict:
            if item_dict['type'] == "item":
                await ctx.send("This item cannot be used.")
                raise CommandError
            inventory_dict = self.collection.find_one({"_id": ctx.author.id}, {"inventory": 1})
            if inventory_dict is not None and \
                    str(item) in inventory_dict["inventory"] and \
                    inventory_dict["inventory"][str(item)] > 0:
                try:
                    await eval(item_dict['type'] + '(self.bot, ctx, item_dict)')
                except Exception as e:
                    if not isinstance(e, CommandError):
                        await ctx.send(f"Could't use {item_dict['name']}. Please report this issue using $suggest.")
                    raise CommandError
            else:
                await ctx.send(
                    f"You do not have {item_dict['name']}. Buy it from the shop ($shop) before trying again.")
                raise CommandError
        else:
            await ctx.send(f"Could not find item with name or id {item}")
            raise CommandError

    @commands.command(name="iteminfo")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def iteminfo(self, ctx: commands.Context, item_name):
        item_dict = None
        item = item_name.lower()
        try:
            item = int(item)
            if str(item) in self.items_by_id:
                item_dict = self.items_by_id[str(item)]
        except Exception:
            if item in self.id_by_name:
                item_dict = self.items_by_id[str(self.id_by_name[item])]
                item = self.id_by_name[item]
        if item_dict:
            if item_dict["properties"]:
                await ctx.send(eval(f"properties_{item}(ctx)"))
            else:
                await ctx.send(f"{ctx.author.mention} No info available for this item")
        else:
            await ctx.send(f"Could not find item with name or id {item}")
            raise CommandError

    @commands.command(name="inventory", aliases=["inv"])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def inventory(self, ctx: commands.Context, target_user=None, page_number=1):
        """Check what you have in your inventory"""
        if target_user is None:
            target_user = ctx.author
            page_number = 1
        else:
            try:
                converter = commands.MemberConverter()
                target_user = await converter.convert(ctx, target_user)
                page_number = page_number
            except Exception:
                try:
                    page_number = int(target_user)
                    target_user = ctx.author
                except Exception:
                    await ctx.send("Enter a valid page number")
                    raise CommandError
        inventory_dict = self.collection.find_one({"_id": target_user.id}, {"inventory": 1})
        if inventory_dict is not None:
            inventory_dict = inventory_dict['inventory']
            inventory_dict = {key: val for key, val in inventory_dict.items() if val != 0}
            total_items = len(inventory_dict)
            pages = int((total_items - 1) // 5 + 1 + (total_items - 1) % 5 / 10)
            if pages != 0:
                if 0 < page_number <= pages:
                    keys = list(inventory_dict.keys())
                    embed = discord.Embed(title=f"{target_user.name}'s Inventory", color=discord.Colour.orange())
                    if page_number == pages:
                        limit = total_items
                    else:
                        limit = page_number * 5
                    for i in range((page_number - 1) * 5, limit):
                        item_id_str = keys[i]
                        embed.add_field(
                            name=f"{self.items_by_id[item_id_str]['emoji']} {self.items_by_id[item_id_str]['name']} ─ {inventory_dict[item_id_str]}",
                            value=f"(ID - {item_id_str}) {self.items_by_id[item_id_str]['description']}", inline=False)
                    embed.set_footer(icon_url=target_user.avatar_url,
                                     text=f"Requested by {ctx.author.display_name} • Page {page_number}/{pages}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Enter a valid page number")
                    raise CommandError
            else:
                await ctx.send("The inventory is empty lmao. To buy something use $shop")
                raise CommandError
        else:
            self.db_utils.initialize_template().insert_from_template(_id=target_user.id)
            await ctx.send("The inventory is empty lmao. To buy something use $shop")
            raise CommandError

    @commands.command(name="quiz")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def quiz(self, ctx: commands.Context, category: str = None):
        """Get coins for answering questions."""
        if category is None:
            category = "none"
        category = category.lower()
        if category == "help":
            embed = discord.Embed(title="Available Quiz Categories: ", color=discord.Colour.orange())
            for avl_category in self.quiz_help_dict:
                embed.add_field(name=self.quiz_help_dict[avl_category], value=f"$quiz {avl_category}")
            await ctx.send(embed=embed)
            return
        create_footer = False
        if category in self.quiz_categories:
            category = self.quiz_categories[category]
        else:
            category = random.randint(9, 28)
            create_footer = True
        response = requests.get(
            f"https://opentdb.com/api.php?amount=1&type=multiple&category={category}").json()[
            "results"][0]
        options = response["incorrect_answers"]
        options.append(response["correct_answer"])
        random.shuffle(options)
        correct_option = options.index(response["correct_answer"])
        desc_str = ""
        num_to_alphabet = {0: "A", 1: "B", 2: "C", 3: "D"}
        alphabet_to_num = {"A": 0, "B": 1, "C": 2, "D": 3}
        for i in range(len(options)):
            desc_str += f"**{num_to_alphabet[i]}: ** {options[i]}\n"
        q_embed = discord.Embed(title=html.unescape(response["question"]), description=html.unescape(desc_str),
                                color=discord.Colour.orange())
        if create_footer:
            q_embed.set_footer(text="Use $quiz help to get a list of categories")
        sent_embed = await ctx.send(embed=q_embed)

        def check(message):
            return message.channel == ctx.channel and message.author.id == ctx.author.id

        try:
            msg: discord.Message = await self.bot.wait_for('message', timeout=10.0, check=check)
            if msg.content.upper() in alphabet_to_num:
                if alphabet_to_num[msg.content.upper()] == correct_option:
                    r_embed = discord.Embed(title=f"{ctx.author.display_name} gave the correct answer",
                                            description=f"{self.defined_currencies['quiz']} coins were added to your wallet",
                                            color=discord.Colour.green())
                    if create_footer:
                        r_embed.set_footer(text="Use $quiz help to get a list of categories")
                    self.db_utils.initialize_template().add_operators(
                        inc=create_dict(wallet=self.defined_currencies['quiz'])
                    ).upsert_from_template(create_dict(_id=ctx.author.id), wallet=0)
                    await sent_embed.edit(embed=r_embed)
                else:
                    r_embed = discord.Embed(title=f"{ctx.author.display_name} gave the incorrect answer",
                                            description=f"The correct answer was **{num_to_alphabet[correct_option]}: {html.unescape(options[correct_option])}**",
                                            color=discord.Colour.red())
                    if create_footer:
                        r_embed.set_footer(text="Use $quiz help to get a list of categories")
                    await sent_embed.edit(embed=r_embed)
            else:
                await ctx.send(f"{ctx.author.mention} Bruh enter a proper option next time (A/B/C/D)")
        except asyncio.TimeoutError:
            r_embed = discord.Embed(title=f"{ctx.author.display_name}'s answer time ran out",
                                    description=f"The correct answer was **{num_to_alphabet[correct_option]}: {html.unescape(options[correct_option])}** (Timeout = 10 seconds)",
                                    color=discord.Colour.red())
            await sent_embed.edit(embed=r_embed)
            raise CommandError

    @commands.command(name="addmoney", hidden=True)
    @commands.is_owner()
    async def addmoney(self, ctx: commands.Context, amount: int, targeted_user: discord.Member = None):
        if targeted_user is None:
            targeted_user = ctx.author
        self.db_utils.initialize_template().add_operators(
            inc=create_dict(wallet=amount)
        ).upsert_from_template(create_dict(_id=targeted_user.id), wallet=0)
        emb = discord.Embed(description=f"***Added {amount} coins to {targeted_user.display_name}'s balance.***",
                            color=discord.Colour.green())
        await ctx.send(embed=emb)


def create_paged_shop(items: dict):
    items = {key: val for key, val in items.items() if not val['archive']}
    shop_items_len = len(items)
    pages = shop_items_len // 5
    if shop_items_len % 5 != 0:
        pages += 1
    i = 0
    j = -1
    embeds = []
    for item in items:
        if i % 5 == 0:
            j += 1
            embeds.append(discord.Embed(title="Chintu Store", color=discord.Colour.green()))
        embeds[j].add_field(name=f"{items[item]['name']} ─ {items[item]['value']}",
                            value=f"(ID - {item}) {items[item]['description']}", inline=False)
        i += 1
    return embeds, pages


def find_pairs(array: np.ndarray):
    len_without_dup = len(set(array))
    arr_set = list(set(array))
    arr_sum = np.sum(array)
    if len_without_dup > 3:
        return len_without_dup + 1
    elif len_without_dup == 1:
        return len_without_dup
    elif len_without_dup == 3:
        set_sum = np.sum(arr_set)
        if arr_sum - arr_set[0] * 3 == set_sum - arr_set[0] or arr_sum - arr_set[1] * 3 == set_sum - arr_set[1] \
                or arr_sum - arr_set[0] * 3 == set_sum - arr_set[0]:
            return 6
        else:
            return 4
    if arr_set[0] * 4 + arr_set[1] == arr_sum or arr_set[1] * 4 + arr_set[0] == arr_sum:
        return 2
    else:
        return 3


def setup(bot):
    bot.add_cog(Currency(bot))
