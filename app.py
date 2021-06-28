from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from copy import deepcopy

from helpers import (login_required, client_verif, location_verif, deal_verif, select_lastId, insert_client, select_location, insert_tengo, 
                    insert_operacion, insert_busco, insert_caracteristicas, insert_location, match_operation, match_location, match_propertyType, 
                    match_carRangos, match_carOpciones, match_equipamiento, insert_match, asign_roles, asign_listingOperations, asign_listingPropertyTypes,
                    count_listingStatus, get_caracteristicas, order_clientsRequests, asingn_requestOperations, asign_requestPropertyTypes,
                    count_requestStatus, asign_requestGeneralities, asign_requestLocations, insert_nuevaOperacion, asign_matchClients, asign_matchListings,
                    asign_matchPropertyTypes, asign_matchOperations, count_matchStatus)

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///renection.db")

# Global user full name
username = dict()

def get_username(user_id):
    db = SQL("sqlite:///renection.db")
    username = db.execute("SELECT nombre, apellido FROM usuarios WHERE id = ?",
                user_id)
    return username[0]
    


#/////////////////////////////////////// HOME PAGE /////////////////////////////////////////////////////
@app.route("/")
@login_required
def index():
    global username 
    username = get_username(session["user_id"])

    return redirect("/matching")


#/////////////////////////////////////// REGISTER /////////////////////////////////////////////////////

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")
    
    else: 
        # Verificar input de email, nombre, apellido
        if not request.form.get("email"):
            return render_template("register.html")
        elif not request.form.get("name"):
            return render_template("register.html")
        elif not request.form.get("lastname"):
            return render_template("register.html")
        # Verificar que no exista el usuario
        db = SQL("sqlite:///renection.db")
        verificar_usuario = db.execute("SELECT email FROM usuarios WHERE email = :email",
                                        email=request.form.get("email"))
        if len(verificar_usuario) == 1:
            return render_template("register.html")
        # Verificar contraseña
        elif not request.form.get("password"):
            return render_template("register.html")
        # Verificar confirmación
        elif request.form.get("password") != request.form.get("confirm"):
            return render_template("register.html")

        # Ingresar usuario a base de datos
        db.execute("INSERT INTO usuarios (email, hash, nombre, apellido) VALUES (:email, :hash, :nombre, :apellido)",
                email=request.form.get("email"), hash=generate_password_hash(request.form.get("password")),
                nombre=request.form.get("name"), apellido=request.form.get("lastname"))

        # Recordar qué usuario se registró
        user = db.execute("SELECT * FROM usuarios WHERE email = :email",
                        email=request.form.get("email"))
        session["user_id"] = user[0]["id"]

        # Redireccionar a home:
        return redirect("/")

#/////////////////////////////////////// LOGIN /////////////////////////////////////////////////////

@app.route("/login", methods=["GET", "POST"])
def login():

    # Olvidar cualquier inicio de sesion
    session.clear() 

    if request.method == "GET":
        return render_template("login.html")

    else:
        db = SQL("sqlite:///renection.db")
        # Verificar input de email
        if not request.form.get("email"):
            return render_template("login.html")

        # Verificar input de contraseña
        elif not request.form.get("password"):
            return render_template("login.html")

        # Verificar email en base de datos:
        rows = db.execute("SELECT * FROM usuarios WHERE email = :email",
                          email=request.form.get("email"))

        # Verificar que el usuario exista y que su contraseña sea correcta
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html")

        # Recordar que usuario ingresó
        session["user_id"] = rows[0]["id"]

        # Redireccionar usuario a página de inicio
        return redirect("/")


#/////////////////////////////////////// NEW LISTING /////////////////////////////////////////////////////

