# vim: set fileencoding=utf-8 :
"""Contains translation of various informations for reverse translation"""

class TranslationError(Exception):
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return "No translation for " + repr(self.text)

ACTIVITY_DOMAIN = {
    'health' : {'fr':u'Santé', 'de':u'Gesundheitswesen', 'it':u'Sanità'},
    'social' : {'fr':u'Service social', 'de':u'Sozialwesen',
                'it':u'Servizi sociali'},
    'culture': {'fr':u'Conservation des biens culturels',
                'de':u'Kulturgütererhaltung',
                'it':u'Conservazione dei beni culturali'},
    'nature': {'fr':u'Protection de la nature et de l\'environnement',
               'de':u'Umwelt- und Naturschutz',
               'it':u'Protezione dell\'ambiente e della natura'},
    'forest': {'fr':u'Entretien des forêts',
               'de':u'Forstwesen',
               'it':u'Boschi'},
    'agriculture': {'fr':u'Agriculture',
                    'de':u'Landwirtschaft',
                    'it':u'Agricoltura'},
    'dev_cooperation': {
        'fr':u'Coopération au développement et aide humanitaire',
        'de':u'Entwicklungszusammenarbeit und humanitäre Hilfe',
        'it':u'Cooperazione allo sviluppo e aiuto umanitario'},
    'disaster_help': {
        'de':u'Bewältigung von Katastrophen und Notlagen'}
}

ACTIVITY_DOMAIN_REVERSE = {v[1]:k for k, values in ACTIVITY_DOMAIN.items() for v in values.items()}

def to_activity_domain(txt):
    key = txt.strip()
    if key not in ACTIVITY_DOMAIN_REVERSE:
        raise TranslationError(key)
    return ACTIVITY_DOMAIN_REVERSE[key]

