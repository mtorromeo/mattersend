#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import argparse
import json
import csv
import mimetypes

from io import StringIO

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

name = 'mattersend'
version = '2.0'
url = 'https://github.com/mtorromeo/mattersend'
description = "Library and CLI utility to send messages to mattermost's incoming webhooks"

syntaxes = ['diff', 'apache', 'makefile', 'http', 'json', 'markdown',
            'javascript', 'css', 'nginx', 'objectivec', 'python', 'xml',
            'perl', 'bash', 'php', 'coffeescript', 'cs', 'cpp', 'sql', 'go',
            'ruby', 'java', 'ini', 'latex', 'plain', 'auto']

mime_to_syntax = {
    'text/x-diff': 'diff',
    'application/json': 'json',
    'application/x-javascript': 'javascript',
    'text/x-python': 'python',
    'application/xml': 'xml',
    'text/x-perl': 'perl',
    'text/x-sh': 'bash',
    'text/x-csrc': 'cpp',
    'text/x-chdr': 'cpp',
    'text/x-c++src': 'cpp',
    'text/x-c++hdr': 'cpp',
    'text/x-c': 'cpp',
    'application/x-sql': 'sql',
    'application/x-ruby': 'ruby',
    'text/x-java-source': 'java',
    'application/x-latex': 'latex',
}

ext_to_syntax = {
    'Makefile': 'makefile',
    '.mk': 'makefile',
    '.htaccess': 'apache',
    '.json': 'json',
    '.js': 'javascript',
    '.css': 'css',
    '.m': 'objectivec',
    '.py': 'python',
    '.xml': 'xml',
    '.pl': 'perl',
    '.sh': 'bash',
    '.php': 'php',
    '.phtml': 'php',
    '.phps': 'php',
    '.php3': 'php',
    '.php4': 'php',
    '.php5': 'php',
    '.php7': 'php',
    '.coffee': 'coffeescript',
    '.cs': 'cs',
    '.c': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.cpp': 'cpp',
    '.h': 'cpp',
    '.hh': 'cpp',
    '.dic': 'cpp',
    '.sql': 'sql',
    '.go': 'go',
    '.rb': 'ruby',
    '.java': 'java',
    '.ini': 'ini',
    '.latex': 'latex',
}