@app.route("/listings/new", methods=["GET", "POST"])
@login_required
def new_listing():
    if request.method == "GET":
        return render_template("new_listing.html", user=username)

    else:
        db = SQL("sqlite:///renection.db")
        #-------------- VERFICATION -----------------------
        if deal_verif("listing") == "error":
            return redirect("/listings/new") 
        if client_verif() == "error":
            return redirect("/listings/new")
        if location_verif() == "error":
            return redirect("/listings/new")

        # ------------ INGRESAR PROPIEDAD -----------------      
        # Ingresar propietario
        insert_client()
        id_dueno = select_lastId("clientes")

        # Ingresar tengo
        id_ubicacion = select_location("region", "district", "commune") 
        insert_tengo(id_dueno, id_ubicacion)
        id_tengo = select_lastId("tengo")
        
        # Ingresar operacion 
        modalidades = list()
        if request.form.get("sell") == '1':
            modalidades.append("venta")
        if request.form.get("rent") == '1':
            modalidades.append("arriendo")
        for modalidad in modalidades:
            insert_operacion("tengo_operacion", modalidad, id_tengo)
        
        # Ingresar características
        insert_caracteristicas("tengo_tipo_de_propiedad", id_tengo)
        insert_caracteristicas("tengo_caracteristicas_rangos", id_tengo)
        insert_caracteristicas("tengo_caracteristicas_opciones", id_tengo)
        insert_caracteristicas("tengo_equipamiento", id_tengo)

        # ------------ COMPARAR CON REQUERIMIENTOS -----------------  
        categoria = "tengo"
        for modalidad in modalidades:
            candidatos_operaciones = db.execute ("SELECT busco_operacion.id, busco_operacion.id_busco, busco_operacion.precio_min, busco_operacion.precio_max FROM busco_operacion INNER JOIN busco ON busco_operacion.id_busco = busco.id WHERE busco.id_usuario = ? AND busco_operacion.tipo = ? AND busco_operacion.activo = 1", 
                                    session["user_id"], modalidad)
            candidatos = deepcopy(candidatos_operaciones)
            idsBusquedas = match_operation(modalidad, id_tengo, categoria, candidatos)
            if len(idsBusquedas) >= 1:
                idsBusquedas = match_location(idsBusquedas, id_tengo, categoria)
                if len(idsBusquedas) >= 1:
                    idsBusquedas = match_propertyType(idsBusquedas, id_tengo, categoria)
                    if len(idsBusquedas) >= 1:
                        idsBusquedas = match_carRangos(idsBusquedas, id_tengo, categoria)
                        if len(idsBusquedas) >= 1:
                            idsBusquedas = match_carOpciones(idsBusquedas, id_tengo, categoria)
                            if len(idsBusquedas) >= 1:
                                idsBusquedas = match_equipamiento(idsBusquedas, id_tengo, categoria)
                                if len(idsBusquedas) >= 1:
                                    insert_match(idsBusquedas, id_tengo, categoria, candidatos_operaciones, modalidad)

        # --------- REDIRECCIONAR A DASHBOARD -------------
        return redirect("/")

#/////////////////////////////////////// NEW REQUEST /////////////////////////////////////////////////////

