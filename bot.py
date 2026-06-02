import discord
from discord import app_commands
from discord.ext import commands
import os

# ID kanału na oceny (zostaje bez zmian)
KANAL_OCEN_ID = 1511099870650302504 

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True          # <--- TO WŁĄCZA CZŁONKÓW
        intents.message_content = True  # <--- TO WŁĄCZA TREŚĆ WIADOMOŚCI
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(WidokOceny())
        await self.tree.sync()

bot = Bot()

# ==============================================================================
# 🌟 SYSTEM OCEN USŁUG (Zostaje i działa tak jak chciałeś)
# ==============================================================================

class ModalOpinii(discord.ui.Modal, title="Napisz swoją opinię"):
    opis = discord.ui.TextInput(
        label="Co sądzisz o wykonanej usłudze/grafice?",
        style=discord.TextStyle.paragraph,
        placeholder="Twoja opinia o grafice, kontakcie itp...",
        required=True,
        max_length=300
    )

    def __init__(self, gwiazdki: int):
        super().__init__()
        self.gwiazdki = gwiazdki

    async def on_submit(self, interaction: discord.Interaction):
        kanal_ocen = bot.get_channel(KANAL_OCEN_ID)
        if not kanal_ocen:
            await interaction.response.send_message("Błąd: Nie znaleziono kanału do wysyłania ocen!", ephemeral=True)
            return

        embed = discord.Embed(title="⭐ Nowa Ocena Usługi ⭐", color=discord.Color.purple())
        embed.add_field(name="Zamawiający", value=interaction.user.mention, inline=True)
        embed.add_field(name="Ocena wykonania", value="⭐" * self.gwiazdki, inline=True)
        embed.add_field(name="Opinia klienta", value=self.opis.value, inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await kanal_ocen.send(embed=embed)
        await interaction.response.send_message("Dziękujemy za wystawienie oceny za usługę!", ephemeral=True)

class WidokOceny(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def obsluga_gwiazdki(self, interaction: discord.Interaction, gwiazdki: int):
        await interaction.response.send_modal(ModalOpinii(gwiazdki))

    @discord.ui.button(label="⭐ 1", style=discord.ButtonStyle.danger, custom_id="star_1")
    async def star_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.obsluga_gwiazdki(interaction, 1)

    @discord.ui.button(label="⭐ 2", style=discord.ButtonStyle.secondary, custom_id="star_2")
    async def star_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.obsluga_gwiazdki(interaction, 2)

    @discord.ui.button(label="⭐ 3", style=discord.ButtonStyle.secondary, custom_id="star_3")
    async def star_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.obsluga_gwiazdki(interaction, 3)

    @discord.ui.button(label="⭐ 4", style=discord.ButtonStyle.primary, custom_id="star_4")
    async def star_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.obsluga_gwiazdki(interaction, 4)

    @discord.ui.button(label="⭐ 5", style=discord.ButtonStyle.success, custom_id="star_5")
    async def star_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.obsluga_gwiazdki(interaction, 5)

@bot.tree.command(name="ocena", description="Wysyła panel do oceny wykonanej usługi graficznej")
@app_commands.checks.has_permissions(administrator=True)
async def ocena(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Oceń wykonanie naszej usługi!",
        description="Kliknij odpowiednią liczbę gwiazdek poniżej, aby ocenić jakość zamówionej grafiki oraz kontakt z grafikiem.",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed, view=WidokOceny())

# ==============================================================================
# 🔨 NOWE FUNKCJE SYSTEMOWE I MODERACYJNE (Twoje nowe centrum dowodzenia)
# ==============================================================================

# 1. CZYSZCZENIE CZATU (/clear)
@bot.tree.command(name="clear", description="Czyści określoną liczbę wiadomości na kanale")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, ilosc: int):
    if ilosc < 1:
        await interaction.response.send_message("Musisz podać liczbę większą od 0!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True) # Żeby bot nie dostał laga przy usuwaniu
    usuniete = await interaction.channel.purge(limit=ilosc)
    await interaction.followup.send(f"Pomyślnie usunięto {len(usuniete)} wiadomości!", ephemeral=True)

# 2. BANOWANIE (/ban)
@bot.tree.command(name="ban", description="Banuje użytkownika z serwera")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak podanego powodu"):
    await uzytkownik.ban(reason=powod)
    embed = discord.Embed(title="🔨 Użytkownik Zbanowany", color=discord.Color.red())
    embed.add_field(name="Użytkownik", value=uzytkownik.mention, inline=True)
    embed.add_field(name="Przez", value=interaction.user.mention, inline=True)
    embed.add_field(name="Powód", value=powod, inline=False)
    await interaction.response.send_message(embed=embed)

# 3. WYRZUCANIE (/kick)
@bot.tree.command(name="kick", description="Wyrzuca użytkownika z serwera")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, uzytkownik: discord.Member, powod: str = "Brak podanego powodu"):
    await uzytkownik.kick(reason=powod)
    embed = discord.Embed(title="👢 Użytkownik Wyrzucony", color=discord.Color.orange())
    embed.add_field(name="Użytkownik", value=uzytkownik.mention, inline=True)
    embed.add_field(name="Przez", value=interaction.user.mention, inline=True)
    embed.add_field(name="Powód", value=powod, inline=False)
    await interaction.response.send_message(embed=embed)

# 4. INFORMACJE O UŻYTKOWNIKU (/userinfo)
@bot.tree.command(name="userinfo", description="Pokazuje informacje o danym użytkowniku")
async def userinfo(interaction: discord.Interaction, uzytkownik: discord.Member = None):
    uzytkownik = uzytkownik or interaction.user
    embed = discord.Embed(title=f"👤 Informacje o {uzytkownik.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=uzytkownik.display_avatar.url)
    embed.add_field(name="ID", value=uzytkownik.id, inline=True)
    embed.add_field(name="Status na serwerze", value=uzytkownik.top_role.mention, inline=True)
    embed.add_field(name="Dołączył do Discorda", value=uzytkownik.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="Dołączył do serwera", value=uzytkownik.joined_at.strftime("%d.%m.%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

# ==============================================================================
# 🚀 URUCHOMIENIE BOTA
# ==============================================================================

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')

token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("BŁĄD: Brak tokenu DISCORD_TOKEN w zmiennych środowiskowych!")
