
// Sell - Rent Enable Price Input
function enableFormInput(checkbox_id, input_id) {
    let checkbox = document.getElementById(checkbox_id);
    let input = document.getElementById(input_id);
    
    if (checkbox.checked == true) {
        input.disabled = false;
    } else {
        input.disabled = true;
        input.value = "";
    }
}

// Show hidden div when sell selected
function showInput(checkbox_id, input_id) {
    let checkbox = document.getElementById(checkbox_id);
    let input = document.getElementById(input_id);

    if (checkbox.checked == true) {
        input.style.display = "block";
    } else {
        input.style.display = "none";
        input.disabled = true;
    }
}

// Update condition text. 
function updateValueField(selected_value, content_field_id, method) {
    let content = document.getElementById(content_field_id)

    switch(selected_value) {
        case '1':
            if (method === 'listing') {
                content.innerHTML = "<small><strong>Needs Full Renovation</strong></small>";
            } else if (method === 'request') {
                content.innerHTML = "<small><strong>Full Renovation</strong></small>";
            }
            content.style.color = "rgb(255, 0, 0)"
            break;
        case '2':
            if (method === 'listing') {
                content.innerHTML = "<small><strong>Needs Some Renovation</strong></small>";
            } else if (method === 'request') {
                content.innerHTML = "<small><strong>Some Renovation</strong></small>";
            }
            content.style.color = "rgb(255, 150, 0)"
            break;
        case '3':
            content.innerHTML = "<small><strong>Regular</strong></small>";
            content.style.color = "rgb(238, 203, 2)"
            break;
        case '4':
            content.innerHTML = "<small><strong>Good</strong></small>";
            content.style.color = "rgb(103, 197, 92)"
            break;
        case '5':
            content.innerHTML = "<small><strong>Excellent</strong></small>";
            content.style.color = "rgb(17, 161, 0)"
            break;       
    }
}

// Enable New Location Button
let checkedCommunes = 0;
function enableNewLocationBtn(checkboxid, buttonid) {
    let button = document.getElementById(buttonid);
    let checkbox = document.getElementById(checkboxid);
    
    if (checkbox.checked === true) {
        checkedCommunes += 1;
    } else {
        checkedCommunes -= 1;
    }

    if (checkedCommunes === 0) {
        button.disabled = true;
    } else {
        button.disabled = false;
    }
}

// Add New Location Input
let referenceCounter = 1;
function addLocationInput(btnid) { 

    referenceCounter += 1; 
    checkedCommunes = 0;
     button = document.getElementById(btnid);
     button.disabled = true;
    let newInput = document.getElementById("NewLocationInput");
    
    // Crear titulo 
    const h3 = document.createElement('h3');
    h3.setAttribute('class', 'box-subheading');
    const strong = document.createElement('strong');
    strong.textContent = 'Reference ' + referenceCounter.toString();
    h3.appendChild(strong);
    const hr = document.createElement('hr');
    hr.setAttribute('class', 'mt-0');
    
    // Crear col div
    const wrapDiv = document.createElement('div');
    wrapDiv.setAttribute('class', 'col-6 px-4');
    // Crear row div
    const rowDiv = document.createElement('div');
    rowDiv.setAttribute('class', 'form-row');

    // Crear los distintos inputs
    const inputsList = ['Region', 'District', 'Commune'];
    
    for (let inputItem of inputsList) {
        // Crear col-12 & form-group
        let colDiv = document.createElement('div');
        colDiv.setAttribute('class', 'col-12');
        let formGroupDiv = document.createElement('div');
        formGroupDiv.setAttribute('class', 'form-group');
        
        // Crear Label
        let label = document.createElement('label');
        label.setAttribute('for', inputItem + referenceCounter.toString());
        label.textContent = inputItem;

        if (inputItem === 'Commune') {
            // Crear Div para grupo checkbox
            let checkboxWindow = document.createElement('div');
            checkboxWindow.setAttribute('id', 'Commune' + referenceCounter.toString());
            checkboxWindow.setAttribute('class', 'checkbox-group');
            checkboxWindow.setAttribute('style', 'padding-left: 30px;');
            
            formGroupDiv.appendChild(label);
            formGroupDiv.appendChild(checkboxWindow);
            colDiv.appendChild(formGroupDiv);

        } else {
            // Crear Select
            let select = document.createElement('select');
            select.setAttribute('class', 'custom-select');
            select.setAttribute('name', inputItem.toLowerCase() + referenceCounter.toString());
            select.setAttribute('id', inputItem + referenceCounter.toString());
            if (inputItem === 'Region') {
                select.setAttribute('onchange', 'showDistricts(this.value, "' + (inputsList[1] + referenceCounter.toString()) + '", "' + (inputsList[2] + referenceCounter.toString()) + '", "checkbox")');
            } else if (inputItem === 'District') {
                select.setAttribute('onchange', 'showCommunes(this.value, "Commune' + referenceCounter.toString() + '", "checkbox")');
            }
            // Crear Option
            let option = document.createElement('option');
            option.setAttribute('value', '');
            option.textContent = '--';

            // Agrupar Input
            select.appendChild(option);
            formGroupDiv.appendChild(label);
            formGroupDiv.appendChild(select);
            colDiv.appendChild(formGroupDiv);
            
        }
          
        // Añadir a form-row
        rowDiv.appendChild(colDiv);
    }

    // Armar Conjunto
    wrapDiv.append(h3, hr, rowDiv);
    newInput.appendChild(wrapDiv);

    // Agregar botón al final
    var newLocationDiv = document.getElementById("NewLocationDiv");
    newLocationDiv.parentNode.removeChild(newLocationDiv);
    newInput.appendChild(newLocationDiv);

    // Mostrar regiones
    showRegions('Region' + referenceCounter.toString());
}


