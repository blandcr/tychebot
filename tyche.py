# Dice rolling bot for stuffsies

# LICENSE: GNU AGPLv3 because fuck the man. See LICENSE for details.

# \copyright    Copyright (c) 2016 Clint Bland (http://vela.みんな)
# \version      0.a
# \author       Clint Bland

import re
import sys
import tyche_calc_parser


def get_args ():
    import argparse as ap

    pp = ap.ArgumentParser ()

    pp.add_argument (
        "--config",
        dest="config",
        help="path to config file.",
        required=True
    )

    return pp.parse_args ()

def load_config (config_path):
    from yaml import safe_load, YAMLError

    try:
        with open (config_path, 'r') as ff:
            try:
                config = safe_load (ff)
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
    try:
        config['prefix']
    except Exception:
        config['prefix'] = '!'

def verify (config):
    try:
        config['token']
    except Exception:
        print ('Config file must have a `token : <YOUR DISCORD TOKEN>` entry')
        sys.exit (-1)


# takes an expr like "1d6" and returns an array of results of dice rolls
def diceroll_inner(expr):
    import random
    rng = random.SystemRandom()

    out = []
    roll = expr.split('d')

    # default to 1d if num_dice is omitted
    if roll[0] == '':
        roll[0] = "1"

    num_dice, die_order = map(int, roll)
    num_dice = max(min(num_dice, 256), 0) # 0 to 256 dice

    for die in range(num_dice):
        result = rng.randint(1, die_order)
        out.append(result)
    return out


# takes an expr like "2d6" and returns a result as "result+result"
def diceroll_repl(expr):
    out = ''
    for result in diceroll_inner( expr.group(0) ):
        out += '{}+'.format(result)
    return '('+out[:-1]+')' # strip the trailing `+`


# takes an expr like "1d6" and returns a result as "1d6 : <result> -> <total>"
def diceroll(expr):
    out = '`' + expr + ' : '
    total = 0
    for result in diceroll_inner(expr):
        total = total + result
        out += '{}, '.format(result)
    out = out[:-2]  # strip the trailing ` ,`
    out += ' -> {}` | '.format(total)

    return out


def run (config):
    import discord
    import asyncio
    from discord.ext import commands

    tyche = commands.Bot (
        command_prefix=config['prefix'],
        description='What fortunes may come your way are for me to decide.'
    )

    @tyche.event
    @asyncio.coroutine
    def on_ready ():
        print(
            '(II) Logged in as {} | {}'.format(tyche.user.name, tyche.user.id)
        )

    @tyche.command (
        pass_context=True,
        description= \
"""
Perform the specified calculation, replaces dice rolls with their results.
Exampls:
    !calc d6          -- rolls 1d6
    !calc 20d20 + 10  -- rolls 20d20 and adds 10
"""
    )
    @asyncio.coroutine
    def calc (
        context
    ):
        request = context.message.content[
            len(''.join ((context.prefix, context.command.name))):
        ].lstrip(' ')

        inter = re.sub(r'\d*d\d+', diceroll_repl, request)

        def evaluate(repl):
            return ''.join([
                repl.group(1),
                '{}'.format(tyche_calc_parser.evaluate(repl.group(2)))
            ])

        result = re.sub(r'(\s*)([\s\-+*/()\d]*[\-+*/()\d])', evaluate, inter)

        yield from tyche.say (
            '{} : `{} : {} -> {}`'.format (
                context.message.author.display_name, request, inter, result
            )
        )

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
    def roll (
        context
    ):
        request = context.message.content[
            len(''.join ((context.prefix, context.command.name))):
        ].lstrip(' ')
        rolls = request.split(' ')

        try:
            out = ''
            for roll in rolls:
                out += diceroll(roll)
            out = out[:-3] # strip the trailing ` | `
            yield from tyche.say (
                '{} : {}'.format (context.message.author.display_name, out)
            )
        except Exception:
            yield from tyche.say (
                'OH GOD SOMETHING HAPPENED AND WAS HORRIBLE PLS SAVE ME'
            )

    # RUN!
    tyche.run(config['token'])

if __name__ == "__main__":

    args = get_args ()

    config = load_config (args.config)

    munge (config)

    verify (config)

    run (config)

    sys.exit (0)

