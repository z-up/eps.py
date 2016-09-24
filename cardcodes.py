__card_unicodes = ( ('1',  '2',  '3',  '4',  '5',  '6'),
                    ('A',  'B',  'C',  'D',  'E',  'F'),
                    ('Ⅰ',  'Ⅱ',  'Ⅲ',  'Ⅳ',  'Ⅴ',  'Ⅵ'),
                    ('⚀',  '⚁',  '⚂',  '⚃',  '⚄',  '⚅'),
                    ('△',  '▽',  '□',  '◇',  '⬠',  '⬡'),
                    ('+',  '-',  '÷',  '*',  '=',  '√') )

CARD_UNICODES = {rl + cn: v for rl, row in zip("ABCDEF", __card_unicodes) for cn, v in zip("123456", row)}
CARD_ASCII_CODES = dict([(v, k) for (k, v) in CARD_UNICODES.items()])


