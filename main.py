import os
import random as rand
import discord
from deep_translator import GoogleTranslator
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re
import asyncio

load_dotenv()
token = os.getenv("TOKEN")

prefix = "!t"
intents = discord.Intents.all()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

bot.remove_command("help")

YOUR_USER_ID = (1195361246195757118, 1335606447144173610)
LOG_CHANNEL_ID = 1505527971883126844
ALLOWED_GUILD_ID = 1505460695410671797

warnings = {}
user_messages = {}

SPAM_MSG_LIMIT = 4
SPAM_TIME_WINDOW = 3
RESET_VIOLATION_HOURS = 1

@bot.event
async def on_ready():
    print(f"==========================================")
    print(f"🤖 Bot đã đăng nhập thành công: {bot.user}")
    print(f"🛡️ Hệ thống bảo mật và chống spam đã kích hoạt!")
    print(f"==========================================")
    # Khởi động vòng lặp tự động quét dọn bộ đếm sau mỗi 1 giờ không tái phạm
    auto_reset_warnings.start()
    
@tasks.loop(minutes=1)
async def auto_reset_warnings():
    """Tác vụ chạy ngầm: Cứ mỗi 1 phút quét qua danh sách để xóa bộ đếm nếu hết hạn 1h"""
    current_time = datetime.now()
    
    # 1. Quét bộ đếm spam
    for user_id in list(spam_warnings.keys()):
        data = spam_warnings[user_id]
        if current_time - data["last_violation"] >= timedelta(hours=RESET_VIOLATION_HOURS):
            del spam_warnings[user_id]
            print(f"🧹 [Auto-Reset] Đã đặt lại bộ đếm SPAM cho user ID: {user_id}")

    # 2. Quét bộ đếm nói tục
    for user_id in list(bad_word_warnings.keys()):
        data = bad_word_warnings[user_id]
        if current_time - data["last_violation"] >= timedelta(hours=RESET_VIOLATION_HOURS):
            del bad_word_warnings[user_id]
            print(f"🧹 [Auto-Reset] Đã đặt lại bộ đếm NÓI TỤC cho user ID: {user_id}")
            
async def handle_greetings(message):
    if message.content.lower() == "hello":
        await message.channel.send(f"Xin chào {message.author.mention}!")
    elif message.content.lower() == "hi":
        await message.channel.send(f"Chào {message.author.mention}!")
    elif (
        message.content == f"<@{bot.user.id}>"
        or message.content == "<@1514521082772590753>"
    ):
        color = 0x1ABAFF

        embed = discord.Embed(
            description=(
                f"👋 **Xin chào {message.author.mention}**\n"
                f"🤖 **Tôi là Bot Discord của bạn và sẵn sàng để phục vụ!**\n"
                f"🔖 **Prefix của tôi là `{prefix}`**\n"
                f"ℹ️ **Để khám phá các tính năng và lệnh của tôi, hãy sử dụng `{prefix}help`** 💡"
            ),
            color=color,
        )
        await message.channel.send(embed=embed)


bad_words = [
    # Chửi phổ biến
    "địt",
    "dit",
    "djt",
    "đjt",
    "đụ",
    "du",
    "đụ má",
    "du ma",
    "đéo",
    "deo",
    "đếch",
    "dech",
    "dm",
    "dmm",
    "đm",
    "dmk",
    "dmn",
    "vcl",
    "vl",
    "vkl",
    "vloz",
    "vái",
    "vai",
    "vái l",
    "vailon",
    # Bộ phận cơ thể
    "cặc",
    "cak",
    "cac",
    "cu",
    "chim",
    "buồi",
    "buoi",
    "lồn",
    "lon",
    "cl",
    "cailon",
    "dái",
    "zái",
    "cứt",
    "cut",
    "đái",
    "ỉa",
    # Xúc phạm
    "ngu",
    "ngu lol",
    "ngu l",
    "óc chó",
    "oc cho",
    "thiểu năng",
    "súc vật",
    "suc vat",
    "chó chết",
    "con chó",
    "thằng chó",
    "con điên",
    "thằng điên",
    "khốn nạn",
    "óc l",
    "óc c",
    "rác rưởi",
    "phế vật",
    "vô dụng",
    # Chửi gia đình
    "mẹ mày",
    "me may",
    "bố mày",
    "bo may",
    "ông già mày",
    "cả nhà mày",
    "tổ sư",
    "tiên sư",
    "mả mẹ",
    "con mẹ mày",
    # Toxic game/chat
    "trash",
    "dog",
    "ez",
    "noob",
    "gà",
    "óc",
    "brain dead",
    "retard",
    # Biến thể bypass
    "d!t",
    "d1t",
    "djtme",
    "d m",
    "đ m",
    "v l",
    "c c",
    "l o n",
    "c a c",
    "d e o",
    # Tiếng Anh
    "fuck",
    "fck",
    "shit",
    "bitch",
    "asshole",
    "motherfucker",
    "mf",
    "bastard",
    "dick",
    "pussy",
    "slut",
    "whore",
]


