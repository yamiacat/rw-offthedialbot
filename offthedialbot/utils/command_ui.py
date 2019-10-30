"""Holds api for working with a custom command ui."""
import utils
import asyncio


class CommandUI:

    def __init__(self, ctx, embed):
        """Initilize command UI and declare self variables."""
        self.reply_task = None

    async def __new__(cls, ctx, embed):
        """Use async to create embed and passive task on class creation."""
        self = super().__new__(cls)

        self.ctx = ctx
        self.embed = embed

        ctx.ui = await self.create_ui(ctx, embed)
        return self

    @staticmethod
    async def create_ui(ctx, embed):
        """Create and return the discord embed UI."""
        ui = await ctx.send(embed=embed)
        await ui.add_reaction('❌')
        return ui

    async def update(self):
        """Update the ui with new information."""
        await self.ctx.ui.edit(embed=self.embed)

    async def end(self, status: bool):
        """End UI interaction and display status."""
        key = {True: utils.embeds.SUCCESS, False: utils.embeds.CANCELED}
        await self.ctx.ui.edit(embed=key[status])
        await self.ctx.ui.clear_reactions()

    async def get_reply(self, event: str = 'message', *, timeout: int = 120, valids: list = None):
        """Get the reply from the user."""

        # Add valid reactions if valids are specified
        for react in (valids if valids else []):
            await self.ctx.ui.add_reaction(react)

        # Key that determines which check to use for the event
        check = {
            'message': lambda m: utils.checks.msg(m, self.ctx),
            'reaction_add': lambda r, u: utils.checks.react((r, u), self.ctx, valids=valids)
        }
        # Create Tasks
        reply_task = asyncio.create_task(self.ctx.bot.wait_for(event, check=check[event]))
        cancel_task = asyncio.create_task(
            self.ctx.bot.wait_for('reaction_add', check=lambda r, u: utils.checks.react((r, u), self.ctx, valids='❌'))
        )
        # asyncio.wait the set of tasks
        wait_result = await self.wait_tasks({reply_task, cancel_task})

        # Get result
        if wait_result[1] == cancel_task:
            await self.end(status=False)
            reply = False

        else:
            reply = wait_result[0]

            # Once tasks are waited
            if event == 'message':
                await reply.delete()

            # Remove valid reactions if valids are specified
            for react in (valids if valids else []):
                await self.ctx.ui.remove_reaction(react)

        return reply

    @staticmethod
    async def wait_tasks(tasks: set):
        """Try statement to asyncio.wait a set of tasks, and return the first completed."""
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # If timeout occurs
        except asyncio.TimeoutError:
            task = None
            reply = None

        # If task completes
        else:
            # Cancel pending tasks
            for rest in pending:
                rest.cancel()

            task = done.pop()
            reply = task.result()

        return reply, task
