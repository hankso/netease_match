#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Thu Dec 28 23:40:42 2017

@author: hankso

Function Encrypt utils two times AES encryption on data and return the result, here is the process:
    1. First we need to import some modules:
        - random
        - binascii (built-in)
        - base64
        - Crypto (`pip install Crypto`)
    2. Then we generate secKey -- a string containing 16 random characters within [a-z][A-Z][0-9]
    3. Next in AES, text should be padded until len(text)%16 == 0
    4. After data been encrypted by AES with public key, convert it from binary to ascii and decode as utf-8 format
    5. Encrypt the result once more with private key(secKey generated before), convert.
    6. Finally return encrypted data and slightly modified private key.

p.s. even same input data may get different result, because when stringify dict-format data to string(by json.dumps(data)), items may take different order like this:
    '{"limit": 50, "offset": 0, "songid": 25729689}'
    '{"songid": 25729689, "limit": 50, "offset": 0}'
and that doesn't matter.
'''

import random, binascii, json
from base64 import b64encode as b64
from Crypto.Cipher import AES

biMod = 157794750267131502212476817800345498121872783333389747424011531025366277535262539913701806290766479189477533597854989606803194253978660329941980786072432806427833685472618792592200595694346872951301770580765135349259590167490536138082469680638514416594216629258349130257685001248172188325316586707301643237607L

def Encrypt(data, secKey=0):
    if not secKey:
        secKey = ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN'
                                        'OPQRSTUVWXYZ0123456789') for _ in xrange(16)])
    aes = lambda text, secKey, pad: b64(
            AES.new(secKey, 2, '0102030405060708').encrypt(text + chr(pad)*pad)
            ).decode('utf8')

    data = json.dumps(data)
    for key in ['0CoJUm6Qyw8W8jud', secKey]: # two times AES encrypt with different key
        data = aes(data, key, 16 - len(data)%16)
    biBase = int(binascii.hexlify(secKey[::-1]), 16)
    return {
                'params': data,
                'encSecKey': modpow(biBase, 65537, biMod).__format__('x').zfill(256)
    } # 'encSecKey': format( pow(biBase, 65537) % biMod, 'x' ).zfill(256)

def modpow(b, e, m):
    '''
    param:  b(base), e(exponent), m(mod)
    return: b**e %m

    This algorithm is must faster than python built-in pow(b, e) % m, especially when b & e are super huge numbers
    Example:
        In[2]: b = 123456789101112131415L
        In[3]: e = 50000
        In[4]: m = 15779475026713150221L
        In[5]: timeit (pow(b, e) % m)
        1 loop, best of 3: 305 ms per loop
        In[6]: timeit modpow(b, e, m)
        The slowest run took 16.19 times longer than the fastest. This could mean that an intermediate result is being cached.
        100000 loops, best of 3: 5.92 µs per loop
    '''
    result = 1
    while (e > 0):
        if e & 1:
            result = (result * b) % m
        e = e >> 1
        b = (b * b) % m
    return result
