# MABLE

print("Starting")

import board
import gc

from kmk.hid import HIDModes
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.modules.combos import Combos, Chord
from kmk.modules.holdtap import HoldTap
# from naginata import initNaginata
from kmk.modules.split import Split, SplitType, SplitSide

keyboard = KMKKeyboard()
keyboard.debug_enabled = True


keyboard.col_pins = (board.D10, board.D7, board.D4, board.D5, board.D1,)
keyboard.row_pins = (board.D2, board.D3, board.D0, board.D9,)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

split = Split(split_type=SplitType.BLE, split_side=SplitSide.LEFT)
# split = Split(split_type=SplitType.BLE, split_side=SplitSide.RIGHT)
keyboard.modules.append(split)

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

# initNaginata(keyboard, layers, 1)

# combos.combos = [
#     Chord((KC.H  , KC.J  ), KC.NGON , timeout = 100, per_key_timeout = False, fast_reset = True),
#     Chord((KC.NGF, KC.NGG), KC.NGOFF, timeout = 100, per_key_timeout = False, fast_reset = True),
# ]

gc.collect()

keyboard.keymap = [
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.Q     ,KC.W     ,KC.E     ,KC.R     ,KC.T     ,KC.Y     ,KC.U     ,KC.I     ,KC.O     ,KC.P     ,
        KC.A     ,KC.S     ,KC.D     ,KC.F     ,KC.G     ,KC.H     ,KC.J     ,KC.K     ,KC.L     ,KC.SCLN  ,
        KC.Z     ,KC.X     ,KC.C     ,KC.V     ,KC.B     ,KC.N     ,KC.M     ,KC.COMM  ,KC.DOT   ,KC.SLSH  ,
        KC.NO    ,KC.NO    ,KC.LCTRL ,LOWER    ,SSPC     ,SENT     ,RAISE    ,KC.RCTRL ,KC.NO    ,KC.NO    ,
    ],
    # [
    # #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
    #     KC.NGQ   ,KC.NGW   ,KC.NGE   ,KC.NGR   ,KC.NGT   ,KC.NGY   ,KC.NGU   ,KC.NGI   ,KC.NGO   ,KC.NP0_  ,
    #     KC.NGA   ,KC.NGS   ,KC.NGD   ,KC.NGF   ,KC.NGG   ,KC.NGH   ,KC.NGJ   ,KC.NGK   ,KC.NGL   ,KC.NGSCLN,
    #     KC.NGZ   ,KC.NGX   ,KC.NGC   ,KC.NGV   ,KC.NGB   ,KC.NGN   ,KC.NGM   ,KC.NGCOMM,KC.NGDOT ,KC.NGSLSH,
    #     KC.NO    ,KC.NO    ,KC.LCTRL ,LOWER    ,KC.NGSFT ,KC.NGSFT2,RAISE    ,KC.RCTRL ,KC.NO    ,KC.NO    ,
    # ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.TAB   ,KC.COLN  ,KC.SCLN  ,KC.DQT   ,KC.QUOT  ,KC.SLSH  ,KC.N7    ,KC.N8    ,KC.N9    ,KC.MINS  ,
        KC.ESC   ,KC.LBRC  ,KC.LCBR  ,KC.LPRN  ,KC.NO    ,KC.ASTR  ,KC.N4    ,KC.N5    ,KC.N6    ,KC.PLUS  ,
        KC.NO    ,KC.RBRC  ,KC.RCBR  ,KC.RPRN  ,KC.NO    ,KC.N0    ,KC.N1    ,KC.N2    ,KC.N3    ,KC.EQL   ,
        KC.NO    ,KC.NO    ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.NO    ,KC.NO    ,
    ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.TILD  ,KC.AT    ,KC.HASH  ,KC.DLR   ,KC.NO    ,KC.NO    ,KC.HOME  ,KC.UP    ,KC.END   ,KC.DEL   ,
        KC.CIRC  ,KC.AMPR  ,KC.QUES  ,KC.PERC  ,KC.INT3  ,KC.NO    ,KC.LEFT  ,KC.DOWN  ,KC.RIGHT ,KC.BSPC  ,
        KC.GRV   ,KC.PIPE  ,KC.EXLM  ,KC.UNDS  ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
        KC.NO    ,KC.NO    ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.TRNS  ,KC.NO    ,KC.NO    ,
    ],
    [
    #  |---------+---------+---------+---------+---------+---------+---------+---------+---------+---------|
        KC.RESET ,KC.F1    ,KC.F2    ,KC.F3    ,KC.F4    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.BT_CLR,
        KC.DEBUG ,KC.F5    ,KC.F6    ,KC.F7    ,KC.F8    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.BT_NXT,
        KC.NO    ,KC.F9    ,KC.F10   ,KC.F11   ,KC.F12   ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.BT_PRV,
        KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,KC.NO    ,
    ],
]

if __name__ == '__main__':
    keyboard.go(hid_type=HIDModes.BLE, ble_name='MABLE')