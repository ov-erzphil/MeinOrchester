"""Shared, filename-based instrument classification for both Drive synchronizers."""
import re
import unicodedata

ALIASES = {
 'Violine': r'violin(?:e[n]?|o|i|s)?|violon[s]?|geige[n]?|viol|vln|vn|vl',
 'Viola': r'viola[s]?|viole|bratsche[n]?|vla|va',
 'Violoncello': r'violoncell(?:o|i|os|e|es)|cell(?:o|i|os)|vc|vlc|vcl',
 'Kontrabass': r'kontrabass|kontrabasse|kontrabasser|contrabass(?:o|i)?|contrabbass(?:o|i)|contrebasses?|double\s*bass(?:es)?|basses|kb|cb|db',
 'Flöte': r'flote[n]?|floete[n]?|flute[s]?|flaut[oi]|fl',
 'Piccolo': r'piccolo(?:flote)?|picc|ottavino|petite\s*flute',
 'Altflöte': r'altflote|alto\s*flute|flute\s*alto|afl',
 'Oboe': r'oboe[n]?s?|hautbois|ob|hob',
 'Englischhorn': r'englisch\s*horn|english\s*horn|cor\s*anglais|corno\s*inglese|eh|ca',
 'Klarinette': r'klarinette[n]?|clarinet[s]?|clarinette[s]?|clarinett[oi]|klar|kl|cl',
 'Bassklarinette': r'bass\s*klarinette|bass\s*clarinet|clarinette\s*basse|clarinetto\s*basso|bcl|bkl',
 'Fagott': r'fagott[oi]?|bassoon[s]?|basson[s]?|fg|fag|bn|bsn',
 'Kontrafagott': r'kontrafagott|contrafagott[oi]|contrabassoon|double\s*bassoon|contrebasson|kfg|cfg|cbn|cbsn',
 'Horn': r'horner|horn[s]?|french\s*horn[s]?|hrn|hr|hn|corno|corni|cor',
 'Trompete': r'trompete[n]?|trumpet[s]?|trompette[s]?|tromb[ae]|trpt|trp|tpt|tr',
 'Posaune': r'posaune[n]?|trombone[s]?|tromboni|pos|tbn|trb|trbn',
 'Tuba': r'tuba[s]?|tube|tba',
 'Kornett': r'kornett|cornet[s]?|cornett[oi]',
 'Saxophon': r'saxophon[e]?[s]?|saxofon[oi]?|sax|asax|tsax|ssax|bsax',
 'Harfe': r'harfe[n]?|harp[s]?|harpe[s]?|harpa|harfa|arpa|arpe|арфа|харфа|hrf|hrp|hp|hf',
 'Pauke': r'pauke[n]?|timpani|timp|pk',
 'Schlagwerk': r'schlagwerk|shlagwerk|schlagzeug|percussion|perkussion|perc|drum\s*set|drumset|drums?|snare\s*drum|becken|glockenspiel|tamtam|tam\s*tam|triangel|tamburin|schellen|trommel|congas?|bongos?|crotales|vibraphon|chimes|rohrenglocken|toms|gran\s*cassa',
 'Cembalo': r'cembalo|harpsichord|hpschd|hpd',
 'Celesta': r'celesta|celeste|cel',
 'Klavier': r'klavier|piano|pno|pf',
 'Keyboard': r'keyboard|kbd',
 'Gitarre': r'gitarre|guitar|guitare|chitarra|gtr|gui',
 'E-Bass': r'e\s*bass|bassgitarre|bass\s*guitar',
 'Orgel': r'orgel|truhenorgel|organ|orgue|organo',
 'Partitur': r'partitur|gesamtpartitur|spielpartitur|full\s*score|fullscore|score',
}

def normalized(name):
    return ''.join(c for c in unicodedata.normalize('NFD',name.casefold()) if not unicodedata.combining(c)).replace('_',' ').replace('-',' ')

def pattern(value):
    return re.compile(r'(?<![^\W\d_])(?:'+value+r')(?![^\W\d_])', re.I)

PATTERNS={k:pattern(v) for k,v in ALIASES.items()}

def part_name(name):
    text=re.sub(r'\.pdf$','',name,flags=re.I)
    # A score title is not a player part. Prefer explicit part fields after titles.
    if re.search(r'konzert|concerto',text,re.I):
        for separator in (',','_-_'):
            if separator in text:
                tail=text.rsplit(separator,1)[1]
                if any(p.search(normalized(tail)) for p in PATTERNS.values()):
                    return normalized(tail)
    if re.search(r'glazunov_sax_cello',text,re.I):
        return 'cello'
    return normalized(text)

def classify(name):
    text=part_name(name)
    text=re.sub(r'(?<![a-z])gr\s*\.\s*tr\.?', 'grosse trommel', text)
    tags=[]
    # Match compound instruments first, masking them before their parent names.
    for label in ('Englischhorn','Bassklarinette','Kontrafagott','Altflöte','Piccolo','E-Bass'):
        p=PATTERNS[label]
        if p.search(text):
            tags.append(label)
            text=p.sub(' ',text)
    tags.extend(k for k,p in PATTERNS.items() if k not in tags and k not in ('Englischhorn','Bassklarinette','Kontrafagott','Altflöte','Piccolo','E-Bass') and p.search(text))
    if any(k in tags for k in ('Piccolo','Altflöte')):
        tags.append('Flöte')
    if 'Pauke' in tags:
        tags.append('Schlagwerk')
    if 'Posaune' in tags:
        p=ALIASES['Posaune']
        # Only read numbers directly adjacent to a part name, never from the work.
        voices=set()
        number=r'([123](?:\s*\.?\s*(?:und|[+&/,])\s*[123])*)'
        after=list(re.finditer(r'(?<![a-z])(?:'+p+r')\s*\.?\s*'+number+r'(?!\d)',text))
        before=list(re.finditer(r'(?<![a-z0-9])'+number+r'\s*\.?\s*(?:'+p+r')(?![a-z])',text))
        for m in after or before:
            voices.update(int(n) for n in re.findall('[123]',m.group(1)))
        if re.search(r'bass\s*(?:posaune|trombone)|trombone\s*basso|bassposaune',text):
            voices.add(3)
        tags.extend('Bassposaune' if n==3 else f'Posaune {n}' for n in sorted(voices))
    # German compound bass trombone needs a separate boundary-aware match.
    if re.search(r'(?<![a-z])bassposaune(?![a-z])',text):
        tags.extend(('Posaune','Bassposaune'))
    return sorted(set(tags))

def horn_voices(name):
    if 'Horn' not in classify(name): return []
    text=part_name(name)
    values=set()
    for m in re.finditer(r'(?<!\d)([1-4](?:\s*\.?\s*(?:und|[+&/,])\s*[1-4])*)\s*\.?\s*(?:horn|hrn|hr|hn|corni|corno)|(?:horn|hrn|hr|hn|corni|corno)\s*\.?\s*([1-4](?:\s*\.?\s*(?:und|[+&/,])\s*[1-4])*)(?!\d)',text):
        values.update(map(int,re.findall('[1-4]',m.group(1) or m.group(2))))
    return sorted(values)