@bot.event
async def on_message(message):
    # 1. Bỏ qua nếu là bot hoặc tin nhắn DM
    if message.author.bot or not message.guild:
        return

    # 2. Kiểm tra nếu không thuộc Server được cấu hình kiểm tra từ cấm
    if message.guild.id != ALLOWED_GUILD_ID:
        await handle_greetings(message)
        await bot.process_commands(message)
        return

    # 3. Bỏ qua Admin/Mod/Staff (Không lọc từ cấm & không check spam)
    perms = message.author.guild_permissions
    ignore_roles = {"Staff", "Admin", "Mod"}
    has_ignore_role = any(role.name in ignore_roles for role in message.author.roles)

    if (
        perms.administrator
        or perms.manage_messages
        or perms.manage_guild
        or has_ignore_role
    ):
        await handle_greetings(message)
        await bot.process_commands(message)
        return

    user_id = message.author.id
    current_time = datetime.now()

    # ==========================================
    # 4. BỘ LỌC 1: KIỂM TRA SPAM TIN NHẮN
    # ==========================================
    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id].append(current_time)

    # Lọc bỏ mốc thời gian cũ quá 3 giây
    user_messages[user_id] = [
        msg_time
        for msg_time in user_messages[user_id]
        if current_time - msg_time < timedelta(seconds=SPAM_TIME_WINDOW)
    ]

    # Xử lý khi dính ngưỡng Spam
    if len(user_messages[user_id]) >= SPAM_MSG_LIMIT:
        
        # Hàm phụ xử lý bất đồng bộ các tác vụ nặng (Xóa tin, gửi log) ở nền để tránh delay bot
        async def cleanup_spam_tasks(msg_obj, u_id, emb):
            try:
                def is_spam_author(m):
                    return m.author.id == u_id
                # Tìm và xóa sạch tối đa 10 tin nhắn spam trước đó của người này
                await msg_obj.channel.purge(limit=10, check=is_spam_author)
            except Exception as e:
                print(f"❌ Lỗi xóa tin nhắn spam ngầm: {e}")
                
            try:
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel and emb:
                    await log_channel.send(embed=emb)
            except Exception as e:
                print(f"❌ Lỗi gửi log spam ngầm: {e}")

        # Tăng bộ đếm vi phạm SPAM riêng biệt kèm mốc thời gian vi phạm mới nhất
        if user_id not in spam_warnings:
            spam_warnings[user_id] = {"count": 0, "last_violation": current_time}
        
        spam_warnings[user_id]["count"] += 1
        spam_warnings[user_id]["last_violation"] = current_time
        spam_warn_count = spam_warnings[user_id]["count"]

        # Tạo sẵn Embed log gửi về kênh quản lý
        embed = discord.Embed(title="🚫 Vi phạm: Spam tin nhắn", color=discord.Color.orange())
        embed.add_field(name="👤 Người dùng", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
        embed.add_field(name="💬 Nội dung", value=message.content[:100] if message.content else "File/Embed", inline=False)
        embed.add_field(name="⚠ Số lần vi phạm Spam", value=f"**{spam_warn_count}** (Sẽ reset sau 1h không tái phạm)", inline=False)
        embed.add_field(name="📍 Kênh", value=message.channel.mention, inline=False)

        # Đẩy tác vụ nặng chạy ngầm, bot không cần chờ đợi xóa xong nữa
        asyncio.create_task(cleanup_spam_tasks(message, user_id, embed))

        # Reset bộ đếm thời gian ngay lập tức để tránh trùng lặp logic
        user_messages[user_id] = [] 

        # Áp dụng hình phạt theo cấp độ vi phạm Spam
        if spam_warn_count == 1:
            await message.channel.send(
                f"{message.author.mention} ⚠ Cảnh báo: Vui lòng dừng hành vi spam tin nhắn! (Tin nhắn cũ đã bị xóa)"
            )
        elif spam_warn_count == 2:
            try:
                await message.author.timeout(
                    timedelta(minutes=10), reason="Spam tin nhắn lần 2"
                )
                await message.channel.send(
                    f"{message.author.mention} ⏳ Bạn đã bị Timeout **10 phút** vì cố tình spam!"
                )
            except Exception as e:
                print(f"❌ Lỗi timeout spam: {e}")
        elif spam_warn_count >= 3:
            try:
                # Gửi DM riêng trước khi đá
                try:
                    await message.author.send(
                        f"⚠️ Bạn đã bị **Kick** khỏi server **{message.guild.name}** vì lý do: Cố tình spam tin nhắn quá 3 lần."
                    )
                except discord.Forbidden:
                    print(f"⚠️ Không thể gửi DM cho {message.author}.")

                # Thực hiện đá khỏi server
                await message.author.kick(reason="Spam tin nhắn quá 3 lần")
                await message.channel.send(
                    f"👢 **{message.author}** đã bị Kick khỏi server vì cố tình spam nhiều lần!"
                )
            except Exception as e:
                print(f"❌ Lỗi kick spam: {e}")

        return  # Ngắt tại đây nếu dính spam

    # ==========================================
    # 5. BỘ LỌC 2: KIỂM TRA TỪ CẤM (NÓI TỤC)
    # ==========================================
    msg = message.content.lower()
    is_bad = False

    for word in bad_words:
        pattern = rf"(?:^|\s|[.,!?;*~])" + re.escape(word) + rf"(?:$|\s|[.,!?;*~])"
        if re.search(pattern, msg):
            is_bad = True
            break

    # Xử lý khi dính từ cấm
    if is_bad:
        try:
            await message.delete()  # Xóa tin nhắn gõ tục ngay lập tức
        except (discord.Forbidden, discord.NotFound):
            pass

        # Tăng bộ đếm vi phạm NÓI TỤC riêng biệt kèm mốc thời gian vi phạm mới nhất
        if user_id not in bad_word_warnings:
            bad_word_warnings[user_id] = {"count": 0, "last_violation": current_time}
            
        bad_word_warnings[user_id]["count"] += 1
        bad_word_warnings[user_id]["last_violation"] = current_time
        bad_word_warn_count = bad_word_warnings[user_id]["count"]

        # Gửi log vi phạm về kênh log
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🚫 Vi phạm từ cấm", color=discord.Color.red())
            embed.add_field(name="👤 Người dùng", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
            embed.add_field(name="💬 Tin nhắn gốc", value=message.content, inline=False)
            embed.add_field(name="⚠ Số lần vi phạm Nói tục", value=f"**{bad_word_warn_count}** (Sẽ reset sau 1h không tái phạm)", inline=False)
            embed.add_field(name="📍 Kênh", value=message.channel.mention, inline=False)
            await log_channel.send(embed=embed)

        # Áp dụng hình phạt theo cấp độ vi phạm Nói tục
        if bad_word_warn_count == 1:
            await message.channel.send(
                f"{message.author.mention} ⚠ Cảnh báo: Vui lòng không sử dụng từ ngữ thô tục!"
            )
        elif bad_word_warn_count == 2:
            try:
                await message.author.timeout(
                    timedelta(minutes=10), reason="Chửi thề lần 2"
                )
                await message.channel.send(
                    f"{message.author.mention} ⏳ Bạn đã bị Timeout **10 phút** vì tiếp tục vi phạm từ ngữ thô tục!"
                )
            except Exception as e:
                print(f"❌ Lỗi timeout nói tục: {e}")
        elif bad_word_warn_count >= 3:
            try:
                # Gửi DM riêng trước khi đá
                try:
                    await message.author.send(
                        f"⚠️ Bạn đã bị **Kick** khỏi server **{message.guild.name}** vì lý do: Vi phạm từ ngữ thô tục quá 3 lần."
                    )
                except discord.Forbidden:
                    print(f"⚠️ Không thể gửi DM cho {message.author}.")

                # Thực hiện đá khỏi server
                await message.author.kick(reason="Vi phạm từ cấm quá 3 lần")
                await message.channel.send(
                    f"👢 **{message.author}** đã bị Kick khỏi server vì cố tình vi phạm nhiều lần!"
                )
            except Exception as e:
                print(f"❌ Lỗi kick nói tục: {e}")

        return  # Ngắt tại đây nếu tin nhắn vi phạm từ cấm

    # ==========================================
    # 6. TIN NHẮN HỢP LỆ -> Xử lý lệnh và chào hỏi bình thường
    # ==========================================
    await handle_greetings(message)
    await bot.process_commands(message)


# ==========================================
# SỰ KIỆN TỰ ĐỘNG RESET SẠCH SẼ KHI THÀNH VIÊN RỜI/BỊ KICK KHỎI SERVER
# ==========================================
@bot.event
async def on_member_remove(member):
    user_id = member.id
    if user_id in spam_warnings: 
        del spam_warnings[user_id]
    if user_id in bad_word_warnings: 
        del bad_word_warnings[user_id]
    if user_id in user_messages: 
        del user_messages[user_id]
    print(f"🧹 Đã giải phóng toàn bộ dữ liệu lưu trữ của user: {member} ({user_id})")
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            description=f"⚠️ | **Lệnh** `{ctx.message.content}` **không tồn tại!**",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        print(f"⚠️ | Lỗi: Lệnh `{ctx.message.content}` không tồn tại.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"⚠️ | **Lỗi: Thiếu đối số yêu cầu cho lệnh** `{ctx.command}`."
        )
        print(f"⚠️ | Lỗi: Thiếu đối số yêu cầu cho lệnh {ctx.command}.")
    else:
        print(f"⚠️ | Lỗi không xác định: {error}")


class HelpPaginator(discord.ui.View):

    def __init__(self, pages):
        super().__init__(timeout=60)  # Tự động đóng sau 60s
        self.pages = pages
        self.current_page = 0

    async def update_message(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=self.pages[self.current_page], color=0x808080
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.gray)
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_message(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.gray)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_message(interaction)


@bot.command(name="help")
async def help_command(ctx):
    pages = [
        (
            "**COMMAND SUPPORT (Trang 1/2):**\n"
            "------------------------------------------------\n"
            "=> __***Lệnh cho Member & Admin:***__\n\n"
            ":one: `!t` `ping`\n - **kiểm tra độ trễ giữa máy chủ Discord và máy tính**\n"
            ":two: `!t` `random 'member' 'phần thưởng'`\n * **member: Thành viên muốn random**\n - **phần thưởng: Món quà muốn tặng (ko cần cũng được)**\n"
            ":three: `!t` `translate 'ngôn ngữ đầu vào' 'ngôn ngữ đầu ra' 'văn bản`'\n * **ngôn ngữ đầu vào: Ngôn ngữ chính**\n - **ngôn ngữ đầu ra: Ngôn ngữ cần dịch**\n - **văn bản: Văn bản muốn dịch**\n"
            ":four: `!t` `languages`\n * **hỗ trợ ngôn ngữ cho lệnh traslate**\n"
        ),
        (
            "**COMMAND SUPPORT (Trang 2/2):**\n"
            "=> __***Lệnh dành cho `Administrator`:***__\n"
            ":one: `!t` `userinfo 'member'`\n * **member: Thành viên muốn xem thông tin**\n    **(nếu ko có thành viên muốn xem thông thì thông tin sẽ là người dùng lệnh)**\n"
            ":two: `!t` `kick 'member' 'reason'`\n * **member: Tên thành viên muốn kick**\n - **reason: Lý do kick**\n"
            ":three: `!t` `ban 'member' 'reason'`\n * **member: Tên thành viên muốn ban**\n - **reason: Lý do ban**\n"
            ":four: `!t` `unban 'member' 'reason'`\n * **member: Tên thành viên muốn unban**\n - **reason: Lý do unban**\n"
            ":five: `!t` `add_role 'member' 'role'`\n * **member: Tên thành viên muốn app role**\n - **role: Role muốn thêm**\n"
            ":six: `!t` `remove_role 'member' 'role'`\n * **member: Tên thành viên muốn remove role**\n - **role: Role muốn xóa**"
        ),
    ]

    view = HelpPaginator(pages)
    embed = discord.Embed(description=pages[0], color=0x808080)
    view.message = await ctx.send(embed=embed, view=view)


@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"**🏓 Pong! Độ trễ hiện tại là** `{latency}ms`")


@bot.command()
async def hello(ctx):
    await ctx.send("hello!")


@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason="Ko có lý do"):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.kick_members
    ):
        await ctx.send("**❌ | Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None:
        await ctx.send(
            "```!tkick 'member' 'reason'\n       ^^^^^^   ^^^^^\n^ là chỗ cần điền```"
        )
        return

    if (
        ctx.author.top_role <= member.top_role
        and ctx.author.id not in YOUR_USER_ID
    ):
        await ctx.send(
            "**❌ | Bạn không thể kick người có role cao hơn hoặc bằng bạn!**"
        )
        return

    if member.bot:
        await ctx.send("**❌ | Lệnh này không thể kick bot!**")
        return

    if member == ctx.author:
        await ctx.send("**❌ | Bạn không thể tự kick chính mình!**")
        return

    if member == ctx.guild.owner:
        await ctx.send("**❌ | Không thể kick chủ server!**")
        return

    bot_top_role = ctx.guild.me.top_role
    if bot_top_role.position <= member.top_role.position:
        await ctx.send("**Bot không thể kick thành viên này!**")
        return

    try:
        try:
            await member.send(
                f"Bạn đã bị **đá** khỏi **{ctx.guild.name}** | reason: {reason}"
            )
        except discord.Forbidden:
            pass

        await member.kick(reason=reason)
        await ctx.send(
            f"{member.mention} **đã bị đá khỏi server** | reason: {reason}"
        )
    except discord.Forbidden:
        await ctx.send("**❌ | Bot không có quyền kick thành viên này!**")
    except Exception as e:
        await ctx.send(f"**❌ | Đã xảy ra lỗi:** `{e}`")


@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do"):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.ban_members
    ):
        await ctx.send("**❌ | Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None:
        await ctx.send(
            "```!tban 'member' 'reason'\n      ^^^^^^   ^^^^^\n^ là chỗ cần điền```"
        )
        return

    if member.bot:
        await ctx.send("**❌ | Không thể ban bot!**")
        return

    if member == ctx.author:
        await ctx.send("**❌ | Bạn không thể tự ban chính mình!**")
        return

    if member == ctx.guild.owner:
        await ctx.send("**❌ | Không thể ban chủ server!**")
        return

    if ctx.author.id not in YOUR_USER_ID:
        if ctx.author.top_role <= member.top_role:
            await ctx.send(
                "**❌ | Bạn không thể ban người có role cao hơn hoặc bằng bạn!**"
            )
            return

    if ctx.guild.me.top_role <= member.top_role:
        await ctx.send("**❌ | Bot không thể ban thành viên này!**")
        return

    try:
        try:
            await member.send(
                f"Bạn đã bị **ban** khỏi **{ctx.guild.name}** | Lý do: {reason}"
            )
        except discord.Forbidden:
            pass

        await member.ban(reason=reason)
        await ctx.send(
            f"✅ | {member.mention} **đã bị ban khỏi server** | Lý do: {reason}"
        )
    except discord.Forbidden:
        await ctx.send("**❌ | Bot không có quyền ban thành viên này!**")
    except Exception as e:
        await ctx.send(f"**⚠️ | Đã xảy ra lỗi:** `{e}`")


@bot.command()
async def unban(ctx, user_id: int = None):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.ban_members
    ):
        await ctx.send("**❌ | Bạn không có quyền sử dụng lệnh này!**")
        return

    if user_id is None:
        await ctx.send(
            "```!tunban 'user_id'\n        ^^^^^^^\n^ ID người dùng cần gỡ ban```"
        )
        return

    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ | **Đã gỡ ban thành công**: {user} (`{user.id}`)")
    except discord.NotFound:
        await ctx.send("**❌ | Người dùng này không nằm trong danh sách ban!**")
    except discord.Forbidden:
        await ctx.send("**❌ | Bot không có quyền gỡ ban!**")
    except Exception as e:
        await ctx.send(f"**⚠️ | Đã xảy ra lỗi:** `{e}`")


