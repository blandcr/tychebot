# Dice rolling bot for stuffsies

# LICENSE: GNU AGPLv3 because fuck the man. See LICENSE for details.

# \copyright    Copyright (c) 2016 Clint Bland (http://vela.みんな)
# \version      0.a
# \author       Clint Bland

import sys

def get_args ():
    import argparse as ap

    pp = ap.ArgumentParser ()

    pp.AddArgument (
        "--config",
        dest="config",
        help="path to config file.",
        required=True
    )

    return pp.parse_args ()

def load_config (config_path):
    from yaml import safe_load_all, YAMLError

    try:
        with open (config_path, 'r') as ff:
            try:
                config = safe_load_all (ff)
                if config is None:
                    print ("Config file is empty or unrecognizable!")
                    sys.exit (-1)
                else:
                    return config
            except YAMLError:
                print ("Error parsing config file. TODO: print the deetz.")
                sys.exit (-1)
    except FileNotFoundError:
        print ("Config file `{}` does not exist!".format(config_path))
        sys.exit (-1)

def munge (config):
    if not config.has_key ('prefix'):
        config['prefix'] = '.'

def verify (config):
    if not config.has_key ('token'):
        print ('Config file must have a `token : <YOUR DISCORD TOKEN>` entry')
        sys.exit (-1)

def run (config):
    import discord
    import asyncio
    from discord.ext import commands

    import random

    rng = random.SystemRandom()

    tyche = commands.Bot (
        command_prefix=config['prefix'],
        deascription='What fortunes may come your way are for me to decide.'
    )

    @tyche.event
    @asyncio.coroutine
    def on_ready ():
        print('(II) Logged in as {} | {}'.format(tyche.user.name, tyche.user.id))

    @tyche.command (
        pass_context=True,
        description= \
"""
Roll the specified dice, even if they are a geometrical impossibility in our
euclidean 3space.
Examples:
    !roll 1d6     -- rolls 1d6
    !roll 3d20    -- rolls 3d20, providing each roll as well as the sum
    !roll 4d7     -- rolls 4d7 (what's a seven sided die?)
    !roll 1d6 2d3 -- rolls 1d6 and then 2d3, providing each roll as well as the
                     sum of the 2d3
"""
    )
    @asyncio.coroutine
    def roll_action (
        context,
        request
    ):
        try:
            rolls = (map(int, roll.split('d')) for roll in request.split(' '))
        except Exception:
            yield from tyche.say (
                '{}, I do not understand what is this.'.format(context.author)
            )

        try:
            out = ''
            for roll in rolls:
                out = out + '{}d{} :'.format(roll)
                total = 0
                for die in range (roll[0]):
                    result = rng.randint(0, roll[1])
                    total = total + result
                    out = out + '{}, '.format(result)
                out = out[:-2] # strip the trailing ` ,`
                out = out + ' -> {} | '.format(total)
            out = out[:-3] # strip the trailing ` | `
            yield from tyche.say ('{} : {}'.format (context.author, out))
        except Exception:
            yield from tyche.say (
                'OH GOD SOMETHING HAPPENED AND WAS HORRIBLE PLS SAVE ME'
            )

if __name__ == "__main__":

    args = get_args ()

    config = load_config (args.config)

    munge (config)

    verify (config)

    run (config)

    sys.exit (0)

