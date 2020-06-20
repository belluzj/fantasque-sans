# Generate features for ligatures
#
# Adapted from https://github.com/tonsky/FiraCode/blob/master/gen_calt.clj

from textwrap import dedent
import tempfile


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

    # print(fea_code)  # DEBUG

    # Add the dummy "LIG" glyph
    lig = font.createChar(-1, 'LIG')
    lig.width = font['space'].width
    with tempfile.NamedTemporaryFile(suffix='.fea') as f:
        f.write(fea_code)
        f.seek(0)
        font.mergeFeature(f.name)


def rule(liga):
    """
    [f f i] => { [LIG LIG i] f_f_i.liga
                 [LIG   f i] LIG
                 [ f    f i] LIG }
    """
    # ignores:
    #   ignore sub {0} {0}' {1};
    #   ignore sub {0}' {1} {1};
    rules = [
        ignore(prefix=liga[:1], head=liga[0], suffix=liga[1:]),
        ignore(head=liga[0], suffix=(liga[1:] + [liga[-1]])),
    ]

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


def indent(text, prefix):
    return '\n'.join(prefix + line for line in text.split('\n'))
