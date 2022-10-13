import math
import discord
import yaml
from schema import Schema
from discord.ext import tasks
from web3 import Web3

schema = Schema({"address": str, "function_name": str,
                "abi": str, "token": str, "rpc": str, "interval": int})

with open("config.yaml", "r") as configfile:
    config = yaml.safe_load(configfile)
    schema.validate(config)

address = config.get("address")
function_name = config.get("function_name")
ABI_path = config.get("abi")

ABI = open(f"abi/{ABI_path}", "r").read()
client = discord.Client(intents=None)
w3 = Web3(Web3.HTTPProvider(config.get("rpc")))
contract = w3.eth.contract(address=address, abi=ABI)


@client.event
async def on_ready():
    updateTVL.start()


@tasks.loop(minutes=config.get("interval"))
async def updateTVL():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Exegol TVL"))
    totalSupply = getattr(contract.functions, function_name)().call()
    formattedSupply = f"${round((totalSupply / math.pow(10,6)), 2)}"
    try:
        await client.user.edit(username=formattedSupply)
    except:
        print("Failed to update username")


client.run(config.get("token"))
