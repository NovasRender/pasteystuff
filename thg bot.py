import discord
import time
import random
import string
import json
from io import StringIO

global_debug_mode = True
activedisclaimers = """
DISCLAIMER: PRONOUNS FOR THE CURRENT MOMENT DO NOT WORK, UNTIL I GET THIS WORKING THEY/THEM PRONOUNS WILL BE AUTOMATICALLY ASSIGNED, I APOLIGISE FOR MY SUCKY CODING, I SUCK AT MULTIINSTANCE STUFF!\n\nALTERNATE DISCLAIMER THAT THIS IS STILL IN A VERY EARLY BETA, PLEASE LET ME KNOW (@NOVADEVV) IF THERE ARE ANY ISSUES <3\n\nother than that thank you for using my bot !!
"""
time = time.time

credentials = "credentials.txt"
WEBHOOK_URL = "https://discord.com/api/webhooks/1366003318542831657/Mq8fKON4AkrZO_O_Xaj_rMAUN3dwETu6CULgL4VjlPWthO1oCbE9AuAZEzckY7p7kMOk"


async def globaldebug(interaction):
    if global_debug_mode:
        data = sessions_data.get(interaction.channel_id)
        if data:
            embed = discord.Embed(
                title="GLOBAL DEBUG MODE ENABLED",
                description="Session data has been attached as a JSON file.",
                color=discord.Color.red()
            )

            pretty_json = json.dumps(data, indent=4)

            json_file = StringIO(pretty_json)
            discord_file = discord.File(json_file, filename="session_debug.json")

            await interaction.followup.send(embed=embed, file=discord_file)
        else:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="No session data found",
                    description="There is no session data associated with this channel.",
                    color=discord.Color.orange()
                )
            )


with open(credentials, "r") as file:
    first_line = file.readline().strip()
    token = first_line.split("=")[1]

def loaddatafile(filename: str) -> list:
    actions = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            clean_line = line.strip()
            if clean_line:  # Ignore empty lines
                actions.append(clean_line)
    return actions

actionlist = loaddatafile("actions.txt")
deathlist = loaddatafile("deaths.txt")

if not deathlist:
    print("[ERROR] deaths.txt is empty! Please add some deaths.")
    deathlist = [
        "S|{player1} mysteriously disappeared into the mist.",
        "M|{player1} and {player2} were caught in a deadly trap together.",
        "A|{player1} watched as {players} were swept away by a flash flood."
    ]


print(actionlist)
print(deathlist)

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

startup_timestamp = int(time())


def create_embed(title: str = None, description: str = None) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        color=0xe69500
    )
    embed.set_footer(text="Made with 💖 by Nova")
    return embed

def format_death_description(description, player1, player2=None, pronouns1=None, pronouns2=None):

    if pronouns1:
        description = description.replace("{primary}", pronouns1[0]).replace("{secondary}", pronouns1[1])

    if player2 and pronouns2:
        description = description.replace("{player2}", player2).replace("{secondary}", pronouns2[1])
    
    return description

def parse_tributes(session_data):
    players = []
    player_pronouns = {}

    for tribute_entry in session_data['tributes']:
        name = tribute_entry['character_name']
        primary = tribute_entry['primary']
        secondary = tribute_entry['secondary']

        players.append(name)
        player_pronouns[name] = (primary, secondary)

    return players, player_pronouns