@bot.command()
async def add_role(
    ctx, member: discord.Member = None, role: discord.Role = None
):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.manage_roles
    ):
        await ctx.send("**❌ | Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None or role is None:
        await ctx.send(
            "```!tadd_role 'member' 'role'\n            ^^^^^^   ^^^^\n^ là chỗ cần điền```"
        )
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"✅ | {member.mention} **đã được thêm role**")
    except discord.Forbidden:
        await ctx.send(
            "**❌ | Bot không có đủ quyền hạn để thêm role cho thành viên!**"
        )
    except discord.HTTPException:
        await ctx.send("**⚠️ | Đã xảy ra lỗi khi thêm role cho thành viên!**")
    except Exception as e:
        print(f"⚠️ | Đã xảy ra lỗi: {e}")


@bot.command()
async def remove_role(
    ctx, member: discord.Member = None, *, role: discord.Role = None
):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.manage_roles
    ):
        await ctx.send("**❌ | Bạn không có quyền thực hiện hành động này!**")
        return

    if member is None or role is None:
        await ctx.send(
            "```!tremove_role 'member' 'role'\n              ^^^^^^   ^^^^\n^ là chỗ cần điền```"
        )
        return

    try:
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} **đã bị xóa role**")
    except discord.Forbidden:
        await ctx.send(
            "**❌ | Bot không có đủ quyền hạn để xóa role của thành viên!**"
        )
    except discord.HTTPException:
        await ctx.send("**⚠️ | Đã xảy ra lỗi khi xóa role của thành viên!**")
    except Exception as e:
        print(f"⚠️ | Đã xảy ra lỗi: {e}")


