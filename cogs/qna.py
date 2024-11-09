import discord
from discord.ext import commands
import json
import random

class QNA(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Load questions from the JSON file
        with open("./dependencies/vcaa_algorithmic_questions.json", "r") as file:
            self.questions_data = json.load(file)["questions"]
        # Track active question and answer per user
        self.active_questions = {}

    @commands.command(name="algo")
    async def algo(self, ctx):
        """Command to ask a random algorithm question."""
        # Select a random question
        question = random.choice(self.questions_data)
        question_text = f"**Question:** {question['question']}\n"
        for option, text in question["options"].items():
            question_text += f"{option}: {text}\n"
        
        await ctx.send(question_text)
        self.active_questions[ctx.author.id] = question  # Save the question for the user

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        # Check if the message is an answer to an active question
        if message.author.id in self.active_questions:
            user_answer = message.content.strip().upper()
            correct_answer = self.active_questions[message.author.id]["answer"]

            # Respond based on whether the answer is correct or not
            if user_answer == correct_answer:
                await message.channel.send("✅ Correct answer! Well done!")
            else:
                await message.channel.send(f"❌ Incorrect. The correct answer was {correct_answer}.")

            # Remove the question after answering
            del self.active_questions[message.author.id]

async def setup(client):
    await client.add_cog(QNA(client))