def calculateRound(players, player_pronouns, round_number, session_data):
    playercount = len(players)
    deaths = 0
    outcome = ""
    threshold_without_deaths = 5

    surviving_players = players.copy()
    used_players = set()

    if 'no_death_count' not in session_data:
        session_data['no_death_count'] = 0
    if 'round_deaths' not in session_data:
        session_data['round_deaths'] = []
    if 'all_deaths' not in session_data:
        session_data['all_deaths'] = []

    no_death_count = session_data['no_death_count']
    round_deaths = session_data['round_deaths']

    # If it's a recap round
    if round_number % 5 == 0:
        description = f"🏹 ROUND RECAP 🏹\n"
        description += f"## 💥 {len(round_deaths)} cannon shot{'s' if len(round_deaths) != 1 else ''} can be heard in the distance\n"
        for death in round_deaths:
            description += f"- ☠️ {death}\n"

        description += f"\n## 💫 Survivors\n"
        for player in surviving_players:
            description += f"- 💫 {player}\n"

        description += "\n📜 *The games will continue in the coming rounds, prepare tributes.*\n"

        # Optional: add a random lore footer
        

        session_data['round_deaths'] = []

        return description

    if no_death_count >= threshold_without_deaths:
        deaths = random.choices([1, 2], weights=[70, 30], k=1)[0]
        session_data['no_death_count'] = 0
    else:
        deaths = random.choices([0, 1, 2], weights=[50, 40, 10], k=1)[0]

    if deaths > 0:
        session_data['no_death_count'] = 0
        for part in range(deaths):
            death_event = random.choice(deathlist)
            type_of_death = death_event.split("|")[0]
            death_description = death_event.split("|")[1]

            if type_of_death == "S":
                player1 = random.choice(surviving_players)
                surviving_players.remove(player1)  # Ensure the player is fully removed
                used_players.add(player1)
                outcome += death_description.format(player1=player1, pronoun=player_pronouns[player1][0]) + "\n"
                session_data['round_deaths'].append(f"{player1} > District ??")

            elif type_of_death == "M":
                if len(surviving_players) >= 2:
                    player1 = random.choice(surviving_players)
                    surviving_players.remove(player1)
                    used_players.add(player1)
                    player2 = random.choice(surviving_players)
                    surviving_players.remove(player2)
                    used_players.add(player2)
                    outcome += death_description.format(
                        player1=player1, player2=player2,
                        pronoun1=player_pronouns.get(player1, ('they',))[0],
                        pronoun2=player_pronouns.get(player2, ('they',))[0]
                    ) + "\n"
                    session_data['round_deaths'].append(f"{player1} > District ??")
                    session_data['round_deaths'].append(f"{player2} > District ??")

            elif type_of_death == "A":
                player1 = random.choice(surviving_players)
                surviving_players.remove(player1)
                used_players.add(player1)
                num_deaths = min(len(surviving_players), random.randint(1, 3))
                dead_players = random.sample(surviving_players, num_deaths)
                for dp in dead_players:
                    surviving_players.remove(dp)
                    used_players.add(dp)
                outcome += " ▶ " + death_description.format(
                    player1=player1, players=", ".join(dead_players),
                    pronoun1=player_pronouns.get(player1, ('they',))[0]
                ) + "\n\n"
                session_data['round_deaths'].append(f"{player1} > District ??")
                for dp in dead_players:
                    session_data['round_deaths'].append(f"{dp} > District ??")

        session_data['all_deaths'].extend(session_data['round_deaths'])

    # Normal actions
    for player in surviving_players:
        if player in used_players:
            continue

        action_entry = random.choice(actionlist)
        _, action_text = action_entry.split("|", 1)
        action_text = action_text.strip()

        if "{Player1}" in action_text and "{Player2}" in action_text:
            remaining_players = [p for p in surviving_players if p != player and p not in used_players]
            if remaining_players:
                player2 = random.choice(remaining_players)
                used_players.add(player2)
            else:
                player2 = player
            action_text = action_text.replace("{Player1}", player).replace("{Player2}", player2)

        elif "{Player1}" in action_text:
            action_text = action_text.replace("{Player1}", player)

        used_players.add(player)
        outcome += f" ▷ {action_text}\n\n"

    session_data['no_death_count'] += 1

    lore_snippets = [
            "A whisper of rebellion rustled through the trees...",
            "A cannon echoed like thunder across the arena...",
            "Somewhere, a sponsor tightened their grip on a gift...",
            "Eyes in the sky watched without blinking..."
        ]
        
    description = f"{random.choice(lore_snippets)}\n\n"
    description += outcome

    return description



