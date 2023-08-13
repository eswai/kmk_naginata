# Vpico KMK薙刀式

print("Starting")

import board

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

keyboard.col_pins = (board.GP15, board.GP14, board.GP13, board.GP12, board.GP11, board.GP20, board.GP19, board.GP18, board.GP17, board.GP16,)
keyboard.row_pins = (board.GP7, board.GP8, board.GP9, board.GP10,)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

layers = Layers()
keyboard.modules.append(layers)

combos = Combos()
keyboard.modules.append(combos)

holdtap = HoldTap()
holdtap.tap_time = 100
keyboard.modules.append(holdtap)

combo_layers = {
  (2, 3): 4,
}
keyboard.modules.append(Layers(combo_layers))

keyboard.debug_enabled = True

LOWER = KC.MO(2)
RAISE = KC.MO(3)
SSPC = KC.HT(KC.SPC, KC.LSFT)
SENT = KC.HT(KC.ENTER, KC.LSFT)
NGTG = KC.TG(1)

kbuf = set() # 入力バッファ

#　かな変換の処理
def ngpress(*args, **kwargs):
    print(args[0])
    kbuf.add(args[0])
    return False

def ngrelease(*args, **kwargs):
    print(args[0])
    for a in ngdic:
      if a[0] == kbuf:
          keyboard.tap_key(simple_key_sequence(a[1]))
          break
    kbuf.clear()
    return False

def naginata_on(*args, **kwargs):
    layers.activate_layer(keyboard, 1)
    kbuf.clear()
    keyboard.tap_key(KC.LANG1)
    keyboard.tap_key(KC.INT4)
    return False

def naginata_off(*args, **kwargs):
    layers.deactivate_layer(keyboard, 1)
    kbuf.clear()
    keyboard.tap_key(KC.LANG2)
    keyboard.tap_key(KC.INT5)
    return False

# キーの定義
ngkeys = [
  'NGQ', 'NGW', 'NGE', 'NGR', 'NGT', 'NGY', 'NGU', 'NGI', 'NGO', 'NGP', 
  'NGA', 'NGS', 'NGD', 'NGF', 'NGG', 'NGH', 'NGJ', 'NGK', 'NGL', 'NGSCLN',
  'NGZ', 'NGX', 'NGC', 'NGV', 'NGB', 'NGN', 'NGM', 'NGCOMM', 'NGDOT', 'NGSLSH',
  'NGSFT'
]
for k in ngkeys:
    make_key(names=(k,), on_press=ngpress, on_release=ngrelease)

make_key(names=('NGON' ,), on_release=naginata_on) # on_releaseの方が安定するような
make_key(names=('NGOFF',), on_release=naginata_off)

combos.combos = [
  Chord((KC.H  , KC.J  ), KC.NGON , timeout=100, per_key_timeout=False, fast_reset=True),
  Chord((KC.NGF, KC.NGG), KC.NGOFF, timeout=100, per_key_timeout=False, fast_reset=True),
]

