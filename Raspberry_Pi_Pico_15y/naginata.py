# 薙刀式 v15y 実装

import supervisor

from kmk.keys import KC
from kmk.keys import make_key
from kmk.handlers.sequences import send_string
from kmk.handlers.sequences import simple_key_sequence
from kmk.handlers.sequences import unicode_string_sequence

pressed_keys = set() # 同時に押しているキー
nginput = [] # 未変換のキー
ng_layer = 0
kblayers = None
kb = None

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
        # 連続シフトする
        for rs in [KC.NGSFT, KC.NGSFT2, KC.NGF, KC.NGV, KC.NGJ, KC.NGM]:
            if rs in pressed_keys and number_of_candidates([rs, kc]) > 0:
                nginput.append([rs, kc])
                break
        # 連続シフトではない
        else:
            nginput.append([kc])
            # pressed_keys.discard(KC.NGSFT)

    if len(nginput) > 1 or number_of_candidates(nginput[0]) == 1:
        ng_type(nginput[0])
        del nginput[0]

    return False

def ng_release(*args, **kwargs):
    global pressed_keys, now
    kc = args[0]
    pressed_keys.discard(kc)

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
        if skc == k[0]: # 部分集合
            if type(k[1]) is list:
                kb.tap_key(simple_key_sequence(k[1]))
            else:
                k[1]() # lambda
            break
    # JIみたいにJIを含む同時押しはたくさんあるが、JIのみの同時押しがないとき
    # 最後の１キーを別に分けて変換する
    else:
        kl = keys.pop(-1)
        ng_type(keys)
        ng_type([kl])

def number_of_candidates(keys):
    noc = 0
    
    skc = set(map(lambda x: KC.NGSFT if x == KC.NGSFT2 else x, keys))
    for k in ngdic: # (set(KC), list(KC))
        if skc <= k[0]: # 部分集合
            if KC.NGSFT in k[0]:
                if keys[0] == KC.NGSFT or keys[0] == KC.NGSFT2:  # 前置シフトしか認めない
                    noc += 1
            else:
                noc += 1
            # if noc > 1:
            #     break

    print('NG num of candidates %d' % noc)
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

def ng_henshu1_on(*args, **kwargs):
    global henshu_mode
    henshu_mode = 1
    return False

def ng_henshu2_on(*args, **kwargs):
    global henshu_mode
    henshu_mode = 2
    return False

def ng_henshu_off(*args, **kwargs):
    global henshu_mode
    henshu_mode = 0
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
# make_key(names=('NGH1', ), on_press = ng_henshu1_on, on_release = ng_henshu_off)
# make_key(names=('NGH2', ), on_press = ng_henshu2_on, on_release = ng_henshu_off)

# KC.A.before_press_handler(ng_henshu)
# KC.NGA.before_press_handler(ng_henshu)

