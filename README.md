Questo e' un sito di food delivery. In questa app di django, i commercianti possono inserire i propri locali e gli utenti possono ordinare il cibo.

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

Il sito sara' visitabile all'indirizzo **127.0.0.1:8000**.
