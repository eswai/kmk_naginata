# 薙刀式 v15y 実装

import supervisor

from kmk.keys import KC
from kmk.keys import make_key
from kmk.handlers.sequences import send_string
from kmk.handlers.sequences import simple_key_sequence
from kmk.handlers.sequences import unicode_string_sequence

pressed_keys = set() # 同時に押しているキー
nginput = [] # 未変換のキー [[KC.NGM], [KC.NGJ, KC.NGW]] (なぎ)のように、同時押しの組み合わせを2次元配列へ格納
ng_layer = 0 # KC.NG*を定義しているレイヤーの番号
kblayers = None # Layersオブジェクト
kb = None # KMKKeyboardオブジェクト

def ng_initialize(_kb, _layers, _ng_layer):
    global kb, kblayers, ng_layer
    kb = _kb
    kblayers = _layers
    ng_layer = _ng_layer

#　かな変換の処理
def ng_press(*args, **kwargs):
    global pressed_keys, now
    kc = args[0]
    pressed_keys.add(kc)

    # 後置シフトはしない
    if kc in [KC.NGSFT, KC.NGSFT2]:
        nginput.append([kc])
    # 前のキーとの同時押しの可能性があるなら前に足す
    # 同じキー連打を除外
    elif len(nginput) > 0 and nginput[-1][-1] != kc and number_of_candidates(nginput[-1] + [kc]) > 0:
        nginput[-1] = nginput[-1] + [kc]
    # 前のキーと同時押しはない
    else:
        nginput.append([kc])
        # pressed_keys.discard(KC.NGSFT)

    # 連続シフトする
    # がある　がる x (JIの組み合わせがあるからJがC/Oされる) strictモードを作る
    # あいあう　あいう x
    # ぎょあう　ぎょう x
    # どか どが x 先にFがc/oされてJが残される
    for rs in [{KC.NGD, KC.NGF}, {KC.NGC, KC.NGV}, {KC.NGJ, KC.NGK}, {KC.NGM, KC.NGCOMM}, {KC.NGSFT}, {KC.NGSFT2}, {KC.NGF}, {KC.NGV}, {KC.NGJ}, {KC.NGM}]:
        rskc = list(rs) + nginput[-1]
        # rskc.append(kc)
        # じょじょ よを先に押すと連続シフトしない x
        # Falseにすると、がる が　がある になる x
        if kc not in rs and rs <= pressed_keys and number_of_candidates(rskc, True) > 0:
            nginput[-1] = rskc
            break

    if len(nginput) > 1 or number_of_candidates(nginput[0]) == 1:
        ng_type(nginput[0])
        del nginput[0]

    return False

def ng_release(*args, **kwargs):
    global pressed_keys, now
    kc = args[0]
    pressed_keys.discard(kc)

    # 全部キーを離したらバッファを全部吐き出す
    if len(pressed_keys) == 0:
        while len(nginput) > 0:
            ng_type(nginput[0])
            del nginput[0]

    return False

def ng_type(keys):
    if len(keys) == 0:
        return

    if len(keys) == 1 and keys[0] == KC.NGSFT2:
        kb.tap_key(KC.ENT)
        return
    
    skc = set(map(lambda x: KC.NGSFT if x == KC.NGSFT2 else x, keys))
    for k in ngdic:
        if skc == (k[0] | k[1]):
            if type(k[2]) is list:
                kb.tap_key(simple_key_sequence(k[2]))
            else:
                k[2]() # lambda
            break
    # JIみたいにJIを含む同時押しはたくさんあるが、JIのみの同時押しがないとき
    # 最後の１キーを別に分けて変換する
    else:
        kl = keys.pop(-1)
        ng_type(keys)
        ng_type([kl])

