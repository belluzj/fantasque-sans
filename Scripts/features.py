# Generate features for ligatures
#
# Adapted from https://github.com/tonsky/FiraCode/blob/master/gen_calt.clj

from __future__ import unicode_literals

from textwrap import dedent
from collections import defaultdict
import tempfile
import sys

PY3 = sys.version_info[0] == 3
if PY3:
    binary_type = bytes
    text_type = str
else:
    binary_type = str
    text_type = unicode

def ensure_binary(s, encoding='utf-8', errors='strict'):
    if isinstance(s, binary_type):
        return s
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    raise TypeError("not expecting type '%s'" % type(s))

def update_features(font):
    """Find ligatures in the font and generate features for them."""
    # [ ["dash" "greater" "greater"] ... ]
    ligas = [name[:-len('.liga')].split('_')
             for name in font if name.endswith('.liga') and
                                 font[name].isWorthOutputting()]

    rules = '\n\n'.join(rule(liga)
                        for liga in sorted(ligas, key=lambda l: -len(l)))

    fea_code = dedent('''\
        languagesystem DFLT dflt;
        languagesystem latn dflt;
        languagesystem grek dflt;
        languagesystem cyrl dflt;

        feature calt {{
        {}
        }} calt;
    ''').format(indent(rules, '  '))
    fea_code = ensure_binary(fea_code)

    # print(fea_code)  # DEBUG

    # Add the dummy "LIG" glyph
    lig = font.createChar(-1, 'LIG')
    lig.width = font['space'].width
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fea') as f:
        f.write(fea_code)
        f.seek(0)
        font.mergeFeature(f.name)


def rule(liga):
    """
    [f f i] => { [LIG LIG i] f_f_i.liga
                 [LIG   f i] LIG
                 [ f    f i] LIG }
    """
    rules = []
    # standard ignores:
    #   ignore sub {0} {0}' {1};
    #   ignore sub {0}' {1} {1};
    if tuple(liga) not in skip_ignores:
        rules.extend(
            [
                ignore(prefix=liga[:1], head=liga[0], suffix=liga[1:]),
                ignore(head=liga[0], suffix=(liga[1:] + [liga[-1]])),
            ]
        )

    # careful with repeats:
    # #133 ->->->->, /**/**/**/, etc.
    if len(liga) > 2 and liga[0] == liga[-1]:
        rules.append(ignore([liga[-2]], liga[0], liga[1:]))
        rules.append(ignore(head=liga[0], suffix=(liga[1:] + [liga[1]])))

    # Don't cut into `prefix` to complete a ligature.
    #  i.e. regex `(?=`>  is not `(?`=>.
    rules.extend(
        [
            ignore(prefix[:-n], liga[0], liga[1:])
            for prefix in ignore_prefixes
            for n in range(1, len(liga))
            if prefix[-n:] == liga[:n]
        ]
    )
    # hardcoded ignores, i.e. `<||>`
    rules.extend(ignores[tuple(liga)])

    name = "_".join(liga)
    # substitution logic
    #   sub {0}'  {1}  by LIG;
    #   sub LIG {1}' by {0}_{1}.liga;
    for i in range(len(liga)):
        init = _join(["LIG" for lig in liga[:i]])
        tail = _join(liga[i + 1 :])
        replace = "LIG" if (i + 1 < len(liga)) else (name + ".liga")
        rules.append("sub{0} {1}'{2} by {3};".format(init, liga[i], tail, replace))

    # put it all together
    lines = (
        ["lookup " + name + " {"] + ["  " + r for r in rules] + ["}} {0};".format(name)]
    )
    return "\n".join(lines)


def _join(items):
    return (" " + " ".join(items)) if items else ""


def ignore(prefix=None, head=None, suffix=None):
    """ don't substitute `head` if it's surrounded by `prefix` and `suffix` """
    assert head
    pref = _join(prefix)
    rest = _join(suffix)
    return "ignore sub{0} {1}'{2};".format(pref, head, rest)