@app.route("/requests/new", methods=["GET", "POST"])
@login_required
def new_request():
    if request.method == "GET":
        return render_template("new_request.html", user=username)

    else: 
        db = SQL("sqlite:///renection.db")
        #--------------  VERFICATION ----------------------
        if client_verif() == "error":
            return redirect("/requests/new")

        if deal_verif("request") == "error":
            return redirect("/requests/new")

        # ------------- INGRESAR BÚSQUEDA ------------------

        # Ingresar cliente
        insert_client()
        id_cliente = select_lastId("clientes")

        # Ingresar a busco
        insert_busco(id_cliente)
        id_busco = select_lastId("busco")
        
        # Ingresar operacion
        modalidades = list()
        if request.form.get("buy") == '1':
            modalidades.append("venta")
        if request.form.get("rent") == '1':
            modalidades.append("arriendo")
        for modalidad in modalidades:
            insert_operacion("busco_operacion", modalidad, id_busco)

        # Ingresar ubicacion
        insert_location(id_busco)
        
        # Ingresar caracteristicas
        insert_caracteristicas("busco_tipo_de_propiedad", id_busco)
        insert_caracteristicas("busco_caracteristicas_rangos" ,id_busco)
        insert_caracteristicas("busco_caracteristicas_opciones", id_busco)
        insert_caracteristicas("busco_equipamiento", id_busco)

        # ----------- COMPARAR CON LISTINGS ----------------
        categoria = "busco"
        for modalidad in modalidades:
            candidatos_operaciones = db.execute("SELECT tengo_operacion.id, tengo_operacion.id_tengo, tengo_operacion.precio FROM tengo_operacion INNER JOIN tengo ON tengo_operacion.id_tengo = tengo.id WHERE tengo.id_usuario = ? AND tengo_operacion.tipo = ? AND tengo_operacion.activo = 1",
                                                session["user_id"], modalidad)
            candidatos = deepcopy(candidatos_operaciones)
            idsPropiedades = match_operation(modalidad, id_busco, categoria, candidatos)
            if len(idsPropiedades) >= 1:
                idsPropiedades = match_location(idsPropiedades, id_busco, categoria)
                if len(idsPropiedades) >= 1:
                    idsPropiedades = match_propertyType(idsPropiedades, id_busco, categoria)
                    if len(idsPropiedades) >= 1:
                        idsPropiedades = match_carRangos(idsPropiedades, id_busco, categoria)
                        if len(idsPropiedades) >= 1:
                            idsPropiedades = match_carOpciones(idsPropiedades, id_busco, categoria)
                            if len(idsPropiedades) >= 1:
                                idsPropiedades = match_equipamiento(idsPropiedades, id_busco, categoria)
                                if len(idsPropiedades) >= 1:
                                    insert_match(idsPropiedades, id_busco, categoria, candidatos_operaciones, modalidad)


        # ----------- REDIRECCIONAR A DASHBOARD ----------------
        return redirect("/")

#/////////////////////////////////////// REQUESTS /////////////////////////////////////////////////////

@app.route("/requests")
@login_required
def myrequests():
    db = SQL("sqlite:///renection.db")
    
    requerimientos = db.execute("SELECT busco.id, busco.id_cliente, busco.fecha, clientes.ci, clientes.nombre, clientes.apellido, clientes.telefono, clientes.email FROM busco INNER JOIN clientes ON busco.id_cliente = clientes.id WHERE busco.id_usuario = ? ORDER BY busco.id DESC",
                                session["user_id"])
    
    if requerimientos:
        
        ids_requerimientos = list()
        for i in range(len(requerimientos)):
            ids_requerimientos.append(requerimientos[i]["id"])
        
        placeholders = ', '.join('?' * len(ids_requerimientos))
        operaciones = db.execute("SELECT * FROM busco_operacion WHERE id_busco IN (%s) ORDER BY id DESC" % placeholders,
                                    tuple(ids_requerimientos))
        tipos_de_propiedades = db.execute("SELECT id_busco, tipo FROM busco_tipo_de_propiedad WHERE id_busco IN (%s) ORDER BY id DESC" % placeholders,
                                            tuple(ids_requerimientos))
        generalidades = db.execute("SELECT id_busco, columna, valor FROM busco_caracteristicas_rangos WHERE columna IN ('dormitorios_min', 'dormitorios_max', 'banos_min', 'banos_max', 'estacionamientos_min', 'estacionamientos_max', 'bodegas_min', 'bodegas_max') AND id_busco IN (%s) ORDER BY id DESC" % placeholders,
                                    tuple(ids_requerimientos))
        ubicaciones = db.execute("SELECT config_busco_ubicacion.id_busco, ubicacion.region, ubicacion.comuna FROM config_busco_ubicacion INNER JOIN ubicacion ON config_busco_ubicacion.id_ubicacion = ubicacion.id WHERE id_busco IN (%s)" % placeholders,
                                tuple(ids_requerimientos))

        requerimientos = asingn_requestOperations(requerimientos, operaciones)
        requerimientos = asign_requestPropertyTypes(requerimientos, tipos_de_propiedades)
        requerimientos = asign_requestGeneralities(requerimientos, generalidades)
        requerimientos = asign_requestLocations(requerimientos, ubicaciones)
        resumen = count_requestStatus(requerimientos)
    

    else: 
        resumen = {
        "activos": 0,
        "inactivos": 0,
        "activos_compra": 0,
        "inactivos_compra": 0,
        "activos_arriendo": 0,
        "inactivos_arriendo": 0
        }
        
    return render_template("requests.html", requerimientos=requerimientos, resumen=resumen, user=username)