def number_of_candidates(keys, strict = False):
    if not keys:
        return 0

    noc = 0
    
    # skc = set(map(lambda x: KC.NGSFT if x == KC.NGSFT2 else x, keys))
    if strict:
        if keys[0] in [KC.NGSFT, KC.NGSFT2] and len(keys) == 1:
            noc = 1
        elif keys[0] in [KC.NGSFT, KC.NGSFT2] and len(keys) > 1:
            skc = set(keys[1:])
            for k in ngdic:
                if KC.NGSFT in k[0] and skc == k[1]:
                    noc += 1
        else:
            for rs in [{KC.NGD, KC.NGF}, {KC.NGC, KC.NGV}, {KC.NGJ, KC.NGK}, {KC.NGM, KC.NGCOMM}]:
                if len(keys) == 3 and set(keys[0:2]) == rs:
                    for k in ngdic:
                        if k[0] == rs and {keys[2]} == k[1]:
                            noc = 1
                            break
                    else:
                        continue
                    break
            else:
                skc = set(keys)
                for k in ngdic:
                    if not k[0] and skc == k[1]:
                        noc += 1
    else:
        if set(keys) in [{KC.NGSFT}, {KC.NGSFT2}, {KC.NGD, KC.NGF}, {KC.NGC, KC.NGV}, {KC.NGJ, KC.NGK}, {KC.NGM, KC.NGCOMM}]:
            noc = 2
        elif keys[0] in [KC.NGSFT, KC.NGSFT2] and len(keys) > 1:
            skc = set(keys[1:])
            for k in ngdic:
                if KC.NGSFT in k[0] and skc <= k[1]: # <=だけ違う
                    noc += 1
        else:
            for rs in [{KC.NGD, KC.NGF}, {KC.NGC, KC.NGV}, {KC.NGJ, KC.NGK}, {KC.NGM, KC.NGCOMM}]:
                if len(keys) == 3 and set(keys[0:2]) == rs:
                    for k in ngdic:
                        if k[0] == rs and {keys[2]} == k[1]:
                            noc = 1
                            break
                    else:
                        continue
                    break
            else:
                skc = set(keys)
                for k in ngdic:
                    if not k[0] and skc <= k[1]: # <=だけ違う
                        noc += 1

    print('NG num of candidates %d (%d)' % (noc, strict))
    return noc

def naginata_on(*args, **kwargs):
    kblayers.activate_layer(kb, ng_layer)
    nginput.clear()
    kb.tap_key(KC.LANG1)
    kb.tap_key(KC.INT4)
    return False

def naginata_off(*args, **kwargs):
    kblayers.deactivate_layer(kb, ng_layer)
    nginput.clear()
    kb.tap_key(KC.LANG2)
    kb.tap_key(KC.INT5)
    return False

# キーの定義
ngkeys = [
    'NGQ', 'NGW', 'NGE', 'NGR', 'NGT', 'NGY', 'NGU', 'NGI', 'NGO', 'NGP', 
    'NGA', 'NGS', 'NGD', 'NGF', 'NGG', 'NGH', 'NGJ', 'NGK', 'NGL', 'NGSCLN',
    'NGZ', 'NGX', 'NGC', 'NGV', 'NGB', 'NGN', 'NGM', 'NGCOMM', 'NGDOT', 'NGSLSH',
    'NGSFT', 'NGSFT2'
]
for k in ngkeys:
    make_key(names=(k,), on_press = ng_press, on_release = ng_release)

make_key(names=('NGON' ,), on_release = naginata_on) # on_releaseの方が安定する
make_key(names=('NGOFF',), on_release = naginata_off)

