import asyncio
from datetime import timedelta, datetime as d
import random
import re
from requests import get
from json import loads
from os import getenv
from discord import Embed
import wavelink
from discord.ext import commands