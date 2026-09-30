import os
import random
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


# ==================================================
# 設定
# ==================================================

TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません。")

JST = ZoneInfo("Asia/Tokyo")


# ==================================================
# Intents
# ==================================================

intents = discord.Intents.default()

# 新入生検知・メンバー情報
intents.members = True

# 夜更かし職人
intents.presences = True


# ==================================================
# Bot
# ==================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==================================================
# 謎の称号
# ==================================================

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


# ==================================================
# Webhook
# ==================================================

async def send_webhook(title, description):
    """
    WEBHOOK_URL が設定されている場合だけ通知。
    Webhookが壊れていてもBot本体を止めない。
    """

    if not WEBHOOK_URL:
        return

    data = {
        "username": "じいちゃん学園Bot",
        "embeds": [
            {
                "title": title,
                "description": description,
                "timestamp": datetime.now(JST).isoformat()
            }
        ]
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.post(
                WEBHOOK_URL,
                json=data
            ) as response:

                if response.status >= 400:
                    print(
                        f"Webhook error: HTTP {response.status}"
                    )

    except Exception as e:
        print(f"Webhook送信失敗: {e}")


# ==================================================
# 起動
# ==================================================

@bot.event
async def on_ready():

    print("=" * 40)
    print(f"ログイン成功: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print(f"サーバー数: {len(bot.guilds)}")
    print("=" * 40)

    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンド同期: {len(synced)}個")

    except Exception as e:
        print(f"コマンド同期エラー: {e}")


# ==================================================
# 新入生
# ==================================================

@bot.event
async def on_member_join(member):

    print(f"新入生: {member}")

    await send_webhook(
        "🎒 新入生入学",
        f"{member.mention} がじいちゃん学園に入学しました！"
    )


# ==================================================
# 生活指導
# ==================================================

@bot.tree.command(
    name="warn",
    description="生活指導を行います"
)
@app_commands.checks.has_permissions(
    moderate_members=True
)
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
        f"{member.mention}\n理由：{reason}"
    )


# ==================================================
# 廊下に立ってろ！
# ==================================================

@bot.tree.command(
    name="timeout",
    description="生徒を廊下に立たせます"
)
@app_commands.checks.has_permissions(
    moderate_members=True
)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int = 10
):

    if minutes < 1 or minutes > 40320:
        await interaction.response.send_message(
            "⏰ 1〜40320分で指定してください。",
            ephemeral=True
        )
        return

    try:

        until = discord.utils.utcnow() + timedelta(
            minutes=minutes
        )

        await member.timeout(
            until,
            reason="じいちゃん学園：廊下に立ってろ！"
        )

        await interaction.response.send_message(
            f"🔇 **廊下に立ってろ！**\n"
            f"{member.mention}\n"
            f"{minutes}分間"
        )

        await send_webhook(
            "🔇 廊下に立ってろ！",
            f"{member.mention}\n期間：{minutes}分"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botの権限が足りません。",
            ephemeral=True
        )

    except Exception as e:

        print(f"Timeout error: {e}")

        await interaction.response.send_message(
            "❌ タイムアウトに失敗しました。",
            ephemeral=True
        )


# ==================================================
# 早退
# ==================================================

@bot.tree.command(
    name="kick",
    description="生徒を早退させます"
)
@app_commands.checks.has_permissions(
    kick_members=True
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):

    try:

        await member.kick(reason=reason)

        await interaction.response.send_message(
            f"👢 **早退**\n"
            f"{member}\n"
            f"理由：{reason}"
        )

        await send_webhook(
            "👢 早退",
            f"{member}\n理由：{reason}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botの権限が足りません。",
            ephemeral=True
        )


# ==================================================
# 卒業
# ==================================================

@bot.tree.command(
    name="ban",
    description="生徒を卒業させます"
)
@app_commands.checks.has_permissions(
    ban_members=True
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):

    try:

        await member.ban(reason=reason)

        await interaction.response.send_message(
            f"🎓 **卒業**\n"
            f"{member}\n"
            f"理由：{reason}"
        )

        await send_webhook(
            "🎓 卒業",
            f"{member}\n理由：{reason}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botの権限が足りません。",
            ephemeral=True
        )


# ==================================================
# 再入学
# ==================================================

