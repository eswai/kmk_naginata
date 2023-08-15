# Vpico KMK薙刀式

print("Starting")

import board
import supervisor

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.keys import make_key
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.handlers.sequences import send_string
from kmk.handlers.sequences import simple_key_sequence
from kmk.modules.combos import Combos, Chord, Sequence
from kmk.modules.holdtap import HoldTap

keyboard = KMKKeyboard()
# keyboard.debug_enabled = True

keyboard.col_pins = (board.GP15, board.GP14, board.GP13, board.GP12, board.GP11, board.GP20, board.GP19, board.GP18, board.GP17, board.GP16,)
keyboard.row_pins = (board.GP7, board.GP8, board.GP9, board.GP10,)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

combos = Combos()
keyboard.modules.append(combos)

holdtap = HoldTap()
holdtap.tap_time = 100
keyboard.modules.append(holdtap)

layers = Layers()
keyboard.modules.append(layers)
layers.combo_layers = {
    (2, 3): 4,
}

LOWER = KC.MO(2)
RAISE = KC.MO(3)
SSPC = KC.HT(KC.SPC, KC.LSFT)
SENT = KC.HT(KC.ENTER, KC.LSFT)
NGTG = KC.TG(1)

pressed_keys = 0
nginput = []
max_keys = 5
shift_keys = [KC.NGSFT, KC.NGSFT2, KC.NGF, KC.NGV, KC.NGJ, KC.NGM]
now = 0

class KeyAction:
    def __init__(self, keycode, press_at, release_at):
        self.keycode = keycode
        self.press_at = press_at
        self.release_at = release_at
    
    def keycode_s(self):
        return self.keycode if self.keycode != KC.NGSFT2 else KC.NGSFT
    
    def release_at_t(self, t):
        return self.release_at if self.release_at > 0 else t

    def is_shift(self):
        return self.keycode in shift_keys

#　かな変換の処理
def ng_press(*args, **kwargs):
    global pressed_keys, now
    now = supervisor.ticks_ms()
    kc = args[0]
    pressed_keys += 1

    # オーバーフロー
    if pressed_keys > max_keys or len(nginput) >= max_keys:
        s = ng_type(True)
        t = False
        # 連続シフトの引き継ぎ
        for ka in nginput[0:s]:
            if ka.is_shift and ka.release_at == 0:
                if s < len(nginput):
                    ka.press_at = nginput[s].press_at
                else:
                    ka.press_at = now
                t = ka
                break
        del nginput[0:s]
        if t:
            nginput.insert(0, t)

    nginput.append(KeyAction(kc, now, 0))
    return False

def ng_release(*args, **kwargs):
    global pressed_keys, now
    now = supervisor.ticks_ms()
    kc = args[0]
    if pressed_keys > 0:
        pressed_keys -= 1
    
    # リリース時間保存
    for ka in nginput:
        if ka.keycode == kc and ka.release_at == 0:
            ka.release_at = now
            break

    # かな変換し出力
    if pressed_keys == 0 and len(nginput) > 0:
        ng_type()
        nginput.clear()

    return False

def ng_type(partial = False):
    # partial nginputの全部を出力するか、最初だけ出力するか
    if len(nginput) == 1 and nginput[0].keycode == KC.NGSFT2:
        keyboard.tap_key(KC.ENT)
        return 1

    # キーの組合せから、辞書にあるものだけを抜き出す
    lllka = [] # list(list(list(KeyAction)))
    l = min([len(nginput), 5]) # ガード
    for lindex in ngcomb[l]: # list(list(num))
        llka = [] # list(list(KeyAction))
        is_exist = True
        for cindex in lindex: # list(num)
            lka = [] # list(KeyAction)
            for i in cindex: # num
                lka.append(nginput[i])
            skc = set(map(lambda x: x.keycode_s(), lka))
            for k in ngdic: # (set(KC), list(KC))
                if k[0] == skc:
                    break
            else:
                is_exist = False
                break
            llka.append(lka)
        if is_exist:
            lllka.append(llka)
    
    # 組み合わせの点数づけをして、点数の高い組合せを選ぶ
    best_score = 0
    best_comb = [] # list(list(KeyAction))
    for c in lllka:
        s = scoring(c)
        if s >= best_score:
            best_comb = c
            best_score = s

    if partial:
        bc = best_comb[0:1] # 最初の組合せだけ変換する
    else:
        bc = best_comb

    # かなに変換する
    keyseq = []
    ks = set() # 削除するキーセット
    for k in bc:
        s = set(map(lambda x: x.keycode_s(), k))
        for ka in k:
            ks.add(ka)
        for l in ngdic:
            if l[0] == s:
                keyseq += l[1]
                break

    kcs = simple_key_sequence(keyseq)
    keyboard.tap_key(kcs)

    # 何キー処理したが返す
    return len(ks)

