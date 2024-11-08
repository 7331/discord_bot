import discord
from discord.ui import InputText, Modal
from discord.enums import InputTextStyle
from string import ascii_letters, digits
from random import choices
from discord.ext import commands
from functools import lru_cache

#simple verification challenge using pycord

DEFAULT_VERIFICATION_ROLE = 'verified'
DEFAULT_TIMEOUT = 15
DEFAULT_CODE_LENGTH = 8


class VerificationModal(Modal):
    def __init__(self, *, timeout: float = DEFAULT_TIMEOUT, verification_code_length: int = DEFAULT_CODE_LENGTH, hardcode: str):
        self.verification_code = hardcode or ''.join(choices(ascii_letters + digits, k=verification_code_length))
        self.length = len(self.verification_code)
        
        super().__init__(title=f'Your code: {self.verification_code}', timeout=timeout)
        
        self.verification_input = InputText(
            style=InputTextStyle.short if self.length <= 12 else InputTextStyle.long,
            label=f'Your code is case sensitive',
            placeholder='3/3 attempts remaining...',
            min_length=self.length,
            max_length=self.length,
            required=True
        )
        self.add_item(self.verification_input)

    async def callback(self, interaction: discord.Interaction):
        # extra security check author
        if self.verification_input.value == self.verification_code:
            # verified
            print('good')
        else:
            # not verified
            print('bad')

    async def on_timeout(self):
        print('timeout')

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        print('error')

class VerificationSlashCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    @lru_cache(maxsize=None)
    def get_member_role(guild: discord.Guild) -> discord.Role:
        return discord.utils.get(guild.roles, name=DEFAULT_VERIFICATION_ROLE)
    
    async def invoked_by(ctx: discord.ApplicationContext) -> bool:
        print(ctx.author)
        return True

    @commands.cooldown(
        1, 5, commands.BucketType.user
    )  # The command can only be used once in 5 seconds
    # one command running per user at a time
    @commands.guild_only()
    @commands.check(invoked_by)
    @commands.slash_command(
        name='verify',
        description='self verification',
        guild_ids=[1268024121674043412])
    async def verification_slash_command(self, ctx: discord.ApplicationContext):
        verification_modal = VerificationModal()
        await ctx.send_modal(verification_modal)

    @verification_slash_command.after_invoke
    async def record_slash_command_usage(self, ctx: discord.ApplicationContext):
        print('logged')

def setup(bot):
    bot.add_cog(VerificationSlashCommand(bot))
