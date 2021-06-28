var currentFormBox = 0;
var listingTabHeading = ["Owner", "Deal", "Property Location", "Main Features", "Specific Features", "Equipment"];
var requestTabHeading = ["Client", "Deal", "Location", "Main Features", "Specigic Features", "Equipment"];
showFormBox(currentFormBox);

function showFormBox(n) {
    var formBoxes = document.getElementsByClassName("form-box");
    formBoxes[n].style.display = "block";
    if (n == 0) {
        document.getElementById("PrevBtn").style.display = "none";
    } else {
        document.getElementById("PrevBtn").style.display = "inline";
    } 
    if (n == (formBoxes.length - 1)) {
        if (window.location.href.indexOf("listings") > -1){
            document.getElementById("NextBtn").innerHTML = "List It !";
        } else {
            document.getElementById("NextBtn").innerHTML = "Submit It !"; 
        }
        
    } else {
        document.getElementById("NextBtn").innerHTML = "Next";
    }
    fixStepIndicator(n);
}

function nextPrev(n) {
    var formBoxes = document.getElementsByClassName("form-box");
    if (n == 1 && !validateForm()) return false;
    formBoxes[currentFormBox].style.display = "none";
    currentFormBox = currentFormBox + n;
    if (currentFormBox >= formBoxes.length) {
        if (document.getElementById("NewListingForm") != null) {
            document.getElementById("NewListingForm").submit();
        }
        else if (document.getElementById("NewRequestForm") != null) {
            document.getElementById("NewRequestForm").submit();
        }
        return false;
    }
    showFormBox(currentFormBox);
}

function validateForm() {
    var valid = true;
    if ((document.getElementById("NewListingForm") != null) || (document.getElementById("NewRequestForm") != null)) {
        // client checking if needed
        if (currentFormBox == 0) {
            var clientMainIds = ["Name", "LastName", "ClientId"];
            var clientMainIds_counter = 0
            for (let i = 0; i< clientMainIds.length; i++) {
                if (document.getElementById(clientMainIds[i]).value == "") {
                    document.getElementById(clientMainIds[i]).className += " invalid";
                    clientMainIds_counter += 1;
                    valid = false;
                } 
                if (clientMainIds_counter > 0) {
                    document.getElementById("ClientMainInfoMissing").classList.remove("d-none");
                } else {
                    document.getElementById("ClientMainInfoMissing").classList.add("d-none");
                }
            } 
            if ((document.getElementById("Phone").value == "") && (document.getElementById("Email").value == "")) {
                document.getElementById("ClientContactInfoMissing").classList.remove("d-none");
                valid = false;
            } else {
                document.getElementById("ClientContactInfoMissing").classList.add("d-none");
            }
        }

        // Propert type checking
        else if (currentFormBox == 1) {
            var propertyTypes = ["TypeApartment", "TypeCommercial", "TypeHouse", "TypeIndustrial", "TypeLand", "TypeOffice"];
            var propertyTypesCheched = 0
            for (let i = 0; i < propertyTypes.length; i++) {
                if (document.getElementById(propertyTypes[i]).checked) {
                    propertyTypesCheched += 1;
                }
            }
            if (propertyTypesCheched == 0) {
                document.getElementById("PropertyTypesError").classList.remove("d-none");
                valid = false;
            } else {
                document.getElementById("PropertyTypesError").classList.add("d-none");
            }
        }
    } 
    // Listing Deal Verification
    if ((document.getElementById("NewListingForm") != null) && (currentFormBox == 1)) {
        var deals = ["Sell", "Rent"];
        var dealsChecked = 0;
        for (let i = 0; i < deals.length; i++) {
            if(document.getElementById(deals[i]).checked) {
                dealsChecked += 1;
            }
        }
        if (dealsChecked == 0) {
            document.getElementById("NoDealSelected").classList.remove("d-none");
            valid = false;
        } else {
            document.getElementById("NoDealSelected").classList.add("d-none");
        }
        if ((document.getElementById("Sell").checked && (document.getElementById("SellPrice").value == "")) || (document.getElementById("Rent").checked && (document.getElementById("RentPrice").value == ""))) {
            document.getElementById("SpecifyPrice").classList.remove("d-none");
            valid = false;
        } else {
            document.getElementById("SpecifyPrice").classList.add("d-none");
        } 
        if (document.getElementById("Sell").checked && (document.getElementById("SellPrice").value == "")) {
            document.getElementById("SellPrice").className += " invalid";
        }
        if (document.getElementById("Rent").checked && (document.getElementById("RentPrice").value == "")) {
            document.getElementById("RentPrice").className += " invalid";
        }
    }
    // Request Deal Verification
    if ((document.getElementById("NewRequestForm") != null) && (currentFormBox == 1)) {
        if ((document.getElementById("Buy").checked == false) && (document.getElementById("Rent").checked == false)) {
            document.getElementById("NoDealSelected").classList.remove("d-none");
            valid = false;
        } else {
            document.getElementById("NoDealSelected").classList.add("d-none");
        }
    }
    // Location checking
    if ((document.getElementById("NewListingForm") != null) && (currentFormBox == 2)) {
        // Reference checking
        var locationReferenceIds = ["Region", "District", "Commune"];
        var referenceCounter = 0;
        for (let i = 0; i < locationReferenceIds.length; i++) {
            if (document.getElementById(locationReferenceIds[i]).value == "") {
                referenceCounter += 1;
            }
        }
        if (referenceCounter > 0) {
            document.getElementById("ReferenceError").classList.remove("d-none");
            valid = false;
        } else {
            document.getElementById("ReferenceError").classList.add("d-none");
        }
        //Adress Checking
        var locationAdressIds = ["Street", "StreetNumber"];
        var adressCounter = 0
        if (document.getElementById("TypeApartment").checked) {
            locationAdressIds.push("ApartmentNumber");
        }
        for (let i = 0; i < locationAdressIds.length; i++) {
            if (document.getElementById(locationAdressIds[i]).value == "") {
                document.getElementById(locationAdressIds[i]).className += " invalid";
                adressCounter += 1;
            }
            if (adressCounter > 0) {
                document.getElementById("AdressError").classList.remove("d-none");
                valid = false;
            } else {
                document.getElementById("AdressError").classList.add("d-none");
            }
        }

    }
    if (valid) {
        document.getElementsByClassName("form-step")[currentFormBox].className += " finish";
    }
    return valid;
}

function fixStepIndicator(n) {
    var steps = document.getElementsByClassName("form-step");
    var headings = document.getElementById("StepHeading");
    for (let i = 0; i < steps.length; i++) {
        steps[i].className = steps[i].className.replace(" active", "");
    }
    steps[n].className += " active";

    if (document.getElementById("NewListingForm") != null) {
        headings.innerHTML = listingTabHeading[n];
    }
    if (document.getElementById("NewRequestForm") != null) {
        headings.innerHTML = requestTabHeading[n];
    }
}   
