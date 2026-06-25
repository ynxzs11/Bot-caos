import discord
from discord import app_commands
from discord.ui import Modal, TextInput, View
import random

# --- CONFIGURAÇÕES ---
import os
TOKEN = os.getenv("DISCORD_TOKEN")

# IDs (Certifique-se de preencher os valores corretos)
ID_CARGO_MEMBRO = 1518620698959151324
ID_CARGO_VERIFICADO = 000000000000000000 # <-- DEFINA ISSO
ID_CARGO_ADV1 = 1518622737587765407
ID_CARGO_ADV2 = 1518622784761233500
ID_CARGO_ADV3 = 1518622827148873858

ID_CANAL_SOLICITACOES = 1518623560883634258
ID_CANAL_LOGS_STAFF = 1518627200448860160
ID_CANAL_ANUNCIOS_PROMO = 1518697552147382393
ID_CANAL_ANUNCIOS_REBAIX = 1518697552147382393
ID_CANAL_PD_STAFF = 1518717793858486324
ID_CANAL_PD_PUBLICO = 1518697654769422536
ID_CANAL_ADV_STAFF = 000000000000000000 
ID_CANAL_ADV_PUBLICO = 1518679203124482048

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(BotaoRegistroView())
        self.add_view(AdminAprovacaoView())
        await self.tree.sync()

client = Client()

# --- CLASSES DE INTERAÇÃO ---

class AdminAprovacaoView(View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.green, custom_id="adm_aprovar", emoji="✅")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_registro(interaction, aprovado=True)
        
    @discord.ui.button(label="Reprovar", style=discord.ButtonStyle.red, custom_id="adm_reprovar", emoji="✖️")
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.processar_registro(interaction, aprovado=False)
        
    async def processar_registro(self, interaction: discord.Interaction, aprovado: bool):
        await interaction.response.defer()
        embed = interaction.message.embeds[0]
        user_id = int(embed.fields[0].value.replace('<@', '').replace('>', ''))
        nome_rp = embed.fields[2].value
        id_game = embed.fields[1].value
        
        member = interaction.guild.get_member(user_id)
        role_verificado = interaction.guild.get_role(ID_CARGO_VERIFICADO)
        
        if aprovado and member:
            try:
                await member.edit(nick=f"{nome_rp} | {id_game}")
                if role_verificado: await member.add_roles(role_verificado)
                embed.color = discord.Color.green()
                embed.title = "✅ Registro Aprovado"
            except: pass
        else:
            embed.color = discord.Color.red()
            embed.title = "✖️ Registro Reprovado"
            
        self.clear_items()
        await interaction.edit_original_response(embed=embed, view=self)

class FormularioRegistro(Modal, title="Registro FiveM"):
    nome_rp = TextInput(label="Nome do Personagem", max_length=20)
    id_game = TextInput(label="ID do Jogo", max_length=6)
    recrutador = TextInput(label="Recrutador", required=False)
    
    async def on_submit(self, interaction: discord.Interaction):
        canal_admin = interaction.guild.get_channel(ID_CANAL_SOLICITACOES)
        embed = discord.Embed(title="Solicitação de Registro", color=discord.Color.gold())
        embed.add_field(name="Usuário", value=interaction.user.mention)
        embed.add_field(name="ID", value=self.id_game.value)
        embed.add_field(name="Nome", value=self.nome_rp.value)
        await canal_admin.send(embed=embed, view=AdminAprovacaoView())
        await interaction.response.send_message("✅ Solicitação enviada!", ephemeral=True)

class BotaoRegistroView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="INICIAR REGISTRO", style=discord.ButtonStyle.blurple, custom_id="btn_registro_inicio", emoji="📝")
    async def botao_callback(self, interaction: discord.Interaction, button: discord.ui.Button): 
        await interaction.response.send_modal(FormularioRegistro())

# --- FUNÇÃO QUE FALTAVA ---
async def log_adv_completo(guild, membro, staff, nivel, motivo, acao):
    canal = guild.get_channel(ID_CANAL_ADV_STAFF)
    if canal:
        embed = discord.Embed(title=f"⚠️ {nivel}", color=discord.Color.yellow())
        embed.add_field(name="Membro", value=membro.mention)
        embed.add_field(name="Motivo", value=motivo)
        await canal.send(embed=embed)

# --- EVENTOS E COMANDOS ---
@client.event
async def on_ready():
    print(f'Bot logado como {client.user}')

@client.tree.command(name="comecar", description="Inicia o sistema de registro")
async def comecar(interaction: discord.Interaction):
    embed = discord.Embed(title="Verificação Obrigatória", description="Clique abaixo para se registrar.", color=discord.Color.dark_gray())
    await interaction.channel.send(embed=embed, view=BotaoRegistroView())
    await interaction.response.send_message("Sistema iniciado!", ephemeral=True)

# ... (Mantenha as outras funções de LOG e COMANDOS que já estavam corretas no seu script)

client.run(TOKEN)