emoji_to_code = {
    'smile': '1f604',
    'smiley': '1f603',
    'grinning': '1f600',
    'blush': '1f60a',
    'relaxed': '263a',
    'wink': '1f609',
    'heart_eyes': '1f60d',
    'kissing_heart': '1f618',
    'kissing_closed_eyes': '1f61a',
    'kissing': '1f617',
    'kissing_smiling_eyes': '1f619',
    'stuck_out_tongue_winking_eye': '1f61c',
    'stuck_out_tongue_closed_eyes': '1f61d',
    'stuck_out_tongue': '1f61b',
    'flushed': '1f633',
    'grin': '1f601',
    'pensive': '1f614',
    'relieved': '1f60c',
    'unamused': '1f612',
    'disappointed': '1f61e',
    'persevere': '1f623',
    'cry': '1f622',
    'joy': '1f602',
    'sob': '1f62d',
    'sleepy': '1f62a',
    'disappointed_relieved': '1f625',
    'cold_sweat': '1f630',
    'sweat_smile': '1f605',
    'sweat': '1f613',
    'weary': '1f629',
    'tired_face': '1f62b',
    'fearful': '1f628',
    'scream': '1f631',
    'angry': '1f620',
    'rage': '1f621',
    'pout': '1f621',
    'triumph': '1f624',
    'confounded': '1f616',
    'laughing': '1f606',
    'satisfied': '1f606',
    'yum': '1f60b',
    'mask': '1f637',
    'sunglasses': '1f60e',
    'sleeping': '1f634',
    'dizzy_face': '1f635',
    'astonished': '1f632',
    'worried': '1f61f',
    'frowning': '1f626',
    'anguished': '1f627',
    'smiling_imp': '1f608',
    'imp': '1f47f',
    'open_mouth': '1f62e',
    'grimacing': '1f62c',
    'neutral_face': '1f610',
    'confused': '1f615',
    'hushed': '1f62f',
    'no_mouth': '1f636',
    'innocent': '1f607',
    'smirk': '1f60f',
    'expressionless': '1f611',
    'man_with_gua_pi_mao': '1f472',
    'man_with_turban': '1f473',
    'cop': '1f46e',
    'construction_worker': '1f477',
    'guardsman': '1f482',
    'baby': '1f476',
    'boy': '1f466',
    'girl': '1f467',
    'man': '1f468',
    'woman': '1f469',
    'older_man': '1f474',
    'older_woman': '1f475',
    'person_with_blond_hair': '1f471',
    'angel': '1f47c',
    'princess': '1f478',
    'smiley_cat': '1f63a',
    'smile_cat': '1f638',
    'heart_eyes_cat': '1f63b',
    'kissing_cat': '1f63d',
    'smirk_cat': '1f63c',
    'scream_cat': '1f640',
    'crying_cat_face': '1f63f',
    'joy_cat': '1f639',
    'pouting_cat': '1f63e',
    'japanese_ogre': '1f479',
    'japanese_goblin': '1f47a',
    'see_no_evil': '1f648',
    'hear_no_evil': '1f649',
    'speak_no_evil': '1f64a',
    'skull': '1f480',
    'alien': '1f47d',
    'hankey': '1f4a9',
    'poop': '1f4a9',
    'shit': '1f4a9',
    'fire': '1f525',
    'sparkles': '2728',
    'star2': '1f31f',
    'dizzy': '1f4ab',
    'boom': '1f4a5',
    'collision': '1f4a5',
    'anger': '1f4a2',
    'sweat_drops': '1f4a6',
    'droplet': '1f4a7',
    'zzz': '1f4a4',
    'dash': '1f4a8',
    'ear': '1f442',
    'eyes': '1f440',
    'nose': '1f443',
    'tongue': '1f445',
    'lips': '1f444',
    '+1': '1f44d',
    'thumbsup': '1f44d',
    '-1': '1f44e',
    'thumbsdown': '1f44e',
    'ok_hand': '1f44c',
    'facepunch': '1f44a',
    'punch': '1f44a',
    'fist': '270a',
    'v': '270c',
    'wave': '1f44b',
    'hand': '270b',
    'raised_hand': '270b',
    'open_hands': '1f450',
    'point_up_2': '1f446',
    'point_down': '1f447',
    'point_right': '1f449',
    'point_left': '1f448',
    'raised_hands': '1f64c',
    'pray': '1f64f',
    'point_up': '261d',
    'clap': '1f44f',
    'muscle': '1f4aa',
    'walking': '1f6b6',
    'runner': '1f3c3',
    'running': '1f3c3',
    'dancer': '1f483',
    'couple': '1f46b',
    'family': '1f46a',
    'two_men_holding_hands': '1f46c',
    'two_women_holding_hands': '1f46d',
    'couplekiss': '1f48f',
    'couple_with_heart': '1f491',
    'dancers': '1f46f',
    'ok_woman': '1f646',
    'no_good': '1f645',
    'ng_woman': '1f645',
    'information_desk_person': '1f481',
    'raising_hand': '1f64b',
    'massage': '1f486',
    'haircut': '1f487',
    'nail_care': '1f485',
    'bride_with_veil': '1f470',
    'person_with_pouting_face': '1f64e',
    'person_frowning': '1f64d',
    'bow': '1f647',
    'tophat': '1f3a9',
    'crown': '1f451',
    'womans_hat': '1f452',
    'athletic_shoe': '1f45f',
    'mans_shoe': '1f45e',
    'shoe': '1f45e',
    'sandal': '1f461',
    'high_heel': '1f460',
    'boot': '1f462',
    'shirt': '1f455',
    'tshirt': '1f455',
    'necktie': '1f454',
    'womans_clothes': '1f45a',
    'dress': '1f457',
    'running_shirt_with_sash': '1f3bd',
    'jeans': '1f456',
    'kimono': '1f458',
    'bikini': '1f459',
    'briefcase': '1f4bc',
    'handbag': '1f45c',
    'pouch': '1f45d',
    'purse': '1f45b',
    'eyeglasses': '1f453',
    'ribbon': '1f380',
    'closed_umbrella': '1f302',
    'lipstick': '1f484',
    'yellow_heart': '1f49b',
    'blue_heart': '1f499',
    'purple_heart': '1f49c',
    'green_heart': '1f49a',
    'heart': '2764',
    'broken_heart': '1f494',
    'heartpulse': '1f497',
    'heartbeat': '1f493',
    'two_hearts': '1f495',
    'sparkling_heart': '1f496',
    'revolving_hearts': '1f49e',
    'cupid': '1f498',
    'love_letter': '1f48c',
    'kiss': '1f48b',
    'ring': '1f48d',
    'gem': '1f48e',
    'bust_in_silhouette': '1f464',
    'busts_in_silhouette': '1f465',
    'speech_balloon': '1f4ac',
    'footprints': '1f463',
    'thought_balloon': '1f4ad',
    'dog': '1f436',
    'wolf': '1f43a',
    'cat': '1f431',
    'mouse': '1f42d',
    'hamster': '1f439',
    'rabbit': '1f430',
    'frog': '1f438',
    'tiger': '1f42f',
    'koala': '1f428',
    'bear': '1f43b',
    'pig': '1f437',
    'pig_nose': '1f43d',
    'cow': '1f42e',
    'boar': '1f417',
    'monkey_face': '1f435',
    'monkey': '1f412',
    'horse': '1f434',
    'sheep': '1f411',
    'elephant': '1f418',
    'panda_face': '1f43c',
    'penguin': '1f427',
    'bird': '1f426',
    'baby_chick': '1f424',
    'hatched_chick': '1f425',
    'hatching_chick': '1f423',
    'chicken': '1f414',
    'snake': '1f40d',
    'turtle': '1f422',
    'bug': '1f41b',
    'bee': '1f41d',
    'honeybee': '1f41d',
    'ant': '1f41c',
    'beetle': '1f41e',
    'snail': '1f40c',
    'octopus': '1f419',
    'shell': '1f41a',
    'tropical_fish': '1f420',
    'fish': '1f41f',
    'dolphin': '1f42c',
    'flipper': '1f42c',
    'whale': '1f433',
    'whale2': '1f40b',
    'cow2': '1f404',
    'ram': '1f40f',
    'rat': '1f400',
    'water_buffalo': '1f403',
    'tiger2': '1f405',
    'rabbit2': '1f407',
    'dragon': '1f409',
    'racehorse': '1f40e',
    'goat': '1f410',
    'rooster': '1f413',
    'dog2': '1f415',
    'pig2': '1f416',
    'mouse2': '1f401',
    'ox': '1f402',
    'dragon_face': '1f432',
    'blowfish': '1f421',
    'crocodile': '1f40a',
    'camel': '1f42b',
    'dromedary_camel': '1f42a',
    'leopard': '1f406',
    'cat2': '1f408',
    'poodle': '1f429',
    'feet': '1f43e',
    'paw_prints': '1f43e',
    'bouquet': '1f490',
    'cherry_blossom': '1f338',
    'tulip': '1f337',
    'four_leaf_clover': '1f340',
    'rose': '1f339',
    'sunflower': '1f33b',
    'hibiscus': '1f33a',
    'maple_leaf': '1f341',
    'leaves': '1f343',
    'fallen_leaf': '1f342',
    'herb': '1f33f',
    'ear_of_rice': '1f33e',
    'mushroom': '1f344',
    'cactus': '1f335',
    'palm_tree': '1f334',
    'evergreen_tree': '1f332',
    'deciduous_tree': '1f333',
    'chestnut': '1f330',
    'seedling': '1f331',
    'blossom': '1f33c',
    'globe_with_meridians': '1f310',
    'sun_with_face': '1f31e',
    'full_moon_with_face': '1f31d',
    'new_moon_with_face': '1f31a',
    'new_moon': '1f311',
    'waxing_crescent_moon': '1f312',
    'first_quarter_moon': '1f313',
    'moon': '1f314',
    'waxing_gibbous_moon': '1f314',
    'full_moon': '1f315',
    'waning_gibbous_moon': '1f316',
    'last_quarter_moon': '1f317',
    'waning_crescent_moon': '1f318',
    'last_quarter_moon_with_face': '1f31c',
    'first_quarter_moon_with_face': '1f31b',
    'crescent_moon': '1f319',
    'earth_africa': '1f30d',
    'earth_americas': '1f30e',
    'earth_asia': '1f30f',
    'volcano': '1f30b',
    'milky_way': '1f30c',
    'stars': '1f320',
    'star': '2b50',
    'sunny': '2600',
    'partly_sunny': '26c5',
    'cloud': '2601',
    'zap': '26a1',
    'umbrella': '2614',
    'snowflake': '2744',
    'snowman': '26c4',
    'cyclone': '1f300',
    'foggy': '1f301',
    'rainbow': '1f308',
    'ocean': '1f30a',
    'bamboo': '1f38d',
    'gift_heart': '1f49d',
    'dolls': '1f38e',
    'school_satchel': '1f392',
    'mortar_board': '1f393',
    'flags': '1f38f',
    'fireworks': '1f386',
    'sparkler': '1f387',
    'wind_chime': '1f390',
    'rice_scene': '1f391',
    'jack_o_lantern': '1f383',
    'ghost': '1f47b',
    'santa': '1f385',
    'christmas_tree': '1f384',
    'gift': '1f381',
    'tanabata_tree': '1f38b',
    'tada': '1f389',
    'confetti_ball': '1f38a',
    'balloon': '1f388',
    'crossed_flags': '1f38c',
    'crystal_ball': '1f52e',
    'movie_camera': '1f3a5',
    'camera': '1f4f7',
    'video_camera': '1f4f9',
    'vhs': '1f4fc',
    'cd': '1f4bf',
    'dvd': '1f4c0',
    'minidisc': '1f4bd',
    'floppy_disk': '1f4be',
    'computer': '1f4bb',
    'iphone': '1f4f1',
    'phone': '260e',
    'telephone': '260e',
    'telephone_receiver': '1f4de',
    'pager': '1f4df',
    'fax': '1f4e0',
    'satellite': '1f4e1',
    'tv': '1f4fa',
    'radio': '1f4fb',
    'loud_sound': '1f50a',
    'sound': '1f509',
    'speaker': '1f508',
    'mute': '1f507',
    'bell': '1f514',
    'no_bell': '1f515',
    'loudspeaker': '1f4e2',
    'mega': '1f4e3',
    'hourglass_flowing_sand': '23f3',
    'hourglass': '231b',
    'alarm_clock': '23f0',
    'watch': '231a',
    'unlock': '1f513',
    'lock': '1f512',
    'lock_with_ink_pen': '1f50f',
    'closed_lock_with_key': '1f510',
    'key': '1f511',
    'mag_right': '1f50e',
    'bulb': '1f4a1',
    'flashlight': '1f526',
    'high_brightness': '1f506',
    'low_brightness': '1f505',
    'electric_plug': '1f50c',
    'battery': '1f50b',
    'mag': '1f50d',
    'bathtub': '1f6c1',
    'bath': '1f6c0',
    'shower': '1f6bf',
    'toilet': '1f6bd',
    'wrench': '1f527',
    'nut_and_bolt': '1f529',
    'hammer': '1f528',
    'door': '1f6aa',
    'smoking': '1f6ac',
    'bomb': '1f4a3',
    'gun': '1f52b',
    'hocho': '1f52a',
    'knife': '1f52a',
    'pill': '1f48a',
    'syringe': '1f489',
    'moneybag': '1f4b0',
    'yen': '1f4b4',
    'dollar': '1f4b5',
    'pound': '1f4b7',
    'euro': '1f4b6',
    'credit_card': '1f4b3',
    'money_with_wings': '1f4b8',
    'calling': '1f4f2',
    'e-mail': '1f4e7',
    'inbox_tray': '1f4e5',
    'outbox_tray': '1f4e4',
    'email': '2709',
    'envelope': '2709',
    'envelope_with_arrow': '1f4e9',
    'incoming_envelope': '1f4e8',
    'postal_horn': '1f4ef',
    'mailbox': '1f4eb',
    'mailbox_closed': '1f4ea',
    'mailbox_with_mail': '1f4ec',
    'mailbox_with_no_mail': '1f4ed',
    'postbox': '1f4ee',
    'package': '1f4e6',
    'memo': '1f4dd',
    'pencil': '1f4dd',
    'page_facing_up': '1f4c4',
    'page_with_curl': '1f4c3',
    'bookmark_tabs': '1f4d1',
    'bar_chart': '1f4ca',
    'chart_with_upwards_trend': '1f4c8',
    'chart_with_downwards_trend': '1f4c9',
    'scroll': '1f4dc',
    'clipboard': '1f4cb',
    'date': '1f4c5',
    'calendar': '1f4c6',
    'card_index': '1f4c7',
    'file_folder': '1f4c1',
    'open_file_folder': '1f4c2',
    'scissors': '2702',
    'pushpin': '1f4cc',
    'paperclip': '1f4ce',
    'black_nib': '2712',
    'pencil2': '270f',
    'straight_ruler': '1f4cf',
    'triangular_ruler': '1f4d0',
    'closed_book': '1f4d5',
    'green_book': '1f4d7',
    'blue_book': '1f4d8',
    'orange_book': '1f4d9',
    'notebook': '1f4d3',
    'notebook_with_decorative_cover': '1f4d4',
    'ledger': '1f4d2',
    'books': '1f4da',
    'book': '1f4d6',
    'open_book': '1f4d6',
    'bookmark': '1f516',
    'name_badge': '1f4db',
    'microscope': '1f52c',
    'telescope': '1f52d',
    'newspaper': '1f4f0',
    'art': '1f3a8',
    'clapper': '1f3ac',
    'microphone': '1f3a4',
    'headphones': '1f3a7',
    'musical_score': '1f3bc',
    'musical_note': '1f3b5',
    'notes': '1f3b6',
    'musical_keyboard': '1f3b9',
    'violin': '1f3bb',
    'trumpet': '1f3ba',
    'saxophone': '1f3b7',
    'guitar': '1f3b8',
    'space_invader': '1f47e',
    'video_game': '1f3ae',
    'black_joker': '1f0cf',
    'flower_playing_cards': '1f3b4',
    'mahjong': '1f004',
    'game_die': '1f3b2',
    'dart': '1f3af',
    'football': '1f3c8',
    'basketball': '1f3c0',
    'soccer': '26bd',
    'baseball': '26be',
    'tennis': '1f3be',
    '8ball': '1f3b1',
    'rugby_football': '1f3c9',
    'bowling': '1f3b3',
    'golf': '26f3',
    'mountain_bicyclist': '1f6b5',
    'bicyclist': '1f6b4',
    'checkered_flag': '1f3c1',
    'horse_racing': '1f3c7',
    'trophy': '1f3c6',
    'ski': '1f3bf',
    'snowboarder': '1f3c2',
    'swimmer': '1f3ca',
    'surfer': '1f3c4',
    'fishing_pole_and_fish': '1f3a3',
    'coffee': '2615',
    'tea': '1f375',
    'sake': '1f376',
    'baby_bottle': '1f37c',
    'beer': '1f37a',
    'beers': '1f37b',
    'cocktail': '1f378',
    'tropical_drink': '1f379',
    'wine_glass': '1f377',
    'fork_and_knife': '1f374',
    'pizza': '1f355',
    'hamburger': '1f354',
    'fries': '1f35f',
    'poultry_leg': '1f357',
    'meat_on_bone': '1f356',
    'spaghetti': '1f35d',
    'curry': '1f35b',
    'fried_shrimp': '1f364',
    'bento': '1f371',
    'sushi': '1f363',
    'fish_cake': '1f365',
    'rice_ball': '1f359',
    'rice_cracker': '1f358',
    'rice': '1f35a',
    'ramen': '1f35c',
    'stew': '1f372',
    'oden': '1f362',
    'dango': '1f361',
    'egg': '1f373',
    'bread': '1f35e',
    'doughnut': '1f369',
    'custard': '1f36e',
    'icecream': '1f366',
    'ice_cream': '1f368',
    'shaved_ice': '1f367',
    'birthday': '1f382',
    'cake': '1f370',
    'cookie': '1f36a',
    'chocolate_bar': '1f36b',
    'candy': '1f36c',
    'lollipop': '1f36d',
    'honey_pot': '1f36f',
    'apple': '1f34e',
    'green_apple': '1f34f',
    'tangerine': '1f34a',
    'orange': '1f34a',
    'mandarin': '1f34a',
    'lemon': '1f34b',
    'cherries': '1f352',
    'grapes': '1f347',
    'watermelon': '1f349',
    'strawberry': '1f353',
    'peach': '1f351',
    'melon': '1f348',
    'banana': '1f34c',
    'pear': '1f350',
    'pineapple': '1f34d',
    'sweet_potato': '1f360',
    'eggplant': '1f346',
    'tomato': '1f345',
    'corn': '1f33d',
    'house': '1f3e0',
    'house_with_garden': '1f3e1',
    'school': '1f3eb',
    'office': '1f3e2',
    'post_office': '1f3e3',
    'hospital': '1f3e5',
    'bank': '1f3e6',
    'convenience_store': '1f3ea',
    'love_hotel': '1f3e9',
    'hotel': '1f3e8',
    'wedding': '1f492',
    'church': '26ea',
    'department_store': '1f3ec',
    'european_post_office': '1f3e4',
    'city_sunrise': '1f307',
    'city_sunset': '1f306',
    'japanese_castle': '1f3ef',
    'european_castle': '1f3f0',
    'tent': '26fa',
    'factory': '1f3ed',
    'tokyo_tower': '1f5fc',
    'japan': '1f5fe',
    'mount_fuji': '1f5fb',
    'sunrise_over_mountains': '1f304',
    'sunrise': '1f305',
    'night_with_stars': '1f303',
    'statue_of_liberty': '1f5fd',
    'bridge_at_night': '1f309',
    'carousel_horse': '1f3a0',
    'ferris_wheel': '1f3a1',
    'fountain': '26f2',
    'roller_coaster': '1f3a2',
    'ship': '1f6a2',
    'boat': '26f5',
    'sailboat': '26f5',
    'speedboat': '1f6a4',
    'rowboat': '1f6a3',
    'anchor': '2693',
    'rocket': '1f680',
    'airplane': '2708',
    'seat': '1f4ba',
    'helicopter': '1f681',
    'steam_locomotive': '1f682',
    'tram': '1f68a',
    'station': '1f689',
    'mountain_railway': '1f69e',
    'train2': '1f686',
    'bullettrain_side': '1f684',
    'bullettrain_front': '1f685',
    'light_rail': '1f688',
    'metro': '1f687',
    'monorail': '1f69d',
    'train': '1f68b',
    'railway_car': '1f683',
    'trolleybus': '1f68e',
    'bus': '1f68c',
    'oncoming_bus': '1f68d',
    'blue_car': '1f699',
    'oncoming_automobile': '1f698',
    'car': '1f697',
    'red_car': '1f697',
    'taxi': '1f695',
    'oncoming_taxi': '1f696',
    'articulated_lorry': '1f69b',
    'truck': '1f69a',
    'rotating_light': '1f6a8',
    'police_car': '1f693',
    'oncoming_police_car': '1f694',
    'fire_engine': '1f692',
    'ambulance': '1f691',
    'minibus': '1f690',
    'bike': '1f6b2',
    'aerial_tramway': '1f6a1',
    'suspension_railway': '1f69f',
    'mountain_cableway': '1f6a0',
    'tractor': '1f69c',
    'barber': '1f488',
    'busstop': '1f68f',
    'ticket': '1f3ab',
    'vertical_traffic_light': '1f6a6',
    'traffic_light': '1f6a5',
    'warning': '26a0',
    'construction': '1f6a7',
    'beginner': '1f530',
    'fuelpump': '26fd',
    'izakaya_lantern': '1f3ee',
    'lantern': '1f3ee',
    'slot_machine': '1f3b0',
    'hotsprings': '2668',
    'moyai': '1f5ff',
    'circus_tent': '1f3aa',
    'performing_arts': '1f3ad',
    'round_pushpin': '1f4cd',
    'triangular_flag_on_post': '1f6a9',
    'jp': '1f1ef-1f1f5',
    'kr': '1f1f0-1f1f7',
    'de': '1f1e9-1f1ea',
    'cn': '1f1e8-1f1f3',
    'us': '1f1fa-1f1f8',
    'fr': '1f1eb-1f1f7',
    'es': '1f1ea-1f1f8',
    'it': '1f1ee-1f1f9',
    'ru': '1f1f7-1f1fa',
    'gb': '1f1ec-1f1e7',
    'uk': '1f1ec-1f1e7',
    'one': '0031-20e3',
    'two': '0032-20e3',
    'three': '0033-20e3',
    'four': '0034-20e3',
    'five': '0035-20e3',
    'six': '0036-20e3',
    'seven': '0037-20e3',
    'eight': '0038-20e3',
    'nine': '0039-20e3',
    'zero': '0030-20e3',
    'keycap_ten': '1f51f',
    '1234': '1f522',
    'hash': '0023-20e3',
    'symbols': '1f523',
    'arrow_up': '2b06',
    'arrow_down': '2b07',
    'arrow_left': '2b05',
    'arrow_right': '27a1',
    'capital_abcd': '1f520',
    'abcd': '1f521',
    'abc': '1f524',
    'arrow_upper_right': '2197',
    'arrow_upper_left': '2196',
    'arrow_lower_right': '2198',
    'arrow_lower_left': '2199',
    'left_right_arrow': '2194',
    'arrow_up_down': '2195',
    'arrows_counterclockwise': '1f504',
    'arrow_backward': '25c0',
    'arrow_forward': '25b6',
    'arrow_up_small': '1f53c',
    'arrow_down_small': '1f53d',
    'leftwards_arrow_with_hook': '21a9',
    'arrow_right_hook': '21aa',
    'information_source': '2139',
    'rewind': '23ea',
    'fast_forward': '23e9',
    'arrow_double_up': '23eb',
    'arrow_double_down': '23ec',
    'arrow_heading_down': '2935',
    'arrow_heading_up': '2934',
    'ok': '1f197',
    'twisted_rightwards_arrows': '1f500',
    'repeat': '1f501',
    'repeat_one': '1f502',
    'new': '1f195',
    'up': '1f199',
    'cool': '1f192',
    'free': '1f193',
    'ng': '1f196',
    'signal_strength': '1f4f6',
    'cinema': '1f3a6',
    'koko': '1f201',
    'u6307': '1f22f',
    'u7a7a': '1f233',
    'u6e80': '1f235',
    'u5408': '1f234',
    'u7981': '1f232',
    'ideograph_advantage': '1f250',
    'u5272': '1f239',
    'u55b6': '1f23a',
    'u6709': '1f236',
    'u7121': '1f21a',
    'restroom': '1f6bb',
    'mens': '1f6b9',
    'womens': '1f6ba',
    'baby_symbol': '1f6bc',
    'wc': '1f6be',
    'potable_water': '1f6b0',
    'put_litter_in_its_place': '1f6ae',
    'parking': '1f17f',
    'wheelchair': '267f',
    'no_smoking': '1f6ad',
    'u6708': '1f237',
    'u7533': '1f238',
    'sa': '1f202',
    'm': '24c2',
    'passport_control': '1f6c2',
    'baggage_claim': '1f6c4',
    'left_luggage': '1f6c5',
    'customs': '1f6c3',
    'accept': '1f251',
    'secret': '3299',
    'congratulations': '3297',
    'cl': '1f191',
    'sos': '1f198',
    'id': '1f194',
    'no_entry_sign': '1f6ab',
    'underage': '1f51e',
    'no_mobile_phones': '1f4f5',
    'do_not_litter': '1f6af',
    'non-potable_water': '1f6b1',
    'no_bicycles': '1f6b3',
    'no_pedestrians': '1f6b7',
    'children_crossing': '1f6b8',
    'no_entry': '26d4',
    'eight_spoked_asterisk': '2733',
    'sparkle': '2747',
    'negative_squared_cross_mark': '274e',
    'white_check_mark': '2705',
    'eight_pointed_black_star': '2734',
    'heart_decoration': '1f49f',
    'vs': '1f19a',
    'vibration_mode': '1f4f3',
    'mobile_phone_off': '1f4f4',
    'a': '1f170',
    'b': '1f171',
    'ab': '1f18e',
    'o2': '1f17e',
    'diamond_shape_with_a_dot_inside': '1f4a0',
    'loop': '27bf',
    'recycle': '267b',
    'aries': '2648',
    'taurus': '2649',
    'gemini': '264a',
    'cancer': '264b',
    'leo': '264c',
    'virgo': '264d',
    'libra': '264e',
    'scorpius': '264f',
    'sagittarius': '2650',
    'capricorn': '2651',
    'aquarius': '2652',
    'pisces': '2653',
    'ophiuchus': '26ce',
    'six_pointed_star': '1f52f',
    'atm': '1f3e7',
    'chart': '1f4b9',
    'heavy_dollar_sign': '1f4b2',
    'currency_exchange': '1f4b1',
    'copyright': '00a9',
    'registered': '00ae',
    'tm': '2122',
    'x': '274c',
    'bangbang': '203c',
    'interrobang': '2049',
    'exclamation': '2757',
    'heavy_exclamation_mark': '2757',
    'question': '2753',
    'grey_exclamation': '2755',
    'grey_question': '2754',
    'o': '2b55',
    'top': '1f51d',
    'end': '1f51a',
    'back': '1f519',
    'on': '1f51b',
    'soon': '1f51c',
    'arrows_clockwise': '1f503',
    'clock12': '1f55b',
    'clock1230': '1f567',
    'clock1': '1f550',
    'clock130': '1f55c',
    'clock2': '1f551',
    'clock230': '1f55d',
    'clock3': '1f552',
    'clock330': '1f55e',
    'clock4': '1f553',
    'clock430': '1f55f',
    'clock5': '1f554',
    'clock530': '1f560',
    'clock6': '1f555',
    'clock7': '1f556',
    'clock8': '1f557',
    'clock9': '1f558',
    'clock10': '1f559',
    'clock11': '1f55a',
    'clock630': '1f561',
    'clock730': '1f562',
    'clock830': '1f563',
    'clock930': '1f564',
    'clock1030': '1f565',
    'clock1130': '1f566',
    'heavy_multiplication_x': '2716',
    'heavy_plus_sign': '2795',
    'heavy_minus_sign': '2796',
    'heavy_division_sign': '2797',
    'spades': '2660',
    'hearts': '2665',
    'clubs': '2663',
    'diamonds': '2666',
    'white_flower': '1f4ae',
    '100': '1f4af',
    'heavy_check_mark': '2714',
    'ballot_box_with_check': '2611',
    'radio_button': '1f518',
    'link': '1f517',
    'curly_loop': '27b0',
    'wavy_dash': '3030',
    'part_alternation_mark': '303d',
    'trident': '1f531',
    'black_medium_square': '25fc',
    'white_medium_square': '25fb',
    'black_medium_small_square': '25fe',
    'white_medium_small_square': '25fd',
    'black_small_square': '25aa',
    'white_small_square': '25ab',
    'small_red_triangle': '1f53a',
    'black_square_button': '1f532',
    'white_square_button': '1f533',
    'black_circle': '26ab',
    'white_circle': '26aa',
    'red_circle': '1f534',
    'large_blue_circle': '1f535',
    'small_red_triangle_down': '1f53b',
    'white_large_square': '2b1c',
    'black_large_square': '2b1b',
    'large_orange_diamond': '1f536',
    'large_blue_diamond': '1f537',
    'small_orange_diamond': '1f538',
    'small_blue_diamond': '1f539',
    'ca': '1f1e8-1f1e6',
    'eh': '1f1e8-1f1e6',
    'pk': '1f1f5-1f1f0',
    'za': '1f1ff-1f1e6',
    'slightly_smiling_face': '1f642',
    'slightly_frowning_face': '1f641',
    'upside_down_face': '1f643',
    'mm': 'mm',
    'mattermost': 'mattermost',
    'basecamp': 'basecamp',
    'basecampy': 'basecampy',
    'bowtie': 'bowtie',
    'feelsgood': 'feelsgood',
    'finnadie': 'finnadie',
    'fu': 'fu',
    'goberserk': 'goberserk',
    'godmode': 'godmode',
    'hurtrealbad': 'hurtrealbad',
    'metal': 'metal',
    'neckbeard': 'neckbeard',
    'octocat': 'octocat',
    'rage1': 'rage1',
    'rage2': 'rage2',
    'rage3': 'rage3',
    'rage4': 'rage4',
    'shipit': 'shipit',
    'squirrel': 'squirrel',
    'suspect': 'suspect',
    'taco': 'taco',
    'trollface': 'trollface',
}


