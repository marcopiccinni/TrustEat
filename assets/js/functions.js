function autoReload(value) {
    setTimeout("location.href= '/'", value)
}

// ---------- order/check.html
function checkStatusPayment() {
    let pay = document.getElementById("id_Pagamento");
    let sel_pay = pay.options[pay.selectedIndex].text;
    let card = document.getElementById("id_Carta");
    card.disabled = sel_pay !== "Carta di credito";
    checkValues();
}

// ---------- order/check.html
function checkValues() {
    let pay = document.getElementById("id_Pagamento");
    let sel_pay = pay.options[pay.selectedIndex].text;
    let card = document.getElementById("id_Carta");
    let sel_card = card.options[card.selectedIndex].text;
    let errorCard = document.getElementById("id_ErrorCard");
    let button = document.getElementById("id_SubmitForm");
    let time = document.getElementById("id_Orario");
    let sel_time = time.value;
    let errorTime = document.getElementById("id_ErrorTime");
    if (sel_time === '') {
        errorTime.hidden = false;
        button.classList.add("disabled");
        button.setAttribute('type', 'button');
    } else if (sel_time > time.min && sel_time < time.max) {
        errorTime.hidden = true;
        button.classList.remove("disabled");
        button.setAttribute('type', 'submit');
        if (sel_pay === "Carta di credito") {
            if (sel_card === '---------') {
                errorCard.hidden = false;
                button.classList.add("disabled");
                button.setAttribute('type', 'button');
            } else {
                errorCard.hidden = true;
                button.classList.remove("disabled");
                button.setAttribute('type', 'submit');
            }
        } else {
            errorCard.hidden = true;
            button.classList.remove("disabled");
            button.setAttribute('type', 'submit');
        }
    } else {
        errorTime.hidden = false;
        button.classList.add("disabled");
        button.setAttribute('type', 'button');
    }
}

// ---------------- order/placed_order.html
function stampa() {
    let but = document.getElementById('id_PrintButton');
    but.hidden = true;
    print();
    but.hidden = false;
}

// ----------- acconts/registrazione.html
function setDate() {
    let dateObj = new Date();
    let month = dateObj.getMonth() + 1; //months from 1-12
    if (month < 10)
        month = String(0) + String(month);
    let day = dateObj.getDate();
    let year = dateObj.getFullYear();

    document.getElementById('scad').value = String(year + "-" + month + "-" + day);
}

// ----------- acconts/registrazione.html
function checkCard() {
    let cc = document.getElementById('cc').value;
    let check = document.getElementById('choice_1').checked;
    let but = document.getElementById("but");
    if (check && cc === "") {
        alert('Perfavore, inserisci il codice della carta');
        but.setAttribute('type', 'button');
        return false;
    } else if (check && cc.length !== 16) {
        alert('La carta deve contenere 16 numeri');
        but.setAttribute('type', 'button');
        return false;
    } else
        return true;
}

// ----------- acconts/registrazione.html
function checkIntestatario() {
    let intest = document.getElementById('intest').value;
    let check = document.getElementById('choice_1').checked;
    if (check && intest === "") {
        alert("Perfavore, inserisci l'intestatario della carta");
        let but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    } else
        return true;
}

// ----------- acconts/registrazione.html
function checkData() {
    let scad = document.getElementById('scad').value;
    let check = document.getElementById('choice_1').checked;

    let dateObj = new Date();
    let month = dateObj.getMonth() + 1; //months from 1-12
    if (month < 10)
        month = String(0) + String(month);
    let day = dateObj.getDate();
    let year = dateObj.getFullYear();

    let newdate = String(year + "-" + month + "-" + day);

    let parts = newdate.split("-");
    let newdate_num = parts[0] + parts[1] + parts[2];
    parts = scad.split("-");
    let scad_num = parts[0] + parts[1] + parts[2];
    let but = document.getElementById("but");
    if (scad.length < 10) {
        alert("Perfavore, inserisci una data di scadenza");
        setDate();
        but.setAttribute('type', 'button');
        return false;
    } else if (check && parseInt(scad_num) < parseInt(newdate_num)) {
        alert("Perfavore, inserisci una carta non scaduta");
        setDate();
        but.setAttribute('type', 'button');
        return false;
    }
    return true;
}

// ----------- acconts/registrazione.html
function checkChoice() {
    let check_yes = document.getElementById("choice_1").checked;
    let check_no = document.getElementById("choice_2").checked;

    if (!check_yes && !check_no) {
        alert("Perfavore, scegliere se aggiungere o meno la carta di credito.");
        let but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    } else
        return true;
}

// ----------- acconts/registrazione.html
function checkPassword() {
    let pass1 = document.getElementById('id_password1').value;
    let pass2 = document.getElementById('id_password2').value;
    let but = document.getElementById("but");

    if (pass1 !== pass2) {
        alert("Attenzione, le due password non combaciano");
        but.setAttribute('type', 'button');
        return false;
    } else {
        if (pass1.length < 8) {
            alert("Attenzione, la password deve contenere almeno 8 caratteri");
            but.setAttribute('type', 'button');
            return false;
        } else
            return true;
    }
}

// ----------- acconts/registrazione.html
function check_check() {
    if (checkChoice() && checkCard() && checkIntestatario() && checkData() && checkPassword()) {
        let but = document.getElementById("but");
        but.setAttribute('type', 'submit');
    }
}

// ---------- conferma prima di eliminazione o cose importanti
function conf_del(question) {
    return confirm(question);
}

// ------------ order/list_order.html
function selection_view(button_selected) {
    document.getElementById('delivering').hidden = true;
    document.getElementById('delivered').hidden = true;
    document.getElementById('refused').hidden = true;

    document.getElementById("Da consegnare").className = document.getElementById("Da consegnare").className.replace(/(?:^|\s)btn-light(?!\S)/g, ' btn-outline-light ');
    document.getElementById("Consegnati").className = document.getElementById("Consegnati").className.replace(/(?:^|\s)btn-light(?!\S)/g, ' btn-outline-light ');
    document.getElementById("Rifiutati").className = document.getElementById("Rifiutati").className.replace(/(?:^|\s)btn-light(?!\S)/g, ' btn-outline-light ');

    switch (button_selected) {
        case 'Da consegnare':
            document.getElementById('delivering').hidden = false;
            document.getElementById(button_selected).className = document.getElementById(button_selected).className.replace(/(?:^|\s)btn-outline-light(?!\S)/g, ' btn-light ');
            break;
        case 'Consegnati':
            document.getElementById('delivered').hidden = false;
            document.getElementById(button_selected).className = document.getElementById(button_selected).className.replace(/(?:^|\s)btn-outline-light(?!\S)/g, ' btn-light ');
            break;
        case 'Rifiutati':
            document.getElementById('refused').hidden = false;
            document.getElementById(button_selected).className = document.getElementById(button_selected).className.replace(/(?:^|\s)btn-outline-light(?!\S)/g, ' btn-light ');
            break;
    }
}