# かな変換テーブル
ngdic = [
  ({KC.NGU                          }, [KC.BSPC                       ]),
  ({KC.NGT                          }, [KC.LEFT                       ]),
  ({KC.NGY                          }, [KC.RIGHT                      ]),
  ({KC.NGSFT , KC.NGT               }, [KC.LSFT(KC.LEFT)              ]),
  ({KC.NGSFT , KC.NGY               }, [KC.LSFT(KC.RIGHT)             ]),
  ({KC.NGSFT                        }, [KC.SPC                        ]),
  ({KC.NGM   , KC.NGV               }, [KC.ENT                        ]),
  ({KC.NGSFT , KC.NGM               }, [KC.DOT,  KC.ENT               ]),
  ({KC.NGSFT , KC.NGV               }, [KC.COMM, KC.ENT               ]),

  # 清音
  ({KC.NGJ                          }, [KC.A                          ]), # あ
  ({KC.NGK                          }, [KC.I                          ]), # い
  ({KC.NGL                          }, [KC.U                          ]), # う
  ({KC.NGSFT , KC.NGO               }, [KC.E                          ]), # え
  ({KC.NGSFT , KC.NGN               }, [KC.O                          ]), # お
  ({KC.NGF                          }, [KC.K, KC.A                    ]), # か
  ({KC.NGW                          }, [KC.K, KC.I                    ]), # き
  ({KC.NGH                          }, [KC.K, KC.U                    ]), # く
  ({KC.NGS                          }, [KC.K, KC.E                    ]), # け
  ({KC.NGV                          }, [KC.K, KC.O                    ]), # こ
  ({KC.NGSFT , KC.NGU               }, [KC.S, KC.A                    ]), # さ
  ({KC.NGR                          }, [KC.S, KC.I                    ]), # し
  ({KC.NGO                          }, [KC.S, KC.U                    ]), # す
  ({KC.NGSFT , KC.NGA               }, [KC.S, KC.E                    ]), # せ
  ({KC.NGB                          }, [KC.S, KC.O                    ]), # そ
  ({KC.NGN                          }, [KC.T, KC.A                    ]), # た
  ({KC.NGSFT , KC.NGG               }, [KC.T, KC.I                    ]), # ち
  ({KC.NGSFT , KC.NGL               }, [KC.T, KC.U                    ]), # つ
  ({KC.NGE                          }, [KC.T, KC.E                    ]), # て
  ({KC.NGD                          }, [KC.T, KC.O                    ]), # と
  ({KC.NGM                          }, [KC.N, KC.A                    ]), # な
  ({KC.NGSFT , KC.NGD               }, [KC.N, KC.I                    ]), # に
  ({KC.NGSFT , KC.NGW               }, [KC.N, KC.U                    ]), # ぬ
  ({KC.NGSFT , KC.NGR               }, [KC.N, KC.E                    ]), # ね
  ({KC.NGSFT , KC.NGJ               }, [KC.N, KC.O                    ]), # の
  ({KC.NGC                          }, [KC.H, KC.A                    ]), # は
  ({KC.NGX                          }, [KC.H, KC.I                    ]), # ひ
  ({KC.NGSFT , KC.NGX               }, [KC.H, KC.I                    ]), # ひ
  ({KC.NGSFT , KC.NGSCLN            }, [KC.H, KC.U                    ]), # ふ
  ({KC.NGP                          }, [KC.H, KC.E                    ]), # へ
  ({KC.NGZ                          }, [KC.H, KC.O                    ]), # ほ
  ({KC.NGSFT , KC.NGZ               }, [KC.H, KC.O                    ]), # ほ
  ({KC.NGSFT , KC.NGF               }, [KC.M, KC.A                    ]), # ま
  ({KC.NGSFT , KC.NGB               }, [KC.M, KC.I                    ]), # み
  ({KC.NGSFT , KC.NGCOMM            }, [KC.M, KC.U                    ]), # む
  ({KC.NGSFT , KC.NGS               }, [KC.M, KC.E                    ]), # め
  ({KC.NGSFT , KC.NGK               }, [KC.M, KC.O                    ]), # も
  ({KC.NGSFT , KC.NGH               }, [KC.Y, KC.A                    ]), # や
  ({KC.NGSFT , KC.NGP               }, [KC.Y, KC.U                    ]), # ゆ
  ({KC.NGSFT , KC.NGI               }, [KC.Y, KC.O                    ]), # よ
  ({KC.NGDOT                        }, [KC.R, KC.A                    ]), # ら
  ({KC.NGSFT , KC.NGE               }, [KC.R, KC.I                    ]), # り
  ({KC.NGI                          }, [KC.R, KC.U                    ]), # る
  ({KC.NGSLSH                       }, [KC.R, KC.E                    ]), # れ
  ({KC.NGSFT , KC.NGSLSH            }, [KC.R, KC.E                    ]), # れ
  ({KC.NGA                          }, [KC.R, KC.O                    ]), # ろ
  ({KC.NGSFT , KC.NGDOT             }, [KC.W, KC.A                    ]), # わ
  ({KC.NGSFT , KC.NGC               }, [KC.W, KC.O                    ]), # を
  ({KC.NGCOMM                       }, [KC.N, KC.N                    ]), # ん
  ({KC.NGSCLN                       }, [KC.MINS                       ]), # ー

  # 濁音
  ({KC.NGJ   , KC.NGF               }, [KC.G, KC.A                    ]), # が
  ({KC.NGJ   , KC.NGW               }, [KC.G, KC.I                    ]), # ぎ
  ({KC.NGF   , KC.NGH               }, [KC.G, KC.U                    ]), # ぐ
  ({KC.NGJ   , KC.NGS               }, [KC.G, KC.E                    ]), # げ
  ({KC.NGJ   , KC.NGV               }, [KC.G, KC.O                    ]), # ご
  ({KC.NGF   , KC.NGU               }, [KC.Z, KC.A                    ]), # ざ
  ({KC.NGJ   , KC.NGR               }, [KC.Z, KC.I                    ]), # じ
  ({KC.NGF   , KC.NGO               }, [KC.Z, KC.U                    ]), # ず
  ({KC.NGJ   , KC.NGA               }, [KC.Z, KC.E                    ]), # ぜ
  ({KC.NGJ   , KC.NGB               }, [KC.Z, KC.O                    ]), # ぞ
  ({KC.NGF   , KC.NGN               }, [KC.D, KC.A                    ]), # だ
  ({KC.NGJ   , KC.NGG               }, [KC.D, KC.I                    ]), # ぢ
  ({KC.NGF   , KC.NGL               }, [KC.D, KC.U                    ]), # づ
  ({KC.NGJ   , KC.NGE               }, [KC.D, KC.E                    ]), # で
  ({KC.NGJ   , KC.NGD               }, [KC.D, KC.O                    ]), # ど
  ({KC.NGJ   , KC.NGC               }, [KC.B, KC.A                    ]), # ば
  ({KC.NGJ   , KC.NGX               }, [KC.B, KC.I                    ]), # び
  ({KC.NGF   , KC.NGSCLN            }, [KC.B, KC.U                    ]), # ぶ
  ({KC.NGF   , KC.NGP               }, [KC.B, KC.E                    ]), # べ
  ({KC.NGJ   , KC.NGZ               }, [KC.B, KC.O                    ]), # ぼ
  ({KC.NGQ                          }, [KC.V, KC.U                    ]), # ゔ
  ({KC.NGSFT , KC.NGQ               }, [KC.V, KC.U                    ]), # ゔ

  # 半濁音
  ({KC.NGM   , KC.NGC               }, [KC.P, KC.A                    ]), # ぱ
  ({KC.NGM   , KC.NGX               }, [KC.P, KC.I                    ]), # ぴ
  ({KC.NGV   , KC.NGSCLN            }, [KC.P, KC.U                    ]), # ぷ
  ({KC.NGV   , KC.NGP               }, [KC.P, KC.E                    ]), # ぺ
  ({KC.NGM   , KC.NGZ               }, [KC.P, KC.O                    ]), # ぽ

  # 小書き
  ({KC.NGQ   , KC.NGH               }, [KC.X, KC.Y, KC.A              ]), # ゃ
  ({KC.NGQ   , KC.NGP               }, [KC.X, KC.Y, KC.U              ]), # ゅ
  ({KC.NGQ   , KC.NGI               }, [KC.X, KC.Y, KC.O              ]), # ょ
  ({KC.NGQ   , KC.NGJ               }, [KC.X, KC.A                    ]), # ぁ
  ({KC.NGQ   , KC.NGK               }, [KC.X, KC.I                    ]), # ぃ
  ({KC.NGQ   , KC.NGL               }, [KC.X, KC.U                    ]), # ぅ
  ({KC.NGQ   , KC.NGO               }, [KC.X, KC.E                    ]), # ぇ
  ({KC.NGQ   , KC.NGN               }, [KC.X, KC.O                    ]), # ぉ
  ({KC.NGQ   , KC.NGDOT             }, [KC.X, KC.W, KC.A              ]), # ゎ
  ({KC.NGG                          }, [KC.X, KC.T, KC.U              ]), # っ
  ({KC.NGQ   , KC.NGS               }, [KC.X, KC.K, KC.E              ]), # ヶ
  ({KC.NGQ   , KC.NGF               }, [KC.X, KC.K, KC.A              ]), # ヵ

  # 清音拗音 濁音拗音 半濁拗音
  ({KC.NGR   , KC.NGH               }, [KC.S, KC.Y, KC.A              ]), # しゃ
  ({KC.NGR   , KC.NGP               }, [KC.S, KC.Y, KC.U              ]), # しゅ
  ({KC.NGR   , KC.NGI               }, [KC.S, KC.Y, KC.O              ]), # しょ
  ({KC.NGJ   , KC.NGR   , KC.NGH    }, [KC.Z, KC.Y, KC.A              ]), # じゃ
  ({KC.NGJ   , KC.NGR   , KC.NGP    }, [KC.Z, KC.Y, KC.U              ]), # じゅ
  ({KC.NGJ   , KC.NGR   , KC.NGI    }, [KC.Z, KC.Y, KC.O              ]), # じょ
  ({KC.NGW   , KC.NGH               }, [KC.K, KC.Y, KC.A              ]), # きゃ
  ({KC.NGW   , KC.NGP               }, [KC.K, KC.Y, KC.U              ]), # きゅ
  ({KC.NGW   , KC.NGI               }, [KC.K, KC.Y, KC.O              ]), # きょ
  ({KC.NGJ   , KC.NGW   , KC.NGH    }, [KC.G, KC.Y, KC.A              ]), # ぎゃ
  ({KC.NGJ   , KC.NGW   , KC.NGP    }, [KC.G, KC.Y, KC.U              ]), # ぎゅ
  ({KC.NGJ   , KC.NGW   , KC.NGI    }, [KC.G, KC.Y, KC.O              ]), # ぎょ
  ({KC.NGG   , KC.NGH               }, [KC.T, KC.Y, KC.A              ]), # ちゃ
  ({KC.NGG   , KC.NGP               }, [KC.T, KC.Y, KC.U              ]), # ちゅ
  ({KC.NGG   , KC.NGI               }, [KC.T, KC.Y, KC.O              ]), # ちょ
  ({KC.NGJ   , KC.NGG   , KC.NGH    }, [KC.D, KC.Y, KC.A              ]), # ぢゃ
  ({KC.NGJ   , KC.NGG   , KC.NGP    }, [KC.D, KC.Y, KC.U              ]), # ぢゅ
  ({KC.NGJ   , KC.NGG   , KC.NGI    }, [KC.D, KC.Y, KC.O              ]), # ぢょ
  ({KC.NGD   , KC.NGH               }, [KC.N, KC.Y, KC.A              ]), # にゃ
  ({KC.NGD   , KC.NGP               }, [KC.N, KC.Y, KC.U              ]), # にゅ
  ({KC.NGD   , KC.NGI               }, [KC.N, KC.Y, KC.O              ]), # にょ
  ({KC.NGX   , KC.NGH               }, [KC.H, KC.Y, KC.A              ]), # ひゃ
  ({KC.NGX   , KC.NGP               }, [KC.H, KC.Y, KC.U              ]), # ひゅ
  ({KC.NGX   , KC.NGI               }, [KC.H, KC.Y, KC.O              ]), # ひょ
  ({KC.NGJ   , KC.NGX   , KC.NGH    }, [KC.B, KC.Y, KC.A              ]), # びゃ
  ({KC.NGJ   , KC.NGX   , KC.NGP    }, [KC.B, KC.Y, KC.U              ]), # びゅ
  ({KC.NGJ   , KC.NGX   , KC.NGI    }, [KC.B, KC.Y, KC.O              ]), # びょ
  ({KC.NGM   , KC.NGX   , KC.NGH    }, [KC.P, KC.Y, KC.A              ]), # ぴゃ
  ({KC.NGM   , KC.NGX   , KC.NGP    }, [KC.P, KC.Y, KC.U              ]), # ぴゅ
  ({KC.NGM   , KC.NGX   , KC.NGI    }, [KC.P, KC.Y, KC.O              ]), # ぴょ
  ({KC.NGB   , KC.NGH               }, [KC.M, KC.Y, KC.A              ]), # みゃ
  ({KC.NGB   , KC.NGP               }, [KC.M, KC.Y, KC.U              ]), # みゅ
  ({KC.NGB   , KC.NGI               }, [KC.M, KC.Y, KC.O              ]), # みょ
  ({KC.NGE   , KC.NGH               }, [KC.R, KC.Y, KC.A              ]), # りゃ
  ({KC.NGE   , KC.NGP               }, [KC.R, KC.Y, KC.U              ]), # りゅ
  ({KC.NGE   , KC.NGI               }, [KC.R, KC.Y, KC.O              ]), # りょ

  # 清音外来音 濁音外来音
  ({KC.NGM   , KC.NGE   , KC.NGK    }, [KC.T, KC.H, KC.I              ]), # てぃ
  ({KC.NGM   , KC.NGE   , KC.NGP    }, [KC.T, KC.H, KC.U              ]), # てゅ
  ({KC.NGJ   , KC.NGE   , KC.NGK    }, [KC.D, KC.H, KC.I              ]), # でぃ
  ({KC.NGJ   , KC.NGE   , KC.NGP    }, [KC.D, KC.H, KC.U              ]), # でゅ
  ({KC.NGM   , KC.NGD   , KC.NGL    }, [KC.T, KC.O, KC.X, KC.U        ]), # とぅ
  ({KC.NGJ   , KC.NGD   , KC.NGL    }, [KC.D, KC.O, KC.X, KC.U        ]), # どぅ
  ({KC.NGM   , KC.NGR   , KC.NGO    }, [KC.S, KC.Y, KC.E              ]), # しぇ
  ({KC.NGM   , KC.NGG   , KC.NGO    }, [KC.T, KC.Y, KC.E              ]), # ちぇ
  ({KC.NGJ   , KC.NGR   , KC.NGO    }, [KC.Z, KC.Y, KC.E              ]), # じぇ
  ({KC.NGJ   , KC.NGG   , KC.NGO    }, [KC.D, KC.Y, KC.E              ]), # ぢぇ
  ({KC.NGV   , KC.NGSCLN, KC.NGJ    }, [KC.F, KC.A                    ]), # ふぁ
  ({KC.NGV   , KC.NGSCLN, KC.NGK    }, [KC.F, KC.I                    ]), # ふぃ
  ({KC.NGV   , KC.NGSCLN, KC.NGO    }, [KC.F, KC.E                    ]), # ふぇ
  ({KC.NGV   , KC.NGSCLN, KC.NGN    }, [KC.F, KC.O                    ]), # ふぉ
  ({KC.NGV   , KC.NGSCLN, KC.NGP    }, [KC.F, KC.Y, KC.U              ]), # ふゅ
  ({KC.NGV   , KC.NGK   , KC.NGO    }, [KC.I, KC.X, KC.E              ]), # いぇ
  ({KC.NGV   , KC.NGL   , KC.NGK    }, [KC.W, KC.I                    ]), # うぃ
  ({KC.NGV   , KC.NGL   , KC.NGO    }, [KC.W, KC.E                    ]), # うぇ
  ({KC.NGV   , KC.NGL   , KC.NGN    }, [KC.U, KC.X, KC.O              ]), # うぉ
  ({KC.NGM   , KC.NGQ   , KC.NGJ    }, [KC.V, KC.A                    ]), # ゔぁ
  ({KC.NGM   , KC.NGQ   , KC.NGK    }, [KC.V, KC.I                    ]), # ゔぃ
  ({KC.NGM   , KC.NGQ   , KC.NGO    }, [KC.V, KC.E                    ]), # ゔぇ
  ({KC.NGM   , KC.NGQ   , KC.NGN    }, [KC.V, KC.O                    ]), # ゔぉ
  ({KC.NGM   , KC.NGQ   , KC.NGP    }, [KC.V, KC.U, KC.X, KC.Y, KC.U  ]), # ゔゅ
  ({KC.NGV   , KC.NGH   , KC.NGJ    }, [KC.K, KC.U, KC.X, KC.A        ]), # くぁ
  ({KC.NGV   , KC.NGH   , KC.NGK    }, [KC.K, KC.U, KC.X, KC.I        ]), # くぃ
  ({KC.NGV   , KC.NGH   , KC.NGO    }, [KC.K, KC.U, KC.X, KC.E        ]), # くぇ
  ({KC.NGV   , KC.NGH   , KC.NGN    }, [KC.K, KC.U, KC.X, KC.O        ]), # くぉ
  ({KC.NGV   , KC.NGH   , KC.NGDOT  }, [KC.K, KC.U, KC.X, KC.W, KC.A  ]), # くゎ
  ({KC.NGF   , KC.NGH   , KC.NGJ    }, [KC.G, KC.U, KC.X, KC.A        ]), # ぐぁ
  ({KC.NGF   , KC.NGH   , KC.NGK    }, [KC.G, KC.U, KC.X, KC.I        ]), # ぐぃ
  ({KC.NGF   , KC.NGH   , KC.NGO    }, [KC.G, KC.U, KC.X, KC.E        ]), # ぐぇ
  ({KC.NGF   , KC.NGH   , KC.NGN    }, [KC.G, KC.U, KC.X, KC.O        ]), # ぐぉ
  ({KC.NGF   , KC.NGH   , KC.NGDOT  }, [KC.G, KC.U, KC.X, KC.W, KC.A  ]), # ぐゎ
  ({KC.NGV   , KC.NGL   , KC.NGJ    }, [KC.T, KC.S, KC.A              ]), # つぁ
]