#/////////////////////////////////////// REQUEST DELETE/////////////////////////////////////////////////////
@app.route("/requests/delete/request-id=<request_id>")
@login_required
def deletete_request(request_id):
    db = SQL("sqlite:///renection.db")
    db.execute("DELETE FROM match WHERE id_busco = ?",
                request_id)
    db.execute("DELETE FROM busco_equipamiento WHERE id_busco = ?",
                request_id)
    db.execute("DELETE FROM busco_caracteristicas_opciones WHERE id_busco = ?",
                request_id)
    db.execute("DELETE FROM busco_caracteristicas_rangos WHERE id_busco = ?",
                request_id)
    db.execute("DELETE FROM busco_tipo_de_propiedad WHERE id_busco = ?",
                request_id)
    db.execute("DELETE FROM busco_operacion WHERE id_busco = ?",
                request_id)
    id_cliente = db.execute("SELECT id_cliente FROM busco WHERE id = ?",
                            request_id)
    db.execute("DELETE FROM busco WHERE id = ?",
                request_id)
    db.execute("DELETE FROM clientes WHERE id = ?",
                id_cliente[0]["id_cliente"])
    
    return redirect("/requests")



#/////////////////////////////////////// MATCHING /////////////////////////////////////////////////////
@app.route("/matching")
@login_required
def mymatching():
    db = SQL("sqlite:///renection.db")

    matches = db.execute("SELECT * FROM match WHERE id_usuario = ? ORDER BY id DESC",
                            session["user_id"])
    if matches:
        busquedas_clientes = db.execute("SELECT busco.id, clientes.ci, clientes.nombre, clientes.apellido, clientes.telefono, clientes.email FROM busco INNER JOIN clientes ON busco.id_cliente = clientes.id WHERE busco.id IN (SELECT id_busco FROM match WHERE id_usuario = ?) ORDER BY busco.id DESC",
                                    session["user_id"])
        tipos_propiedad_requerimientos = db.execute("SELECT id_busco, tipo FROM busco_tipo_de_propiedad WHERE id_busco IN (SELECT id_busco FROM match WHERE id_usuario = ?) ORDER BY id DESC",
                                                    session["user_id"])
        propiedades = db.execute("SELECT tengo.id, tengo.calle, tengo.numero, tengo.depto, ubicacion.region, ubicacion.comuna, tengo_caracteristicas_rangos.dormitorios, tengo_caracteristicas_rangos.banos, tengo_caracteristicas_rangos.estacionamientos, tengo_caracteristicas_rangos.bodegas, tengo_caracteristicas_rangos.superficie_u, tengo_caracteristicas_rangos.superficie_t FROM ((tengo INNER JOIN ubicacion ON tengo.id_ubicacion = ubicacion.id) INNER JOIN tengo_caracteristicas_rangos ON tengo.id = tengo_caracteristicas_rangos.id_tengo) WHERE tengo.id IN (SELECT id_tengo FROM match WHERE id_usuario = ?) ORDER BY tengo.id DESC",
                                    session["user_id"])
        operaciones_propiedades = db.execute("SELECT id, tipo, precio FROM tengo_operacion WHERE id IN (SELECT id_tengo_operacion FROM match WHERE id_usuario = ?) ORDER BY id DESC",
                                                session["user_id"])
        tipos_propiedad_propiedades = db.execute("SELECT id_tengo, tipo FROM tengo_tipo_de_propiedad WHERE id_tengo IN (SELECT id_tengo FROM match WHERE id_usuario = ?) ORDER BY id DESC",
                                                    session["user_id"])

        matches = asign_matchClients(matches, busquedas_clientes)
        matches = asign_matchListings(matches, propiedades)
        matches = asign_matchPropertyTypes(matches, tipos_propiedad_propiedades, tipos_propiedad_requerimientos)
        matches = asign_matchOperations(matches, operaciones_propiedades)
        resumen = count_matchStatus(matches)
    
    else:
        resumen = {
            "nodisponibles_compra": 0,
            "activos_compra": 0,
            "inactivos_compra": 0,
            "concretados_compra": 0,
            "nodisponibles_arriendo": 0,
            "activos_arriendo": 0,
            "inactivos_arriendo": 0,
            "concretados_arriendo": 0
    }

    return render_template("matching.html", user=username, matches=matches, resumen=resumen)

