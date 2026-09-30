import os
import random
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks


# =========================================================
# 設定
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 夜更かし判定
NIGHT_START = 23
NIGHT_END = 6

# 夜更かし称号
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

# ユーザーごとの称号
user_titles = {}

# 直前のオンライン状態
previous_status = {}


# =========================================================
# Bot設定
# =========================================================

intents = discord.Intents.default()

# メンバーのオンライン状態を取得
intents.members = True
intents.presences = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# Webhook通知
# =========================================================

async def send_webhook(title, message):

    if not WEBHOOK_URL:
        print("WEBHOOK_URL が設定されていません")
        return

    try:
        webhook = discord.Webhook.from_url(
            WEBHOOK_URL,
            client=discord.Client(
                intents=discord.Intents.none()
            )
        )

        embed = discord.Embed(
            title=title,
            description=message
        )

        await webhook.send(
            embed=embed,
            username="じいちゃん学園・教頭"
        )

    except Exception as e:
        print(f"Webhookエラー: {e}")


# =========================================================
# 起動
# =========================================================

@bot.event
async def on_ready():

    print(f"ログイン成功: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")

    if not status_checker.is_running():
        status_checker.start()


# =========================================================
# ⚠️ 生活指導
# =========================================================

@bot.tree.command(
    name="warn",
    description="生徒に生活指導を行います"
)
@app_commands.checks.has_permissions(
    moderate_members=True
)
async def warn(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):

    embed = discord.Embed(
        title="⚠️ 生活指導",
        description=(
            f"{member.mention} さん\n\n"
            f"先生から生活指導を受けました。\n"
            f"📋 理由：{reason}"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# 🔇 廊下に立ってろ！
# =========================================================

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
    minutes: int,
    reason: str = "理由なし"
):

    if minutes < 1 or minutes > 40320:
        await interaction.response.send_message(
            "❌ 1〜40320分で指定してください。",
            ephemeral=True
        )
        return

    try:

        await member.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        embed = discord.Embed(
            title="🔇 廊下に立ってろ！",
            description=(
                f"{member.mention} さんが廊下送りになりました。\n\n"
                f"⏰ 時間：{minutes}分\n"
                f"📋 理由：{reason}"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botにタイムアウト権限がありません。",
            ephemeral=True
        )


# =========================================================
# 👢 早退
# =========================================================

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

        await member.kick(
            reason=reason
        )

        embed = discord.Embed(
            title="👢 早退",
            description=(
                f"{member.display_name} さんは"
                "本日早退となりました。\n\n"
                f"📋 理由：{reason}"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botにキック権限がありません。",
            ephemeral=True
        )


# =========================================================
# 🎓 卒業
# =========================================================

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

        await member.ban(
            reason=reason
        )

        embed = discord.Embed(
            title="🎓 卒業証書",
            description=(
                f"**{member.display_name} 様**\n\n"
                "あなたは本日をもちまして、\n"
                "じいちゃん学園を卒業することを\n"
                "ここに証します。\n\n"
                f"🎓 卒業理由：{reason}\n\n"
                "🎓 卒業おめでとうございます。"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ BotにBAN権限がありません。",
            ephemeral=True
        )


# =========================================================
# 🔓 再入学
# =========================================================

@bot.tree.command(
    name="unban",
    description="卒業生を再入学させます"
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
            user
        )

        embed = discord.Embed(
            title="🔓 再入学",
            description=(
                f"🎓 **{user.display_name}** さんが\n"
                "じいちゃん学園へ再入学しました！\n\n"
                "🏫 おかえりなさい。"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except ValueError:

        await interaction.response.send_message(
            "❌ ユーザーIDが正しくありません。",
            ephemeral=True
        )

    except discord.NotFound:

        await interaction.response.send_message(
            "❌ そのユーザーは卒業していません。",
            ephemeral=True
        )


# =========================================================
# 🧹 黒板消去
# =========================================================

@bot.tree.command(
    name="clear",
    description="メッセージを黒板消去します"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    if amount < 1 or amount > 100:

        await interaction.response.send_message(
            "❌ 1〜100件で指定してください。",
            ephemeral=True
        )
        return

    await interaction.response.defer(
        ephemeral=True
    )

    deleted = await interaction.channel.purge(
        limit=amount
    )

    await interaction.followup.send(
        f"🧹 **黒板消去完了！**\n"
        f"{len(deleted)}件を消去しました。",
        ephemeral=True
    )


# =========================================================
# 📢 校内放送
# =========================================================

@bot.tree.command(
    name="announce",
    description="校内放送を行います"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def announce(
    interaction: discord.Interaction,
    message: str
):

    embed = discord.Embed(
        title="📢 校内放送",
        description=message
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# 🎲 謎の称号
# =========================================================

@bot.tree.command(
    name="称号",
    description="謎の称号を授与します"
)
async def title(
    interaction: discord.Interaction
):

    member = interaction.user

    new_title = random.choice(
        TITLES
    )

    user_titles[
        member.id
    ] = new_title

    embed = discord.Embed(
        title="🎓 謎の称号授与式",
        description=(
            f"👤 **{member.display_name}**\n\n"
            f"🏷️ **{new_title}**\n\n"
            "本日よりこの称号を授与します。"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# 🏷️ 自分の称号確認
# =========================================================

@bot.tree.command(
    name="称号確認",
    description="自分の現在の称号を確認します"
)
async def title_check(
    interaction: discord.Interaction
):

    member = interaction.user

    title = user_titles.get(
        member.id,
        "まだ称号がありません"
    )

    await interaction.response.send_message(
        f"🏷️ **{member.display_name}** さんの称号\n\n"
        f"🎓 {title}"
    )


# =========================================================
# 🌙 夜更かし職人検知
# =========================================================

@tasks.loop(minutes=1)
async def status_checker():

    now = discord.utils.utcnow()

    # 日本時間に変換
    from zoneinfo import ZoneInfo

    japan_time = now.astimezone(
        ZoneInfo("Asia/Tokyo")
    )

    hour = japan_time.hour
    minute = japan_time.minute

    # 23:00〜05:59
    night = (
        hour >= NIGHT_START
        or hour < NIGHT_END
    )

    if not night:
        return

    for guild in bot.guilds:

        for member in guild.members:

            status = member.status

            online = status in (
                discord.Status.online,
                discord.Status.idle,
                discord.Status.dnd
            )

            before = previous_status.get(
                member.id,
                False
            )

            previous_status[
                member.id
            ] = online

            # オフライン→オンラインになった瞬間だけ
            if online and not before:

                # 03:00〜04:59
                if hour in (3, 4):

                    user_title = "🌙 夜更かし職人"

                    user_titles[
                        member.id
                    ] = user_title

                    await send_webhook(
                        "🌙 夜更かし職人 認定！",
                        (
                            f"👤 **{member.display_name}**\n"
                            f"🕒 {hour:02d}:{minute:02d}\n\n"
                            "この時間までオンラインなのは、"
                            "もはや職人芸です。\n\n"
                            f"🏷️ 称号：**{user_title}**"
                        )
                    )


# =========================================================
# エラー処理
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(
        error,
        app_commands.MissingPermissions
    ):

        message = (
            "🏫 あなたにはこの操作をする権限がありません。"
        )

    else:

        print(
            f"コマンドエラー: {error}"
        )

        message = (
            "❌ コマンド実行中にエラーが発生しました。"
        )

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


# =========================================================
# 起動
# =========================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN が設定されていません。"
    )

bot.run(TOKEN)import os
import random
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks


# =========================================================
# 設定
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 夜更かし判定
NIGHT_START = 23
NIGHT_END = 6

# 夜更かし称号
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

# ユーザーごとの称号
user_titles = {}

# 直前のオンライン状態
previous_status = {}


# =========================================================
# Bot設定
# =========================================================

intents = discord.Intents.default()

# メンバーのオンライン状態を取得
intents.members = True
intents.presences = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# Webhook通知
# =========================================================

async def send_webhook(title, message):

    if not WEBHOOK_URL:
        print("WEBHOOK_URL が設定されていません")
        return

    try:
        webhook = discord.Webhook.from_url(
            WEBHOOK_URL,
            client=discord.Client(
                intents=discord.Intents.none()
            )
        )

        embed = discord.Embed(
            title=title,
            description=message
        )

        await webhook.send(
            embed=embed,
            username="じいちゃん学園・教頭"
        )

    except Exception as e:
        print(f"Webhookエラー: {e}")


# =========================================================
# 起動
# =========================================================

@bot.event
async def on_ready():

    print(f"ログイン成功: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")

    if not status_checker.is_running():
        status_checker.start()


# =========================================================
# ⚠️ 生活指導
# =========================================================

@bot.tree.command(
    name="warn",
    description="生徒に生活指導を行います"
)
@app_commands.checks.has_permissions(
    moderate_members=True
)
async def warn(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "理由なし"
):

    embed = discord.Embed(
        title="⚠️ 生活指導",
        description=(
            f"{member.mention} さん\n\n"
            f"先生から生活指導を受けました。\n"
            f"📋 理由：{reason}"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# 🔇 廊下に立ってろ！
# =========================================================

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
    minutes: int,
    reason: str = "理由なし"
):

    if minutes < 1 or minutes > 40320:
        await interaction.response.send_message(
            "❌ 1〜40320分で指定してください。",
            ephemeral=True
        )
        return

    try:

        await member.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        embed = discord.Embed(
            title="🔇 廊下に立ってろ！",
            description=(
                f"{member.mention} さんが廊下送りになりました。\n\n"
                f"⏰ 時間：{minutes}分\n"
                f"📋 理由：{reason}"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botにタイムアウト権限がありません。",
            ephemeral=True
        )


# =========================================================
# 👢 早退
# =========================================================

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

        await member.kick(
            reason=reason
        )

        embed = discord.Embed(
            title="👢 早退",
            description=(
                f"{member.display_name} さんは"
                "本日早退となりました。\n\n"
                f"📋 理由：{reason}"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Botにキック権限がありません。",
            ephemeral=True
        )


# =========================================================
# 🎓 卒業
# =========================================================

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

        await member.ban(
            reason=reason
        )

        embed = discord.Embed(
            title="🎓 卒業証書",
            description=(
                f"**{member.display_name} 様**\n\n"
                "あなたは本日をもちまして、\n"
                "じいちゃん学園を卒業することを\n"
                "ここに証します。\n\n"
                f"🎓 卒業理由：{reason}\n\n"
                "🎓 卒業おめでとうございます。"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ BotにBAN権限がありません。",
            ephemeral=True
        )


# =========================================================
# 🔓 再入学
# =========================================================

@bot.tree.command(
    name="unban",
    description="卒業生を再入学させます"
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
            user
        )

        embed = discord.Embed(
            title="🔓 再入学",
            description=(
                f"🎓 **{user.display_name}** さんが\n"
                "じいちゃん学園へ再入学しました！\n\n"
                "🏫 おかえりなさい。"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

    except ValueError:

        await interaction.response.send_message(
            "❌ ユーザーIDが正しくありません。",
            ephemeral=True
        )

    except discord.NotFound:

        await interaction.response.send_message(
            "❌ そのユーザーは卒業していません。",
            ephemeral=True
        )


# =========================================================
# 🧹 黒板消去
# =========================================================

@bot.tree.command(
    name="clear",
    description="メッセージを黒板消去します"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    if amount < 1 or amount > 100:

        await interaction.response.send_message(
            "❌ 1〜100件で指定してください。",
            ephemeral=True
        )
        return

    await interaction.response.defer(
        ephemeral=True
    )

    deleted = await interaction.channel.purge(
        limit=amount
    )

    await interaction.followup.send(
        f"🧹 **黒板消去完了！**\n"
        f"{len(deleted)}件を消去しました。",
        ephemeral=True
    )


# =========================================================
# 📢 校内放送
# =========================================================

@bot.tree.command(
    name="announce",
    description="校内放送を行います"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def announce(
    interaction: discord.Interaction,
    message: str
):

    embed = discord.Embed(
        title="📢 校内放送",
        description=message
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# 🎲 謎の称号
# =========================================================

@bot.tree.command(
    name="称号",
    description="謎の称号を授与します"
)
async def title(
    interaction: discord.Interaction
):

    member = interaction.user

    new_title = random.choice(
        TITLES
    )

    user_titles[
        member.id
    ] = new_title

    embed = discord.Embed(
        title="🎓 謎の称号授与式",
        description=(
            f"👤 **{member.display_name}**\n\n"
            f"🏷️ **{new_title}**\n\n"
            "本日よりこの称号を授与します。"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# 🏷️ 自分の称号確認
# =========================================================

@bot.tree.command(
    name="称号確認",
    description="自分の現在の称号を確認します"
)
async def title_check(
    interaction: discord.Interaction
):

    member = interaction.user

    title = user_titles.get(
        member.id,
        "まだ称号がありません"
    )

    await interaction.response.send_message(
        f"🏷️ **{member.display_name}** さんの称号\n\n"
        f"🎓 {title}"
    )


# =========================================================
# 🌙 夜更かし職人検知
# =========================================================

@tasks.loop(minutes=1)
async def status_checker():

    now = discord.utils.utcnow()

    # 日本時間に変換
    from zoneinfo import ZoneInfo

    japan_time = now.astimezone(
        ZoneInfo("Asia/Tokyo")
    )

    hour = japan_time.hour
    minute = japan_time.minute

    # 23:00〜05:59
    night = (
        hour >= NIGHT_START
        or hour < NIGHT_END
    )

    if not night:
        return

    for guild in bot.guilds:

        for member in guild.members:

            status = member.status

            online = status in (
                discord.Status.online,
                discord.Status.idle,
                discord.Status.dnd
            )

            before = previous_status.get(
                member.id,
                False
            )

            previous_status[
                member.id
            ] = online

            # オフライン→オンラインになった瞬間だけ
            if online and not before:

                # 03:00〜04:59
                if hour in (3, 4):

                    user_title = "🌙 夜更かし職人"

                    user_titles[
                        member.id
                    ] = user_title

                    await send_webhook(
                        "🌙 夜更かし職人 認定！",
                        (
                            f"👤 **{member.display_name}**\n"
                            f"🕒 {hour:02d}:{minute:02d}\n\n"
                            "この時間までオンラインなのは、"
                            "もはや職人芸です。\n\n"
                            f"🏷️ 称号：**{user_title}**"
                        )
                    )


# =========================================================
# エラー処理
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(
        error,
        app_commands.MissingPermissions
    ):

        message = (
            "🏫 あなたにはこの操作をする権限がありません。"
        )

    else:

        print(
            f"コマンドエラー: {error}"
        )

        message = (
            "❌ コマンド実行中にエラーが発生しました。"
        )

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


# =========================================================
# 起動
# =========================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN が設定されていません。"
    )

bot.run(TOKEN)