keyboard.keymap = [
  [
 # |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
    KC.Q     ,KC.W     ,KC.E     ,KC.R     ,KC.T     ,KC.Y     ,KC.U     ,KC.I     ,KC.O     ,KC.P     ,
    KC.A     ,KC.S     ,KC.D     ,KC.F     ,KC.G     ,KC.H     ,KC.J     ,KC.K     ,KC.L     ,KC.SCLN  ,
    KC.Z     ,KC.X     ,KC.C     ,KC.V     ,KC.B     ,KC.N     ,KC.M     ,KC.COMM  ,KC.DOT   ,KC.SLSH  ,
    KC.LCTL  ,KC.LSFT  ,KC.LGUI  ,LOWER    ,SSPC     ,SENT     ,RAISE    ,KC.RCTRL ,KC.NGON  ,KC.NGOFF ,
  ],
  [
 # |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
    KC.NGQ   ,KC.NGW   ,KC.NGE   ,KC.NGR   ,KC.NGT   ,KC.NGY   ,KC.NGU   ,KC.NGI   ,KC.NGO   ,KC.NGP   ,
    KC.NGA   ,KC.NGS   ,KC.NGD   ,KC.NGF   ,KC.NGG   ,KC.NGH   ,KC.NGJ   ,KC.NGK   ,KC.NGL   ,KC.NGSCLN,
    KC.NGZ   ,KC.NGX   ,KC.NGC   ,KC.NGV   ,KC.NGB   ,KC.NGN   ,KC.NGM   ,KC.NGCOMM,KC.NGDOT ,KC.NGSLSH,
    KC.LCTL  ,KC.LSFT  ,KC.LGUI  ,LOWER    ,KC.NGSFT ,KC.NGSFT ,RAISE    ,KC.RCTRL ,KC.NGON  ,KC.NGOFF ,
  ],
  [
 # |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
    KC.TAB   ,KC.COLN  ,KC.SCLN  ,KC.DQT   ,KC.QUOT  ,KC.SLSH  ,KC.N7    ,KC.N8    ,KC.N9    ,KC.MINS  ,
    KC.ESC   ,KC.LBRC  ,KC.LCBR  ,KC.LPRN  ,KC.NO    ,KC.ASTR  ,KC.N4    ,KC.N5    ,KC.N6    ,KC.PLUS  ,
    KC.NO    ,KC.RBRC  ,KC.RCBR  ,KC.RPRN  ,KC.NO    ,KC.N0    ,KC.N1    ,KC.N2    ,KC.N3    ,KC.EQL   ,
    KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,
  ],
  [
 # |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
    KC.TILD  ,KC.AT    ,KC.HASH  ,KC.DLR   ,KC.NO    ,KC.NO    ,KC.HOME  ,KC.UP    ,KC.END   ,KC.DEL   ,
    KC.CIRC  ,KC.AMPR  ,KC.QUES  ,KC.PERC  ,KC.INT3  ,KC.NO    ,KC.LEFT  ,KC.DOWN  ,KC.RIGHT ,KC.BSPC  ,
    KC.GRV   ,KC.PIPE  ,KC.EXLM  ,KC.UNDS  ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
    KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,
  ],
  [
 # |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
    KC.RESET ,KC.F1    ,KC.F2    ,KC.F3    ,KC.F4    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
    KC.DEBUG ,KC.F5    ,KC.F6    ,KC.F7    ,KC.F8    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
    KC.NO    ,KC.F9    ,KC.F10   ,KC.F11   ,KC.F12   ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
    KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
  ],
]

if __name__ == '__main__':
    keyboard.go()