#/////////////////////////////////////// MANAGE MATCHING /////////////////////////////////////////////////////
@app.route("/matching/manage-match/action=<action>&match-id=<match_id>")
@login_required
def manage_match(action, match_id):
    
    db = SQL("sqlite:///renection.db")
    
    if action == 'activate':
        estado = 1
    elif action == 'deactivate':
        estado = 2
    elif action == 'leased':
        estado = 3
    elif action == 'sold':
        estado = 3
        idbusco_idtengo = db.execute("SELECT id_busco, id_tengo FROM match WHERE id = ?",
                                    match_id)
        db.execute("UPDATE busco_operacion SET activo = ? WHERE id_busco = ?",
                    0, idbusco_idtengo[0]["id_busco"])
        db.execute("UPDATE tengo_operacion SET activo = ? WHERE id_tengo = ?",
                    0, idbusco_idtengo[0]["id_tengo"])
        id_comprador = db.execute("SELECT id FROM clientes WHERE id = (SELECT id_cliente FROM busco WHERE id = (SELECT id_busco FROM match WHERE id = ?))",
                                    match_id)
        db.execute("UPDATE tengo SET id_cliente = ? WHERE id = (SELECT id_tengo FROM match WHERE id = ?)",
                    id_comprador[0]["id"], match_id)
    
    db.execute("UPDATE match SET estado = ? WHERE id = ?",
                estado, match_id)
    
    return redirect("/matching")

#/////////////////////////////////////// CLIENTS /////////////////////////////////////////////////////

@app.route("/clients")
@login_required
def myclients():
    db = SQL("sqlite:///renection.db")
    
    #Seleccionar clientes del usuario
    clientes = db.execute("SELECT id, ci, nombre, apellido, telefono, email, fecha FROM clientes WHERE id_usuario = ? ORDER BY id DESC",
                            session["user_id"])
    vendedores_arrendadores = db.execute("SELECT tengo.id_cliente, tengo_operacion.tipo, tengo_operacion.activo FROM tengo INNER JOIN tengo_operacion ON tengo.id = tengo_operacion.id_tengo WHERE tengo.id_usuario = ?",
                                        session["user_id"])
    compradores_arrendatarios = db.execute("SELECT busco.id_cliente, busco_operacion.tipo, busco_operacion.activo FROM busco INNER JOIN busco_operacion ON busco.id = busco_operacion.id_busco WHERE busco.id_usuario = ?",
                                            session["user_id"])
    
    # Asignar roles en modalidades de venta y arriendo
    clientes = asign_roles(clientes, vendedores_arrendadores, "propietarios")
    clientes = asign_roles(clientes, compradores_arrendatarios, "requirientes")

                

    return render_template("clients.html", clientes=clientes, user=username)