# かな変換テーブル setはdictionaryのキーにできないので配列に
# れ、をプレス時に出したい x
ngdic = [
    #  前置シフト      同時押し                        かな
    (  set()     , { KC.NGU                    }, [ KC.BSPC                      ]),
    (  set()     , { KC.NGSFT                  }, [ KC.SPC                       ]),
    (  set()     , { KC.NGM, KC.NGV            }, [ KC.ENT                       ]),
    (  set()     , { KC.NGT                    }, [ KC.LEFT                      ]),
    (  set()     , { KC.NGY                    }, [ KC.RIGHT                     ]),
    ({ KC.NGSFT }, { KC.NGT                    }, [ KC.LSFT(KC.LEFT)             ]),
    ({ KC.NGSFT }, { KC.NGY                    }, [ KC.LSFT(KC.RIGHT)            ]),
    (  set()     , { KC.NGSCLN                 }, [ KC.MINS                      ]), # ー
    ({ KC.NGSFT }, { KC.NGV                    }, [ KC.COMM, KC.ENT              ]), # 、{Enter}
    ({ KC.NGSFT }, { KC.NGM                    }, [ KC.DOT, KC.ENT               ]), # 。{Enter}

    (  set()     , { KC.NGJ                    }, [ KC.A                         ]), # あ
    (  set()     , { KC.NGK                    }, [ KC.I                         ]), # い
    (  set()     , { KC.NGL                    }, [ KC.U                         ]), # う
    ({ KC.NGSFT }, { KC.NGO                    }, [ KC.E                         ]), # え
    ({ KC.NGSFT }, { KC.NGN                    }, [ KC.O                         ]), # お
    (  set()     , { KC.NGF                    }, [ KC.K, KC.A                   ]), # か
    (  set()     , { KC.NGW                    }, [ KC.K, KC.I                   ]), # き
    (  set()     , { KC.NGH                    }, [ KC.K, KC.U                   ]), # く
    (  set()     , { KC.NGS                    }, [ KC.K, KC.E                   ]), # け
    (  set()     , { KC.NGV                    }, [ KC.K, KC.O                   ]), # こ
    ({ KC.NGSFT }, { KC.NGU                    }, [ KC.S, KC.A                   ]), # さ
    (  set()     , { KC.NGR                    }, [ KC.S, KC.I                   ]), # し
    (  set()     , { KC.NGO                    }, [ KC.S, KC.U                   ]), # す
    ({ KC.NGSFT }, { KC.NGA                    }, [ KC.S, KC.E                   ]), # せ
    (  set()     , { KC.NGB                    }, [ KC.S, KC.O                   ]), # そ
    (  set()     , { KC.NGN                    }, [ KC.T, KC.A                   ]), # た
    ({ KC.NGSFT }, { KC.NGG                    }, [ KC.T, KC.I                   ]), # ち
    ({ KC.NGSFT }, { KC.NGL                    }, [ KC.T, KC.U                   ]), # つ
    (  set()     , { KC.NGE                    }, [ KC.T, KC.E                   ]), # て
    (  set()     , { KC.NGD                    }, [ KC.T, KC.O                   ]), # と
    (  set()     , { KC.NGM                    }, [ KC.N, KC.A                   ]), # な
    ({ KC.NGSFT }, { KC.NGD                    }, [ KC.N, KC.I                   ]), # に
    ({ KC.NGSFT }, { KC.NGW                    }, [ KC.N, KC.U                   ]), # ぬ
    ({ KC.NGSFT }, { KC.NGR                    }, [ KC.N, KC.E                   ]), # ね
    ({ KC.NGSFT }, { KC.NGJ                    }, [ KC.N, KC.O                   ]), # の
    (  set()     , { KC.NGC                    }, [ KC.H, KC.A                   ]), # は
    (  set()     , { KC.NGX                    }, [ KC.H, KC.I                   ]), # ひ
    ({ KC.NGSFT }, { KC.NGX                    }, [ KC.H, KC.I                   ]), # ひ
    ({ KC.NGSFT }, { KC.NGSCLN                 }, [ KC.H, KC.U                   ]), # ふ
    (  set()     , { KC.NGP                    }, [ KC.H, KC.E                   ]), # へ
    (  set()     , { KC.NGZ                    }, [ KC.H, KC.O                   ]), # ほ
    ({ KC.NGSFT }, { KC.NGZ                    }, [ KC.H, KC.O                   ]), # ほ
    ({ KC.NGSFT }, { KC.NGF                    }, [ KC.M, KC.A                   ]), # ま
    ({ KC.NGSFT }, { KC.NGB                    }, [ KC.M, KC.I                   ]), # み
    ({ KC.NGSFT }, { KC.NGCOMM                 }, [ KC.M, KC.U                   ]), # む
    ({ KC.NGSFT }, { KC.NGS                    }, [ KC.M, KC.E                   ]), # め
    ({ KC.NGSFT }, { KC.NGK                    }, [ KC.M, KC.O                   ]), # も
    ({ KC.NGSFT }, { KC.NGH                    }, [ KC.Y, KC.A                   ]), # や
    ({ KC.NGSFT }, { KC.NGP                    }, [ KC.Y, KC.U                   ]), # ゆ
    ({ KC.NGSFT }, { KC.NGI                    }, [ KC.Y, KC.O                   ]), # よ
    (  set()     , { KC.NGDOT                  }, [ KC.R, KC.A                   ]), # ら
    ({ KC.NGSFT }, { KC.NGE                    }, [ KC.R, KC.I                   ]), # り
    (  set()     , { KC.NGI                    }, [ KC.R, KC.U                   ]), # る
    (  set()     , { KC.NGSLSH                 }, [ KC.R, KC.E                   ]), # れ
    ({ KC.NGSFT }, { KC.NGSLSH                 }, [ KC.R, KC.E                   ]), # れ
    (  set()     , { KC.NGA                    }, [ KC.R, KC.O                   ]), # ろ
    ({ KC.NGSFT }, { KC.NGDOT                  }, [ KC.W, KC.A                   ]), # わ
    ({ KC.NGSFT }, { KC.NGC                    }, [ KC.W, KC.O                   ]), # を
    (  set()     , { KC.NGCOMM                 }, [ KC.N, KC.N                   ]), # ん
    (  set()     , { KC.NGQ                    }, [ KC.V, KC.U                   ]), # ゔ
    ({ KC.NGSFT }, { KC.NGQ                    }, [ KC.V, KC.U                   ]), # ゔ
    (  set()     , { KC.NGJ, KC.NGF            }, [ KC.G, KC.A                   ]), # が
    (  set()     , { KC.NGJ, KC.NGW            }, [ KC.G, KC.I                   ]), # ぎ
    (  set()     , { KC.NGF, KC.NGH            }, [ KC.G, KC.U                   ]), # ぐ
    (  set()     , { KC.NGJ, KC.NGS            }, [ KC.G, KC.E                   ]), # げ
    (  set()     , { KC.NGJ, KC.NGV            }, [ KC.G, KC.O                   ]), # ご
    (  set()     , { KC.NGF, KC.NGU            }, [ KC.Z, KC.A                   ]), # ざ
    (  set()     , { KC.NGJ, KC.NGR            }, [ KC.Z, KC.I                   ]), # じ
    (  set()     , { KC.NGF, KC.NGO            }, [ KC.Z, KC.U                   ]), # ず
    (  set()     , { KC.NGJ, KC.NGA            }, [ KC.Z, KC.E                   ]), # ぜ
    (  set()     , { KC.NGJ, KC.NGB            }, [ KC.Z, KC.O                   ]), # ぞ
    (  set()     , { KC.NGF, KC.NGN            }, [ KC.D, KC.A                   ]), # だ
    (  set()     , { KC.NGJ, KC.NGG            }, [ KC.D, KC.I                   ]), # ぢ
    (  set()     , { KC.NGF, KC.NGL            }, [ KC.D, KC.U                   ]), # づ
    (  set()     , { KC.NGJ, KC.NGE            }, [ KC.D, KC.E                   ]), # で
    (  set()     , { KC.NGJ, KC.NGD            }, [ KC.D, KC.O                   ]), # ど
    (  set()     , { KC.NGJ, KC.NGC            }, [ KC.B, KC.A                   ]), # ば
    (  set()     , { KC.NGJ, KC.NGX            }, [ KC.B, KC.I                   ]), # び
    (  set()     , { KC.NGF, KC.NGSCLN         }, [ KC.B, KC.U                   ]), # ぶ
    (  set()     , { KC.NGF, KC.NGP            }, [ KC.B, KC.E                   ]), # べ
    (  set()     , { KC.NGJ, KC.NGZ            }, [ KC.B, KC.O                   ]), # ぼ
    (  set()     , { KC.NGF, KC.NGL            }, [ KC.V, KC.U                   ]), # ゔ
    (  set()     , { KC.NGM, KC.NGC            }, [ KC.P, KC.A                   ]), # ぱ
    (  set()     , { KC.NGM, KC.NGX            }, [ KC.P, KC.I                   ]), # ぴ
    (  set()     , { KC.NGV, KC.NGSCLN         }, [ KC.P, KC.U                   ]), # ぷ
    (  set()     , { KC.NGV, KC.NGP            }, [ KC.P, KC.E                   ]), # ぺ
    (  set()     , { KC.NGM, KC.NGZ            }, [ KC.P, KC.O                   ]), # ぽ
    (  set()     , { KC.NGQ, KC.NGH            }, [ KC.X, KC.Y, KC.A             ]), # ゃ
    (  set()     , { KC.NGQ, KC.NGP            }, [ KC.X, KC.Y, KC.U             ]), # ゅ
    (  set()     , { KC.NGQ, KC.NGI            }, [ KC.X, KC.Y, KC.O             ]), # ょ
    (  set()     , { KC.NGQ, KC.NGJ            }, [ KC.X, KC.A                   ]), # ぁ
    (  set()     , { KC.NGQ, KC.NGK            }, [ KC.X, KC.I                   ]), # ぃ
    (  set()     , { KC.NGQ, KC.NGL            }, [ KC.X, KC.U                   ]), # ぅ
    (  set()     , { KC.NGQ, KC.NGO            }, [ KC.X, KC.E                   ]), # ぇ
    (  set()     , { KC.NGQ, KC.NGN            }, [ KC.X, KC.O                   ]), # ぉ
    (  set()     , { KC.NGQ, KC.NGDOT          }, [ KC.X, KC.W, KC.A             ]), # ゎ
    (  set()     , { KC.NGG                    }, [ KC.X, KC.T, KC.U             ]), # っ
    (  set()     , { KC.NGQ, KC.NGS            }, [ KC.X, KC.K, KC.E             ]), # ヶ
    (  set()     , { KC.NGQ, KC.NGF            }, [ KC.X, KC.K, KC.A             ]), # ヵ
    (  set()     , { KC.NGR, KC.NGH            }, [ KC.S, KC.Y, KC.A             ]), # しゃ
    (  set()     , { KC.NGR, KC.NGP            }, [ KC.S, KC.Y, KC.U             ]), # しゅ
    (  set()     , { KC.NGR, KC.NGI            }, [ KC.S, KC.Y, KC.O             ]), # しょ
    (  set()     , { KC.NGJ, KC.NGR, KC.NGH    }, [ KC.Z, KC.Y, KC.A             ]), # じゃ
    (  set()     , { KC.NGJ, KC.NGR, KC.NGP    }, [ KC.Z, KC.Y, KC.U             ]), # じゅ
    (  set()     , { KC.NGJ, KC.NGR, KC.NGI    }, [ KC.Z, KC.Y, KC.O             ]), # じょ
    (  set()     , { KC.NGW, KC.NGH            }, [ KC.K, KC.Y, KC.A             ]), # きゃ
    (  set()     , { KC.NGW, KC.NGP            }, [ KC.K, KC.Y, KC.U             ]), # きゅ
    (  set()     , { KC.NGW, KC.NGI            }, [ KC.K, KC.Y, KC.O             ]), # きょ
    (  set()     , { KC.NGJ, KC.NGW, KC.NGH    }, [ KC.G, KC.Y, KC.A             ]), # ぎゃ
    (  set()     , { KC.NGJ, KC.NGW, KC.NGP    }, [ KC.G, KC.Y, KC.U             ]), # ぎゅ
    (  set()     , { KC.NGJ, KC.NGW, KC.NGI    }, [ KC.G, KC.Y, KC.O             ]), # ぎょ
    (  set()     , { KC.NGG, KC.NGH            }, [ KC.T, KC.Y, KC.A             ]), # ちゃ
    (  set()     , { KC.NGG, KC.NGP            }, [ KC.T, KC.Y, KC.U             ]), # ちゅ
    (  set()     , { KC.NGG, KC.NGI            }, [ KC.T, KC.Y, KC.O             ]), # ちょ
    (  set()     , { KC.NGJ, KC.NGG, KC.NGH    }, [ KC.D, KC.Y, KC.A             ]), # ぢゃ
    (  set()     , { KC.NGJ, KC.NGG, KC.NGP    }, [ KC.D, KC.Y, KC.U             ]), # ぢゅ
    (  set()     , { KC.NGJ, KC.NGG, KC.NGI    }, [ KC.D, KC.Y, KC.O             ]), # ぢょ
    (  set()     , { KC.NGD, KC.NGH            }, [ KC.N, KC.Y, KC.A             ]), # にゃ
    (  set()     , { KC.NGD, KC.NGP            }, [ KC.N, KC.Y, KC.U             ]), # にゅ
    (  set()     , { KC.NGD, KC.NGI            }, [ KC.N, KC.Y, KC.O             ]), # にょ
    (  set()     , { KC.NGX, KC.NGH            }, [ KC.H, KC.Y, KC.A             ]), # ひゃ
    (  set()     , { KC.NGX, KC.NGP            }, [ KC.H, KC.Y, KC.U             ]), # ひゅ
    (  set()     , { KC.NGX, KC.NGI            }, [ KC.H, KC.Y, KC.O             ]), # ひょ
    (  set()     , { KC.NGJ, KC.NGX, KC.NGH    }, [ KC.B, KC.Y, KC.A             ]), # びゃ
    (  set()     , { KC.NGJ, KC.NGX, KC.NGP    }, [ KC.B, KC.Y, KC.U             ]), # びゅ
    (  set()     , { KC.NGJ, KC.NGX, KC.NGI    }, [ KC.B, KC.Y, KC.O             ]), # びょ
    (  set()     , { KC.NGM, KC.NGX, KC.NGH    }, [ KC.P, KC.Y, KC.A             ]), # ぴゃ
    (  set()     , { KC.NGM, KC.NGX, KC.NGP    }, [ KC.P, KC.Y, KC.U             ]), # ぴゅ
    (  set()     , { KC.NGM, KC.NGX, KC.NGI    }, [ KC.P, KC.Y, KC.O             ]), # ぴょ
    (  set()     , { KC.NGB, KC.NGH            }, [ KC.M, KC.Y, KC.A             ]), # みゃ
    (  set()     , { KC.NGB, KC.NGP            }, [ KC.M, KC.Y, KC.U             ]), # みゅ
    (  set()     , { KC.NGB, KC.NGI            }, [ KC.M, KC.Y, KC.O             ]), # みょ
    (  set()     , { KC.NGE, KC.NGH            }, [ KC.R, KC.Y, KC.A             ]), # りゃ
    (  set()     , { KC.NGE, KC.NGP            }, [ KC.R, KC.Y, KC.U             ]), # りゅ
    (  set()     , { KC.NGE, KC.NGI            }, [ KC.R, KC.Y, KC.O             ]), # りょ
    (  set()     , { KC.NGM, KC.NGE, KC.NGK    }, [ KC.T, KC.H, KC.I             ]), # てぃ
    (  set()     , { KC.NGM, KC.NGE, KC.NGP    }, [ KC.T, KC.H, KC.U             ]), # てゅ
    (  set()     , { KC.NGJ, KC.NGE, KC.NGK    }, [ KC.D, KC.H, KC.I             ]), # でぃ
    (  set()     , { KC.NGJ, KC.NGE, KC.NGP    }, [ KC.D, KC.H, KC.U             ]), # でゅ
    (  set()     , { KC.NGM, KC.NGD, KC.NGL    }, [ KC.T, KC.O, KC.X, KC.U       ]), # とぅ
    (  set()     , { KC.NGJ, KC.NGD, KC.NGL    }, [ KC.D, KC.O, KC.X, KC.U       ]), # どぅ
    (  set()     , { KC.NGM, KC.NGR, KC.NGO    }, [ KC.S, KC.Y, KC.E             ]), # しぇ
    (  set()     , { KC.NGM, KC.NGG, KC.NGO    }, [ KC.T, KC.Y, KC.E             ]), # ちぇ
    (  set()     , { KC.NGJ, KC.NGR, KC.NGO    }, [ KC.Z, KC.Y, KC.E             ]), # じぇ
    (  set()     , { KC.NGJ, KC.NGG, KC.NGO    }, [ KC.D, KC.Y, KC.E             ]), # ぢぇ
    (  set()     , { KC.NGV, KC.NGSCLN, KC.NGJ }, [ KC.F, KC.A                   ]), # ふぁ
    (  set()     , { KC.NGV, KC.NGSCLN, KC.NGK }, [ KC.F, KC.I                   ]), # ふぃ
    (  set()     , { KC.NGV, KC.NGSCLN, KC.NGO }, [ KC.F, KC.E                   ]), # ふぇ
    (  set()     , { KC.NGV, KC.NGSCLN, KC.NGN }, [ KC.F, KC.O                   ]), # ふぉ
    (  set()     , { KC.NGV, KC.NGSCLN, KC.NGP }, [ KC.F, KC.Y, KC.U             ]), # ふゅ
    (  set()     , { KC.NGV, KC.NGK, KC.NGO    }, [ KC.I, KC.X, KC.E             ]), # いぇ
    (  set()     , { KC.NGV, KC.NGL, KC.NGK    }, [ KC.W, KC.I                   ]), # うぃ
    (  set()     , { KC.NGV, KC.NGL, KC.NGO    }, [ KC.W, KC.E                   ]), # うぇ
    (  set()     , { KC.NGV, KC.NGL, KC.NGN    }, [ KC.U, KC.X, KC.O             ]), # うぉ
    (  set()     , { KC.NGM, KC.NGQ, KC.NGJ    }, [ KC.V, KC.A                   ]), # ゔぁ
    (  set()     , { KC.NGM, KC.NGQ, KC.NGK    }, [ KC.V, KC.I                   ]), # ゔぃ
    (  set()     , { KC.NGM, KC.NGQ, KC.NGO    }, [ KC.V, KC.E                   ]), # ゔぇ
    (  set()     , { KC.NGM, KC.NGQ, KC.NGN    }, [ KC.V, KC.O                   ]), # ゔぉ
    (  set()     , { KC.NGM, KC.NGQ, KC.NGP    }, [ KC.V, KC.U, KC.X, KC.Y, KC.U ]), # ゔゅ
    (  set()     , { KC.NGV, KC.NGH, KC.NGJ    }, [ KC.K, KC.U, KC.X, KC.A       ]), # くぁ
    (  set()     , { KC.NGV, KC.NGH, KC.NGK    }, [ KC.K, KC.U, KC.X, KC.I       ]), # くぃ
    (  set()     , { KC.NGV, KC.NGH, KC.NGO    }, [ KC.K, KC.U, KC.X, KC.E       ]), # くぇ
    (  set()     , { KC.NGV, KC.NGH, KC.NGN    }, [ KC.K, KC.U, KC.X, KC.O       ]), # くぉ
    (  set()     , { KC.NGV, KC.NGH, KC.NGDOT  }, [ KC.K, KC.U, KC.X, KC.W, KC.A ]), # くゎ
    (  set()     , { KC.NGF, KC.NGH, KC.NGJ    }, [ KC.G, KC.U, KC.X, KC.A       ]), # ぐぁ
    (  set()     , { KC.NGF, KC.NGH, KC.NGK    }, [ KC.G, KC.U, KC.X, KC.I       ]), # ぐぃ
    (  set()     , { KC.NGF, KC.NGH, KC.NGO    }, [ KC.G, KC.U, KC.X, KC.E       ]), # ぐぇ
    (  set()     , { KC.NGF, KC.NGH, KC.NGN    }, [ KC.G, KC.U, KC.X, KC.O       ]), # ぐぉ
    (  set()     , { KC.NGF, KC.NGH, KC.NGDOT  }, [ KC.G, KC.U, KC.X, KC.W, KC.A ]), # ぐゎ
    (  set()     , { KC.NGV, KC.NGL, KC.NGJ    }, [ KC.T, KC.S, KC.A             ]), # つぁ

    ({ KC.NGJ, KC.NGK    }, { KC.NGD    }, [ KC.LSFT(KC.SLSH), KC.ENT                            ]), # ？{改行}
    ({ KC.NGJ, KC.NGK    }, { KC.NGC    }, [ KC.LSFT(KC.N1), KC.ENT                              ]), # ！{改行}

    # Mac縦書き
    ({ KC.NGJ, KC.NGK    }, { KC.NGQ    }, [ KC.LGUI(KC.DOWN)                                   ]), # ^{End}
    ({ KC.NGJ, KC.NGK    }, { KC.NGW    }, [ unicode_string_sequence('『』'), KC.UP              ]), # 『』{改行}{↑}
    ({ KC.NGJ, KC.NGK    }, { KC.NGE    }, [ KC.D, KC.H, KC.I                                   ]), # /*ディ*/
    ({ KC.NGJ, KC.NGK    }, { KC.NGR    }, [ KC.LGUI(KC.S)                                      ]), # ^s
    ({ KC.NGJ, KC.NGK    }, { KC.NGV    }, [ KC.ENT, KC.DOWN                                    ]), # {改行}{↓}
    ({ KC.NGJ, KC.NGK    }, { KC.NGB    }, [ KC.ENT, KC.LEFT                                    ]), # {改行}{←}
    ({ KC.NGD, KC.NGF    }, { KC.NGY    }, [ KC.LCTL(KC.A)                                      ]), # {Home}
    ({ KC.NGD, KC.NGF    }, { KC.NGU    }, [ KC.LSFT(KC.LCTL(KC.E)), KC.BSPC                    ]), # +{End}{BS}
    ({ KC.NGD, KC.NGF    }, { KC.NGI    }, [ KC.LANG1, KC.LANG1                                 ]), # {vk1Csc079}
    ({ KC.NGD, KC.NGF    }, { KC.NGO    }, [ KC.DEL                                             ]), # {Del}
    ({ KC.NGD, KC.NGF    }, { KC.NGP    }, [ KC.ESC, KC.ESC, KC.ESC                             ]), # {Esc 3}
    ({ KC.NGD, KC.NGF    }, { KC.NGH    }, [ KC.ENT, KC.LCTL(KC.E)                              ]), # {Enter}{End}
    ({ KC.NGD, KC.NGF    }, { KC.NGJ    }, [ KC.UP                                              ]), # {↑}
    ({ KC.NGD, KC.NGF    }, { KC.NGK    }, [ KC.LSFT(KC.UP)                                     ]), # +{↑}
    ({ KC.NGD, KC.NGF    }, { KC.NGL    }, [ KC.LSFT(KC.UP)] * 7                                 ), # +{↑ 7}
    ({ KC.NGD, KC.NGF    }, { KC.NGSCLN }, [ KC.LCTL(KC.K)                                      ]), # ^i
    ({ KC.NGD, KC.NGF    }, { KC.NGN    }, [ KC.LCTL(KC.E)                                      ]), # {End}
    ({ KC.NGD, KC.NGF    }, { KC.NGM    }, [ KC.DOWN                                            ]), # {↓}
    ({ KC.NGD, KC.NGF    }, { KC.NGCOMM }, [ KC.LSFT(KC.DOWN)                                   ]), # +{↓}
    ({ KC.NGD, KC.NGF    }, { KC.NGDOT  }, [ KC.LSFT(KC.DOWN)] * 7                               ), # +{↓ 7}
    ({ KC.NGD, KC.NGF    }, { KC.NGSLSH }, [ KC.LCTL(KC.J)                                      ]), # ^u
    ({ KC.NGM, KC.NGCOMM }, { KC.NGQ    }, [ KC.LCTL(KC.A), KC.RIGHT, KC.LCTL(KC.E), KC.DEL, KC.DEL, KC.DEL, KC.DEL, KC.LEFT ]), # {Home}{→}{End}{Del 4}{←}
    ({ KC.NGM, KC.NGCOMM }, { KC.NGE    }, [ KC.LCTL(KC.A), KC.ENT, KC.SPC, KC.SPC, KC.SPC, KC.LEFT ]), # {Home}{改行}{Space 3}{←}
    ({ KC.NGM, KC.NGCOMM }, { KC.NGR    }, [ KC.SPC, KC.SPC, KC.SPC                             ]), # {Space 3}
    ({ KC.NGM, KC.NGCOMM }, { KC.NGA    }, [ KC.LCTL(KC.A), KC.RIGHT, KC.LCTL(KC.E), KC.DEL, KC.DEL, KC.LEFT ]), # {Home}{→}{End}{Del 2}{←}
    ({ KC.NGM, KC.NGCOMM }, { KC.NGD    }, [ KC.LCTL(KC.A), KC.ENT, KC.SPC, KC.LEFT             ]), # {Home}{改行}{Space 1}{←}
    ({ KC.NGM, KC.NGCOMM }, { KC.NGB    }, [ KC.ENT, KC.LCTL(KC.E), KC.ENT, KC.SPC              ]), # {改行}{End}{改行}{Space}
    ({ KC.NGC, KC.NGV    }, { KC.NGY    }, [ KC.LSFT(KC.LCTL(KC.A))                             ]), # +{Home}
    ({ KC.NGC, KC.NGV    }, { KC.NGU    }, [ KC.LGUI(KC.X)                                      ]), # ^x
    ({ KC.NGC, KC.NGV    }, { KC.NGI    }, [ KC.LGUI(KC.V)                                      ]), # ^v
    ({ KC.NGC, KC.NGV    }, { KC.NGO    }, [ KC.LSFT(KC.LGUI(KC.Z))                             ]), # ^y
    ({ KC.NGC, KC.NGV    }, { KC.NGP    }, [ KC.LGUI(KC.Z)                                      ]), # ^z
    ({ KC.NGC, KC.NGV    }, { KC.NGH    }, [ KC.LGUI(KC.C)                                      ]), # ^c
    ({ KC.NGC, KC.NGV    }, { KC.NGJ    }, [ KC.RIGHT                                           ]), # {→}
    ({ KC.NGC, KC.NGV    }, { KC.NGK    }, [ KC.LSFT(KC.RIGHT)                                  ]), # +{→}
    ({ KC.NGC, KC.NGV    }, { KC.NGL    }, [ KC.LSFT(KC.RIGHT)] * 5                              ), # +{→ 5}
    ({ KC.NGC, KC.NGV    }, { KC.NGSCLN }, [ KC.LSFT(KC.RIGHT)] * 20                             ), # +{→ 20}
    ({ KC.NGC, KC.NGV    }, { KC.NGN    }, [ KC.LSFT(KC.LCTL(KC.E))                             ]), # +{End}
    ({ KC.NGC, KC.NGV    }, { KC.NGM    }, [ KC.LEFT                                            ]), # {←}
    ({ KC.NGC, KC.NGV    }, { KC.NGCOMM }, [ KC.LSFT(KC.LEFT)                                   ]), # +{←}
    ({ KC.NGC, KC.NGV    }, { KC.NGDOT  }, [ KC.LSFT(KC.LEFT)] * 5                               ), # +{← 5}
    ({ KC.NGC, KC.NGV    }, { KC.NGSLSH }, [ KC.LSFT(KC.LEFT)] * 20                              ), # +{← 20}

]
