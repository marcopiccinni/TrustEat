function autoReload(value) {
    var timeID = setTimeout("location.href= '/'", value)
}

// ---------- order/check.html
function checkStatusPayment() {
    var pay = document.getElementById("id_Pagamento");
    var sel_pay = pay.options[pay.selectedIndex].text;
    var card = document.getElementById("id_Carta");
    card.disabled = sel_pay !== "Carta di credito";
    checkValues();
}

function checkValues() {
    var pay = document.getElementById("id_Pagamento");
    var sel_pay = pay.options[pay.selectedIndex].text;
    var card = document.getElementById("id_Carta");
    var sel_card = card.options[card.selectedIndex].text;
    var errorCard = document.getElementById("id_ErrorCard");
    var button = document.getElementById("id_SubmitForm");
    var time = document.getElementById("id_Orario");
    var sel_time = time.value;
    var errorTime = document.getElementById("id_ErrorTime");
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
                console.log('carta vuota');
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
    var but = document.getElementById('id_PrintButton');
    but.hidden = true;
    print();
    but.hidden = false;
}

// ----------- acconts/registrazione.html
function setDate() {
    var dateObj = new Date();
    var month = dateObj.getMonth() + 1; //months from 1-12
    if (month < 10)
        month = String(0) + String(month);
    var day = dateObj.getDate();
    var year = dateObj.getFullYear();

    newdate = year + "-" + month + "-" + day;
    newdate = String(newdate);
    document.getElementById('scad').value = newdate;
}

// ----------- acconts/registrazione.html
function checkCard() {
    var cc = document.getElementById('cc').value;
    var check = document.getElementById('choice_1').checked;
    console.log(cc.length);
    if (check && cc == "") {
        alert('Perfavore, inserisci il codice della carta');
        var but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    }
    else if (check && cc.length != 16) {
        alert('La carta deve contenere 16 numeri');
        var but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    }
    else {
        return true;
    }
}

// ----------- acconts/registrazione.html
function checkIntestatario() {
    var intest = document.getElementById('intest').value;
    var check = document.getElementById('choice_1').checked;
    if (check && intest == "") {
        alert("Perfavore, inserisci l'intestatario della carta");
        var but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    }
    else {
        return true;
    }
}

// ----------- acconts/registrazione.html
function checkData() {
    var scad = document.getElementById('scad').value;
    var check = document.getElementById('choice_1').checked;

    var dateObj = new Date();
    var month = dateObj.getMonth() + 1; //months from 1-12
    if (month < 10)
        month = String(0) + String(month);
    var day = dateObj.getDate();
    var year = dateObj.getFullYear();

    newdate = year + "-" + month + "-" + day;
    newdate = String(newdate);

    var parts = newdate.split("-");
    newdate_num = parts[0] + parts[1] + parts[2];
    parts = scad.split("-");
    scad_num = parts[0] + parts[1] + parts[2];
    if (scad.length < 10) {
        alert("Perfavore, inserisci una data di scadenza");
        setDate();
        var but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    }
    else if (check) {
        if (parseInt(scad_num) < parseInt(newdate_num)) {
            alert("Perfavore, inserisci una carta non scaduta");
            setDate();
            var but = document.getElementById("but");
            but.setAttribute('type', 'button');
            return false;
        }
    }

    return true;
}

// ----------- acconts/registrazione.html
function checkChoice() {
    var check_yes = document.getElementById("choice_1").checked;
    var check_no = document.getElementById("choice_2").checked;

    if (!check_yes && !check_no) {
        alert("Perfavore, scegliere se aggiungere o meno la carta di credito.");
        var but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    }
    else
        return true;
}

// ----------- acconts/registrazione.html
function checkPassword() {
    var pass1 = document.getElementById('id_password1').value;
    var pass2 = document.getElementById('id_password2').value;

    if (pass1 != pass2) {
        alert("Attenzione, le due password non combaciano");
        var but = document.getElementById("but");
        but.setAttribute('type', 'button');
        return false;
    }
    else {
        if (pass1.length < 8) {
            alert("Attenzione, la password deve contenere almeno 8 caratteri");
            var but = document.getElementById("but");
            but.setAttribute('type', 'button');
            return false;
        }
        else {
            return true;
        }
    }
}

// ----------- acconts/registrazione.html
function check_check() {
    if (checkChoice() && checkCard() && checkIntestatario() && checkData() && checkPassword()) {
        var but = document.getElementById("but");
        but.setAttribute('type', 'submit');
    }
}


// ---------- conferma prima di eliminazione o cose importanti
function conf_del(question) {
    return confirm(question);
}


// function conf_del(question) {
//     if (confirm(question)) {
//         return true
//     } else
//         return false
// }