import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands, tasks

# =========================
# 設定
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

JST = ZoneInfo("Asia/Tokyo")

# =========================
# 謎の称号
# =========================

TITLES = [
    "🥔 じゃがいも担当",
    "🗿 校内石像",
    "🦆 廊下のアヒル",
    "📚 謎の図書委員",
    "🧃 給食牛乳管理官",
    "🪑 イスの守護者",
    "🌳 校庭の木",
    "🧹 黒板消し職人",
    "🧠 謎の天才",
    "🐟 金魚鉢監視員",
    "🚪 ドア開閉係",
    "💤 睡眠学習の達人",
    "📢 校内放送乱入者",
    "🎒 永遠の新入生",
    "🗿 存在が校則",
    "🧑‍🏫 自称先生",
    "🥖 パン係",
    "🛸 異世界からの転校生",
]

user_titles = {}

# =========================
# Webhook
# =========================

async def send_webhook(
    title: str,
    description: str,
    color: int = 0x5865F2
):
    if not WEBHOOK_URL:
        return

    try:
        async with discord.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                WEBHOOK_URL,
                session=session
            )

            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.now(JST)
            )

            await webhook.send(
                embed=embed,
                username="じいちゃん学園Bot"
            )

    except Exception as e:
        print(f"Webhook error: {e}")


# =========================
# Bot起動
# =========================

@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンド同期: {len(synced)}個")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")

    if not night_watch.is_running():
        night_watch.start()


# =========================
# 新入生
# =========================

@bot.event
async def on_member_join(member):
    print(f"新入生: {member}")

    await send_webhook(
        "🎒 新入生入学",
        f"{member.mention} がじいちゃん学園に入学しました！",
        0x57F287
    )


# =========================
# 生活指導
# =========================

@bot.tree.command(
    name="warn",
    description="生活指導を行います"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):
    await interaction.response.send_message(
        f"⚠️ **生活指導**\n"
        f"{member.mention}\n"
        f"理由：{reason}"
    )

    await send_webhook(
        "⚠️ 生活指導",
        f"{member} に生活指導\n理由：{reason}",
        0xFEE75C
    )


# =========================
# 廊下に立ってろ
# =========================

@bot.tree.command(
    name="timeout",
    description="廊下に立ってろ！"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int = 10
):
    duration = discord.utils.utcnow() + __import__("datetime").timedelta(
        minutes=minutes
    )

    await member.timeout(
        duration,
        reason="じいちゃん学園：廊下に立ってろ！"
    )

    await interaction.response.send_message(
        f"🔇 **廊下に立ってろ！**\n"
        f"{member.mention}\n"
        f"{minutes}分間です。"
    )

    await send_webhook(
        "🔇 廊下に立ってろ！",
        f"{member} が廊下送りになりました。\n期間：{minutes}分",
        0xED4245
    )


# =========================
# 早退
# =========================

@bot.tree.command(
    name="kick",
    description="生徒を早退させます"
)
@app_commands.checks.kick_members()
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):
    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 **早退**\n"
        f"{member} が早退しました。\n"
        f"理由：{reason}"
    )

    await send_webhook(
        "👢 早退",
        f"{member} が早退しました。\n理由：{reason}",
        0xED4245
    )


# =========================
# 卒業
# =========================

@bot.tree.command(
    name="ban",
    description="生徒を卒業させます"
)
@app_commands.checks.ban_members()
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):
    await member.ban(reason=reason)

    await interaction.response.send_message(
        f"🎓 **卒業**\n"
        f"{member} はじいちゃん学園を卒業しました。\n"
        f"理由：{reason}"
    )

    await send_webhook(
        "🎓 卒業",
        f"{member} が卒業しました。\n理由：{reason}",
        0xED4245
    )


# =========================
# 再入学
# =========================