@bot.command()
async def fake(ctx, user: discord.Member, *, message: str):
    try:
        # Đã sửa lỗi so sánh ID Admin ở đây
        if (
            ctx.author.id not in YOUR_USER_ID
            and not ctx.author.guild_permissions.administrator
        ):
            await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
            return

        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name=user.display_name)
        await webhook.send(
            content=message,
            username=user.display_name,
            avatar_url=user.avatar.url,
        )
        await webhook.delete()
    except discord.Forbidden:
        await ctx.send("**Bot không có quyền tạo webhook trong kênh này!**")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {str(e)}")


@fake.error
async def fake_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Bạn phải chỉ định một người dùng và tin nhắn!**")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("**Không tìm thấy người dùng!**")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("**Bot không có quyền thực hiện hành động này!**")
    else:
        await ctx.send(f"Đã xảy ra lỗi: {str(error)}")


@bot.command()
async def clear(ctx, amount: int = None):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.manage_messages
    ):
        await ctx.send("**Bạn không có quyền thực hiện hành động này!**")
        return

    if amount is None:
        await ctx.send(
            "```!tclear 'số lượng'\n        ^^^^^^^^\nđiền số tin nhắn cần xóa trên ^```"
        )
        return

    if amount < 1:
        await ctx.send("**Số lượng tin nhắn phải lớn hơn 0!**")
        return

    try:
        await ctx.message.delete()
        deleted = await ctx.channel.purge(
            limit=amount, check=lambda msg: not msg.pinned
        )
        await ctx.send(f"**Đã xóa {len(deleted)} tin nhắn!**", delete_after=5)
    except discord.Forbidden:
        await ctx.send("**Bot không có quyền xóa tin nhắn trong kênh này!**")
    except Exception as e:
        await ctx.send(f"**Đã xảy ra lỗi: {e}**")
        print(f"**Đã xảy ra lỗi: {e}**")


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("**Vui lòng nhập số lượng tin nhắn hợp lệ!**")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "```!tclear 'số lượng'\n        ^^^^^^^^\nđiền số tin nhắn cần xóa trên ^```"
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("**Bạn không có quyền để xóa tin nhắn!**")
    elif isinstance(error, discord.Forbidden):
        await ctx.send("**Bot không có quyền để xóa tin nhắn!**")


