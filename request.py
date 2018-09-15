#encoding: utf-8
import time
import sys
import random
import json
import datetime
import requests
import igraph


def get(url, command, params={}, timeout=5, max_retries=5, backoff_factor=1.3):
    query = url + "/" + command + "?"
    for key in params:
        query += key + "=" + str(params[key]) + "&"
    query += "v=5.53"
    delay = 0
    for i in range(max_retries):
        try:
            response = requests.get(query)
            return response
        except:
            print(sys.exc_info()[0])
        time.sleep(delay)
        delay = min(delay * backoff_factor, timeout)
        delay += random.random()
    print('Нет соединения с сервером!')
    sys.exit(0)
    return None


def get_friends(user_id, fields='bdate'):
    """ Returns a list of user IDs or detailed information about a user's friends """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"

    domain = "https://api.vk.com/method"

    query_params = {
        'access_token': access['token'],
        'user_id': user_id,
        'fields': fields
    }
    response = get(domain, 'friends.get', query_params)
    if 'response' not in json.loads(response.text):
        return None
    return json.loads(response.text)['response']['items']


def age_predict(user_id):
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    
    friends = get_friends(user_id)
    years_sum = 0
    count = 0
    for friend in friends:
        if 'bdate' in friend and len(friend['bdate'].split('.')) == 3:
            years_sum += int(friend['bdate'].split('.')[2])
            count += 1
    if count == 0:
        return 'У ваших друзей не указана дата рождения'
    return int(2017 - years_sum / count)


def messages_get_history(user_id, offset, count):
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    assert isinstance(offset, int), "offset must be positive integer"
    assert offset >= 0, "user_id must be positive integer"
    assert count >= 0, "user_id must be positive integer"
    
    domain = "https://api.vk.com/method"
    params = {
        'access_token': access['token'],
        'offset': offset,
        'count': count,
        'user_id': user_id,
        'peer_id': user_id,
        'rev': 1
    }
    messages = get(domain, "messages.getHistory", params)
    return json.loads(messages.text)['response']['items']


def get_all_history(user_id):
    msg = list()
    offset = 0
    while True:
        messages = messages_get_history(user_id, offset, 200)
        msg += messages
        if len(messages) != 200:
            break
        offset += 200
        time.sleep(0.3)
    return msg


def count_dates_from_messages(messages):
    d = {}
    for elem in messages:
        date = datetime.date.fromtimestamp(elem['date']).strftime("%Y-%m-%d")
        if date not in d:
            d[date] = 0
        d[date] += 1
    dd = list()
    for key in d:
        dd.append([key, d[key]])
    dd.sort()
    keys = [elem[0] for elem in dd]
    values = [elem[1] for elem in dd]
    return (keys, values)


def display_messages(dates, counts):
    py.iplot([go.Scatter(x=dates, y=counts)])


def count_length_messages(msg):
    cnt = 0
    for elem in msg:
        if 'body' in elem:
            cnt += len(elem['body'])
    return cnt


def count_send_messages(msg):
    cnt = 0
    for elem in msg:
        if 'out' in elem and elem['out'] == 1:
            cnt += 1
    return cnt    


def get_ids(people):
    return [[int(elem['id']), elem['last_name']] for elem in people]


def get_network(my_id, ids):
    friends_id = dict()
    vertex = list()
    for id1, name1 in ids:
        if id1 not in friends_id:
            friends_id[id1] = [len(friends_id), name1]
            vertex.append(name1)

    edges = set()
    for id1, name1 in ids:
        print(name1)
        fr = get_friends(id1)
        if fr == None:
            continue        
        fr_ids = get_ids(fr)
        for id2, name2 in fr_ids:
            if id2 == my_id or id2 not in friends_id:
                continue
            edges.add((min(friends_id[id1][0], friends_id[id2][0]),
                        max(friends_id[id1][0], friends_id[id2][0])))
    g = igraph.iGraph(vertex, list(edges))
    #g.vertex[0].color_text = 'red'
    l = igraph.iLayout()
    l.vizualizate(g)


access = {
    'token': '123'
    }


if __name__ == "__main__":
    my_id = 123
    fr = get_friends(my_id)
    ids = get_ids(fr)
    get_network(my_id, ids)