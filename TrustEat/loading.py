# from django.db import models

# Create your models here.
import re
from user.models import *
from localManagement.models import *
from dealer.models import *
from order.models import *


def file_import_trace():
    f = open('import.txt', 'w', encoding='utf8')
    f.write("# ---------------------- NON MODIFICARE I CAMPI INIZIALI! ----------------------\n"
            "#   Il seguente file è lo scheletro per l'importazione di dati nel database.\n"
            "# - Per aggiungere nuovi elementi specificarli, evitando spazi tra i ';', \n"
            "#      sotto l'elenco dei campi della tabella su cui si vuole aggiungere i dati.\n"
            "# - LE DATE SONO NEL FORMATO YYYY-MM-DD \n\n\n")
    f.write(
        # LOCAL MANAGEMENT
        '# Local Management\n\n'
        'Localita\ncap;nome_localita\n\n'
        'Locale\nnome_locale;orario_apertura;orario_chiusura;cap;via;num_civico;descrizione;telefono;sito_web;email\n\n'
        'Chiusura\nnome_locale;cap;giorno_chiusura\n\n'
        'Tag\nnome_tag\n\n'
        'IdentificatoDa\nnome_locale;cap;nome_tag\n\n'
        'Tipo\nnome_tipo\n\n'
        'Prodotto\nnome_prodotto;descrizione_prodotto;prezzo;nome_locale;cap;nome_tipo\n\n'
        'Menu\nnome_menu;descrizione_menu;prezzo;nome_locale;cap\n\n'
        'CompostoDa\nnome_locale;cap;nome_menu;nome_prodotto\n\n\n'

        # DEALER
        '# DEALER\n\n'
        'Persona\nemail;CF;nome;cognome;data_di_nascita;cap;via;num_civico;telefono;password\n\n'
        'Commerciante\nemail;p_iva\n\n'
        'Possiede\np_iva;nome_locale;cap\n\n\n'

        # USER
        '# USER\n\n'
        'UtenteRegistrato\nemail\n\n'
        'CartaDiCredito\nnumero_carta;intestatario;scadenza\n\n'
        'Utilizza\nnumero_carta;email\n\n'
        'Recensione\nemail;data;nome_locale;cap;voto;descrizione;p_iva\n\n\n'

        # ORDER
        '# ORDER\n\n'
        'OrdineInAttesa\nemail;data;orario_richiesto;metodo_pagamento;numero_carta\n\n'
        'Accettato\nemail;data;consegnto;descrizione\n\n'
        'Rifiutato\nemail;data;descrizione\n\n'
        'RichiedeM\nemail;data;nome_locale;cap;nome_menu;quantita\n\n'
        'RichiedeP\nemail;data;nome_locale;cap;nome_prodotto;quantita\n\n'
    )
    f.close()