@bot.command()
async def random(
    ctx, members: commands.Greedy[discord.Member], *, prize: str = None
):
    if members:
        selected_member = rand.choice(members)
        message = f"🎲 Thành viên được chọn: {selected_member.mention}"
        if prize:
            message += f"\n🎁 Phần thưởng: {prize}"
        await ctx.send(message)
    else:
        await ctx.send("Vui lòng cung cấp ít nhất hai thành viên để chọn!")


@bot.command(aliases=["uinfo", "whois"])
async def userinfo(ctx, member: discord.Member = None):
    # Đã sửa lỗi so sánh ID Admin ở đây
    if (
        ctx.author.id not in YOUR_USER_ID
        and not ctx.author.guild_permissions.manage_messages
    ):
        await ctx.send("**❌ | Bạn không có quyền sử dụng lệnh này.**")
        return

    if member is None:
        member = ctx.author

    roles = [role.mention for role in member.roles[1:]]
    message_count = 0

    loading = await ctx.send("**⏳ | Đang tải thông tin người dùng...**")

    async for msg in ctx.channel.history(limit=500):
        if msg.author == member:
            message_count += 1

    embed = discord.Embed(
        title="**👤 THÔNG TIN NGƯỜI DÙNG**",
        description=f"**📌 Hồ sơ của** {member.mention}\n━━━━━━━━━━━━━━━━━━",
        color=discord.Color.green(),
        timestamp=ctx.message.created_at,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="**🆔 ID**", value=f"`{member.id}`", inline=True)
    embed.add_field(
        name="**📛 Tên người dùng**", value=f"`{member.name}`", inline=True
    )  # Sửa đổi hệ thống hiển thị tên mới
    embed.add_field(
        name="**🏷️ Biệt danh**", value=f"`{member.display_name}`", inline=True
    )
    embed.add_field(
        name="**📅 Tạo tài khoản**",
        value=member.created_at.strftime("%d/%m/%Y • %H:%M"),
        inline=False,
    )
    embed.add_field(
        name="**📥 Tham gia server**",
        value=member.joined_at.strftime("%d/%m/%Y • %H:%M"),
        inline=False,
    )
    embed.add_field(
        name="**💬 Tin nhắn gần đây**",
        value=f"`{message_count}` tin nhắn",
        inline=True,
    )
    embed.add_field(
        name="**🤖 Bot**", value="✅ Có" if member.bot else "❌ Không", inline=True
    )
    embed.add_field(
        name="**⭐ Vai trò cao nhất**",
        value=member.top_role.mention,
        inline=False,
    )
    embed.add_field(
        name=f"**🎭 Danh sách role** [{len(roles)}]",
        value=", ".join(roles) if roles else "Không có role",
        inline=False,
    )
    embed.set_footer(
        text=f"Yêu cầu bởi {ctx.author}",
        icon_url=ctx.author.display_avatar.url,
    )

    await loading.delete()
    await ctx.send(embed=embed)


