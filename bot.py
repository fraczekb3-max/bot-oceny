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
        try:
            liczba_gwiazdek = int(self.gwiazdki.value)
            if liczba_gwiazdek < 1 or liczba_gwiazdek > 5:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("Błąd! Liczba gwiazdek musi być cyfrą od 1 do 5.", ephemeral=True)
            return

        status_legit = self.legit.value.strip().capitalize()
        if status_legit not in ["Tak", "Nie"]:
            await interaction.response.send_message("Błąd! W polu 'Czy legitna' wpisz dokładnie 'Tak' lub 'Nie'.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⭐ Nowa Ocena Pracy ⭐",
            color=discord.Color.green() if status_legit == "Tak" else discord.Color.red()
        )
        embed.add_field(name="Klient", value=interaction.user.mention, inline=False)
        embed.add_field(name="Ocena", value="⭐" * liczba_gwiazdek, inline=True)
        embed.add_field(name="Czy legitne?", value=f"✅ {status_legit}" if status_legit == "Tak" else f"❌ {status_legit}", inline=True)
        embed.add_field(name="Opinia", value=self.opinia.value, inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        ID_KANALU_OCEN = 1511099870650302504  
        ID_WIADOMOSCI_STATS = 1511306047447498784  

        try:
            kanal = interaction.client.get_channel(ID_KANALU_OCEN)
            if kanal:
                # 1. Wysyłamy nową ocenę klienta
                await kanal.send(embed=embed)
                await interaction.response.send_message("Dziękujemy za opinię! Twoja ocena została opublikowana.", ephemeral=True)
                
                # 2. Zliczamy wszystkie stare oceny z historii kanału, żeby wyliczyć średnią
                sum_stars = 0
                count_reviews = 0
                count_legit = 0
                
                async for message in kanal.history(limit=200):
                    if message.embeds:
                        emb = message.embeds[0]
                        if emb.title == "⭐ Nowa Ocena Pracy ⭐":
                            count_reviews += 1
                            for field in emb.fields:
                                if field.name == "Ocena":
                                    sum_stars += field.value.count("⭐")
                                if field.name == "Czy legitne?" and "✅" in field.value:
                                    count_legit += 1
                
                # Zabezpieczenie matematyczne, jeśli to pierwsza ocena w historii
                if count_reviews == 0:
                    avg_rating = liczba_gwiazdek
                    count_reviews = 1
                    count_legit = 1 if status_legit == "Tak" else 0
                else:
                    avg_rating = round(sum_stars / count_reviews, 2)

                # 3. Tworzymy nowy wygląd kafelka statystyk (w stylu Allegro)
                stats_embed = discord.Embed(
                    title="📊 PODSUMOWANIE OPINII KLIENTÓW 📊",
                    description="Statystyki naszej pracy aktualizowane automatycznie.",
                    color=discord.Color.gold()
                )
                stats_embed.add_field(name="Średnia ocena", value=f"⭐ **{avg_rating}** / 5", inline=True)
                stats_embed.add_field(name="Wszystkich opinii", value=f"📝 {count_reviews}", inline=True)
                stats_embed.add_field(name="Potwierdzone transakcje (Legit)", value=f"✅ {count_legit}", inline=False)
                
                # Pasek postępu zależny od średniej
                progress_bar = "🟩" * int(round(avg_rating)) + "⬜" * (5 - int(round(avg_rating)))
                stats_embed.add_field(name="Status satysfakcji", value=progress_bar, inline=False)

                # 4. Edytujemy Twoją przypiętą wiadomość
                try:
                    stats_message = await kanal.fetch_message(ID_WIADOMOSCI_STATS)
                    await stats_message.edit(content=None, embed=stats_embed)
                except Exception as e:
                    print(f"Błąd edycji wiadomości statystyk: {e}")

            else:
                await interaction.response.send_message("Błąd: Nie znaleziono kanału.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Wystąpił problem: {e}", ephemeral=True)


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