def scoring(comb): #list(list(KeyAction))
    score = 0
    for lka in comb: # list(KeyAction)
        if len(lka) == 1:
            score += 100
        else:
            latest_press = max(map(lambda x: x.press_at, lka))
            earliest_release = min(map(lambda x: x.release_at_t(now), lka))
            overlap = earliest_release - latest_press
            for ka in lka:
                score += overlap * 1000 / (ka.release_at_t(now) - ka.press_at)
    
    return score / len(comb)
        

def naginata_on(*args, **kwargs):
    layers.activate_layer(keyboard, 1)
    nginput.clear()
    keyboard.tap_key(KC.LANG1)
    keyboard.tap_key(KC.INT4)
    return False

def naginata_off(*args, **kwargs):
    layers.deactivate_layer(keyboard, 1)
    nginput.clear()
    keyboard.tap_key(KC.LANG2)
    keyboard.tap_key(KC.INT5)
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

combos.combos = [
    Chord((KC.H  , KC.J  ), KC.NGON , timeout = 100, per_key_timeout = False, fast_reset = True),
    Chord((KC.NGF, KC.NGG), KC.NGOFF, timeout = 100, per_key_timeout = False, fast_reset = True),
]

# かな変換テーブル setはdictionaryのキーにできないので配列に
ngdic = [
    ({KC.NGU                          }, [KC.BSPC                       ]),
    ({KC.NGSFT                        }, [KC.SPC                        ]),
    ({KC.NGM   , KC.NGV               }, [KC.ENT                        ]),

    # 出現頻度順
    ({KC.NGK                          }, [KC.I                          ]), # い
    ({KC.NGL                          }, [KC.U                          ]), # う
    ({KC.NGCOMM                       }, [KC.N, KC.N                    ]), # ん
    ({KC.NGF                          }, [KC.K, KC.A                    ]), # か
    ({KC.NGSFT , KC.NGJ               }, [KC.N, KC.O                    ]), # の
    ({KC.NGD                          }, [KC.T, KC.O                    ]), # と
    ({KC.NGR                          }, [KC.S, KC.I                    ]), # し
    ({KC.NGN                          }, [KC.T, KC.A                    ]), # た
    ({KC.NGSFT , KC.NGV               }, [KC.COMM, KC.ENT               ]), #  、
    ({KC.NGH                          }, [KC.K, KC.U                    ]), # く
    ({KC.NGM                          }, [KC.N, KC.A                    ]), # な
    ({KC.NGE                          }, [KC.T, KC.E                    ]), # て
    ({KC.NGSFT , KC.NGD               }, [KC.N, KC.I                    ]), # に
    ({KC.NGC                          }, [KC.H, KC.A                    ]), # は
    ({KC.NGV                          }, [KC.K, KC.O                    ]), # こ
    ({KC.NGI                          }, [KC.R, KC.U                    ]), # る
    ({KC.NGSFT , KC.NGM               }, [KC.DOT,  KC.ENT               ]), # 。
    ({KC.NGJ   , KC.NGF               }, [KC.G, KC.A                    ]), # が
    ({KC.NGJ   , KC.NGE               }, [KC.D, KC.E                    ]), # で
    ({KC.NGG                          }, [KC.X, KC.T, KC.U              ]), # っ
    ({KC.NGO                          }, [KC.S, KC.U                    ]), # す
    ({KC.NGW                          }, [KC.K, KC.I                    ]), # き
    ({KC.NGSFT , KC.NGF               }, [KC.M, KC.A                    ]), # ま
    ({KC.NGSFT , KC.NGK               }, [KC.M, KC.O                    ]), # も
    ({KC.NGSFT , KC.NGL               }, [KC.T, KC.U                    ]), # つ
    ({KC.NGSFT , KC.NGN               }, [KC.O                          ]), # お
    ({KC.NGDOT                        }, [KC.R, KC.A                    ]), # ら
    ({KC.NGSFT , KC.NGC               }, [KC.W, KC.O                    ]), # を
    ({KC.NGSFT , KC.NGU               }, [KC.S, KC.A                    ]), # さ
    ({KC.NGJ                          }, [KC.A                          ]), # あ
    ({KC.NGSFT , KC.NGE               }, [KC.R, KC.I                    ]), # り
    ({KC.NGSLSH                       }, [KC.R, KC.E                    ]), # れ
    ({KC.NGSFT , KC.NGSLSH            }, [KC.R, KC.E                    ]), # れ
    ({KC.NGF   , KC.NGN               }, [KC.D, KC.A                    ]), # だ
    ({KC.NGSFT , KC.NGA               }, [KC.S, KC.E                    ]), # せ
    ({KC.NGS                          }, [KC.K, KC.E                    ]), # け
    ({KC.NGJ   , KC.NGR               }, [KC.Z, KC.I                    ]), # じ
    ({KC.NGSCLN                       }, [KC.MINS                       ]), # ー
    ({KC.NGSFT , KC.NGI               }, [KC.Y, KC.O                    ]), # よ
    ({KC.NGJ   , KC.NGD               }, [KC.D, KC.O                    ]), # ど
    ({KC.NGB                          }, [KC.S, KC.O                    ]), # そ
    ({KC.NGSFT , KC.NGO               }, [KC.E                          ]), # え
    ({KC.NGSFT , KC.NGDOT             }, [KC.W, KC.A                    ]), # わ
    ({KC.NGSFT , KC.NGG               }, [KC.T, KC.I                    ]), # ち
    ({KC.NGSFT , KC.NGB               }, [KC.M, KC.I                    ]), # み
    ({KC.NGSFT , KC.NGS               }, [KC.M, KC.E                    ]), # め
    ({KC.NGJ   , KC.NGC               }, [KC.B, KC.A                    ]), # ば
    ({KC.NGSFT , KC.NGH               }, [KC.Y, KC.A                    ]), # や
    ({KC.NGX                          }, [KC.H, KC.I                    ]), # ひ
    ({KC.NGSFT , KC.NGX               }, [KC.H, KC.I                    ]), # ひ
    ({KC.NGA                          }, [KC.R, KC.O                    ]), # ろ
    ({KC.NGZ                          }, [KC.H, KC.O                    ]), # ほ
    ({KC.NGSFT , KC.NGZ               }, [KC.H, KC.O                    ]), # ほ
    ({KC.NGR   , KC.NGI               }, [KC.S, KC.Y, KC.O              ]), # しょ
    ({KC.NGF   , KC.NGSCLN            }, [KC.B, KC.U                    ]), # ぶ
    ({KC.NGSFT , KC.NGSCLN            }, [KC.H, KC.U                    ]), # ふ
    ({KC.NGSFT , KC.NGR               }, [KC.N, KC.E                    ]), # ね
    ({KC.NGJ   , KC.NGV               }, [KC.G, KC.O                    ]), # ご
    ({KC.NGJ   , KC.NGR   , KC.NGI    }, [KC.Z, KC.Y, KC.O              ]), # じょ
    ({KC.NGJ   , KC.NGS               }, [KC.G, KC.E                    ]), # げ
    ({KC.NGR   , KC.NGP               }, [KC.S, KC.Y, KC.U              ]), # しゅ
    ({KC.NGSFT , KC.NGCOMM            }, [KC.M, KC.U                    ]), # む
    ({KC.NGW   , KC.NGI               }, [KC.K, KC.Y, KC.O              ]), # きょ
    ({KC.NGF   , KC.NGO               }, [KC.Z, KC.U                    ]), # ず
    ({KC.NGJ   , KC.NGW               }, [KC.G, KC.I                    ]), # ぎ
    ({KC.NGR   , KC.NGH               }, [KC.S, KC.Y, KC.A              ]), # しゃ
    ({KC.NGG   , KC.NGI               }, [KC.T, KC.Y, KC.O              ]), # ちょ
    ({KC.NGJ   , KC.NGX               }, [KC.B, KC.I                    ]), # び
    ({KC.NGF   , KC.NGU               }, [KC.Z, KC.A                    ]), # ざ
    ({KC.NGF   , KC.NGH               }, [KC.G, KC.U                    ]), # ぐ
    ({KC.NGJ   , KC.NGA               }, [KC.Z, KC.E                    ]), # ぜ
    ({KC.NGP                          }, [KC.H, KC.E                    ]), # へ
    ({KC.NGF   , KC.NGP               }, [KC.B, KC.E                    ]), # べ
    ({KC.NGSFT , KC.NGP               }, [KC.Y, KC.U                    ]), # ゆ
    ({KC.NGJ   , KC.NGR   , KC.NGP    }, [KC.Z, KC.Y, KC.U              ]), # じゅ
    ({KC.NGJ   , KC.NGZ               }, [KC.B, KC.O                    ]), # ぼ
    ({KC.NGV   , KC.NGSCLN            }, [KC.P, KC.U                    ]), # ぷ
    ({KC.NGE   , KC.NGI               }, [KC.R, KC.Y, KC.O              ]), # りょ
    ({KC.NGJ   , KC.NGB               }, [KC.Z, KC.O                    ]), # ぞ
    ({KC.NGM   , KC.NGC               }, [KC.P, KC.A                    ]), # ぱ
    ({KC.NGW   , KC.NGP               }, [KC.K, KC.Y, KC.U              ]), # きゅ
    ({KC.NGG   , KC.NGP               }, [KC.T, KC.Y, KC.U              ]), # ちゅ
    ({KC.NGJ   , KC.NGW   , KC.NGI    }, [KC.G, KC.Y, KC.O              ]), # ぎょ
    ({KC.NGM   , KC.NGZ               }, [KC.P, KC.O                    ]), # ぽ
    ({KC.NGD   , KC.NGP               }, [KC.N, KC.Y, KC.U              ]), # にゅ
    ({KC.NGX   , KC.NGI               }, [KC.H, KC.Y, KC.O              ]), # ひょ
    ({KC.NGF   , KC.NGL               }, [KC.D, KC.U                    ]), # づ
    ({KC.NGJ   , KC.NGR   , KC.NGH    }, [KC.Z, KC.Y, KC.A              ]), # じゃ
    ({KC.NGG   , KC.NGH               }, [KC.T, KC.Y, KC.A              ]), # ちゃ
    ({KC.NGSFT , KC.NGW               }, [KC.N, KC.U                    ]), # ぬ
    ({KC.NGM   , KC.NGE   , KC.NGK    }, [KC.T, KC.H, KC.I              ]), # てぃ
    ({KC.NGM   , KC.NGX               }, [KC.P, KC.I                    ]), # ぴ
    ({KC.NGE   , KC.NGP               }, [KC.R, KC.Y, KC.U              ]), # りゅ
    ({KC.NGV   , KC.NGP               }, [KC.P, KC.E                    ]), # ぺ
    ({KC.NGW   , KC.NGH               }, [KC.K, KC.Y, KC.A              ]), # きゃ
    ({KC.NGV   , KC.NGSCLN, KC.NGJ    }, [KC.F, KC.A                    ]), # ふぁ
    ({KC.NGJ   , KC.NGE   , KC.NGK    }, [KC.D, KC.H, KC.I              ]), # でぃ
    ({KC.NGQ   , KC.NGJ               }, [KC.X, KC.A                    ]), # ぁ
    ({KC.NGM   , KC.NGR   , KC.NGO    }, [KC.S, KC.Y, KC.E              ]), # しぇ
    ({KC.NGJ   , KC.NGX   , KC.NGI    }, [KC.B, KC.Y, KC.O              ]), # びょ
    ({KC.NGE   , KC.NGH               }, [KC.R, KC.Y, KC.A              ]), # りゃ
    ({KC.NGV   , KC.NGSCLN, KC.NGK    }, [KC.F, KC.I                    ]), # ふぃ
    ({KC.NGM   , KC.NGG   , KC.NGO    }, [KC.T, KC.Y, KC.E              ]), # ちぇ
    ({KC.NGJ   , KC.NGW   , KC.NGH    }, [KC.G, KC.Y, KC.A              ]), # ぎゃ
    ({KC.NGV   , KC.NGL   , KC.NGO    }, [KC.W, KC.E                    ]), # うぇ
    ({KC.NGQ   , KC.NGK               }, [KC.X, KC.I                    ]), # ぃ
    ({KC.NGV   , KC.NGSCLN, KC.NGO    }, [KC.F, KC.E                    ]), # ふぇ
    ({KC.NGM   , KC.NGX   , KC.NGI    }, [KC.P, KC.Y, KC.O              ]), # ぴょ
    ({KC.NGM   , KC.NGX   , KC.NGP    }, [KC.P, KC.Y, KC.U              ]), # ぴゅ
    ({KC.NGJ   , KC.NGR   , KC.NGO    }, [KC.Z, KC.Y, KC.E              ]), # じぇ
    ({KC.NGV   , KC.NGSCLN, KC.NGN    }, [KC.F, KC.O                    ]), # ふぉ
    ({KC.NGQ   , KC.NGO               }, [KC.X, KC.E                    ]), # ぇ
    ({KC.NGQ                          }, [KC.V, KC.U                    ]), # ゔ
    ({KC.NGSFT , KC.NGQ               }, [KC.V, KC.U                    ]), # ゔ
    ({KC.NGJ   , KC.NGX   , KC.NGP    }, [KC.B, KC.Y, KC.U              ]), # びゅ
    ({KC.NGJ   , KC.NGG               }, [KC.D, KC.I                    ]), # ぢ
    ({KC.NGB   , KC.NGI               }, [KC.M, KC.Y, KC.O              ]), # みょ
    ({KC.NGX   , KC.NGH               }, [KC.H, KC.Y, KC.A              ]), # ひゃ
    ({KC.NGB   , KC.NGP               }, [KC.M, KC.Y, KC.U              ]), # みゅ
    ({KC.NGJ   , KC.NGW   , KC.NGP    }, [KC.G, KC.Y, KC.U              ]), # ぎゅ
    ({KC.NGQ   , KC.NGN               }, [KC.X, KC.O                    ]), # ぉ
    ({KC.NGM   , KC.NGQ   , KC.NGJ    }, [KC.V, KC.A                    ]), # ゔぁ
    ({KC.NGV   , KC.NGL   , KC.NGK    }, [KC.W, KC.I                    ]), # うぃ
    ({KC.NGD   , KC.NGI               }, [KC.N, KC.Y, KC.O              ]), # にょ
    ({KC.NGQ   , KC.NGL               }, [KC.X, KC.U                    ]), # ぅ
    ({KC.NGQ   , KC.NGP               }, [KC.X, KC.Y, KC.U              ]), # ゅ
    ({KC.NGJ   , KC.NGE   , KC.NGP    }, [KC.D, KC.H, KC.U              ]), # でゅ
    ({KC.NGB   , KC.NGH               }, [KC.M, KC.Y, KC.A              ]), # みゃ
    ({KC.NGD   , KC.NGH               }, [KC.N, KC.Y, KC.A              ]), # にゃ
    ({KC.NGV   , KC.NGL   , KC.NGN    }, [KC.U, KC.X, KC.O              ]), # うぉ
    ({KC.NGM   , KC.NGD   , KC.NGL    }, [KC.T, KC.O, KC.X, KC.U        ]), # とぅ
    ({KC.NGV   , KC.NGH   , KC.NGN    }, [KC.K, KC.U, KC.X, KC.O        ]), # くぉ
    ({KC.NGX   , KC.NGP               }, [KC.H, KC.Y, KC.U              ]), # ひゅ
    ({KC.NGJ   , KC.NGD   , KC.NGL    }, [KC.D, KC.O, KC.X, KC.U        ]), # どぅ
    ({KC.NGM   , KC.NGQ   , KC.NGK    }, [KC.V, KC.I                    ]), # ゔぃ
    ({KC.NGM   , KC.NGQ   , KC.NGO    }, [KC.V, KC.E                    ]), # ゔぇ
    ({KC.NGM   , KC.NGX   , KC.NGH    }, [KC.P, KC.Y, KC.A              ]), # ぴゃ
    ({KC.NGJ   , KC.NGX   , KC.NGH    }, [KC.B, KC.Y, KC.A              ]), # びゃ
    ({KC.NGV   , KC.NGL   , KC.NGJ    }, [KC.T, KC.S, KC.A              ]), # つぁ
    ({KC.NGV   , KC.NGSCLN, KC.NGP    }, [KC.F, KC.Y, KC.U              ]), # ふゅ
    ({KC.NGQ   , KC.NGI               }, [KC.X, KC.Y, KC.O              ]), # ょ
    ({KC.NGQ   , KC.NGH               }, [KC.X, KC.Y, KC.A              ]), # ゃ
    ({KC.NGM   , KC.NGQ   , KC.NGN    }, [KC.V, KC.O                    ]), # ゔぉ
    ({KC.NGJ   , KC.NGG   , KC.NGH    }, [KC.D, KC.Y, KC.A              ]), # ぢゃ
    ({KC.NGQ   , KC.NGDOT             }, [KC.X, KC.W, KC.A              ]), # ゎ

    # 統計にない
    ({KC.NGQ   , KC.NGS               }, [KC.X, KC.K, KC.E              ]), # ヶ
    ({KC.NGQ   , KC.NGF               }, [KC.X, KC.K, KC.A              ]), # ヵ
    ({KC.NGJ   , KC.NGG   , KC.NGP    }, [KC.D, KC.Y, KC.U              ]), # ぢゅ
    ({KC.NGJ   , KC.NGG   , KC.NGI    }, [KC.D, KC.Y, KC.O              ]), # ぢょ
    ({KC.NGM   , KC.NGE   , KC.NGP    }, [KC.T, KC.H, KC.U              ]), # てゅ
    ({KC.NGJ   , KC.NGG   , KC.NGO    }, [KC.D, KC.Y, KC.E              ]), # ぢぇ
    ({KC.NGV   , KC.NGK   , KC.NGO    }, [KC.I, KC.X, KC.E              ]), # いぇ
    ({KC.NGM   , KC.NGQ   , KC.NGP    }, [KC.V, KC.U, KC.X, KC.Y, KC.U  ]), # ゔゅ
    ({KC.NGV   , KC.NGH   , KC.NGJ    }, [KC.K, KC.U, KC.X, KC.A        ]), # くぁ
    ({KC.NGV   , KC.NGH   , KC.NGK    }, [KC.K, KC.U, KC.X, KC.I        ]), # くぃ
    ({KC.NGV   , KC.NGH   , KC.NGO    }, [KC.K, KC.U, KC.X, KC.E        ]), # くぇ
    ({KC.NGV   , KC.NGH   , KC.NGDOT  }, [KC.K, KC.U, KC.X, KC.W, KC.A  ]), # くゎ
    ({KC.NGF   , KC.NGH   , KC.NGJ    }, [KC.G, KC.U, KC.X, KC.A        ]), # ぐぁ
    ({KC.NGF   , KC.NGH   , KC.NGK    }, [KC.G, KC.U, KC.X, KC.I        ]), # ぐぃ
    ({KC.NGF   , KC.NGH   , KC.NGO    }, [KC.G, KC.U, KC.X, KC.E        ]), # ぐぇ
    ({KC.NGF   , KC.NGH   , KC.NGN    }, [KC.G, KC.U, KC.X, KC.O        ]), # ぐぉ
    ({KC.NGF   , KC.NGH   , KC.NGDOT  }, [KC.G, KC.U, KC.X, KC.W, KC.A  ]), # ぐゎ

    ({KC.NGT                          }, [KC.LEFT                       ]),
    ({KC.NGY                          }, [KC.RIGHT                      ]),
    ({KC.NGSFT , KC.NGT               }, [KC.LSFT(KC.LEFT)              ]),
    ({KC.NGSFT , KC.NGY               }, [KC.LSFT(KC.RIGHT)             ]),
]

