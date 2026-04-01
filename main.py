import discord
from discord.ext import commands
import asyncio

# --- CONFIGURATION ---
TOKEN = 'MTQ4ODYxNTExMTgwNjQyMzA5MA.Gk5TeG.50-Wi0ZyqhSU6QywGhXiJjfaHlv6WAWMKgGNhg'
CATEGORY_ID = 1488187894882631989  
STAFF_ROLE_IDS = [1488664625460285602] 

# --- 1. PERSISTENT CLOSE VIEW ---
class TicketCloseView(discord.ui.View):
    def __init__(self):
        # RULE #1: The Close button view must have timeout=None
        super().__init__(timeout=None)

    @discord.ui.button(label="Cancella il Ticket", style=discord.ButtonStyle.danger, custom_id="perm_delete_btn_v3")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Il ticket si cancellerà tra 5 secondi...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- 2. PERSISTENT PANEL VIEW ---
class TicketPanelView(discord.ui.View):
    def __init__(self):
        # RULE #2: The Main Panel view must have timeout=None
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="perm_dropdown_v3", 
        placeholder="Choose a category to open a ticket...",
        options=[
            discord.SelectOption(label="Supporto Generale", emoji="📩"),
            discord.SelectOption(label="Segnalazione di un utente", emoji="🐛"),
            discord.SelectOption(label="Blacklist", emoji="💰"),
             discord.SelectOption(label="Candidature Staff", emoji="📋"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)

        if not category:
            return await interaction.response.send_message("Error: Category ID invalid.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        for role_id in STAFF_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"ticket-{interaction.user.name.lower()}".replace(" ", "-")
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(title="Supporto", description=f"Ciao {interaction.user.mention}, lo staff risponderà al tuo ticket il prima possibile.", color=discord.Color.green())
        
        # RULE #3: When sending the view, it must be the persistent class
        await ticket_channel.send(embed=embed, view=TicketCloseView())

# --- 3. THE BOT ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This registers the views with the bot's internal listener
        self.add_view(TicketPanelView())
        self.add_view(TicketCloseView())

bot = MyBot()

@bot.event
async def on_ready():
    print(f"### SYSTEM ONLINE: {bot.user.name} ###")

@bot.command()
@commands.has_permissions(administrator=True)
async def post_panel(ctx):
    embed = discord.Embed(title="📩Assistenza", description="Seleziona una delle seguenti categorie per creare un ticket di assistenza.")
    await ctx.send(embed=embed, view=TicketPanelView())

bot.run('MTQ4ODYxNTExMTgwNjQyMzA5MA.GWhOns.ppPZsVF8HSjMYq9HmFfLdlxOcQ94O4UQIK5M_c')
