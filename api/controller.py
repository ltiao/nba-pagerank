from data import teams_details


league_mapping = {
    'NBA': '00',
    'ABA': '01',
}


def test(league='NBA'):
    return teams_details().index.values.tolist()


def trans_kwargs(trans={}):

    def trans_kwargs_dec(func):

        def new_func(*args, **kwargs):

            return func(*args, **kwargs)

        return new_func

    return trans_kwargs_dec
