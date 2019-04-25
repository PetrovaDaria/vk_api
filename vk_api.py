from urllib.request import urlopen
import json


#сопоставление user_id - user_information
cache = {}
statistics = {}
access_token = '12a26c4712a26c4712a26c47d712c01208112a212a26c47487bb5d41844afde0040cf9b'
v = '5.74'


def get_json(request):
    with urlopen(request) as url:
        j = json.loads(url.read())
    return j


def make_request(method, fields):
    return 'https://api.vk.com/method/{}?{}&v={}&access_token={}'.format(method, fields, v, access_token)


def get_user(id_or_name):
    user = get_json(make_request('users.get', 'user_ids={}'.format(id_or_name)))
    if id_or_name not in cache.keys():
        cache[id_or_name] = user
    user_id = get_user_id(user)
    if id_or_name != user_id:
        if user_id not in cache.keys():
            cache[user_id] = user
    return user


def get_user_information(user, field):
    return user['response'][0][field]


def get_user_id(user):
    return get_user_information(user, 'id')


def get_user_first_name(user):
    return get_user_information(user, 'first_name')


def get_user_last_name(user):
    return get_user_information(user, 'last_name')


def is_user_deactivated(user_id):
    if user_id in cache.keys():
        user = cache[user_id]
    else:
        user = get_user(user_id)
    return 'deactivated' in user['response'][0].keys()


def get_friends(user_id):
    return get_json(make_request('friends.get', 'user_id={}'.format(user_id)))


def get_friends_information(friends, field):
    return friends['response'][field]


def get_friends_count(friends):
    return get_friends_information(friends, 'count')


def get_friends_list(friends):
    if 'error' in friends.keys():
        if friends['error']['error_code'] == 15:
            return 'private'
    return get_friends_information(friends, 'items')


def get_common_friends(user_friends):
    i = 1
    for friend_id in user_friends:
        if friend_id in cache.keys():
            friend = cache[friend_id]
        else:
            friend = get_user(friend_id)
        print(str(i) + '. ' + make_user_information(friend))
        if not is_user_deactivated(friend_id):
            friend_friends = get_friends_list(get_friends(friend_id))
            if friend_friends == 'private':
                print('Профиль друга закрыт для данного токена, невозможно посчитать количество общих друзей')
                i += 1
                continue
            common_friends_ids = set(user_friends) & set(friend_friends)
            if len(common_friends_ids) == 0:
                print(' У вас нет общих друзей')
                statistics[make_user_information(friend)] = 0
            else:
                print('', len(common_friends_ids), get_right_spelling(len(common_friends_ids)))
                for id in common_friends_ids:
                    if id in cache.keys():
                        user = cache[id]
                    else:
                        user = get_user(id)
                    print('    ' + make_user_information(user))
                statistics[make_user_information(friend)] = len(common_friends_ids)
        else:
            print(' Ваш друг был удален из ВКонтакте')
        i += 1


def get_right_spelling(friends_count):
    mod100 = friends_count % 100
    if mod100 >= 11 and mod100 <= 19:
        return "общих друзей"
    mod10 = friends_count % 10
    if mod10 == 1:
        return "общего друга"
    else:
        return "общих друзей"


def make_user_information(user):
    first_name = get_user_first_name(user)
    last_name = get_user_last_name(user)
    return last_name + ' ' + first_name


def print_statistics():
    sorted_statistics = sorted(statistics.items(), key=lambda x: x[1], reverse=True)
    for item in sorted_statistics:
        print('Вы и ' + item[0] + ' имеете ' + str(item[1]) + ' ' + get_right_spelling(item[1]))


if __name__ == '__main__':
    user_name_or_id = input()
    user = get_user(user_name_or_id)
    id = get_user_id(user)
    friends = get_friends(id)
    friends_list = get_friends_list(friends)
    if friends_list == 'private':
        print('Ваш профиль является приватным для данного токена')
    else:
        get_common_friends(friends_list)
        print_statistics()