#/////////////////////////////////////// LISTINGS /////////////////////////////////////////////////////
@app.route("/listings")
@login_required
def mylistings():
    db = SQL("sqlite:///renection.db")
    
    #Seleccionar propiedades del usuario
    propiedades = db.execute("SELECT tengo.id, tengo.calle, tengo.numero, tengo.depto, tengo.fecha, ubicacion.region, ubicacion.provincia, ubicacion.comuna, clientes.ci, clientes.nombre, clientes.apellido, clientes.telefono, clientes.email, tengo_caracteristicas_rangos.dormitorios, tengo_caracteristicas_rangos.banos, tengo_caracteristicas_rangos.estacionamientos, tengo_caracteristicas_rangos.bodegas, tengo_caracteristicas_rangos.superficie_u, tengo_caracteristicas_rangos.superficie_t  FROM (((tengo INNER JOIN ubicacion ON tengo.id_ubicacion = ubicacion.id) INNER JOIN clientes ON tengo.id_cliente = clientes.id) INNER JOIN tengo_caracteristicas_rangos ON tengo.id =  tengo_caracteristicas_rangos.id_tengo) WHERE tengo.id_usuario = ? ORDER BY tengo.id DESC", 
                                session["user_id"])
    ids_propiedades = list()
    generalidades = ["dormitorios", "banos", "estacionamientos", "bodegas", "superficie_u", "superficie_t"]
    for i in range(len(propiedades)):
        ids_propiedades.append(propiedades[i]["id"])
        for generalidad in generalidades:
            if not propiedades[i][generalidad]:
                propiedades[i][generalidad] = 0
        
    if ids_propiedades:
        placeholders = ', '.join('?' * len(ids_propiedades))
        operaciones = db.execute("SELECT * FROM tengo_operacion WHERE id_tengo IN (%s) ORDER BY id DESC" % placeholders,
                                tuple(ids_propiedades))
        tipos_de_propiedades = db.execute("SELECT id_tengo, tipo FROM tengo_tipo_de_propiedad WHERE id_tengo IN (%s)" % placeholders,
                                            tuple(ids_propiedades))
       
        propiedades = asign_listingOperations(propiedades, operaciones)
        propiedades = asign_listingPropertyTypes(propiedades, tipos_de_propiedades)
        resumen = count_listingStatus(propiedades)
    
    else: 
        resumen = {
        "activas": 0,
        "inactivas": 0,
        "ventas_activas": 0,
        "ventas_inactivas": 0,
        "arriendo_activas": 0,
        "arriendo_inactivas": 0
    }

    return render_template("listings.html", propiedades=propiedades, resumen=resumen, user=username)