ngcomb = {
    1: [ # 1キー
        [[0      ]], # 0
    ],
    2: [ # 2キー
        [[0      ], [1      ]], # 0 1
        [[0, 1   ]           ], # 01
    ],
    3: [ # 3キー
        # 連続シフトなし
        [[0      ], [1      ], [2      ]], # 0   1   2
        [[0, 1   ], [2      ]           ], # 01  2
        [[0      ], [1, 2   ]           ], # 0   12
        [[0, 1, 2]                      ], # 012
        # 連続シフトあり
        [[0, 1   ], [0, 2   ]           ], # 01  02 : 0が連続シフト
        [[0, 1   ], [1, 2   ]           ], # 01  12 : 1が連続シフト
    ],
    4: [ # 4キー
        # 連続シフトなし
        [[0      ], [1      ], [2      ], [3      ]], # 0   1   2   3
        [[0, 1   ], [2      ], [3      ]           ], # 01  2   3
        [[0      ], [1, 2   ], [3      ]           ], # 0   12  3
        [[0      ], [1      ], [2, 3   ]           ], # 0   1   23
        [[0, 1, 2], [3      ]                      ], # 012 3
        [[0, 1   ], [2, 3   ]                      ], # 01  23
        [[0      ], [1, 2, 3]                      ], # 0   123
        # 0の連続シフト
        [[0, 1   ], [0, 2   ], [0, 3   ]           ], # 01  02  03
        [[0, 1   ], [0, 2   ], [3      ]           ], # 01  02  3
        [[0, 1, 2], [0, 3   ]                      ], # 012 03
        [[0, 1   ], [0, 2, 3]                      ], # 01  023
        # 1の連続シフト
        [[0, 1   ], [1, 2   ], [3      ]           ], # 01  12  3
        [[0, 1   ], [1, 2   ], [1, 3   ]           ], # 01  12  13
        [[0      ], [1, 2   ], [1, 3   ]           ], # 0   12  13
        [[0, 1   ], [1, 2, 3]                      ], # 01  123
        [[0, 1, 2], [1, 3   ]                      ], # 012 13
        # 2の連続シフト
        [[0      ], [1, 2   ], [2, 3   ]           ], # 0   12  23
        [[0, 1, 2], [2, 3   ]                      ], # 012 23
    ],
    5: [ # 5キー
        # 5分割 連続シフトなし
        [[0      ], [1      ], [2      ], [3      ], [4      ]], # 0 1 2 3 4
        # 4分割 連続シフトなし
        [[0, 1   ], [2      ], [3      ], [4      ]           ], # 01  2   3   4
        [[0      ], [1, 2   ], [3      ], [4      ]           ], # 0   12  3   4
        [[0      ], [1      ], [2, 3   ], [4      ]           ], # 0   1   23  4
        [[0      ], [1      ], [2      ], [3, 4   ]           ], # 0   1   2   34
        # 3分割 連続シフトなし
        [[0, 1, 2], [3      ], [4      ]                      ], # 012 3   4
        [[0      ], [1, 2, 3], [4      ]                      ], # 0   123 4
        [[0      ], [1      ], [2, 3, 4]                      ], # 0   1   234
        [[0, 1   ], [2, 3   ], [4      ]                      ], # 01  23  4
        [[0      ], [1, 2   ], [3, 4   ]                      ], # 0   12  34
        [[0, 1   ], [2      ], [3, 4   ]                      ], # 01  2   34
        # 2分割 連続シフトなし
        [[0, 1, 2], [3, 4   ]                                 ], # 012 34
        [[0, 1   ], [2, 3, 4]                                 ], # 01  234
        # 0の連続シフト
        [[0, 1   ], [0, 2   ], [3      ], [4      ]           ], # 01  02  3   4 : 2キー同時
        [[0, 1   ], [0, 2   ], [0, 3   ], [4      ]           ], # 01  02  03  4
        [[0, 1   ], [0, 2   ], [0, 3   ], [0, 4   ]           ], # 01  02  03  04
        [[0, 1, 2], [0, 3, 4]                                 ], # 012 034 : 3キー同時
        [[0, 1   ], [0, 2, 3], [4      ]                      ], # 01  023 4
        [[0, 1   ], [0, 2, 3], [0, 4   ]                      ], # 01  023 04
        [[0, 1   ], [0, 2   ], [0, 3, 4]                      ], # 01  02  034
        # 1の連続シフト
        [[0, 1   ], [1, 2   ], [3      ], [4      ]           ], # 01  12  3   4 : 2キー同時
        [[0, 1   ], [1, 2   ], [1, 3   ], [4      ]           ], # 01  12  13  4
        [[0, 1   ], [1, 2   ], [1, 3   ], [1, 4   ]           ], # 01  12  13  14
        [[0      ], [1, 2   ], [1, 3   ], [4      ]           ], # 0   12  13  4
        [[0      ], [1, 2   ], [1, 3   ], [1, 4   ]           ], # 0   12  13  14
        [[0, 1, 2], [1, 3, 4]                                 ], # 012 134 : 3キー同時
        [[0, 1, 2], [1, 3   ], [4      ]                      ], # 012 13  4
        [[0      ], [1, 2, 3], [1, 4   ]                      ], # 0   123 14
        [[0      ], [1, 2   ], [1, 3, 4]                      ], # 0   12  134
        # 2の連続シフト
        [[0      ], [1, 2   ], [2, 3   ], [4      ]           ], # 0   12  23 4 : 2キー同時
        [[0      ], [1      ], [2, 3   ], [2, 4   ]           ], # 0   1   23 24
        [[0, 1, 2], [2, 3, 4]                                 ], # 012 234 : 3キー同時
        [[0      ], [1, 2   ], [2, 3, 4]                      ], # 0   12  234
        [[0      ], [1, 2, 3], [2, 4   ]                      ], # 0   123 24
        # 3の連続シフト
        [[0      ], [1      ], [2, 3   ], [3, 4   ]           ], # 0   1   23  34 : 2キー
        [[0      ], [1, 2, 3], [3, 4   ]                      ], # 0   123 34 : 3キー同時
    ],
}