LANGUAGES = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "ar": "Arabic",
    "hy": "Armenian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "hi": "Hindi",
    "hu": "Hungarian",
    "is": "Icelandic",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "kn": "Kannada",
    "km": "Khmer",
    "ko": "Korean",
    "la": "Latin",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "pl": "Polish",
    "pt": "Portuguese",
    "pa": "Punjabi",
    "ro": "Romanian",
    "ru": "Russian",
    "sr": "Serbian",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "es": "Spanish",
    "su": "Sundanese",
    "sw": "Swahili",
    "sv": "Swedish",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "**Vietnamese**",
    "cy": "Welsh",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "zu": "Zulu",
}


@bot.command()
async def languages(ctx):
    try:
        languages_str = "\n".join(
            [f"**{key}**: {value}" for key, value in LANGUAGES.items()]
        )
        embed = discord.Embed(
            title="🌍 Danh sách ngôn ngữ",
            description=languages_str,
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"**⚠️ Đã xảy ra lỗi:** `{e}`")


@bot.command()
async def translate(
    ctx, source_lang: str, target_lang: str, *, text_to_translate: str
):
    try:
        translated_text = GoogleTranslator(
            source=source_lang, target=target_lang
        ).translate(text_to_translate)
        embed = discord.Embed(
            title="🔄 Kết quả dịch",
            description=f"**Văn bản gốc (Ngôn ngữ: {source_lang})**:\n{text_to_translate}",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="**Văn bản dịch**", value=translated_text, inline=False
        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"**⚠️ Đã xảy ra lỗi:** `{e}`")


if token is None:
    print("❌ Không tìm thấy TOKEN!")
else:
    print("✅ TOKEN đã được tìm thấy!")
    bot.run(token)
