from discord_slash import SlashCommand
def setup(self):
    return SlashCommand(self, override_type=True)