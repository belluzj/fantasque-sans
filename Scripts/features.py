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
    if len(liga) == 2:
        return dedent('''\
          lookup {0}_{1} {{
            ignore sub {0} {0}' {1};
            ignore sub {0}' {1} {1};
            sub {0}'  {1}  by LIG;
            sub LIG {1}' by {0}_{1}.liga;
          }} {0}_{1};
        ''').format(*liga)
    elif len(liga) == 3:
        return dedent('''\
          lookup {0}_{1}_{2} {{
            ignore sub {0} {0}' {1} {2};
            ignore sub {0}' {1} {2} {2};
            sub {0}' {1}  {2} by LIG;
            sub LIG  {1}' {2} by LIG;
            sub LIG  LIG  {2}' by {0}_{1}_{2}.liga;
          }} {0}_{1}_{2};
        ''').format(*liga)
    elif len(liga) == 4:
        return dedent('''\
            lookup {0}_{1}_{2}_{3} {{
               ignore sub {0} {0}' {1} {2} {3};
               ignore sub {0}' {1} {2} {3} {3};
               sub {0}'   {1}   {2}  {3}  by LIG;
               sub LIG  {1}'  {2}  {3}  by LIG;
               sub LIG LIG  {2}' {3}  by LIG;
               sub LIG LIG LIG {3}' by {0}_{1}_{2}_{3}.liga;
            }} {0}_{1}_{2}_{3};
        ''').format(*liga)


def indent(text, prefix):
    return '\n'.join(prefix + line for line in text.split('\n'))
