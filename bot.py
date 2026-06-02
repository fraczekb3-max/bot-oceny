from flask import Flask
import threading
import os
import discord
from discord.ext import commands
from discord import app_commands

# --- 1. MINI-SERWER FLASK DLA RENDERA ---
app = Flask('')

@app.route('/')
def home():
    return "Bot działa!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask).start()

# --- 2. KONFIGURACJA BOTA ---
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True          
        intents.message_content = True  
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = Bot()

# --- 3. INTERFEJS OCENIANIA (Formularz / Modal) ---
class OcenaModal(discord.ui.Modal, title="Jak oceniasz naszą pracę?"):
    gwiazdki = discord.ui.TextInput(
        label="Liczba gwiazdek (1-5)", 
        placeholder="Wpisz cyfrę od 1 do 5...", 
        min_length=1, 
        max_length=1
    )
    
    opinia = discord.ui.TextInput(
        label="Twoja opinia", 
        style=discord.TextStyle.paragraph, 
        placeholder="Napisz kilka słów o naszej pracy...", 
        required=True
    )
    
    legit = discord.ui.TextInput(
        label="Czy usługa jest legitna? (Wpisz: Tak lub Nie)", 
        placeholder="Tak / Nie", 
        min_length=2, 
        max_length=3,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Sprawdzamy liczbę gwiazdek
        try:
            liczba_gwiazdek = int(self.gwiazdki.value)
            if liczba_gwiazdek < 1 or liczba_gwiazdek > 5:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("Błąd! Liczba gwiazdek musi być cyfrą od 1 do 5.", ephemeral=True)
            return

        # Formatowanie statusu Legit
        status_legit = self.legit.value.strip().capitalize()
        if status_legit not in ["Tak", "Nie"]:
            await interaction.response.send_message("Błąd! W polu 'Czy legitna' wpisz dokładnie 'Tak' lub 'Nie'.", ephemeral=True)
            return

        # Tworzenie Embedu z podsumowaniem oceny
        embed = discord.Embed(
            title="⭐ Nowa Ocena Pracy ⭐",
            color=discord.Color.green() if status_legit == "Tak" else discord.Color.red()
        )
        embed.add_field(name="Klient", value=interaction.user.mention, inline=False)
        embed.add_field(name="Ocena", value="⭐" * liczba_gwiazdek, inline=True)
        embed.add_field(name="Czy legitne?", value=f"✅ {status_legit}" if status_legit == "Tak" else f"❌ {status_legit}", inline=True)
        embed.add_field(name="Opinia", value=self.opinia.value, inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        # --- TWOJE ID KANAŁU Z OCENAMI ---
        ID_KANALU_OCEN = 1511099870650302504  

        try:
            kanal = interaction.client.get_channel(ID_KANALU_OCEN)
            if kanal:
                # Wysyłamy ocenę na publiczny kanał ocen
                await kanal.send(embed=embed)
                # Dyskretna odpowiedź dla klienta w tickecie
                await interaction.response.send_message("Dziękujemy za opinię! Twoja ocena została opublikowana na kanale z ocenami.", ephemeral=True)
            else:
                await interaction.response.send_message("Błąd: Nie znaleziono kanału o podanym ID. Upewnij się, że bot ma do niego dostęp.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Wystąpił problem podczas wysyłania: {e}", ephemeral=True)


# --- 4. KOMENDA URUCHAMIAJĄCA OKNO OCENY ---
@bot.tree.command(name="ocen", description="Oceń naszą pracę")
async def ocen(interaction: discord.Interaction):
    await interaction.response.send_modal(OcenaModal())


# --- 5. START BOTA ---
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Błąd: Brak DISCORD_TOKEN w zmiennych środowiskowych!")