def detect_syntax(basename, mime):
    if mime in mime_to_syntax:
        return mime_to_syntax[mime]

    (_, ext) = os.path.splitext(basename)
    if not ext:
        ext = basename
    return ext_to_syntax[ext] if ext in ext_to_syntax else None


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def md_table(data):
    md = []
    for i, row in enumerate(data):
        if i == 1:
            md.append("| --- " * len(row) + "|")
        md.append("| {} |".format(" | ".join(
            [str(cell).replace("|", "❘").replace("\n", " ").replace("\r", " ") for cell in row]
        )))
    return "\n".join(md)


class Message:
    def __init__(self, channel=None, url=None, username=None, icon=None,
                 config_section='DEFAULT', config_name='mattersend',
                 config_file=None):
        # CONFIG file
        config = configparser.ConfigParser()

        if config_file:
            config.read(config_file)
        elif config_name:
            config.read(["/etc/{}.conf".format(config_name), os.path.expanduser("~/.{}.conf".format(config_name))])

        config = dict(config.items(config_section))

        # merge config file with cli arguments
        self.url = config.get('url') if url is None else url
        self.channel = config.get('channel') if channel is None else channel
        self.username = config.get('username') if username is None else username
        self.icon = config.get('icon') if icon is None else icon

        self.text = ''
        self.attachments = []

    def get_payload(self):
        payload = {}

        for opt in ('text', 'channel', 'username'):
            optvalue = getattr(self, opt)
            if optvalue is not None:
                payload[opt] = optvalue.strip()

        opt, optvalue = self.get_icon()
        if optvalue is not None:
            payload[opt] = optvalue

        if self.attachments:
            payload['attachments'] = [a.data() for a in self.attachments]

        return json.dumps(payload, sort_keys=True, indent=4)

    def get_icon(self):
        if self.icon is None:
            return None, None

        ioptvalue = self.icon.strip()
        ioptname = 'icon_url' if '://' in ioptvalue else 'icon_emoji'

        # workaround mattermost missing icon_emoji until implemented
        if ioptname == 'icon_emoji' and ioptvalue[0] == ':' and ioptvalue[-1] == ':':
            ioptvalue = emoji_to_code.get(ioptvalue[1:-1], False)
            if ioptvalue:
                baseurl = self.url.split('/hooks/', 1)
                if len(baseurl) == 2:
                    ioptname = 'icon_url'
                    ioptvalue = '{0}/static/emoji/{1}.png'.format(baseurl[0], ioptvalue)

        return ioptname, ioptvalue

    def append(self, text, separator=None):
        if self.text and separator is not None:
            self.text += separator
        self.text += text

    def attach_file(self, filename, text=None, tabular=False, syntax='auto', fileinfo=False):
        attachment = Attachment()

        if tabular:
            syntax = None

        (mime, _) = mimetypes.guess_type(filename)
        attachment.title = os.path.basename(filename)

        if text is None:
            with open(filename, 'rUb') as f:
                text = f.read().decode('utf-8')

        if tabular:
            csvfile = StringIO(text.strip())

            if tabular == 'sniff':
                dialect = csv.Sniffer().sniff(text)
            else:
                dialect = tabular

            text = md_table(csv.reader(csvfile, dialect))

        elif syntax == 'auto':
            syntax = detect_syntax(attachment.title, mime)

        if syntax is not None:
            text = md_code(text, syntax)

        attachment.text = text

        if fileinfo:
            statinfo = os.stat(filename)
            attachment.add_field('Size', sizeof_fmt(statinfo.st_size), True)
            attachment.add_field('Mime', mime, True)

        self.attachments.append(attachment)
        return attachment

    def send(self):
        if self.url is None:
            raise TypeError('Missing mattermost webhook URL')

        if self.channel is None:
            raise TypeError('Missing destination channel')

        import requests

        payload = self.get_payload()
        r = requests.post(self.url, data={'payload': payload})

        if r.status_code != 200:
            try:
                r = json.loads(r.text)
            except ValueError:
                r = {'message': r.text, 'status_code': r.status_code}
            raise RuntimeError("{} ({})".format(r['message'], r['status_code']))

        return r


