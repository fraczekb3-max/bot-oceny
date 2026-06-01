import discord
from discord import app_commands
from discord.ext import commands
import os

# TUTAJ WPISZ ID SWOJEGO KANAŁU NA OCENY (usuń te cyfry i wklej swoje)
KANAL_OCEN_ID = 1511099870650302504 

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(WidokOceny())
        await self.tree.sync()

bot = Bot()

class ModalOpinii(discord.ui.Modal, title="Napisz swoją opinię"):
    opis = discord.ui.TextInput(
        label="Co sądzisz o pomocy administratora?",
        style=discord.TextStyle.paragraph,
        placeholder="Twoja opinia...",
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

        embed = discord.Embed(title="⭐ Nowa Ocena Administratora ⭐", color=discord.Color.green())
        embed.add_field(name="Oceniający", value=interaction.user.mention, inline=True)
        embed.add_field(name="Ocena", value="⭐" * self.gwiazdki, inline=True)
        embed.add_field(name="Opinia", value=self.opis.value, inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await kanal_ocen.send(embed=embed)
        await interaction.response.send_message("Dziękujemy za wystawienie oceny!", ephemeral=True)

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

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')

@bot.tree.command(name="ocena", description="Wysyła panel do oceny pracy administracji")
@app_commands.checks.has_permissions(administrator=True)
async def ocena(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Oceń pracę naszej administracji!",
        description="Kliknij odpowiednią liczbę gwiazdek poniżej, aby ocenić pomoc, którą otrzymałeś w tym tickecie.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=WidokOceny())

bot.run(os.environ.get("DISCORD_TOKEN"))