def file_import(*args):
    table = (
        # LOCAL MANAGEMENT
        'Localita', 'Locale', 'Chiusura', 'Tag', 'IdentificatoDa', 'Tipo', 'Prodotto', 'Menu', 'CompostoDa',
        # DEALER
        'Persona', 'Commerciante', 'Possiede',
        # USER
        'UtenteRegistrato', 'CartaDiCredito', 'Utilizza',
        # USER
        'Recensione',
        # ORDER
        'OrdineInAttesa', 'Accettato', 'Rifiutato', 'RichiedeM', 'RichiedeP',
    )
    attr = (
        # LOCAL MANAGEMENT
        ('cap', 'nome_localita'),  # Localita -> 0
        ('nome_locale', 'orario_apertura', 'orario_chiusura', 'cap', 'via', 'num_civico', 'descrizione', 'telefono',
         'sito_web', 'email'),  # Locale -> 1
        ('cod_locale', 'giorno_chiusura'),  # Chiusura -> 2
        'nome_tag',  # Tag -> 3
        ('cod_locale', 'nome_tag'),  # IdentificatoDa -> 4
        'nome_tipo',  # Tipo -> 5
        ('nome_prodotto', 'descrizione_prodotto', 'prezzo', 'cod_locale', 'nome_tipo'),  # Prodotto -> 6
        ('nome_menu', 'descrizione_menu', 'prezzo', 'cod_locale'),  # Menu -> 7
        ('cod_locale', 'nome_menu', 'nome_prodotto'),  # CompostoDa -> 8
        # DEALER
        ('email', 'CF', 'nome', 'cognome', 'data_di_nascita', 'cap', 'via', 'num_civico', 'telefono',
         'password'),  # Persona -> 9
        ('email', 'p_iva'),  # Commerciante -> 10
        ('p_iva', 'cod_locale'),  # Possiede -> 11
        # USER
        'email',  # UtenteRegistrato ->12
        ('numero_carta', 'intestatario', 'scadenza'),  # CartaDiCredito -> 13
        ('cod_carta', 'email'),  # Utilizza -> 14
        ('email', 'date', 'cod_locale', 'voto', 'descrizione', 'p_iva'),  # Recensione -> 15
        # ORDER
        ('email', 'data', 'orario_richiesto', 'metodo_pagamento', 'cod_carta'),  # OrdineInAttesa -> 16
        ('cod_ordine', 'consegnato', 'descrizione'),  # Accettato -> 17
        ('cod_ordine', 'descrizione'),  # Rifiutato -> 18
        ('cod_ordine', 'cod_locale', 'nome_menu', 'quantita'),  # RichiedeM -> 19
        ('cod_ordine', 'cod_locale', 'nome_prodotto', 'quantita'),  # RichiedeP -> 20
    )
    tab = 0
    f = open(str(args[0]), 'r', encoding='utf8')
    for line in f:
        if line[0] == '#' or line[0] == '\n':
            continue
        line = tuple(line.replace('\n', '').split(';'))
        if [re.match('^[ ]', string) for string in line] == [None] * len(line):
            if line[0] in table:
                tab = table.index(line[0])
                # print(line[0] + ': ' + str(tab)) # DEBUG
            else:
                if not any(word in line for word in attr[tab]):
                    # print(str(line))  # DEBUG
                    # LOCAL MANAGEMENT
                    init_ex = 'q=' + str(table[tab]) + '(' + attr[tab][0]
                    if tab == 0:  # Localita
                        init_ex = init_ex + '="' + line[0] + '", ' \
                                  + attr[tab][1] + '="' + line[1] + '")'
                    elif tab == 1:  # Locale
                        init_ex = init_ex + '="' + str(line[0]) + '",' \
                                  + attr[tab][1] + '="' + line[1] + '",' \
                                  + attr[tab][2] + '="' + line[2] + '",' \
                                  + str(attr[tab][3]) + '=Localita.objects.get(cap="' + str(line[3]) + '")' + ',' \
                                  + str(attr[tab][4]) + '="' + str(line[4]) + '",' \
                                  + str(attr[tab][5]) + '="' + str(line[5]) + '"'
                        if str(line[6]) != '':
                            init_ex = init_ex + ',' + str(attr[tab][6]) + '="' + str(line[6]) + '"'
                        if str(line[7]) != '':
                            init_ex = init_ex + ',' + str(attr[tab][7]) + '="' + str(line[7]) + '"'
                        if str(line[8]) != '':
                            init_ex = init_ex + ',' + str(attr[tab][8]) + '="' + str(line[8]) + '"'
                        if str(line[9]) != '':
                            init_ex = init_ex + ',' + str(attr[tab][9]) + '="' + str(line[9]) + '"'
                        init_ex = init_ex + ')'
                    elif tab == 2:  # Chiusura
                        init_ex = init_ex + '=Locale.objects.get(cap="' + str(line[1]) \
                                  + '",nome_locale="' + str(line[0]) + '")' + ',' \
                                  + str(attr[tab][1]) + '="' + line[2] + '")'
                    elif tab == 3 and 'nome_tag' not in line:  # Tag
                        init_ex = 'q=' + str(table[tab]) + '(' + str(attr[tab]) + '="' + str(line[0]) + '")'
                    elif tab == 4:  # IdentificatoDa
                        init_ex = init_ex + '=Locale.objects.get(cap="' + str(line[1]) \
                                  + '",nome_locale="' + str(line[0]) + '")' + ',' \
                                  + str(attr[tab][1]) + '=Tag.objects.get(nome_tag="' + str(line[2]) + '"))'
                    elif tab == 5 and 'nome_tipo' not in line:  # Tipo
                        init_ex = 'q=' + str(table[tab]) + '(' + str(attr[tab]) + '="' + str(line[0]) + '")'
                    elif tab == 6:  # Prodotto
                        init_ex = init_ex + '="' + str(line[0]) + '",' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '",' \
                                  + str(attr[tab][2]) + '="' + str(line[2]) + '",' \
                                  + str(attr[tab][3]) + '=Locale.objects.get(nome_locale="' + str(line[3]) \
                                  + '",cap="' + str(line[4]) + '"),' \
                                  + str(attr[tab][4]) + '=Tipo.objects.get(nome_tipo="' + str(line[5]) + '"))'
                    elif tab == 7:  # Menu
                        init_ex = init_ex + '="' + str(line[0]) + '",' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '",' \
                                  + str(attr[tab][2]) + '="' + str(line[2]) + '",' \
                                  + str(attr[tab][3]) + '=Locale.objects.get(nome_locale="' + str(line[3]) \
                                  + '",cap="' + str(line[4]) + '"))'
                    elif tab == 8:  # CompostoDa
                        init_ex = init_ex + '=Locale.objects.get(nome_locale="' + str(line[0]) \
                                  + '",cap="' + str(line[1]) + '"),' \
                                  + str(attr[tab][1]) + '=Menu.objects.get(nome_menu="' + str(line[2]) \
                                  + '",cod_locale=Locale.objects.get(nome_locale="' + str(line[0]) \
                                  + '",cap="' + str(line[1]) + '")),' \
                                  + str(attr[tab][2]) + '=Prodotto.objects.get(nome_prodotto="' + str(line[3]) \
                                  + '",cod_locale=Locale.objects.get(nome_locale="' + str(line[0]) \
                                  + '",cap="' + str(line[1]) + '").cod_locale))'
                        # DEALER
                    elif tab == 9:  # Persona
                        init_ex = init_ex + '="' + str(line[0]) + '",' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '",' \
                                  + str(attr[tab][2]) + '="' + str(line[2]) + '",' \
                                  + str(attr[tab][3]) + '="' + str(line[3]) + '",' \
                                  + str(attr[tab][4]) + '="' + str(line[4]) + '",' \
                                  + str(attr[tab][5]) + '=Localita.objects.get(cap="' + str(line[5]) + '"),' \
                                  + str(attr[tab][6]) + '="' + str(line[6]) + '",' \
                                  + str(attr[tab][7]) + '="' + str(line[7]) + '",' \
                                  + str(attr[tab][8]) + '="' + str(line[8]) + '",' \
                                  + str(attr[tab][9]) + '="' + str(line[9]) + '")'
                    elif tab == 10:  # Commerciante
                        init_ex = init_ex + '=Persona.objects.get(email="' + str(line[0]) + '"),' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '")'
                    elif tab == 11:  # Possiede
                        init_ex = init_ex + '=Commerciante.objects.get(p_iva="' + str(line[0]) + '"),' \
                                  + str(attr[tab][1]) + '=Locale.objects.get(nome_locale="' + str(line[1]) \
                                  + '",cap="' + str(line[2]) + '"))'
                    elif tab == 12 and 'email' not in line:  # UtenteRegistrato
                        init_ex = 'q=' + str(table[tab]) + '(' + attr[tab] \
                                  + '=Persona.objects.get(email="' + str(line[0]) + '"))'
                    elif tab == 13:  # CartaDiCredito
                        init_ex = init_ex + '="' + str(line[0]) + '",' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '",' \
                                  + str(attr[tab][2]) + '="' + str(line[2]) + '")'
                    elif tab == 14:  # Utilizza
                        init_ex = init_ex + '=CartaDiCredito.objects.get(numero_carta="' + str(line[0]) + '"),' \
                                  + str(attr[tab][1]) + '=Persona.objects.get(email="' + str(line[1]) + '"))'
                        # USER
                    elif tab == 15:  # Recensione
                        init_ex = init_ex + '=UtenteRegistrato.objects.get(email="' + str(line[0]) + '"),' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '",' \
                                  + str(attr[tab][2]) + '=Locale.objects.get(nome_locale="' + str(line[2]) \
                                  + '",cap="' + str(line[3]) + '")'
                        if line[4] != '':
                            init_ex = init_ex + ',' + str(attr[tab][3]) + '="' + str(line[4]) + '"'
                        if line[5] != '':
                            init_ex = init_ex + ',' + str(attr[tab][4]) + '="' + str(line[5]) + '"'
                        if line[6] != '':
                            init_ex = init_ex + ',' + str(attr[tab][5]) + '=Commerciante.objects.get(p_iva="' \
                                      + str(line[6]) + '")'
                        init_ex = init_ex + ')'
                        # ORDER
                    elif tab == 16:  # OrdineInAttesa
                        init_ex = init_ex + '=Persona.objects.get(email="' + str(line[0]) + '"),' \
                                  + str(attr[tab][1]) + '="' + str(line[1]) + '",' \
                                  + str(attr[tab][2]) + '="' + str(line[2]) + '",' \
                                  + str(attr[tab][3]) + '="' + str(line[3]) + '"'
                        if len(line) == 5:
                            init_ex = init_ex + ',' + str(attr[tab][4]) \
                                      + '=CartaDiCredito.objects.get(numero_carta="' + str(line[4]) + '")'
                        init_ex = init_ex + ')'
                    elif tab == 17:  # Accettato
                        init_ex = init_ex + '=OrdineInAttesa.objects.get(email="' + str(line[0]) + '",' \
                                  + 'data="' + str(line[1]) + '"),' \
                                  + str(attr[tab][1]) + '="' + str(line[2]) + '",' \
                                  + str(attr[tab][2]) + '="' + str(line[3]) + '")'
                    elif tab == 18:  # Rifiutato
                        init_ex = init_ex + '=OrdineInAttesa.objects.get(email="' + str(line[0]) + '",' \
                                  + 'data="' + str(line[1]) + '"),' \
                                  + str(attr[tab][1]) + '="' + str(line[2]) + '")'
                    elif tab == 19:  # RichiedeM
                        init_ex = init_ex + '=OrdineInAttesa.objects.get(email="' + str(line[0]) + '",' \
                                  + 'data="' + str(line[1]) + '"),' \
                                  + str(attr[tab][1]) + '=Locale.objects.get(nome_locale="' + str(line[2]) + '",' \
                                  + 'cap="' + str(line[3]) + '"),' \
                                  + str(attr[tab][2]) + '=Menu.objects.get(nome_menu="' + str(line[4]) + '",' \
                                  + 'cod_locale=Locale.objects.get(nome_locale="' + str(line[2]) + '",' \
                                  + 'cap="' + str(line[3]) + '")),' \
                                  + str(attr[tab][3]) + '="' + str(line[5]) + '")'
                    elif tab == 120:  # RichiedeP
                        init_ex = init_ex + '=OrdineInAttesa.objects.get(email="' + str(line[0]) + '",' \
                                  + 'data="' + str(line[1]) + '"),' \
                                  + str(attr[tab][1]) + '=Locale.objects.get(nome_locale="' + str(line[2]) + '",' \
                                  + 'cap="' + str(line[3]) + '"),' \
                                  + str(attr[tab][2]) + '=Prodotto.objects.get(nome_prodotto="' + str(line[4]) + '",' \
                                  + 'cod_locale=Locale.objects.get(nome_locale="' + str(line[2]) + '",' \
                                  + 'cap="' + str(line[3]) + '")),' \
                                  + str(attr[tab][3]) + '="' + str(line[5]) + '")'
                    else:
                        continue

                    print(init_ex + '; q.save()')
                    exec(init_ex + '; q.save()')

        else:
            raise ValidationError('Campo non valido: %(string)s',
                                  code='invalid',
                                  params={'string': str(line)},
                                  )
    f.close()