#/////////////////////////////////////// LISTING DETAILS /////////////////////////////////////////////////////
@app.route("/listings/browse/listing-id=<listing_id>")
@login_required
def browselisting(listing_id):
    db = SQL("sqlite:///renection.db")
    propiedad = db.execute("SELECT * FROM tengo WHERE id = ?",
                        listing_id)
    ubicacion = db.execute("SELECT region, provincia, comuna FROM ubicacion WHERE id = ?",
                            propiedad[0]["id_ubicacion"])
    propietario = db.execute("SELECT ci, nombre, apellido, telefono, email FROM clientes WHERE id = ?",
                                propiedad[0]["id_cliente"])
    operaciones = db.execute("SELECT id, tipo, precio, activo FROM tengo_operacion WHERE id_tengo = ?",
                                listing_id)
    tipos_de_propiedad = db.execute("SELECT tipo FROM tengo_tipo_de_propiedad WHERE id_tengo = ?",
                                    listing_id)
    caracteristicas_rangos = db.execute("SELECT * FROM tengo_caracteristicas_rangos WHERE id_tengo = ?",
                                        listing_id)
    caracteristicas_opciones = db.execute("SELECT * FROM tengo_caracteristicas_opciones WHERE id_tengo = ?",
                                            listing_id)
    equipamiento = db.execute("SELECT * FROM tengo_equipamiento WHERE id_tengo = ?",
                                listing_id)
    
    # Limpiar tipos de propiedad
    for i in range(len(tipos_de_propiedad)):
        tipos_de_propiedad = tipos_de_propiedad[i]["tipo"]
    
    # Eliminar Null en caracteristicas
    for caracteristica, valor in caracteristicas_rangos[0].items():
        if not valor:
            caracteristicas_rangos[0][caracteristica] = "N/S"
    for caracteristica, valor in caracteristicas_opciones[0].items():
        if not valor:
            caracteristicas_opciones[0][caracteristica] = "N/S"
    
    # Cambiar condicion numérico por palabras
    if caracteristicas_rangos[0]["estado"] == 1:
        caracteristicas_rangos[0]["estado"] = "Needs Full Renovation"
    elif caracteristicas_rangos[0]["estado"] == 2:
        caracteristicas_rangos[0]["estado"] = "Needs Some Renovation"
    elif caracteristicas_rangos[0]["estado"] == 3:
        caracteristicas_rangos[0]["estado"] = "Regular"
    elif caracteristicas_rangos[0]["estado"] == 4:
        caracteristicas_rangos[0]["estado"] = "Good"
    elif caracteristicas_rangos[0]["estado"] == 5:
        caracteristicas_rangos[0]["estado"] = "Excellent"

    # Traducir operaciones:
    for i in range(len(operaciones)):
        if operaciones[i]["tipo"] == "venta":
            operaciones[i]["tipo"] = "Sale"
        elif operaciones[i]["tipo"] == "arriendo":
            operaciones[i]["tipo"] = "Rent"

    return render_template("listing_details.html", user=username, propiedad=propiedad[0], ubicacion=ubicacion[0], propietario=propietario[0], operaciones=operaciones, tipos_de_propiedad=tipos_de_propiedad, caracteristicas_rangos=caracteristicas_rangos[0], caracteristicas_opciones=caracteristicas_opciones[0], equipamiento=equipamiento[0])

#/////////////////////////////////////// LISTING ADD OPERATION /////////////////////////////////////////////////////
@app.route("/listings/add-operation/property-id=<listing_id>", methods=["POST"])
@login_required
def add_listing_operation(listing_id):
    db = SQL("sqlite:///renection.db")

    modalidades = list()
    if request.form.get("sell" + listing_id) == '1':
        modalidades.append("venta")
    if request.form.get("rent" + listing_id) == '1':
        modalidades.append("arriendo")
    
    if "venta" in modalidades: 
        operacion_venta = db.execute("SELECT id FROM tengo_operacion WHERE id_tengo = ? AND tipo = ? AND activo = ?",
                                    listing_id, "venta", 1)
        if operacion_venta:
            db.execute("UPDATE tengo_operacion SET activo = ? WHERE id = ?",
                        0, operacion_venta[0]["id"])
            db.execute("UPDATE match SET estado = ? WHERE id_tengo_operacion = ?",
                        0, operacion_venta[0]["id"])
    
    if "arriendo" in modalidades:
        operacion_arriendo = db.execute("SELECT id FROM tengo_operacion WHERE id_tengo = ? AND tipo = ? AND activo = ?",
                                        listing_id, "arriendo", 1)
        if operacion_arriendo:
            db.execute("UPDATE tengo_operacion SET activo = ? WHERE id = ?",
                        0, operacion_arriendo[0]["id"]) 
            db.execute("UPDATE match SET estado = ? WHERE id_tengo_operacion = ?",
                        0, operacion_venta[0]["id"])

    categoria = "tengo"
    for modalidad in modalidades:
        insert_nuevaOperacion(modalidad, listing_id)
        candidatos_operaciones = db.execute ("SELECT busco_operacion.id, busco_operacion.id_busco, busco_operacion.precio_min, busco_operacion.precio_max FROM busco_operacion INNER JOIN busco ON busco_operacion.id_busco = busco.id WHERE busco.id_usuario = ? AND busco_operacion.tipo = ? AND busco_operacion.activo = 1", 
                                                session["user_id"], modalidad)
        candidatos = deepcopy(candidatos_operaciones)
        idsBusquedas = match_operation(modalidad, listing_id, categoria, candidatos)
        if len(idsBusquedas) >= 1:
            idsBusquedas = match_location(idsBusquedas, listing_id, categoria)
            if len(idsBusquedas) >= 1:
                idsBusquedas = match_propertyType(idsBusquedas, listing_id, categoria)
                if len(idsBusquedas) >= 1:
                    idsBusquedas = match_carRangos(idsBusquedas, listing_id, categoria)
                    if len(idsBusquedas) >= 1:
                        idsBusquedas = match_carOpciones(idsBusquedas, listing_id, categoria)
                        if len(idsBusquedas) >= 1:
                            idsBusquedas = match_equipamiento(idsBusquedas, listing_id, categoria)
                            if len(idsBusquedas) >= 1:
                                insert_match(idsBusquedas, listing_id, categoria, candidatos_operaciones, modalidad)
    
    return redirect("/listings")