ignores = defaultdict(
    list,
    {
        ("slash", "asterisk"): [
            "ignore sub slash' asterisk slash;",
            "ignore sub asterisk slash' asterisk;",
        ],
        ("asterisk", "slash"): [
            "ignore sub slash asterisk' slash;",
            "ignore sub asterisk' slash asterisk;",
        ],
        # ("asterisk", "asterisk"): [
        #     "ignore sub slash asterisk' asterisk;",
        #     "ignore sub asterisk' asterisk slash;",
        # ],
        # ("asterisk", "asterisk", "asterisk"): [
        #     "ignore sub slash asterisk' asterisk asterisk;",
        #     "ignore sub asterisk' asterisk asterisk slash;",
        # ],
        # <||>
        ("less", "bar", "bar"): ["ignore sub less' bar bar greater;"],
        ("bar", "bar", "greater"): ["ignore sub less bar' bar greater;"],
        # # :>=
        # ("colon", "greater"): ["ignore sub colon' greater equal;"],
        # # {|}
        # ("braceleft", "bar"): ["ignore sub braceleft' bar braceright;"],
        # ("bar", "braceright"): ["ignore sub braceleft bar' braceright;"],
        # # [|]
        # ("bracketleft", "bar"): ["ignore sub bracketleft' bar bracketright;"],
        # ("bar", "bracketright"): ["ignore sub bracketleft bar' bracketright;"],
        # # <*>>> <+>>> <$>>>
        # ("greater", "greater", "greater"): [
        #     "ignore sub [asterisk plus dollar] greater' greater greater;"
        # ],
        # # <<<*> <<<+> <<<$>
        # ("less", "less", "less"): ["ignore sub less' less less [asterisk plus dollar];"],
        # # =:=
        # ("colon", "equal"): ["ignore sub equal colon' equal;"],
        # =!=
        ("exclam", "equal"): ["ignore sub equal exclam' equal;"],
        # =!==
        ("exclam", "equal", "equal"): ["ignore sub equal exclam' equal equal;"],
        # =<= <=< <=> <=| <=: <=! <=/
        ("less", "equal"): [
            "ignore sub equal less' equal;",
            "ignore sub less' equal [less greater bar colon exclam slash];",
        ],
        # >=<
        # =>= >=> >=< >=| >=: >=! >=/
        ("greater", "equal"): [
            "ignore sub equal greater' equal;",
            "ignore sub greater' equal [less greater bar colon exclam slash];",
        ],
        # <*>> <+>> <$>>
        # >>->> >>=>>
        ("greater", "greater"): [
            # "ignore sub [asterisk plus dollar] greater' greater;",
            # "ignore sub [hyphen equal] greater' greater;",
            # "ignore sub greater' greater [hyphen equal];",
        ],
        # <<*> <<+> <<$>
        # <<-<< <<=<<
        ("less", "less"): [
            # "ignore sub less' less [asterisk plus dollar];",
            # "ignore sub [hyphen equal] less' less;",
            # "ignore sub less' less [hyphen equal];",
        ],
        # ||-|| ||=||
        ("bar", "bar"): [
            "ignore sub [hyphen equal] bar' bar;",
            "ignore sub bar' bar [hyphen equal];",
        ],
        # # <--> >--< |--|
        # ("hyphen", "hyphen"): [
        #     "ignore sub [less greater bar] hyphen' hyphen;",
        #     "ignore sub hyphen' hyphen [less greater bar];",
        # ],
        # # <---> >---< |---|
        # ("hyphen", "hyphen", "hyphen"):
        #     "ignore sub [less greater bar] hyphen' hyphen hyphen;",
        #     "ignore sub hyphen' hyphen hyphen [less greater bar];",
        # ],
        ("equal", "equal"): [  # ==
            # "ignore sub bracketleft equal' equal;", # [==
            # "ignore sub equal' equal bracketright;",#  ==]
            "ignore sub equal [colon exclam] equal' equal;",  # =:== =!==
            # "ignore sub [less greater bar slash] equal' equal;", # <== >== |== /==
            # "ignore sub equal' equal [less greater bar slash];", # ==< ==> ==| ==/
            "ignore sub equal' equal [colon exclam] equal;",  # ==:= ==!=
        ],
        # [===[ ]===]
        # [=== ===]
        # <===> >===< |===| /===/ =:=== =!=== ===:= ===!=
        ("equal", "equal", "equal"): [
            # "ignore sub bracketleft equal' equal equal;",
            # "ignore sub equal' equal equal bracketright;",
            "ignore sub equal [colon exclam] equal' equal equal;",
            "ignore sub [less greater bar slash] equal' equal equal;",
            # "ignore sub equal' equal equal [less greater bar slash];",
            "ignore sub equal' equal equal [colon exclam] equal;",
        ],
        # #118 https://
        ("slash", "slash"): ["ignore sub colon slash' slash;"],
    },
)


ignore_prefixes = [
    ["parenleft", "question", "colon"],
    # Regexp lookahead/lookbehind
    ["parenleft", "question", "equal"],
    ["parenleft", "question", "less", "equal"],
    ["parenleft", "question", "exclam"],
    ["parenleft", "question", "less", "exclam"],
    # PHP <?=
    ["less", "question", "equal"],
]


# DO NOT generate ignores at all
skip_ignores = {
    # # <<*>> <<+>> <<$>>
    # ("less", "asterisk", "greater"),
    # ("less", "plus", "greater"),
    # ("less", "dollar", "greater"),
}


def indent(text, prefix):
    return '\n'.join(prefix + line for line in text.split('\n'))