// Read Regions from CSV
const territory = [];
const regions = [];
async function readCsv() {
    const response = await fetch('/static/OT_Chile.csv');
    const data = await response.text();
    // Slice saca el indice 1
    const rows = data.split('\n').slice(1);
    
    rows.forEach(row => {
        const col = row.split(';');
        territory.push(col);  
        if (regions.indexOf(col[0]) === -1) {
            regions.push(col[0]);
        }         
    });
}

// Show Regions
async function showRegions(element_id) {
    await readCsv();
    let selectRegion = document.getElementById(element_id);
    for (let i = 0; i < regions.length; i++) {
        selectRegion.innerHTML += "<option value=\"" + regions[i] + "\">" + regions[i] + "</option>";
    }
}

// Show Districts
function showDistricts(region, district, commune, mode) {
    let selectDistrict = document.getElementById(district);
    let selectCommune = document.getElementById(commune);
    

    selectDistrict.innerHTML = "<option value='' selected disabled>--</option>";
    if (mode === 'single') {
        selectCommune.innerHTML = "<option value='' selected disabled>--</option>";
    } else if (mode === 'checkbox') {
        selectCommune.innerHTML = "<!-- Generated by Javascript -->";
        let newLocationBtn = document.getElementById("NewLocation");
        newLocationBtn.disabled = true;
        checkedCommunes = 0;
    }

    let districts = [];
    for (let i = 0; i < territory.length; i++) {
        if (region === territory[i][0]) {
            if (districts.indexOf(territory[i][1]) === -1) {
                districts.push(territory[i][1]);
            }
        }
    }
    for (let i = 0; i < districts.length; i++) {
        selectDistrict.innerHTML += "<option value=\"" + districts[i] + "\">" + districts[i] + "</option>";
    }
}

// Show Communes
function showCommunes(district, commune, display) {
    let selectCommune = document.getElementById(commune);
    let communes = [];
    for (let i = 0; i < territory.length; i++) {
        if (district === territory[i][1]) {
            if (communes.indexOf(territory[i][2]) === -1) {
                communes.push(territory[i][2]);
            }
        }
    }
    if (display === 'single') {
        selectCommune.innerHTML = "<option value='' selected disabled>--</option>";
        for (let i = 0; i < communes.length; i++) {
            selectCommune.innerHTML += "<option value=\"" + communes[i] + "\">" + communes[i] + "</option>";
        }
    } else if (display === 'checkbox') {
        selectCommune.innerHTML = "<!-- Generated by Javascript -->";
        for (let i = 0; i < communes.length; i++) {
            // Create Checkbox Group
            checkboxDiv = document.createElement('div');
            checkboxDiv.setAttribute('class', 'custom-control');
            checkboxDiv.setAttribute('class', 'custom-checkbox');

            // Create Checkbox
            input = document.createElement('input');
            input.setAttribute('type','checkbox');
            input.setAttribute('class', 'custom-control-input');
            input.setAttribute('id', ('Commune' + referenceCounter.toString() + communes[i].replace(/\s+/g, '')));
            input.setAttribute('name', ('communes' + referenceCounter.toString() + '[]'));
            input.setAttribute('value', communes[i]);
            input.setAttribute('onchange', 'enableNewLocationBtn(this.id, "NewLocation")');

            // Create Label
            label = document.createElement('label');
            label.setAttribute('for', ('Commune' + referenceCounter.toString() + communes[i].replace(/\s+/g, '')));
            label.setAttribute('class', 'custom-control-label');
            label.textContent = communes[i];

            checkboxDiv.appendChild(input);
            checkboxDiv.appendChild(label);
            selectCommune.appendChild(checkboxDiv);
        }
    }
}

function logValue(value) {
    console.log(value);
}

function listingAlert(element_id, action) {
    if (action == 'delete') {
        let message = confirm("Are you sure you want to delete this property?");
        if (message == true) {
            window.location.replace("/listings/delete/listing-id=" + element_id);
        }
    } else if (action == 'turnOff') {
        let message = confirm("Are you sure you want to turn off this operation?");
        if (message == true) {
            window.location.replace("/listings/turn-operation-off/operation-id=" + element_id);
        }
    }
    
}
function requestAlert(element_id, action) {
    if (action == 'turnOff') {
        let message = confirm("Are you sure you want to turn off this operation?");
        if (message = true) {
            window.location.replace("/requests/turn-operation-off/operation-id=" + element_id);
        }
    } else if (action == 'delete') {
        let message = confirm("Are you sure you want to delete this request?");
        if (message == true) {
            window.location.replace("/requests/delete/request-id=" + element_id);
        }
    }
}