#/////////////////////////////////////// LISTING & REQUEST TURN OFF OPERATION /////////////////////////////////////////////////////
@app.route("/<table>/turn-operation-off/operation-id=<operation_id>")
@login_required
def turn_operation_off(operation_id, table):
    db = SQL("sqlite:///renection.db")
    
    if table == "listings":
        db.execute("UPDATE tengo_operacion SET activo = ? WHERE id = ?",
                    0, operation_id)
        db.execute("UPDATE match SET estado = ? WHERE id_tengo_operacion = ?",
                    0, operation_id)
        return redirect("/listings")
    
    elif table == "requests":
        db.execute("UPDATE busco_operacion SET activo = ? WHERE id = ?",
                    0, operation_id)
        db.execute("UPDATE match SET estado = ? WHERE id_busco_operacion = ?",
                    0, operation_id)
        return redirect("/requests")


#/////////////////////////////////////// LISTING DELETE /////////////////////////////////////////////////////
@app.route("/listings/delete/listing-id=<listing_id>")
@login_required
def delete_listing(listing_id):
    db = SQL("sqlite:///renection.db")
    db.execute("DELETE FROM match WHERE id_tengo = ?",  
                listing_id)
    db.execute("DELETE FROM tengo_equipamiento WHERE id_tengo = ?",
                listing_id)
    db.execute("DELETE FROM tengo_caracteristicas_opciones WHERE id_tengo = ?",
                listing_id)
    db.execute("DELETE FROM tengo_caracteristicas_rangos WHERE id_tengo = ?",
                listing_id)
    db.execute("DELETE FROM tengo_tipo_de_propiedad WHERE id_tengo = ?",
                listing_id)
    db.execute("DELETE FROM tengo_operacion WHERE id_tengo = ?",
                listing_id)
    id_cliente = db.execute("SELECT id_cliente FROM tengo WHERE id = ?",
                            listing_id)
    db.execute("DELETE FROM tengo WHERE id = ?",
                listing_id)
    propiedades_cliente = db.execute("SELECT id FROM tengo WHERE id_cliente = ?",
                                    id_cliente[0]["id_cliente"])
    requerimientos_cliente = db.execute("SELECT id FROM busco WHERE id_cliente = ?",
                                        id_cliente[0]["id_cliente"])
    
    if not propiedades_cliente and not requerimientos_cliente:
        db.execute("DELETE FROM clientes WHERE id = ?",
                    id_cliente[0]["id_cliente"])
    
    return redirect("/listings")

#/////////////////////////////////////// LOGOUT /////////////////////////////////////////////////////

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug = True)