class Attachment:
    def __init__(self, text=''):
        self.text = text
        self.color = None
        self.pretext = None
        self.fallback = None

        self.author_name = None
        self.author_link = None
        self.author_icon = None

        self.title = None
        self.title_link = None

        self.image_url = None
        self.thumb_url = None

        self.fields = []

    def set_author(self, name, link=None, icon=None):
        self.author_name = name
        self.author_link = link
        self.author_icon = icon

    def set_title(self, title, link=None):
        self.title = title
        self.title_link = link

    def add_field(self, title, value, short=None):
        field = {
            'title': str(title),
            'value': str(value),
        }
        if short is not None:
            field['short'] = bool(short)
        self.fields.append(field)

    def data(self):
        data = {k: v for (k, v) in self.__dict__.items() if v}
        if not self.fallback:
            data['fallback'] = self.text
        # 4000+ chars triggers error on mattermost, not sure where the limit is
        data['text'] = data['text'][:3500]
        data['fallback'] = data['fallback'][:3500]
        return data


def md_code(code, syntax='plain'):
    if syntax == 'plain':
        syntax = ''
    return "```{}\n{}```".format(syntax, code)


def main():
    try:
        import setproctitle
        setproctitle.setproctitle(name)
    except ImportError:
        pass

    dialects = csv.list_dialects()
    dialects.sort()
    dialects.insert(0, 'sniff')

    # CLI arguments
    parser = argparse.ArgumentParser(prog=name, description=description)

    parser.add_argument('-V', '--version',  action='version', version="%(prog)s " + version)
    parser.add_argument('-C', '--config',   help='Use a different configuration file')
    parser.add_argument('-s', '--section',  help='Configuration file section', default='DEFAULT')
    parser.add_argument('-c', '--channel',  help='Send to this channel or @username')
    parser.add_argument('-U', '--url',      help='Mattermost webhook URL')
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-i', '--icon',     help='Icon')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--tabular', metavar='DIALECT', const='sniff',
                       nargs='?', choices=dialects,
                       help='Parse input as CSV and format it as a table (DIALECT can be one of %(choices)s)')
    group.add_argument('-y', '--syntax', default='auto')

    parser.add_argument('-I', '--info', action='store_true',
                        help='Include file information in message')
    parser.add_argument('-n', '--dry-run', '--just-print', action='store_true',
                        help="Don't send, just print the payload")
    parser.add_argument('-f', '--file', default='-',
                        help="Read content from FILE. If - reads from standard input (DEFAULT: %(default)s)")

    args = parser.parse_args()

    if args.file == '-':
        message = sys.stdin.read()
        filename = None
    else:
        message = ''
        filename = args.file


    try:
        payload = send(args.channel, message, filename, args.url,
                       args.username, args.icon, args.syntax, args.tabular,
                       args.info, args.dry_run, args.section, name,
                       args.config)
    except (configparser.Error, TypeError, RuntimeError) as e:
        sys.exit(str(e))

    if args.dry_run:
        print(payload)


def send(channel, message='', filename=False, url=None, username=None,
         icon=None, syntax='auto', tabular=False, fileinfo=False,
         just_return=False, config_section='DEFAULT',
         config_name='mattersend', config_file=None):
    msg = Message(channel, url, username, icon, config_section,
                  config_name, config_file)

    if filename:
        if syntax == 'none':
            syntax = None
        msg.attach_file(filename, None, tabular, syntax, fileinfo)
    else:
        if tabular:
            syntax = None
            csvfile = StringIO(message.strip())

            if tabular == 'sniff':
                dialect = csv.Sniffer().sniff(message)
            else:
                dialect = tabular

            message = md_table(csv.reader(csvfile, dialect))

        elif syntax in ('auto', 'none'):
            syntax = None

        if syntax is not None:
            message = md_code(message, syntax)

    msg.text = message

    if just_return:
        payload = msg.get_payload()
        return "POST {}\n{}".format(msg.url, payload)

    msg.send()


if __name__ == '__main__':
    main()