class ContinueButton(discord.ui.View):
    def __init__(self, owner_id, user_id, message_id, thread_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.user_id = user_id
        self.message_id = message_id
        self.thread_id = thread_id

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.green)
    async def continue_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id and interaction.user.id != self.user_id:
            await interaction.response.send_message("You can only continue the game if you are the owner or your own tribute.", ephemeral=True)
            return

        session_data = sessions_data.get(self.thread_id)
        if session_data:
            session_data['round'] += 1
            round_number = session_data['round']

            players, player_pronouns = parse_tributes(session_data)
            round_result = calculateRound(players, player_pronouns, session_data['round'], session_data)

            if session_data.get('death_announcements'):

                round_result += "\n\n" + session_data['death_announcements']

                session_data['death_announcements'] = None

            new_continue_view = ContinueButton(
                owner_id=self.owner_id,
                user_id=self.user_id,
                message_id=self.message_id,
                thread_id=self.thread_id
            )

            await interaction.response.send_message(
                embed=create_embed(title=f"Round {round_number}", description=round_result),
                view=new_continue_view
            )
        else:
            await interaction.response.send_message("This session doesn't exist anymore!", ephemeral=True)

class DeleteTributeButton(discord.ui.View):
    def __init__(self, owner_id, user_id, message_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.user_id = user_id
        self.message_id = message_id

    @discord.ui.button(label="Delete Tribute", style=discord.ButtonStyle.red)
    async def delete_tribute(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id and interaction.user.id != self.user_id:
            await interaction.response.send_message("You can only delete your own tribute or the one who created the session.", ephemeral=True)
            return

        session_data = sessions_data.get(interaction.channel.id)
        if session_data:
            session_data['tributes'] = [
                tribute for tribute in session_data['tributes']
                if tribute.get('message_id') != self.message_id
            ]

            try:
                message = await interaction.channel.fetch_message(self.message_id)
                await message.delete()
            except discord.NotFound:
                pass

            await interaction.response.send_message(embed=create_embed(title="Tribute Removed", description=f"A tribute has been removed from the session."))

            await globaldebug(interaction)
        else:
            await interaction.response.send_message("This session doesn't exist anymore!", ephemeral=True)

class SuggestActionDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Action", value="action"),
            discord.SelectOption(label="Death", value="death")
        ]
        super().__init__(placeholder="Choose the type of suggestion...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_value = self.values[0]
        await interaction.response.send_message(f"You selected: {self.selected_value}", ephemeral=True)

class SuggestActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SuggestActionDropdown())

sessions_data = {}
districts = 1

@tree.command(name="addrandom", description="Generates random tributes and adds them to the session.")
async def addrandom(interaction: discord.Interaction, amount: int):
    if interaction.user.id != 1079316234232922162:
        await interaction.response.send_message("You are unauthorised to be able to do this.")
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message("You can only add random tributes inside a **thread!**", ephemeral=True)
        return

    thread_id = interaction.channel.id
    session_data = sessions_data.get(thread_id)

    if not session_data:
        await interaction.response.send_message("This session no longer exists or isn't valid.", ephemeral=True)
        return

    # Generate random tributes
    for _ in range(amount):
        # Generate a random name (you can adjust this pattern or list)
        random_name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=6))
        
        # Generate random pronouns (you can customize this further)
        primary_pronoun = random.choice(["he", "she", "they"])
        secondary_pronoun = random.choice(["him", "her", "them"])
        
        # Create the tribute embed
        tribute_embed = create_embed(
            title="New Tribute Added!",
            description=f"Character added by {interaction.user.mention}\n\n**{random_name}**\n{primary_pronoun}/{secondary_pronoun}\n"
        )
        
        # Send the tribute embed in the channel
        message = await interaction.channel.send(embed=tribute_embed)

        # Save the tribute info including message ID
        session_data['tributes'].append({
            "user_id": interaction.user.id,
            "character_name": random_name,
            "primary": primary_pronoun,
            "secondary": secondary_pronoun,
            "message_id": message.id
        })

    await interaction.response.send_message(f"{amount} random tributes have been added to the session!", ephemeral=True)

