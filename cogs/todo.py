import discord
from discord.ext import commands
import json

class ToDo(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.tasks = self.load_tasks()

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                content = file.read()

                loaded_tasks = json.loads(content)
                # Convert keys back to integers
                self.tasks = {int(key): value for key, value in loaded_tasks.items()}

                return self.tasks
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


    def save_tasks(self):
        # Convert keys to strings before saving
        tasks_to_save = {str(key): value for key, value in self.tasks.items()}
        with open('tasks.json', 'w') as file:
            json.dump(tasks_to_save, file, indent=4)

    @commands.command(name='addtask', aliases=['at'])
    async def add_task(self, ctx, *, task: str):
        if ctx.author.id not in self.tasks:
            self.tasks[ctx.author.id] = []

        self.tasks[ctx.author.id].append(task)
        self.save_tasks()
        await ctx.send(f'Task "{task}" added.')

    @commands.command(name='removetask', aliases=['rt'])
    async def remove_task(self, ctx, task_index: int):
        user_id = ctx.author.id
        
        if user_id in self.tasks and 1 <= task_index <= len(self.tasks[user_id]):
            removed_task = self.tasks[user_id].pop(task_index - 1)
            self.save_tasks()
            await ctx.send(f'Task "{removed_task}" removed.')
        else:
            await ctx.send('Invalid task index.')


    @commands.command(name='listtasks', aliases=['list'])
    async def list_tasks(self, ctx):
        if ctx.author.id in self.tasks and self.tasks[ctx.author.id]:
            task_list = '\n'.join([f'{index + 1}. {task}' for index, task in enumerate(self.tasks[ctx.author.id])])
            await ctx.send(f'Your tasks:\n{task_list}')
        else:
            await ctx.send('No tasks found.')



async def setup(client):
    await client.add_cog(ToDo(client))