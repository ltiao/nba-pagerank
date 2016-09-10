import json

from data import teams_details


league_mapping = {
    'NBA': '00',
    'ABA': '01',
}


def test(league='NBA'):
    return teams_details().index.values.tolist()


def miserables():
    with open('miserables.json', 'r') as infile:
        mis = json.load(infile)
    return mis


def trans_kwargs(trans={}):

    def trans_kwargs_dec(func):

        def new_func(*args, **kwargs):

            return func(*args, **kwargs)

        return new_func

    return trans_kwargs_dec