@tree.command(name="latency", description="Returns details about the bot's latency.")
async def latency(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    uptime = f"<t:{startup_timestamp}:R>"
    servers = len(client.guilds)
    users = sum(g.member_count for g in client.guilds if g.member_count)

    embed = create_embed(
        title="Bot Stats",
        description=(
            f"🖥️  **Latency:** {latency}ms\n"
            f"💫  **Up Since:** {uptime}\n"
            f"🌍  **Servers:** {servers}\n"
            f"👥  **Users:** {users}"
        )
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="debug", description="get debug data")
async def debug(interaction: discord.Interaction):
    if not global_debug_mode:
        await interaction.response.send_message(embed=create_embed(title="DEBUG MENU", description="GLOBAL DEBUG MODE DISABLED, PLEASE ENABLE IT."))
    else:
        await interaction.response.send_message(embed=create_embed(title="DEBUG EMBED REQUESTED",description=f"gathering data at {startup_timestamp}, please wait."))
        await globaldebug(interaction)

@tree.command(name="newsession", description="Create a new hunger games session!")
async def newsession(interaction: discord.Interaction):
    thread = await interaction.channel.create_thread(
        name=f"{interaction.user.name}'s Session",
        type=discord.ChannelType.public_thread,
        invitable=True
    )

    intro_embed = create_embed(
        title="🏹 Welcome to the Hunger Games!",
        description=f"Prepare your character and step into the arena.\nOnly the strongest will survive. Good luck, tributes!\n\n## {activedisclaimers}"
    )

    welcome_embed = create_embed(
        title="New Session Created",
        description=(
            f"Welcome To **{interaction.user.name}'s** Hunger Games session!\n\n"
            "If you would like to join the session, please use the /joinsession command **inside this thread**.\n\n"
            "You will be asked for your character's name, pronouns, and an optional profile picture.\n"
            "If you don't provide an image, a default picture will be used."
        )
    )

    start_button = discord.ui.Button(label="Start Session", style=discord.ButtonStyle.green)



    async def start_session_callback(start_interaction: discord.Interaction):
        session_data = sessions_data.get(thread.id)
        if not session_data:
            await start_interaction.response.send_message("This session no longer exists!", ephemeral=True)
            return

        if start_interaction.user.id != session_data['owner']:
            await start_interaction.response.send_message("Only the session owner can start the session.", ephemeral=True)
            return

        await start_interaction.message.edit(view=None)

        continue_button_view = ContinueButton(
        owner_id=session_data['owner'],
        user_id=start_interaction.user.id,
        message_id=start_interaction.message.id,
        thread_id=thread.id  # 👈
        )


        await start_interaction.response.send_message(
            embed=create_embed(
                title="The Hunger Games Has Begun!",
                description="May the best survive!\n\nEach round there will be randomized events..."
            ),
            view=continue_button_view
        )



    start_button.callback = start_session_callback
    start_button_view = discord.ui.View()
    start_button_view.add_item(start_button)

    sessions_data[thread.id] = {
        'owner': interaction.user.id,
        'tributes': [],
        'district_counter': 1,  
        'round': 0
    }


    await thread.send(embed=intro_embed)
    await thread.send(embed=welcome_embed, view=start_button_view)
    await interaction.response.send_message(f"Created a session thread: {thread.mention}", ephemeral=True)

@tree.command(name="joinsession", description="Join a hunger games session by submitting your character.")
async def joinsession(interaction: discord.Interaction, name: str, primary_pronoun: str, secondary_pronoun: str, image: discord.Attachment = None):
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message("You can only join a session from **inside a thread!**", ephemeral=True)
        return

    thread_id = interaction.channel.id
    session_data = sessions_data.get(thread_id)

    if not session_data:
        await interaction.response.send_message("This session no longer exists or isn't valid.", ephemeral=True)
        return

    # Check if user is allowed multiple tributes
    if interaction.user.id != session_data['owner']:
        user_tributes = [t for t in session_data['tributes'] if t['user_id'] == interaction.user.id]
        if user_tributes:
            await interaction.response.send_message("You can only join with **one character**!", ephemeral=True)
            return

    district_number = session_data.get('district_counter', 1)
    if district_number > 13:
        await interaction.response.send_message("All districts have been taken!", ephemeral=True)
        return

    district = f"District {district_number}"
    session_data['district_counter'] += 1

    if image:
        image_url = image.url
    else:
        image_url = "attachment://nouserimage.png"

    tribute_embed = create_embed(
        title="New Tribute Joined!",
        description=f"Character added by {interaction.user.mention}\n\n**{name}**\n{primary_pronoun}/{secondary_pronoun}*\n Loyal member of *{district}*"
    )
    tribute_embed.set_thumbnail(url=image_url)

    files = []
    if not image:
        files.append(discord.File("nouserimage.png"))

    message = await interaction.channel.send(embed=tribute_embed, files=files)

    # Save the tribute info including message ID
    session_data['tributes'].append({
        "user_id": interaction.user.id,
        "character_name": name,
        "primary": primary_pronoun,
        "secondary": secondary_pronoun,
        "message_id": message.id
    })

    delete_button = DeleteTributeButton(owner_id=session_data['owner'], user_id=interaction.user.id, message_id=message.id)
    await message.edit(view=delete_button)

    await interaction.response.send_message("You have joined the session!", ephemeral=True)
    await globaldebug(interaction)

@tree.command(name="endsession", description="End the current session.")
async def endsession(interaction: discord.Interaction):
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message("You can only end a session from **inside a thread!**", ephemeral=True)
        return

    thread_id = interaction.channel.id
    session_data = sessions_data.get(thread_id)

    if not session_data:
        await interaction.response.send_message("This session no longer exists or isn't valid.", ephemeral=True)
        return

    if interaction.user.id != session_data['owner']:
        await interaction.response.send_message("Only the session owner can end the session.", ephemeral=True)
        return

    del sessions_data[thread_id]
    await interaction.channel.send("The Hunger Games session has ended! All tributes have been returned to their districts.")

@tree.command(name="suggestaction", description="Suggest an action that could happen during the games!")
async def suggestaction(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Suggest an Action or Death",
        description=(
            "Please select whether the suggestion is an **Action** or a **Death** from the dropdown.\n"
            "Then, enter the description of the event (e.g., player1 dropped a coconut on player2's head, killing them instantly).\n"
            "Example: Player1 throws a spear at Player2, hitting them in the chest and causing instant death."
        ),
        color=0xe69500
    )
    
    view = SuggestActionView()
    await interaction.response.send_message(embed=embed, view=view)

    def check(m):
        return m.author == interaction.user and isinstance(m.channel, discord.TextChannel)

    message = await client.wait_for("message", check=check)
    
    suggestion_description = message.content
    action_type = view.children[0].selected_value
    
    if not suggestion_description:
        await interaction.followup.send("You need to provide a valid suggestion description!", ephemeral=True)
        return

    action_embed = discord.Embed(
        title=f"Suggested {action_type.capitalize()}",
        description=f"**Suggested by**: {interaction.user.mention}\n**Type**: {action_type.capitalize()}\n**Suggestion**: {suggestion_description}",
        color=0xe69500
    )

    async with client.http._HTTPClient__session.post(
        WEBHOOK_URL, json={"embeds": [action_embed.to_dict()]}
    ) as response:
        if response.status == 204:
            await interaction.followup.send(embed=create_embed(title="Success", description="Your suggestion has been sent off, thank you for your pratrionage."))
        else:
            await interaction.followup.send(embed=create_embed(title="Error", description="There was an error creating your suggestion, please try again later"))


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(token)
