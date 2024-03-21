import requests
from globals import AUTODART_USERS_URL
from utils import ppe

def get_player_average(user_id, variant = 'x01', limit = '100',access_token = None):
    # get
    # https://api.autodarts.io/as/v0/users/<user-id>/stats/<variant>?limit=<limit>
    try:
        res = requests.get(AUTODART_USERS_URL + user_id + "/stats/" + variant + "?limit=" + limit, headers={'Authorization': 'Bearer ' + access_token})
        m = res.json()
        # ppi(m)
        return m['average']['average']
    except Exception as e:
        ppe('Receive player-stats failed', e)
        return None