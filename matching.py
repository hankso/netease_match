#!/usr/bin/env python
# coding:utf-8


import time, requests, json, numpy as np, pickle

HEADER = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com',
    'User-Agent':('Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.96 Safari/537.36')
}

EXAMPLE = {
    'encSecKey': ('764178bb85e6cf24902512bd2608b8a7b82d561644f8d0545a02df2408a'
                  'f49601807268ccf33ef8f64604fa09531b49433f3cbe025caf9a779c4c3'
                  '10349f24792a847762c1206181ec43ec590a80a41f29de2cce6bcd42b84'
                  'b04ab9279b05849741c3f45ce40bfe7230644462e438c7310cb0d29ca43'
                  'd9c8301b14c1c9567fba'),
    'params': ('3FSDDgSDqQYPYZB1EHFLjtRY8OvtsLMrn998ov/J6m3B0yKhqE9mFFGulOx1Gw'
               'dtubUFskrxIT+J1g7kE9VdxAz2Bmgl4Sauhpp/51M5BnJaLKe7eRNdUDjkDGXm'
               'vz6b5fnh3hYYDG9ViH6Vmz/22NKNb1XdPEkLRV/ou/Z5XFfslusJ55dSxRpuGJ'
               'SGgyfLucOtWXwmmcOHFa+UXq+vpQ==')
}

USER_DETAIL      = 'http://music.163.com/api/user/detail/{}' # need cookie
USERS_SIMI       = 'http://music.163.com/api/discovery/simiUser?songid={}' # need cookie
USER_FOLLOEWEDS  = 'http://music.163.com/api/user/getfolloweds/{}'
PLAYLISTS_SIMPLE = 'http://music.163.com/api/user/playlist?uid={}&offset={}&limit={}' # both get and post
PLAYLIST_DETAIL  = 'http://music.163.com/api/playlist/detail?id={}' # both get and post
SONG_DETAIL      = 'http://music.163.com/api/song/detail?ids=[{},]' # both get and post
SEARCH_UID       = 'http://music.163.com/api/search/get?s={}&type=1002&offset=0&limit=100' # only post
LOGIN_PHONE      = 'https://music.163.com/weapi/login/cellphone' # only post

current_min_max_playlist=[306324002, 306327619, 998602589]

# 为增大区分度,并且限定标签维数,某些标签被忽略
# TODO: 数据降维
TAGS = {
    # 语种tag
    u'华语':0, u'欧美':0, u'日语':0, u'韩语':0, u'粤语':0, u'小语种':0,

    # 风格tag
    u'摇滚':0, u'民谣':0, u'电子':0, u'爵士':0, u'古典':0, u'轻音乐':0,
    u'古风':0, u'说唱':0, u'R&B/Soul':0, u'New Age':0,
    #u'英伦':0, u'金属':0, u'民族':0, u'舞曲':0, u'朋克':0, u'蓝调':0,
    #u'雷鬼':0, u'另类/独立':0, u'拉丁':0, u'乡村':0, u'世界音乐':0, u'后摇':0,

    # 场景tag
    u'运动':0, u'旅行':0, u'夜晚':0, u'学习':0,
    #u'驾车':0, u'地铁':0, u'清晨':0, u'散步':0,
    #u'酒吧':0, u'工作':0, u'午休':0, u'下午茶':0,

    # 情感tag
    u'孤独':0, u'怀旧':0, u'清新':0, u'浪漫':0, u'伤感':0, u'治愈':0,
    u'兴奋':0, u'快乐':0, u'安静':0, u'思念':0, u'放松':0, u'感动':0,
    u'性感':0,

    # 主题tag
    u'ACG':0, u'吉他':0, u'钢琴':0, u'器乐':0,
    u'儿童':0, u'经典':0, u'翻唱':0, u'影视原声':0,
    #u'榜单':0, u'70后':0, u'80后':0, u'90后':0, u'00后':0,
    #u'网络歌曲':0, u'KTV':0, u'校园':0, u'游戏':0,
}

s = requests.session()
s.headers.update(HEADER)

