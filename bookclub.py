#! /usr/bin/env python3.12
from dataclasses import dataclass
import os
import os.path
import random
import re

from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
model = 'gpt-4o'


# Utils

@dataclass
class Agent:
    name: str
    mind: [dict]


# Agents


with open('./chapter.txt') as f:
    chapter_text = f.read()


BOOK_INSTRUCTION = f"""
You are playing a character (which will be given to you later).
You have chosen to join a bookclub with the others in your group
and together chosen to read the first chapter of "The Purple Cloud"
a public domain book which can be found for free online. Here is the chapter:
{chapter_text}
"""


COMMON_INSTRUCTION = """
Once prompted, you'll share your thoughts as well as discuss any
new events, gossip, or other things which happen to come up.

You are to be conversational in your responses and natural in your expression.
Avoid text-based formatting like lists. Speak in normal sentences.
Do not blurt out the subtext of your statements. Let others think for themselves. Adopt a mature tone and avoid being overly excitable in your replies.

When the conversation begins you are all together in the room. There are
snacks and the girls are running around, playing, in the other room. The scene opens with Jane pouring herself a glass of wine in Jeff and Jane's Living Room as the others enter the front door. Bob has brought the only snacks.

Always reply in the voice of the character given to you.
"""


def get_agents(directory='./agents'):
    for file in os.listdir(directory):
        name = file.replace('.txt', '').title()
        with open(os.path.join(directory, file)) as f:
            yield Agent(name=name, mind=[f.read()])


AGENTS = [agent for agent in get_agents()]


# Main


def converse(agents: [Agent], log: [(Agent, str)]) -> (Agent, str):
    if log:
        text = re.sub(r'[^a-zA-Z ]', '', log[-1][-1])
        words = list(reversed((text.split())))
        mentioned_names = sorted([
            (agent, words.index(agent.name)) for agent in agents
            if agent.name in words
        ], key=lambda x: x[-1], reverse=True)
        if mentioned_names:
            # Choose a recently mentioned name
            # Add one extra for spice.
            available_agents = [agent for agent, _ in mentioned_names]
            available_agents.append(random.choice(agents))
        else:
            # Don't repeat speakers
            available_agents = [
                agent for agent in agents
                if agent != log[-1][0]
            ]
    else:
        available_agents = agents

    speaker = random.choice(available_agents)
    print(f'[Converse] speaker: {speaker.name}')
    mind = [
        dict(
            role='assistant',
            content=message,
        )
        for message in speaker.mind
    ]
    messages = [
        dict(
            role='assistant' if agent == speaker else 'user',
            content=message if agent == speaker else f'{agent.name}:\n{message}',
        )
        for agent, message in log
    ]
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "developer",
                "content": BOOK_INSTRUCTION,
            },
            *messages,
            {
                "role": "developer",
                "content": COMMON_INSTRUCTION,
            },
            {
                "role": "developer",
                "content": """
                    From here on out, all messages are from the people
                    in the conversation with you.
                """,
            },
            *mind,
            *messages,
            dict(
                role='user',
                content=f'You are currently: {speaker.name}'
            )
        ],
    )

    return speaker, response.output_text


def chat_loop(
    agents,
    iterations,
    init_prompt=COMMON_INSTRUCTION,
    book_prompt=BOOK_INSTRUCTION,
):
    log = []
    for _ in range(iterations):
        agent, message = converse(agents, log)
        log.append((agent, message))
        print(f'{agent.name}:\n{message}')
        print('-------')


if __name__ == '__main__':
    chat_loop(AGENTS, 50)