# かな変換テーブル setはdictionaryのキーにできないので配列に
ngdic = [
    ({ KC.NGU                         }, [ KC.BSPC                  ]),
    ({ KC.NGSFT                       }, [ KC.SPC                   ]),
    ({ KC.NGM, KC.NGV                 }, [ KC.ENT                   ]),
    ({ KC.NGT                         }, [ KC.LEFT                  ]),
    ({ KC.NGY                         }, [ KC.RIGHT                 ]),
    ({ KC.NGSFT, KC.NGT               }, [ KC.LSFT(KC.LEFT)         ]),
    ({ KC.NGSFT, KC.NGY               }, lambda: kb.tap_key(simple_key_sequence([KC.LSFT(KC.RIGHT)]))),
    ({ KC.NGSCLN                      }, [ KC.MINS                  ]), # ー
    ({ KC.NGSFT, KC.NGV               }, [ KC.COMM, KC.ENT          ]), # 、{Enter}
    ({ KC.NGSFT, KC.NGM               }, [ KC.DOT, KC.ENT           ]), # 。{Enter}

    ({ KC.NGJ                         }, [ KC.A                     ]), # あ
    ({ KC.NGK                         }, [ KC.I                     ]), # い
    ({ KC.NGL                         }, [ KC.U                     ]), # う
    ({ KC.NGSFT, KC.NGO               }, [ KC.E                     ]), # え
    ({ KC.NGSFT, KC.NGN               }, [ KC.O                     ]), # お
    ({ KC.NGF                         }, [ KC.K, KC.A               ]), # か
    ({ KC.NGW                         }, [ KC.K, KC.I               ]), # き
    ({ KC.NGH                         }, [ KC.K, KC.U               ]), # く
    ({ KC.NGS                         }, [ KC.K, KC.E               ]), # け
    ({ KC.NGV                         }, [ KC.K, KC.O               ]), # こ
    ({ KC.NGSFT, KC.NGU               }, [ KC.S, KC.A               ]), # さ
    ({ KC.NGR                         }, [ KC.S, KC.I               ]), # し
    ({ KC.NGO                         }, [ KC.S, KC.U               ]), # す
    ({ KC.NGSFT, KC.NGA               }, [ KC.S, KC.E               ]), # せ
    ({ KC.NGB                         }, [ KC.S, KC.O               ]), # そ
    ({ KC.NGN                         }, [ KC.T, KC.A               ]), # た
    ({ KC.NGSFT, KC.NGG               }, [ KC.T, KC.I               ]), # ち
    ({ KC.NGSFT, KC.NGL               }, [ KC.T, KC.U               ]), # つ
    ({ KC.NGE                         }, [ KC.T, KC.E               ]), # て
    ({ KC.NGD                         }, [ KC.T, KC.O               ]), # と
    ({ KC.NGM                         }, [ KC.N, KC.A               ]), # な
    ({ KC.NGSFT, KC.NGD               }, [ KC.N, KC.I               ]), # に
    ({ KC.NGSFT, KC.NGW               }, [ KC.N, KC.U               ]), # ぬ
    ({ KC.NGSFT, KC.NGR               }, [ KC.N, KC.E               ]), # ね
    ({ KC.NGSFT, KC.NGJ               }, [ KC.N, KC.O               ]), # の
    ({ KC.NGC                         }, [ KC.H, KC.A               ]), # は
    ({ KC.NGX                         }, [ KC.H, KC.I               ]), # ひ
    ({ KC.NGSFT, KC.NGX               }, [ KC.H, KC.I               ]), # ひ
    ({ KC.NGSFT, KC.NGSCLN            }, [ KC.H, KC.U               ]), # ふ
    ({ KC.NGP                         }, [ KC.H, KC.E               ]), # へ
    ({ KC.NGZ                         }, [ KC.H, KC.O               ]), # ほ
    ({ KC.NGSFT, KC.NGZ               }, [ KC.H, KC.O               ]), # ほ
    ({ KC.NGSFT, KC.NGF               }, [ KC.M, KC.A               ]), # ま
    ({ KC.NGSFT, KC.NGB               }, [ KC.M, KC.I               ]), # み
    ({ KC.NGSFT, KC.NGCOMM            }, [ KC.M, KC.U               ]), # む
    ({ KC.NGSFT, KC.NGS               }, [ KC.M, KC.E               ]), # め
    ({ KC.NGSFT, KC.NGK               }, [ KC.M, KC.O               ]), # も
    ({ KC.NGSFT, KC.NGH               }, [ KC.Y, KC.A               ]), # や
    ({ KC.NGSFT, KC.NGP               }, [ KC.Y, KC.U               ]), # ゆ
    ({ KC.NGSFT, KC.NGI               }, [ KC.Y, KC.O               ]), # よ
    ({ KC.NGDOT                       }, [ KC.R, KC.A               ]), # ら
    ({ KC.NGSFT, KC.NGE               }, [ KC.R, KC.I               ]), # り
    ({ KC.NGI                         }, [ KC.R, KC.U               ]), # る
    ({ KC.NGSLSH                      }, [ KC.R, KC.E               ]), # れ
    ({ KC.NGSFT, KC.NGSLSH            }, [ KC.R, KC.E               ]), # れ
    ({ KC.NGA                         }, [ KC.R, KC.O               ]), # ろ
    ({ KC.NGSFT, KC.NGDOT             }, [ KC.W, KC.A               ]), # わ
    ({ KC.NGSFT, KC.NGC               }, [ KC.W, KC.O               ]), # を
    ({ KC.NGCOMM                      }, [ KC.N, KC.N               ]), # ん
    ({ KC.NGQ                         }, [ KC.V, KC.U               ]), # ゔ
    ({ KC.NGSFT, KC.NGQ               }, [ KC.V, KC.U               ]), # ゔ
    ({ KC.NGJ, KC.NGF                 }, [ KC.G, KC.A               ]), # が
    ({ KC.NGJ, KC.NGW                 }, [ KC.G, KC.I               ]), # ぎ
    ({ KC.NGF, KC.NGH                 }, [ KC.G, KC.U               ]), # ぐ
    ({ KC.NGJ, KC.NGS                 }, [ KC.G, KC.E               ]), # げ
    ({ KC.NGJ, KC.NGV                 }, [ KC.G, KC.O               ]), # ご
    ({ KC.NGF, KC.NGU                 }, [ KC.Z, KC.A               ]), # ざ
    ({ KC.NGJ, KC.NGR                 }, [ KC.Z, KC.I               ]), # じ
    ({ KC.NGF, KC.NGO                 }, [ KC.Z, KC.U               ]), # ず
    ({ KC.NGJ, KC.NGA                 }, [ KC.Z, KC.E               ]), # ぜ
    ({ KC.NGJ, KC.NGB                 }, [ KC.Z, KC.O               ]), # ぞ
    ({ KC.NGF, KC.NGN                 }, [ KC.D, KC.A               ]), # だ
    ({ KC.NGJ, KC.NGG                 }, [ KC.D, KC.I               ]), # ぢ
    ({ KC.NGF, KC.NGL                 }, [ KC.D, KC.U               ]), # づ
    ({ KC.NGJ, KC.NGE                 }, [ KC.D, KC.E               ]), # で
    ({ KC.NGJ, KC.NGD                 }, [ KC.D, KC.O               ]), # ど
    ({ KC.NGJ, KC.NGC                 }, [ KC.B, KC.A               ]), # ば
    ({ KC.NGJ, KC.NGX                 }, [ KC.B, KC.I               ]), # び
    ({ KC.NGF, KC.NGSCLN              }, [ KC.B, KC.U               ]), # ぶ
    ({ KC.NGF, KC.NGP                 }, [ KC.B, KC.E               ]), # べ
    ({ KC.NGJ, KC.NGZ                 }, [ KC.B, KC.O               ]), # ぼ
    ({ KC.NGF, KC.NGL                 }, [ KC.V, KC.U               ]), # ゔ
    ({ KC.NGM, KC.NGC                 }, [ KC.P, KC.A               ]), # ぱ
    ({ KC.NGM, KC.NGX                 }, [ KC.P, KC.I               ]), # ぴ
    ({ KC.NGV, KC.NGSCLN              }, [ KC.P, KC.U               ]), # ぷ
    ({ KC.NGV, KC.NGP                 }, [ KC.P, KC.E               ]), # ぺ
    ({ KC.NGM, KC.NGZ                 }, [ KC.P, KC.O               ]), # ぽ
    ({ KC.NGQ, KC.NGH                 }, [ KC.X, KC.Y, KC.A         ]), # ゃ
    ({ KC.NGQ, KC.NGP                 }, [ KC.X, KC.Y, KC.U         ]), # ゅ
    ({ KC.NGQ, KC.NGI                 }, [ KC.X, KC.Y, KC.O         ]), # ょ
    ({ KC.NGQ, KC.NGJ                 }, [ KC.X, KC.A               ]), # ぁ
    ({ KC.NGQ, KC.NGK                 }, [ KC.X, KC.I               ]), # ぃ
    ({ KC.NGQ, KC.NGL                 }, [ KC.X, KC.U               ]), # ぅ
    ({ KC.NGQ, KC.NGO                 }, [ KC.X, KC.E               ]), # ぇ
    ({ KC.NGQ, KC.NGN                 }, [ KC.X, KC.O               ]), # ぉ
    ({ KC.NGQ, KC.NGDOT               }, [ KC.X, KC.W, KC.A         ]), # ゎ
    ({ KC.NGG                         }, [ KC.X, KC.T, KC.U         ]), # っ
    ({ KC.NGQ, KC.NGS                 }, [ KC.X, KC.K, KC.E         ]), # ヶ
    ({ KC.NGQ, KC.NGF                 }, [ KC.X, KC.K, KC.A         ]), # ヵ
    ({ KC.NGR, KC.NGH                 }, [ KC.S, KC.Y, KC.A         ]), # しゃ
    ({ KC.NGR, KC.NGP                 }, [ KC.S, KC.Y, KC.U         ]), # しゅ
    ({ KC.NGR, KC.NGI                 }, [ KC.S, KC.Y, KC.O         ]), # しょ
    ({ KC.NGJ, KC.NGR, KC.NGH         }, [ KC.Z, KC.Y, KC.A         ]), # じゃ
    ({ KC.NGJ, KC.NGR, KC.NGP         }, [ KC.Z, KC.Y, KC.U         ]), # じゅ
    ({ KC.NGJ, KC.NGR, KC.NGI         }, [ KC.Z, KC.Y, KC.O         ]), # じょ
    ({ KC.NGW, KC.NGH                 }, [ KC.K, KC.Y, KC.A         ]), # きゃ
    ({ KC.NGW, KC.NGP                 }, [ KC.K, KC.Y, KC.U         ]), # きゅ
    ({ KC.NGW, KC.NGI                 }, [ KC.K, KC.Y, KC.O         ]), # きょ
    ({ KC.NGJ, KC.NGW, KC.NGH         }, [ KC.G, KC.Y, KC.A         ]), # ぎゃ
    ({ KC.NGJ, KC.NGW, KC.NGP         }, [ KC.G, KC.Y, KC.U         ]), # ぎゅ
    ({ KC.NGJ, KC.NGW, KC.NGI         }, [ KC.G, KC.Y, KC.O         ]), # ぎょ
    ({ KC.NGG, KC.NGH                 }, [ KC.T, KC.Y, KC.A         ]), # ちゃ
    ({ KC.NGG, KC.NGP                 }, [ KC.T, KC.Y, KC.U         ]), # ちゅ
    ({ KC.NGG, KC.NGI                 }, [ KC.T, KC.Y, KC.O         ]), # ちょ
    ({ KC.NGJ, KC.NGG, KC.NGH         }, [ KC.D, KC.Y, KC.A         ]), # ぢゃ
    ({ KC.NGJ, KC.NGG, KC.NGP         }, [ KC.D, KC.Y, KC.U         ]), # ぢゅ
    ({ KC.NGJ, KC.NGG, KC.NGI         }, [ KC.D, KC.Y, KC.O         ]), # ぢょ
    ({ KC.NGD, KC.NGH                 }, [ KC.N, KC.Y, KC.A         ]), # にゃ
    ({ KC.NGD, KC.NGP                 }, [ KC.N, KC.Y, KC.U         ]), # にゅ
    ({ KC.NGD, KC.NGI                 }, [ KC.N, KC.Y, KC.O         ]), # にょ
    ({ KC.NGX, KC.NGH                 }, [ KC.H, KC.Y, KC.A         ]), # ひゃ
    ({ KC.NGX, KC.NGP                 }, [ KC.H, KC.Y, KC.U         ]), # ひゅ
    ({ KC.NGX, KC.NGI                 }, [ KC.H, KC.Y, KC.O         ]), # ひょ
    ({ KC.NGJ, KC.NGX, KC.NGH         }, [ KC.B, KC.Y, KC.A         ]), # びゃ
    ({ KC.NGJ, KC.NGX, KC.NGP         }, [ KC.B, KC.Y, KC.U         ]), # びゅ
    ({ KC.NGJ, KC.NGX, KC.NGI         }, [ KC.B, KC.Y, KC.O         ]), # びょ
    ({ KC.NGM, KC.NGX, KC.NGH         }, [ KC.P, KC.Y, KC.A         ]), # ぴゃ
    ({ KC.NGM, KC.NGX, KC.NGP         }, [ KC.P, KC.Y, KC.U         ]), # ぴゅ
    ({ KC.NGM, KC.NGX, KC.NGI         }, [ KC.P, KC.Y, KC.O         ]), # ぴょ
    ({ KC.NGB, KC.NGH                 }, [ KC.M, KC.Y, KC.A         ]), # みゃ
    ({ KC.NGB, KC.NGP                 }, [ KC.M, KC.Y, KC.U         ]), # みゅ
    ({ KC.NGB, KC.NGI                 }, [ KC.M, KC.Y, KC.O         ]), # みょ
    ({ KC.NGE, KC.NGH                 }, [ KC.R, KC.Y, KC.A         ]), # りゃ
    ({ KC.NGE, KC.NGP                 }, [ KC.R, KC.Y, KC.U         ]), # りゅ
    ({ KC.NGE, KC.NGI                 }, [ KC.R, KC.Y, KC.O         ]), # りょ
    ({ KC.NGM, KC.NGE, KC.NGK         }, [ KC.S, KC.Y, KC.A         ]), # てぃ
    ({ KC.NGM, KC.NGE, KC.NGP         }, [ KC.S, KC.Y, KC.U         ]), # てゅ
    ({ KC.NGJ, KC.NGE, KC.NGK         }, [ KC.S, KC.Y, KC.O         ]), # でぃ
    ({ KC.NGJ, KC.NGE, KC.NGP         }, [ KC.Z, KC.Y, KC.A         ]), # でゅ
    ({ KC.NGM, KC.NGD, KC.NGL         }, [ KC.Z, KC.Y, KC.U         ]), # とぅ
    ({ KC.NGJ, KC.NGD, KC.NGL         }, [ KC.Z, KC.Y, KC.O         ]), # どぅ
    ({ KC.NGM, KC.NGR, KC.NGO         }, [ KC.K, KC.Y, KC.A         ]), # しぇ
    ({ KC.NGM, KC.NGG, KC.NGO         }, [ KC.K, KC.Y, KC.U         ]), # ちぇ
    ({ KC.NGJ, KC.NGR, KC.NGO         }, [ KC.K, KC.Y, KC.O         ]), # じぇ
    ({ KC.NGJ, KC.NGG, KC.NGO         }, [ KC.G, KC.Y, KC.A         ]), # ぢぇ
    ({ KC.NGV, KC.NGSCLN, KC.NGJ      }, [ KC.G, KC.Y, KC.U         ]), # ふぁ
    ({ KC.NGV, KC.NGSCLN, KC.NGK      }, [ KC.G, KC.Y, KC.O         ]), # ふぃ
    ({ KC.NGV, KC.NGSCLN, KC.NGO      }, [ KC.T, KC.Y, KC.A         ]), # ふぇ
    ({ KC.NGV, KC.NGSCLN, KC.NGN      }, [ KC.T, KC.Y, KC.U         ]), # ふぉ
    ({ KC.NGV, KC.NGSCLN, KC.NGP      }, [ KC.T, KC.Y, KC.O         ]), # ふゅ
    ({ KC.NGV, KC.NGK, KC.NGO         }, [ KC.D, KC.Y, KC.A         ]), # いぇ
    ({ KC.NGV, KC.NGL, KC.NGK         }, [ KC.D, KC.Y, KC.U         ]), # うぃ
    ({ KC.NGV, KC.NGL, KC.NGO         }, [ KC.D, KC.Y, KC.O         ]), # うぇ
    ({ KC.NGV, KC.NGL, KC.NGN         }, [ KC.N, KC.Y, KC.A         ]), # うぉ
    ({ KC.NGM, KC.NGQ, KC.NGJ         }, [ KC.N, KC.Y, KC.U         ]), # ゔぁ
    ({ KC.NGM, KC.NGQ, KC.NGK         }, [ KC.N, KC.Y, KC.O         ]), # ゔぃ
    ({ KC.NGM, KC.NGQ, KC.NGO         }, [ KC.H, KC.Y, KC.A         ]), # ゔぇ
    ({ KC.NGM, KC.NGQ, KC.NGN         }, [ KC.H, KC.Y, KC.U         ]), # ゔぉ
    ({ KC.NGM, KC.NGQ, KC.NGP         }, [ KC.H, KC.Y, KC.O         ]), # ゔゅ
    ({ KC.NGV, KC.NGH, KC.NGJ         }, [ KC.B, KC.Y, KC.A         ]), # くぁ
    ({ KC.NGV, KC.NGH, KC.NGK         }, [ KC.B, KC.Y, KC.U         ]), # くぃ
    ({ KC.NGV, KC.NGH, KC.NGO         }, [ KC.B, KC.Y, KC.O         ]), # くぇ
    ({ KC.NGV, KC.NGH, KC.NGN         }, [ KC.P, KC.Y, KC.A         ]), # くぉ
    ({ KC.NGV, KC.NGH, KC.NGDOT       }, [ KC.P, KC.Y, KC.U         ]), # くゎ
    ({ KC.NGF, KC.NGH, KC.NGJ         }, [ KC.P, KC.Y, KC.O         ]), # ぐぁ
    ({ KC.NGF, KC.NGH, KC.NGK         }, [ KC.M, KC.Y, KC.A         ]), # ぐぃ
    ({ KC.NGF, KC.NGH, KC.NGO         }, [ KC.M, KC.Y, KC.U         ]), # ぐぇ
    ({ KC.NGF, KC.NGH, KC.NGN         }, [ KC.M, KC.Y, KC.O         ]), # ぐぉ
    ({ KC.NGF, KC.NGH, KC.NGDOT       }, [ KC.R, KC.Y, KC.A         ]), # ぐゎ
    ({ KC.NGV, KC.NGL, KC.NGJ         }, [ KC.R, KC.Y, KC.U         ]), # つぁ


]
