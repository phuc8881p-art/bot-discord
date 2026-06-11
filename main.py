import os
import random as rand
import discord
from deep_translator import GoogleTranslator
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

prefix = "!t"
intents = discord.Intents.all()
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

bot.remove_command("help")

YOUR_USER_ID = (1195361246195757118, 1335606447144173610)


async def handle_greetings(message):
    if message.content.lower() == "hello":
        await message.channel.send(f"Xin chào {message.author.mention}!")
    elif message.content.lower() == "hi":
        await message.channel.send(f"Chào {message.author.mention}!")
    elif message.content == f"<@{bot.user.id}>" or message.content == "<@1514521082772590753>":
        color = 0x1ABAFF
        
        embed = discord.Embed(
            description=(
                f"👋 **Xin chào {message.author.mention}**\n\n"
                f"🤖 **Tôi là Bot Discord của bạn và sẵn sàng để phục vụ!**\n"
                f"🔖 **Prefix của tôi là `{prefix}`**\n"
                f"ℹ️ **Để khám phá các tính năng và lệnh của tôi, hãy sử dụng `{prefix}help`** 💡"
            ),
            color=color
        )
        await message.channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await handle_greetings(message)

    await bot.process_commands(message)

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
            ":one:* `!t` `meme_meo`\n * **random meme mèo**\n"
            ":two:* `!t` `ping`\n - **kiểm tra độ trễ giữa máy chủ Discord và máy tính**\n"
            ":three:* `!t` `random 'member' 'phần thưởng'`\n * **member: Thành viên muốn random**\n - **phần thưởng: Món quà muốn tặng (ko cần cũng được)**\n"
            ":four:* `!t` `translate 'ngôn ngữ đầu vào' 'ngôn ngữ đầu ra' 'văn bản`'\n * **ngôn ngữ đầu vào: Ngôn ngữ chính**\n - **ngôn ngữ đầu ra: Ngôn ngữ cần dịch**\n - **văn bản: Văn bản muốn dịch**\n"
            ":five:* `!t` `languages`\n * **hỗ trợ ngôn ngữ cho lệnh traslate**\n"
        ),
        (
            "**COMMAND SUPPORT (Trang 2/2):**\n"
            "=> __***Lệnh dành cho `Administrator`:***__\n"
            ":one:* `!t` `userinfo 'member'`\n * **member: Thành viên muốn xem thông tin**\n    **(nếu ko có thành viên muốn xem thông thì thông tin sẽ là người dùng lệnh)**\n"
            ":two:* `!t` `kick 'member' 'reason'`\n * **member: Tên thành viên muốn kick**\n - **reason: Lý do kick**\n"
            ":three:* `!t` `ban 'member' 'reason'`\n * **member: Tên thành viên muốn ban**\n - **reason: Lý do ban**\n"
            ":four:* `!t` `unban 'member' 'reason'`\n * **member: Tên thành viên muốn unban**\n - **reason: Lý do unban**\n"
            ":five:* `!t` `add_role 'member' 'role'`\n * **member: Tên thành viên muốn app role**\n - **role: Role muốn thêm**\n"
            ":six:* `!t` `remove_role 'member' 'role'`\n * **member: Tên thành viên muốn remove role**\n - **role: Role muốn xóa**"
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
