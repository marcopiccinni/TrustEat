Questo è un sito di food delivery. In questa app di django, i commercianti possono inserire i propri locali e gli utenti possono ordinare il cibo.

Primo, installare python 3.7.1

Lanciare il comando per conoscere le alternative:
```bash
update-alternatives --list python
```

Se da errore eseguire il comando:

```bash
update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
```

Per impostare la priorità ad 1 di python3.7.1 utilizzando il comando python contenuto nella cartella di default /usr/bin/.

Nello stesso modo è possibile inserire anche le alternative, impostando i livelli di priorità differenti, nel caso si volesse, si può switchare velocemente utilizzando update-alternatives.

Altrimenti è possibile usare direttamente il comando:
```bash
update-alternatives --config python
```

Per verificare la corretta modifica dell'interprete di default:
```bash
python --version
```


Secondo, clonare il repository nella tua macchina locale:

```bash
git clone https://github.com/django/django.git
```

Terzo, installare le dipendenze:

```bash
pip install -r requirements.txt
```

Quarto ed ultimo, avviare il server.

```bash
python manage.py runserver
```

Il sito sarà visitabile all'indirizzo **127.0.0.1:8000**.

----------------------------------------------------------------------------------------------------------------------------------------

Contenuto del db:

Il db, caricabile attraverso il seguente comando:

```bash
python manage.py loaddata dati_db_trusteat.json
```

 contiene svariati utenti/commercianti (sarano omessi tuttavia gli utenti creati con la registrazione tramite Google per ovvi motivi) e sono i seguenti:

utenti:

	username: Calvin
	password: Dinamici

	username: Louis
	password: Dinamici


commercianti:

	username: PaperonDePaperoni
	password: Dinamici

	username: Quadro
	password: Dinamici


admin:
	
	username: admin
	password: admin


Gli utenti hanno già effettuato ordini, quindi troveremo già ordini consegnati/rifiutati e relative recensioni lasciate ai locali con, in alcuni casi, le risposte da parte dei commercianti.
Per testare gli ordini in attesa è invece necessario effettuare un ordine, in quanto essi, scoccata la mezzanotte di ogni giorno, vengono impostati come rifiutati, perchè il sito si basa su ordini gestiti giorno per giorno.
Ovviamente sono presenti anche locali in differenti località, con vari prodotti e menù.

N.B. Ricordarsi di spostare un ordine da "ordine in attesa" a "confermato" per poter visualizzare il relativo segnalino sulla mappa.