keyboard.keymap = [
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.Q     ,KC.W     ,KC.E     ,KC.R     ,KC.T     ,KC.Y     ,KC.U     ,KC.I     ,KC.O     ,KC.P     ,
        KC.A     ,KC.S     ,KC.D     ,KC.F     ,KC.G     ,KC.H     ,KC.J     ,KC.K     ,KC.L     ,KC.SCLN  ,
        KC.Z     ,KC.X     ,KC.C     ,KC.V     ,KC.B     ,KC.N     ,KC.M     ,KC.COMM  ,KC.DOT   ,KC.SLSH  ,
        KC.LCTL  ,KC.LSFT  ,KC.LGUI  ,LOWER    ,SSPC     ,SENT     ,RAISE    ,KC.RCTRL ,KC.NGON  ,KC.NGOFF ,
    ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.NGQ   ,KC.NGW   ,KC.NGE   ,KC.NGR   ,KC.NGT   ,KC.NGY   ,KC.NGU   ,KC.NGI   ,KC.NGO   ,KC.NGP   ,
        KC.NGA   ,KC.NGS   ,KC.NGD   ,KC.NGF   ,KC.NGG   ,KC.NGH   ,KC.NGJ   ,KC.NGK   ,KC.NGL   ,KC.NGSCLN,
        KC.NGZ   ,KC.NGX   ,KC.NGC   ,KC.NGV   ,KC.NGB   ,KC.NGN   ,KC.NGM   ,KC.NGCOMM,KC.NGDOT ,KC.NGSLSH,
        KC.LCTL  ,KC.LSFT  ,KC.LGUI  ,LOWER    ,KC.NGSFT ,KC.NGSFT2,RAISE    ,KC.RCTRL ,KC.NGON  ,KC.NGOFF ,
    ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.TAB   ,KC.COLN  ,KC.SCLN  ,KC.DQT   ,KC.QUOT  ,KC.SLSH  ,KC.N7    ,KC.N8    ,KC.N9    ,KC.MINS  ,
        KC.ESC   ,KC.LBRC  ,KC.LCBR  ,KC.LPRN  ,KC.NO    ,KC.ASTR  ,KC.N4    ,KC.N5    ,KC.N6    ,KC.PLUS  ,
        KC.NO    ,KC.RBRC  ,KC.RCBR  ,KC.RPRN  ,KC.NO    ,KC.N0    ,KC.N1    ,KC.N2    ,KC.N3    ,KC.EQL   ,
        KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,
    ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.TILD  ,KC.AT    ,KC.HASH  ,KC.DLR   ,KC.NO    ,KC.NO    ,KC.HOME  ,KC.UP    ,KC.END   ,KC.DEL   ,
        KC.CIRC  ,KC.AMPR  ,KC.QUES  ,KC.PERC  ,KC.INT3  ,KC.NO    ,KC.LEFT  ,KC.DOWN  ,KC.RIGHT ,KC.BSPC  ,
        KC.GRV   ,KC.PIPE  ,KC.EXLM  ,KC.UNDS  ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
        KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,
    ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.RESET ,KC.F1    ,KC.F2    ,KC.F3    ,KC.F4    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
        KC.DEBUG ,KC.F5    ,KC.F6    ,KC.F7    ,KC.F8    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
        KC.NO    ,KC.F9    ,KC.F10   ,KC.F11   ,KC.F12   ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
        KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
    ],
]

if __name__ == '__main__':
    keyboard.go()