@bot.tree.command(
    name="unban",
    description="卒業した生徒を再入学させます"
)
@app_commands.checks.has_permissions(
    ban_members=True
)
async def unban(
    interaction: discord.Interaction,
    user_id: str
):

    try:

        user = await bot.fetch_user(
            int(user_id)
        )

        await interaction.guild.unban(
            user,
            reason="じいちゃん学園：再入学"
        )

        await interaction.response.send_message(
            f"🔓 **再入学**\n"
            f"{user.mention if hasattr(user, 'mention') else user}"
        )

        await send_webhook(
            "🔓 再入学",
            f"{user} が再入学しました！"
        )

    except ValueError:

        await interaction.response.send_message(
            "❌ User IDが正しくありません。",
            ephemeral=True
        )

    except discord.NotFound:

        await interaction.response.send_message(
            "❌ そのユーザーはBANされていません。",
            ephemeral=True
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botの権限が足りません。",
            ephemeral=True
        )

    except Exception as e:

        print(f"Unban error: {e}")

        await interaction.response.send_message(
            "❌ 再入学に失敗しました。",
            ephemeral=True
        )


# ==================================================
# 黒板消去
# ==================================================

@bot.tree.command(
    name="clear",
    description="メッセージを黒板消去します"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def clear(
    interaction: discord.Interaction,
    amount: int = 10
):

    if amount < 1 or amount > 100:

        await interaction.response.send_message(
            "❌ 1〜100件で指定してください。",
            ephemeral=True
        )
        return

    if not isinstance(
        interaction.channel,
        discord.TextChannel
    ):

        await interaction.response.send_message(
            "❌ この場所では使えません。",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    try:

        deleted = await interaction.channel.purge(
            limit=amount
        )

        await interaction.followup.send(
            f"🧹 **黒板消去**\n"
            f"{len(deleted)}件を消去しました。"
        )

    except discord.Forbidden:

        await interaction.followup.send(
            "❌ Botにメッセージ管理権限がありません。"
        )


# ==================================================
# 校内放送
# ==================================================

@bot.tree.command(
    name="announce",
    description="校内放送を行います"
)
@app_commands.checks.has_permissions(
    mention_everyone=True
)
async def announce(
    interaction: discord.Interaction,
    message: str
):

    await interaction.response.send_message(
        f"📢 **校内放送**\n\n{message}"
    )

    await send_webhook(
        "📢 校内放送",
        message
    )


# ==================================================
# 謎の称号
# ==================================================

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


# ==================================================
# 称号確認
# ==================================================

@bot.tree.command(
    name="titlecheck",
    description="現在の称号を確認します"
)
async def titlecheck(
    interaction: discord.Interaction
):

    current = user_titles.get(
        interaction.user.id,
        "🎒 永遠の新入生"
    )

    await interaction.response.send_message(
        f"🏆 **現在の称号**\n"
        f"{interaction.user.mention}\n"
        f"## {current}"
    )


# ==================================================
# 夜更かし職人
# ==================================================

@bot.event
async def on_presence_update(
    before,
    after
):

    try:

        # Bot自身は無視
        if after.bot:
            return

        # 変更前もオンラインなら何もしない
        if before.status != discord.Status.offline:
            return

        # 変更後がオフラインなら何もしない
        if after.status == discord.Status.offline:
            return

        now = datetime.now(JST)

        # 午前3:00〜4:59
        if not (3 <= now.hour < 5):
            return

        guild = after.guild

        role = discord.utils.get(
            guild.roles,
            name="🌙 夜更かし職人"
        )

        # ロールがなければ作る
        if role is None:

            try:

                role = await guild.create_role(
                    name="🌙 夜更かし職人",
                    reason="夜更かし職人システム"
                )

            except discord.Forbidden:

                print(
                    "夜更かし職人ロールを作成できません。"
                    "Botにロール管理権限が必要です。"
                )

                return

        # すでに持っていたら終了
        if role in after.roles:
            return

        try:

            await after.add_roles(
                role,
                reason="夜更かし職人"
            )

            print(
                f"夜更かし職人: {after}"
            )

            await send_webhook(
                "🌙 夜更かし職人",
                f"{after.mention} が午前{now.hour}:{now.minute:02d}にログインしました。"
            )

        except discord.Forbidden:

            print(
                "夜更かし職人ロールを付与できません。"
                "Botのロール位置を確認してください。"
            )

    except Exception as e:

        print(
            f"Presence error: {e}"
        )


# ==================================================
# コマンドエラー
# ==================================================

@bot.tree.error
async def command_error(
    interaction,
    error
):

    print(
        f"Command error: {repr(error)}"
    )

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        message = (
            "🚫 校則違反防止システム："
            "権限がありません。"
        )

    else:

        message = (
            "❌ コマンドでエラーが発生しました。"
        )

    try:

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

    except Exception as e:

        print(
            f"Error handler error: {e}"
        )


# ==================================================
# 起動
# ==================================================

print("じいちゃん学園Bot 起動中...")

bot.run(TOKEN)