class Info(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class User(Info):
    def __init__(self, msg, simplify = True):
        if not isinstance(msg, dict):
            raise TypeError('__init__() only accept dict but got %s'%type(msg))
        if msg.get('code', 200) != 200:
            raise RuntimeError('code: %d'%msg.get('code'))
        # Full-User with profile and bindings
        if msg.get('profile'):
            msg.update(msg.pop('profile'))

        if simplify:
            interesting_attr = ['nickname',     # TEXT
                                'userId',       # TEXT|INT
                                'city',         # INT
                                'gender',       # INT
                                'followed',     # INT
                                'level',        # INT
                                'createTime',   # TEXT
                                'description',  # TEXT
                                'avatarUrl',    # TEXT
                                'signature',    # TEXT
                                ]
            for _ in msg.keys():
                if _ not in interesting_attr: msg.pop(_)

        #==============================
        super(Info, self).__init__(msg)
        #==============================

        # string format time
        for _ in self.keys():
            if 'Time' in _ and isinstance(self[_], (int, float)):
                self[_+'_str'] = parse_time(self[_])

        _playlists = self._get_your_playlists(self.userId)
        self[u'tags'] = self._get_your_tags_from_playlists(_playlists)
        self[u'favorite_list_id'] = None
        for l in _playlists:
            if l.name.endswith(u'喜欢的音乐'):
                self.favorite_list_id = l.id

    def _get_your_tags_from_playlists(self, playlists):
        tags = []
        _TAG = TAGS.copy()
        for l in playlists:
            tags += l.tags * int( 1 + np.log10(l.playCount) if l.playCount else 0 )
        for tag in set(tags):
            if tag in _TAG:
                _TAG[tag] = tags.count(tag) / float(len(tags))
        return  _TAG

    def _get_your_playlists(self, userId):
        rst = get(PLAYLISTS_SIMPLE.format(userId, 0, 100))
        if rst.get('code', 200) != 200:
            print('Error when getting playlists of user {}: {} {}'.format(
                  userId, rst.get('msg',''), rst.get('message','')))
            return []
        else:
            return [Playlist(_) for _ in rst.get('playlist')]


class Playlist(Info):
    def __init__(self, msg, simplify = True):
        if not isinstance(msg, dict):
            raise TypeError('__init__() only accept dict but got %s'%type(msg))

        interesting_attr = ['tags',
                            'id',
                            # 'userId',
                            'name',
                            'description',
                            'playCount',
                            ]
        # interesting_attr += [_ for _ in msg if 'Time' in _ or 'Count' in _]
        if not simplify:
            interesting_attr += ['tracks']
            if not msg.has_key('tracks'):
                rst = get(PLAYLIST_DETAIL.format(msg.get('id')))
                if rst.get('code', 200) == 200: msg = rst.get('result')
                else: raise IOError('code: %d'%rst.get('code'))
        for _ in msg.keys():
            if _ not in interesting_attr: msg.pop(_)

        #==============================
        super(Info, self).__init__(msg)
        #==============================

        for _ in self.keys():
            if 'Time' in _ and isinstance(self[_], (int, float)):
                self[_+'_str'] = parse_time(self[_])

        if not simplify:
            self['trackIds'] = [_.get('id') for _ in self['tracks']]
            self.pop('tracks')

# class Song(Info):
#     def __init__(self, msg):
#         if msg.get('privilege'):
#             msg.update(msg.pop('privilege'))
#         super(Info, self).__init__(msg)
#
# class Event(Info):
#     def __init__(self, msg):
#         if isinstance(msg.get('json'), str):
#             msg['json'] = json.loads(msg['json'])
#         if msg.get('info'):
#             msg.update(msg.pop('info'))
#         super(Info, self).__init__(msg)
#
# class Record(Info):
#     def __init__(self, msg):
#         super(Info, self).__init__()

def tags_cos(user_XX, user_OO_list):
    '''
    Calculate cosine distance of two 1-D vestors,
    which means user similarity here.

    param:  target user_XX and user_OO_list of candidates
    return: list of similarity values
    '''
    if not isinstance(user_OO_list, list):
        user_OO_list = [user_OO_list,]
    cos = lambda u, v: np.dot(u, v) / ( np.linalg.norm(u)*np.linalg.norm(v) )
    return [cos(user_XX.tags.values(), i.tags.values()) for i in user_OO_list]

def parse_time(t = None, format = '%Y.%m.%d-%H:%M:%S'):
    '''
    convert a time in second into str format
    '''
    if not isinstance(t, (float, int)):
        try:
            t = abs(int(t))
        except:
            t = time.time()
    # python time.time is based on 's' and some other
    # (JS Date, etc.) are based on 'ms', so filter it.
    while t > time.time(): t /= 10
    return time.strftime(format, time.localtime(int(t)))

def login_phone(phone=None, password=None):
    if phone==password==None:
        data = EXAMPLE
    else:
        import hashlib
        from encrypt import Encrypt
        data = Encrypt({
            'phone': phone,
            'password': hashlib.md5(password).hexdigest(),
            'rememberLogin': 'true'
        })
    # after login, requests.session will hold the cookie from 'music.163.com'
    msg = s.post(LOGIN_PHONE, data).json()
    if msg.get('code') != 200:
    	raise RuntimeError(
		    'login error: {code} {msg} {message}'.format(
		        msg = msg.get('msg'),
		        code = msg.get('code'),
		        message = msg.get('message')
		    )
		)
    # save cookie into a file
    with open('login_cookies', 'w') as f:
        pickle.dump(s.cookies, f)

    if phone and password:
        return User(msg).userId
    else:
        return None

def check_cookie(session):
    '''
    Update cookies from stored in file login_cookies.
    If there doesn't exist cookie file then login and create it.
    '''
    def wrapper(func):
        if not session.cookies:
            try:
                with open('login_cookies', 'r') as f:
                    session.cookies = pickle.load(f)
                assert session.cookies
            except:
                login_phone()
        return lambda *args, **kwargs: func(*args, **kwargs)
    return wrapper

@check_cookie(s)
def get(url):
    try:
        return s.get(url).json()
    except:
        return {}

@check_cookie(s)
def post(url, data=None):
    try:
        if data:
            return s.post(url, data).json()
        else:
            return s.post(url).json()
    except BaseException, e:
        print('POST error: ' + e.message)
        return {}

def get_users_from_favorite_songs(playlist, num = 50, offset = 0, limit = 100):
    '''
    param:  favoritelist, num, offset, limit
    return: list of many many Users who liked or listent the same song with you.
    '''
    l = []
    maxnum = playlist.trackCount
    limit = limit if limit <= 100 else 100 # 100 is big enough
    # subscribers trackIds
    while 1:
        if offset >= maxnum: break
        if offset + limit > maxnum: limit = maxnum - offset
        for songId in playlist.trackIds[offset:offset+limit]:
            print('SongId: %d'%songId)
            msg = get( USERS_SIMI.format(songId) )
            if msg.get('code', 200) == 200 and msg.get('userprofiles', []).__len__():
                for _ in msg.get('userprofiles'):
                    uid = _.get('userId')
                    print('    find user with id: %d'%uid)
                    l.append( User( get(USER_DETAIL.format(uid)) ) )
                    if len(l) >= num: return l
        offset += limit
    return l

def get_users_followeds(userId):
    '''
    param:  userId
    return: list of users who followed you
    '''
    msg = get(USER_FOLLOEWEDS.format(userId))
    if msg.get('code', 200) != 200:
        return []
    return [User( get( USER_DETAIL.format(user.get('userId')) ) )
            for user in msg.get('followeds', [])]

def get_yourself(username=None, phone=None, password=None):
    assert username or (phone and password), 'please call with param'
    uid = None
    if username:
        msg = post(SEARCH_UID.format(username))
        if msg and msg.get('code') == 200:
            if msg.get('result').get('userprofileCount'):
                uid = msg.get('result').get('userprofiles')[0].get('userId')
            else: raise RuntimeError('Getting uid by username: no search result')
    rst = login_phone(phone, password)
    if rst:
        if uid != rst: uid = rst
    elif not uid: raise RuntimeError('Getting user_XX: no such user')
    print('find your uid: %d'%uid)
    return User(get(USER_DETAIL.format(uid)))

if __name__ == '__main__':

    username = '航概妹的新同桌'
    phone = None
    password = None

    user_XX = get_yourself(username, phone, password)
    user_OO_list = get_users_from_favorite_songs(user_XX.favoritelist, num = 10)
    '''
    here to find the best match boy|girl for the user
    '''
#            user_OO_list.sort(cmp=lambda user1,user2:user1.userId > user2.userId,
#                              key=lambda user: user.userId)
#    raise IOError('invaild username %s, cannot find this user'%username)