@bot.tree.command(
    name="unban",
    description="生徒を再入学させます"
)
@app_commands.checks.ban_members()
async def unban(
    interaction: discord.Interaction,
    user_id: str
):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)

        await interaction.response.send_message(
            f"🔓 **再入学**\n{user} が再入学しました！"
        )

        await send_webhook(
            "🔓 再入学",
            f"{user} がじいちゃん学園に再入学しました。",
            0x57F287
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ 再入学に失敗しました。\n`{e}`",
            ephemeral=True
        )


# =========================
# 黒板消去
# =========================

@bot.tree.command(
    name="clear",
    description="メッセージを黒板消去します"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(
    interaction: discord.Interaction,
    amount: int = 10
):
    if amount < 1 or amount > 100:
        await interaction.response.send_message(
            "1〜100件で指定してください。",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    deleted = await interaction.channel.purge(
        limit=amount
    )

    await interaction.followup.send(
        f"🧹 **黒板消去**\n"
        f"{len(deleted)}件のメッセージを消去しました。"
    )


# =========================
# 校内放送
# =========================

@bot.tree.command(
    name="announce",
    description="校内放送を行います"
)
@app_commands.checks.has_permissions(mention_everyone=True)
async def announce(
    interaction: discord.Interaction,
    message: str
):
    await interaction.response.send_message(
        f"📢 **校内放送**\n\n{message}"
    )

    await send_webhook(
        "📢 校内放送",
        message,
        0x5865F2
    )


# =========================
# 謎の称号
# =========================

@bot.tree.command(
    name="title",
    description="謎の称号を獲得します"
)
async def title(
    interaction: discord.Interaction
):
    new_title = random.choice(TITLES)

    user_titles[interaction.user.id] = new_title

    await interaction.response.send_message(
        f"🏆 **謎の称号獲得！**\n\n"
        f"{interaction.user.mention}\n"
        f"あなたの称号は……\n\n"
        f"## {new_title}"
    )


# =========================
# 称号確認
# =========================

@bot.tree.command(
    name="titlecheck",
    description="自分の称号を確認します"
)
async def titlecheck(
    interaction: discord.Interaction
):
    title = user_titles.get(
        interaction.user.id,
        "🎒 永遠の新入生"
    )

    await interaction.response.send_message(
        f"🏆 **現在の称号**\n"
        f"{interaction.user.mention}\n"
        f"## {title}"
    )


# =========================
# 夜更かし職人
# =========================

night_status = {}


@tasks.loop(minutes=1)
async def night_watch():
    now = datetime.now(JST)

    # 午前3時〜4時59分
    is_night = 3 <= now.hour < 5

    if not is_night:
        return

    for guild in bot.guilds:
        for member in guild.members:

            if member.bot:
                continue

            online = member.status != discord.Status.offline
            previous = night_status.get(member.id, False)

            # オンラインになった瞬間
            if online and not previous:

                role = discord.utils.get(
                    guild.roles,
                    name="🌙 夜更かし職人"
                )

                if role is None:
                    try:
                        role = await guild.create_role(
                            name="🌙 夜更かし職人",
                            reason="夜更かし職人システム"
                        )
                    except Exception as e:
                        print(f"Role creation error: {e}")
                        continue

                try:
                    if role not in member.roles:
                        await member.add_roles(
                            role,
                            reason="夜更かし職人"
                        )

                    await send_webhook(
                        "🌙 夜更かし職人検知",
                        f"{member.mention} が午前3時台〜4時台にオンラインです。",
                        0x5865F2
                    )

                except Exception as e:
                    print(f"Night watch error: {e}")

            night_status[member.id] = online


# =========================
# エラー処理
# =========================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):
    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):
        message = "🚫 校則により、このコマンドは使えません。"

    elif isinstance(
        error,
        app_commands.errors.CheckFailure
    ):
        message = "🚫 権限がありません。"

    else:
        print(f"Command error: {error}")
        message = "❌ コマンド実行中にエラーが発生しました。"

    if interaction.response.is_done():
        await interaction.followup.send(
            message,
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# =========================
# 起動
# =========================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN が設定されていません。"
    )

bot.run(TOKEN)
