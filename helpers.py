from cs50 import SQL
from flask import redirect, session, request
from functools import wraps


#--------------------------------- GRAL -----------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_caracteristicas(tabla):
    if tabla == "busco_caracteristicas_rangos":
        caracteristicas = ("dormitorios_min", "dormitorios_max", "banos_min", "banos_max", "banos_suite_min", "banos_suite_max",
                            "estacionamientos_min", "estacionamientos_max", "bodegas_min", "bodegas_max", "superficie_u_min", "superficie_u_max",
                            "superficie_t_min", "superficie_t_max", "ggcc_min", "ggcc_max", "contribuciones_min", "contribuciones_max",
                            "rentabilidad_min", "estado_min", "estado_max", "ano_construccion_min", "ano_construccion_max", "pisos_construidos_min", 
                            "pisos_construidos_max", "piso_min", "piso_max")

    elif "caracteristicas_opciones" in tabla:
        caracteristicas = ("orientacion", "tipo_vista", "estructura", "piso_dormitorios", "piso_banos", "piso_living_comedor",
                            "piso_cocina", "living_comedor", "tipo_cocina", "distribucion_cocina", "encimera", 
                            "agua_caliente", "calefaccion")
    
    elif "equipamiento" in tabla:
        caracteristicas = ("amoblado", "logia", "comedor_diario", "condominio", "conserje", "ascensor", "estacionamiento_visitas", "lavanderia", 
                            "gas_caneria", "conexion_lavadora", "termopanel", "ventana_bano", "quincho", "gimnasio", "salon_multiuso", "piscina", 
                            "azotea_privada", "sauna")
    
    elif "tipo_de_propiedad" in tabla:
        caracteristicas = ("departamento", "comercial", "casa", "industrial", "terreno", "oficina")

    return caracteristicas

#--------------------------------- CLIENTS -----------------------------------------

def asign_roles(clientes, operaciones, categorias):
    if categorias == "propietarios":
        rol_venta = "vendedor"
        rol_arriendo = "arrendador"
    elif categorias == "requirientes":
        rol_venta = "comprador"
        rol_arriendo = "arrendatario"
    
    for rol in operaciones:
        for i in range(len(clientes)):
            if rol["id_cliente"] == clientes[i]["id"]:
                if "roles" not in clientes[i]:
                    if rol["tipo"] == "venta":
                        clientes[i]["roles"] = {rol_venta : rol["activo"]}
                    elif rol["tipo"] == "arriendo":
                        clientes[i]["roles"] = {rol_arriendo : rol["activo"]}
                else:
                    if rol["tipo"] == "venta":
                        if rol_venta in clientes[i]["roles"]:
                            if clientes[i]["roles"][rol_venta] == 0 and rol["tipo"]["venta"] == 1:
                                clientes[i]["roles"][rol_venta] == 1
                        else:
                            clientes[i]["roles"][rol_venta] = rol["activo"]
                    elif rol["tipo"] == "arriendo":
                        if rol_arriendo in clientes[i]["roles"]:
                            if clientes[i]["roles"][rol_arriendo] == 0 and rol["tipo"]["arriendo"] == 1:
                                clientes[i]["roles"][rol_arriendo] == 1
                        else:
                            clientes[i]["roles"][rol_arriendo] = rol["activo"]
    
    return clientes


#--------------------------------- LISTINGS / REQUESTS -----------------------------------------
def count_requestStatus(requerimientos):
    
    resumen = {
        "activos": 0,
        "inactivos": 0,
        "activos_compra": 0,
        "inactivos_compra": 0,
        "activos_arriendo": 0,
        "inactivos_arriendo": 0
    }

    for requerimiento in requerimientos:
        requerimiento_activo = False

        for operacion in requerimiento["operaciones"]:
            if operacion["tipo"] == "Buy":
                if operacion["estado"] == 1:
                    resumen["activos_compra"] += 1
                    requerimiento_activo = True
                else: 
                    resumen["inactivos_compra"] += 1
            elif operacion["tipo"] == "Lease":
                if operacion["estado"] == 1:
                    resumen["activos_arriendo"] += 1
                    requerimiento_activo = True
                else:
                    resumen["inactivos_arriendo"] += 1
        
        if requerimiento_activo:
            resumen["activos"] += 1
        else:
            resumen["inactivos"] += 1

    return resumen


def count_listingStatus(propiedades):
    resumen = {
        "activas": 0,
        "inactivas": 0,
        "ventas_activas": 0,
        "ventas_inactivas": 0,
        "arriendo_activas": 0,
        "arriendo_inactivas": 0
    }
    # Determinar total de propiedades activas - inactivas
    for propiedad in propiedades:
        propiedad_activa = 0
        
        for operacion in propiedad["operaciones"]:
            if operacion["tipo"] == "Sale":
                if operacion["estado"] == 1:
                    resumen["ventas_activas"] += 1
                    propiedad_activa += 1
                else:
                    resumen["ventas_inactivas"] += 1
            elif operacion["tipo"] == "Lease":
                if operacion["estado"] == 1:
                    resumen["arriendo_activas"] += 1
                    propiedad_activa += 1
                else: 
                    resumen["arriendo_inactivas"] += 1
        
        if propiedad_activa > 0:
            resumen["activas"] += 1
        else: 
            resumen["inactivas"] += 1                

    return resumen


def asign_listingOperations(propiedades, operaciones):
    for i in range(len(propiedades)):
        venta = 0
        arriendo = 0
        propiedades[i]["operaciones"] = list() 
        for operacion in operaciones:
            if propiedades[i]["id"] == operacion["id_tengo"]:
                if operacion["tipo"] == "venta":
                    if venta == 1:
                        continue
                    else:
                        tipo = "Sale"
                        venta = 1
                else:
                    if arriendo == 1:
                        continue
                    else: 
                        tipo = "Lease"
                        arriendo = 1
                
                propiedades[i]["operaciones"].append({
                    "id": operacion["id"],
                    "tipo": tipo, 
                    "estado": operacion["activo"], 
                    "precio": f"{operacion['precio']:,}".replace(",",".")
                })
                if arriendo == 1 and venta == 1:
                    break

    return propiedades


def asign_listingPropertyTypes(propiedades, tipos_de_propiedades):
    for i in range(len(propiedades)):
        for tipo_de_propiedad in tipos_de_propiedades:
            if propiedades[i]["id"] == tipo_de_propiedad["id_tengo"]:
                if "tipo propiedad" not in propiedades[i]:
                    propiedades[i]["tipo propiedad"] = list()
                if tipo_de_propiedad["tipo"] == "departamento":
                    propiedades[i]["tipo propiedad"].append("Apartment")
                elif tipo_de_propiedad["tipo"] == "casa":
                    propiedades[i]["tipo propiedad"].append("House")
                elif tipo_de_propiedad["tipo"] == "oficina":
                    propiedades[i]["tipo propiedad"].append("Office")
                elif tipo_de_propiedad["tipo"] == "comercial":
                    propiedades[i]["tipo propiedad"].append("Commercial")
                elif tipo_de_propiedad["tipo"] == "terreno":
                    propiedades[i]["tipo propiedad"].append("Land")
                elif tipo_de_propiedad["tipo"] == "industrial":
                    propiedades[i]["tipo propiedad"].append("Industrial")
                
    return propiedades


def order_clientsRequests(clientes_requerimientos):   
    
    clientes = list()
    
    # Verificar si el cliente ya existe en la lista, sino agregarlo
    for cliente_requerimiento in clientes_requerimientos:
        añadir_cliente = True
        
        for i in range(len(clientes)):
            if clientes[i]["id"] == cliente_requerimiento["id_cliente"]:
                añadir_cliente = False
                clientes[i]["requerimientos"].append({"id": cliente_requerimiento["id"]})

        if añadir_cliente:
            clientes.append({
                "id": cliente_requerimiento["id_cliente"],
                "ci": cliente_requerimiento["ci"],
                "nombre": cliente_requerimiento["nombre"],
                "apellido": cliente_requerimiento["apellido"],
                "telefono": cliente_requerimiento["telefono"],
                "email": cliente_requerimiento["email"],
                "requerimientos": [{
                    "id":cliente_requerimiento["id"]
                }]
            })
    
    return clientes


def asingn_requestOperations(requerimientos, operaciones):
    
    for i in range(len(requerimientos)):
        venta = 0
        arriendo = 0
        requerimientos[i]["operaciones"] = list()
        for operacion in operaciones:
            if requerimientos[i]["id"] == operacion["id_busco"]:
                if operacion["tipo"] == "venta":
                    if venta == 1:
                        continue
                    else:
                        tipo = "Buy"
                        venta = 1
                else:
                    if arriendo == 1:
                        continue
                    else:
                        tipo = "Lease"
                        arriendo = 1

                if operacion["precio_min"] and operacion["precio_max"]: 
                    requerimientos[i]["operaciones"].append({
                        "id": operacion["id"],
                        "tipo": tipo,
                        "estado": operacion["activo"],
                        "precio_min": f"{operacion['precio_min']:,}".replace(",","."),
                        "precio_max": f"{operacion['precio_max']:,}".replace(",",".")
                    })
                elif operacion["precio_min"]:
                    requerimientos[i]["operaciones"].append({
                        "id": operacion["id"],
                        "tipo": tipo,
                        "estado": operacion["activo"],
                        "precio_min": f"{operacion['precio_min']:,}".replace(",",".")
                    })
                elif operacion["precio_max"]:
                    requerimientos[i]["operaciones"].append({
                        "id": operacion["id"],
                        "tipo": tipo,
                        "estado": operacion["activo"],
                        "precio_max": f"{operacion['precio_max']:,}".replace(",",".")
                    })
                else:
                    requerimientos[i]["operaciones"].append({
                        "id": operacion["id"],
                        "tipo": tipo,
                        "estado": operacion["activo"],
                    })
    return requerimientos


def asign_requestPropertyTypes(requerimientos, tipos_de_propiedades):
    
    for i in range(len(requerimientos)):
        for tipo_de_propiedad in tipos_de_propiedades:
            if requerimientos[i]["id"] == tipo_de_propiedad["id_busco"]:
                if "tipos propiedad" not in requerimientos[i]:
                    requerimientos[i]["tipos propiedad"] = list()
                if tipo_de_propiedad["tipo"] == "departamento":
                    requerimientos[i]["tipos propiedad"].append("Apartment")
                elif tipo_de_propiedad["tipo"] == "casa":
                    requerimientos[i]["tipos propiedad"].append("House")
                elif tipo_de_propiedad["tipo"] == "oficina":
                    requerimientos[i]["tipos propiedad"].append("Office")
                elif tipo_de_propiedad["tipo"] == "comercial":
                    requerimientos[i]["tipos propiedad"].append("Commercial")
                elif tipo_de_propiedad["tipo"] == "terreno":
                    requerimientos[i]["tipos propiedad"].append("Land")
                elif tipo_de_propiedad["tipo"] == "industrial":
                    requerimientos[i]["tipos propiedad"].append("Industrial")
                    
    return requerimientos


def asign_requestGeneralities(requerimientos, generalidades):

    for i in range(len(requerimientos)):
        for generalidad in generalidades:
            if requerimientos[i]["id"] == generalidad["id_busco"]:
                if "generalidades" not in requerimientos[i]:
                    requerimientos[i]["generalidades"] = dict()
                
                requerimientos[i]["generalidades"][generalidad["columna"]] = generalidad["valor"]

    return requerimientos


def asign_requestLocations(requerimientos, ubicaciones):

    for i in range(len(requerimientos)):
        for ubicacion in ubicaciones:
            if requerimientos[i]["id"] == ubicacion["id_busco"]:
                if "ubicaciones" not in requerimientos[i]:
                    requerimientos[i]["ubicaciones"] = dict()
                if ubicacion["region"] not in requerimientos[i]["ubicaciones"]:
                    requerimientos[i]["ubicaciones"][ubicacion["region"]] = list()
                requerimientos[i]["ubicaciones"][ubicacion["region"]].append(ubicacion["comuna"])

    return requerimientos


#--------------------------------- VERIFICATION -----------------------------------------
def client_verif():
    # Client's name missing
    if not request.form.get("client_name"):    
        return "error"
    # Client's last name missing
    elif not request.form.get("client_last_name"):  
        return "error"
    # Client's id missing
    elif not request.form.get("client_id"):   
        return "error"
    # Enter at least one contact means
    elif not request.form.get("client_phone") and not request.form.get("client_email"):
        return "error"


def location_verif():
    # Region Missing
    if not request.form.get("region"):
        return "error"
    # District Missing
    elif not request.form.get("district"):
        return "error"
    # Commune Missing
    elif not request.form.get("commune"):
        return "error"
    # Street Missing
    elif not request.form.get("street"):
        return "error"
    # Street Number Missing
    elif not request.form.get("street_number"):
        return "error"
    # If apartment selected, missing apartment
    elif (request.form.get("type_apartment") == "apartment") and (not request.form.get("apartment_number")):
            return "error"


def deal_verif(form):
    if form == "listing":
        # No modality selected
        if not request.form.get("sell") and not request.form.get("rent"):
            return "error"
        # Sell Price Missing
        elif (request.form.get("sell") == '1') and (not request.form.get("sell_price")):
            return "error"
        # Rent Fee Missing
        elif (request.form.get("rent") == '1') and (not request.form.get("rent_price")): 
            return "error"
    
    elif form == "request":
        # Select at least one modality
        if not request.form.get("buy") and not request.form.get("rent"):
            return "error"
    
    # Property type missing 
    if (not request.form.get("departamento") and not request.form.get("comercial") and not request.form.get("casa") 
    and not request.form.get("industrial") and not request.form.get("terreno") and not request.form.get("oficina")):
        return "error"


#--------------------------------- SELECT -----------------------------------------
def select_lastId(table):
    db = SQL("sqlite:///renection.db")
    lastId = db.execute("SELECT MAX(id) FROM :tabla WHERE id_usuario = :usuario", 
                        tabla=table, usuario=session["user_id"])
    lastId = lastId[0]["MAX(id)"]
    return lastId


def select_location(region, district, commune):
    db = SQL("sqlite:///renection.db")
    idUbicacion = db.execute("SELECT id FROM ubicacion WHERE region = :region AND provincia = :provincia  AND comuna = :comuna",
                            region=request.form.get(region), provincia=request.form.get(district), 
                            comuna=request.form.get(commune).replace('\n','').replace('\r', ''))
    
    idUbicacion = idUbicacion[0]["id"]
    return idUbicacion


#--------------------------------- MATCH -----------------------------------------
def filter_ids(ids, desechados):
    for desechado in desechados:
        ids.remove(desechado)
    return ids


def match_operation(modalidad, idCategoria, categoria, candidatos):
    db = SQL("sqlite:///renection.db")
    
    if categoria == "tengo":
        # Seleccinar precio de la propiedad & candidatos que buscan en esa modalidad
        precio_propiedad = db.execute("SELECT precio FROM tengo_operacion WHERE id_tengo = ? AND tipo = ? AND activo = 1",
                                        idCategoria, modalidad)
        id_candidato = "id_busco"
    
    elif categoria == "busco":
        # Seleccionar precio min y max de la búsqueda & candidatos que tienen en esa modalidad
        precio_requerimiento = db.execute("SELECT precio_min, precio_max FROM busco_operacion WHERE id_busco = ? AND tipo = ? AND activo = 1",
                                idCategoria, modalidad)
        id_candidato = "id_tengo"                           
    
    # Comparar operación ingresada con operaciones de candidatos
    candidatos_desechados = list()
    for i in range(len(candidatos)):
        if categoria == "tengo":
            precio_requerimiento = [{
                "precio_min": candidatos[i]["precio_min"], 
                "precio_max": candidatos[i]["precio_max"]
                }]
        elif categoria == "busco":
            precio_propiedad = [{
                "precio": candidatos[i]["precio"]
                }]
        if precio_requerimiento[0]["precio_min"] != '' and precio_requerimiento[0]["precio_min"] != None:
            if precio_requerimiento[0]["precio_min"] > precio_propiedad[0]["precio"]:
                candidatos_desechados.append(candidatos[i][id_candidato])
        if precio_requerimiento[0]["precio_max"] != '' and precio_requerimiento[0]["precio_max"] != None:
            if precio_requerimiento[0]["precio_max"] < precio_propiedad[0]["precio"]:
                candidatos_desechados.append(candidatos[i][id_candidato])
        candidatos[i] = candidatos[i][id_candidato]
    if len(candidatos_desechados) >= 1: 
        candidatos = filter_ids(candidatos, candidatos_desechados)
                        
    return candidatos


def match_location(candidatos, idCategoria, categoria):
    db = SQL("sqlite:///renection.db")
    placeholders = ', '.join('?' * len(candidatos))
    candidatos_desechados = list()
    
    if categoria == "tengo":
        # Seleccionar ubicación de la propiedad y ubicaciones preferidas de todos los requerimientos vigentes
        ubicacion_propiedad = db.execute("SELECT id_ubicacion FROM tengo WHERE id = ?",
                                idCategoria)
        ubicaciones_requerimientos = db.execute("SELECT id_busco, id_ubicacion FROM config_busco_ubicacion WHERE id_busco IN (%s)" % placeholders,
                                                tuple(candidatos)) 

        # Filtrar requerimientos que no calzan con ubicacion de la propiedad:
        for candidato in candidatos:
            ubicaciones_requerimiento = list()
            for ubicacion_requerimiento in ubicaciones_requerimientos:
                if ubicacion_requerimiento["id_busco"] == candidato:
                    ubicaciones_requerimiento.append(ubicacion_requerimiento["id_ubicacion"])
            if len(ubicaciones_requerimiento) >= 1:
                if ubicacion_propiedad[0]["id_ubicacion"] not in ubicaciones_requerimiento:
                    candidatos_desechados.append(candidato)

    elif categoria == "busco":
        # Seleccionar ubicaciones preferidas del requerimiento y ubicaciones de todas las propiedades vigentes
        ubicaciones_requerimiento = db.execute("SELECT id_ubicacion FROM config_busco_ubicacion WHERE id_busco = ?",
                                                idCategoria)
        if len(ubicaciones_requerimiento) >= 1:
            for i in range(len(ubicaciones_requerimiento)):
                ubicaciones_requerimiento[i] = ubicaciones_requerimiento[i]["id_ubicacion"]
            ubicacion_propiedades = db.execute("SELECT id, id_ubicacion FROM tengo WHERE id IN (%s)" % placeholders,
                                                tuple(candidatos))
            
            # Filtrar propiedades que no cumplen con ubicaciones de requerimiento
            for ubicacion_propiedad in ubicacion_propiedades:
                if ubicacion_propiedad["id_ubicacion"] not in ubicaciones_requerimiento:
                    candidatos_desechados.append(ubicacion_propiedad["id"])
    
    if len(candidatos_desechados) >= 1:
        candidatos = filter_ids(candidatos, candidatos_desechados)

    return candidatos
    

def match_propertyType(candidatos, idCategoria, categoria):
    db = SQL("sqlite:///renection.db")
    placeholders = ', '.join('?' * len(candidatos))
    
    if categoria == "tengo":
        # Seleccionar tipos de la propiedad
        tipos_seleccionados = db.execute("SELECT tipo FROM tengo_tipo_de_propiedad WHERE id_tengo = ?",
                                idCategoria)
        for i in range(len(tipos_seleccionados)):
            tipos_seleccionados[i] = tipos_seleccionados[i]["tipo"]
        # Seleccionar preferencias de ids vigentes
        candidatos_tipos = db.execute("SELECT id_busco, tipo FROM busco_tipo_de_propiedad WHERE id_busco IN (%s)" % placeholders,
                                    tuple(candidatos))
        col_id = "id_busco"
    
    elif categoria == "busco": 
        # Seleccionar tipos a buscar
        tipos_seleccionados = db.execute("SELECT tipo FROM busco_tipo_de_propiedad WHERE id_busco = ?", 
                                idCategoria)
        for i in range(len(tipos_seleccionados)):
            tipos_seleccionados[i] = tipos_seleccionados[i]["tipo"]
        # Seleccionar tipos de ids vigentes
        candidatos_tipos = db.execute("SELECT id_tengo, tipo FROM tengo_tipo_de_propiedad WHERE id_tengo IN (%s)" % placeholders,
                                    tuple(candidatos))
        col_id = "id_tengo"
        
    # Descartar ids que no cumplen
    candidatos_desechados = list()
    for candidato in candidatos:
        preferencias_candidato = list()
        for candidato_tipo in candidatos_tipos:
            if candidato == candidato_tipo[col_id]:
                preferencias_candidato.append(candidato_tipo["tipo"])
        if len(preferencias_candidato) >= 1:
            match_count = 0
            for preferencia in preferencias_candidato:
                if preferencia in tipos_seleccionados:
                    match_count += 1
                    break
            if match_count == 0:
                candidatos_desechados.append(candidato)
    if len(candidatos_desechados) >= 1:
        candidatos = filter_ids(candidatos, candidatos_desechados)

    return candidatos


def match_carRangos(candidatos, idCategoria, categoria):
    db = SQL("sqlite:///renection.db")
    placeholders = ', '.join('?' * len(candidatos))
    candidatos_desechados = list()
    
    if categoria == "tengo":
        # Seleccionar caracteristicas de la propiedad y de cada candidato vigente
        caracteristicas_propiedad = db.execute("SELECT * FROM tengo_caracteristicas_rangos WHERE id_tengo = ?",
                                idCategoria)
        # Seleccionar preferencias de cada id vignete
        caracteristicas_requerimientos = db.execute("SELECT id_busco, columna, valor FROM busco_caracteristicas_rangos WHERE id_busco IN (%s)" % placeholders,
                                                tuple(candidatos))
        
        # Descartar ids que no cumplen
        for caracteristica_requerimiento in caracteristicas_requerimientos:
            if caracteristica_requerimiento["id_busco"] in candidatos_desechados:
                continue
            else:
                if compare_carRangos(caracteristicas_propiedad[0], caracteristica_requerimiento) == 1:
                    candidatos_desechados.append(caracteristica_requerimiento["id_busco"])

    elif categoria == "busco":
        # Seleccionar características requeridas por el requerimiento
        caracteristicas_requerimiento = db.execute("SELECT columna, valor FROM busco_caracteristicas_rangos WHERE id_busco = ?",
                                                    idCategoria)
        # Seleccionar caracteristicas de cada propiedad vigente
        caracteristicas_propiedades = db.execute("SELECT * FROM tengo_caracteristicas_rangos WHERE id_tengo IN (%s)" % placeholders,
                                                tuple(candidatos))
        
        # Descartar ids que no cumplen
        if len(caracteristicas_requerimiento) >= 1:
            for caracteristicas_propiedad in caracteristicas_propiedades:
                for caracteristica_requerimiento in caracteristicas_requerimiento:
                    if compare_carRangos(caracteristicas_propiedad, caracteristica_requerimiento) == 1:
                        candidatos_desechados.append(caracteristicas_propiedad["id_tengo"])
                        break

    if len(candidatos_desechados) >= 1:
            candidatos = filter_ids(candidatos, candidatos_desechados)

    return candidatos

def compare_carRangos(caracteristicas_propiedad, caracteristica_requerimiento):
    if "_min" in caracteristica_requerimiento["columna"]:
        caracteristica = caracteristica_requerimiento["columna"].replace("_min", "")
        if caracteristicas_propiedad[caracteristica] == '' or caracteristicas_propiedad[caracteristica] == None:
            caracteristicas_propiedad[caracteristica] = 0
        if caracteristica_requerimiento["valor"] > caracteristicas_propiedad[caracteristica]:
            return 1
        else:
            return 0
    elif "_max" in caracteristica_requerimiento["columna"]:
        caracteristica = caracteristica_requerimiento["columna"].replace("_max", "")
        if caracteristicas_propiedad[caracteristica] == '' or caracteristicas_propiedad[caracteristica] == None:
            caracteristicas_propiedad[caracteristica] = 0
        if caracteristica_requerimiento["valor"] < caracteristicas_propiedad[caracteristica]:
            return 1
        else: 
            return 0


def match_carOpciones(candidatos, idCategoria, categoria):
    db = SQL("sqlite:///renection.db")
    placeholders = ', '.join('?' * len(candidatos))
    candidatos_desechados = list()
    
    if categoria == "tengo":
        # Seleccionar caracteristicas de la propiedad
        caracteristicas_propiedad = db.execute("SELECT * FROM tengo_caracteristicas_opciones WHERE id_tengo = ?",
                                            idCategoria)
        # Seleccionar preferencias de cada id vigente
        caracteristicas_requerimientos = db.execute("SELECT id_busco, columna, valor FROM busco_caracteristicas_opciones WHERE id_busco IN (%s)" % placeholders,
                                                tuple(candidatos))

        # Descartar ids que no cumplen
        for idcandidato in candidatos:
            preferencias = dict()
            for caracteristica_requerimiento in caracteristicas_requerimientos:
                if idcandidato == caracteristica_requerimiento["id_busco"]:
                    if caracteristica_requerimiento["columna"] in preferencias:
                        preferencias[caracteristica_requerimiento["columna"]].append(caracteristica_requerimiento["valor"])
                    else: 
                        preferencias[caracteristica_requerimiento["columna"]] = [caracteristica_requerimiento["valor"]]
            
            if len(preferencias) >= 1:
                for preferencia in preferencias:
                    if caracteristicas_propiedad[0][preferencia] == None or caracteristicas_propiedad[0][preferencia] == '':
                        caracteristicas_propiedad[0][preferencia] = "none selected"
                    if caracteristicas_propiedad[0][preferencia] not in preferencias[preferencia]:
                        candidatos_desechados.append(idcandidato)
                        break
    
    elif categoria == "busco":
        # Seleccionar características del requerimiento
        caracteristicas_requerimiento = db.execute("SELECT columna, valor FROM busco_caracteristicas_opciones WHERE id_busco = ?",
                                                    idCategoria)
        # Seleccionar características de cada propiedad
        caracteristicas_propiedades = db.execute("SELECT * from tengo_caracteristicas_opciones WHERE id_tengo IN (%s)" % placeholders,
                                                tuple(candidatos))
        
        # Descartar ids que no cumplen
        preferencias = dict()
        for caracteristica_requerimiento in caracteristicas_requerimiento:
            if caracteristica_requerimiento["columna"] in preferencias:
                preferencias[caracteristica_requerimiento["columna"]]. append(caracteristica_requerimiento["valor"])
            else: 
                preferencias[caracteristica_requerimiento["columna"]] = [caracteristica_requerimiento["valor"]]
        
        if len(preferencias) >= 1:
            for caracteristicas_propiedad in caracteristicas_propiedades:
                for preferencia in preferencias:
                    if caracteristicas_propiedad[preferencia] == None or caracteristicas_propiedad[preferencia] == '':
                        caracteristicas_propiedad[preferencia] = "none selected"
                    if caracteristicas_propiedad[preferencia] not in preferencias[preferencia]:
                        candidatos_desechados.append(caracteristicas_propiedad["id_tengo"])
                        break

    if len(candidatos_desechados) >= 1:
        candidatos = filter_ids(candidatos, candidatos_desechados)

    return candidatos


def match_equipamiento(candidatos, idCategoria, categoria):
    db = SQL("sqlite:///renection.db")
    placeholders = ', '.join('?' * len(candidatos))
    candidatos_desechados = list()
    
    if categoria == "tengo":
        # Seleccionar caracteristicas de la propiedad
        equipamiento_propiedad = db.execute("SELECT * FROM tengo_equipamiento WHERE id_tengo = ?",
                                            idCategoria)
        # Seleccionar preferencias de cada id vigente
        equipamiento_requerimientos = db.execute("SELECT id_busco, columna FROM busco_equipamiento WHERE id_busco IN (%s)" % placeholders,
                                                tuple(candidatos))
        
        # Descartar ids que no cumplen
        for equipamiento_requerimiento in equipamiento_requerimientos:
            if equipamiento_requerimiento["id_busco"] in candidatos_desechados:
                continue
            else:
                if equipamiento_propiedad[0][equipamiento_requerimiento["columna"]] == None or equipamiento_propiedad[0][equipamiento_requerimiento["columna"]] == '':
                    candidatos_desechados.append(equipamiento_requerimiento["id_busco"])

    elif categoria == "busco":
        #Seleccionar equipamiento del requerimiento
        equipamientos_requerimiento = db.execute("SELECT columna FROM busco_equipamiento WHERE id_busco = ?",
                                                idCategoria)
        # Seleccionar el equipamiento de las propiedades vigentes
        equipamiento_propiedades = db.execute("SELECT * FROM tengo_equipamiento WHERE id_tengo IN (%s)" % placeholders,
                                                tuple(candidatos))

        # Descartar ids que no cumplen
        for equipamiento_propiedad in equipamiento_propiedades:
            for equipamiento_requerimiento in equipamientos_requerimiento:
                if equipamiento_propiedad[equipamiento_requerimiento["columna"]] == None or equipamiento_propiedad[equipamiento_requerimiento["columna"]] == '':
                    candidatos_desechados.append(equipamiento_propiedad["id_tengo"])
                    break
    
    if len(candidatos_desechados) >= 1:
        candidatos = filter_ids(candidatos, candidatos_desechados)
    
    return candidatos


def insert_match(candidatos, idCategoria, categoria, candidatos_operaciones, modalidad):
    db = SQL("sqlite:///renection.db")

    if categoria == "tengo":
        id_tengo_operacion = db.execute("SELECT id FROM tengo_operacion WHERE id_tengo = ? AND tipo = ? AND activo = ?",
                                        idCategoria, modalidad, 1)
        for candidato in candidatos:
            for candidato_operacion in candidatos_operaciones:
                if candidato_operacion["id_busco"] == candidato:
                    db.execute("INSERT INTO match (id_usuario, id_busco, id_busco_operacion, id_tengo, id_tengo_operacion, estado) VALUES (?, ?, ?, ?, ?, ?)", 
                                session["user_id"], candidato, candidato_operacion["id"], idCategoria, id_tengo_operacion[0]["id"], 1)


    elif categoria == "busco":
        id_busco_operacion = db.execute("SELECT id from busco_operacion WHERE id_busco = ? AND tipo = ? AND activo = ?",
                                        idCategoria, modalidad, 1)
        for candidato in candidatos:
            for candidato_operacion in candidatos_operaciones:
                if candidato_operacion["id_tengo"] == candidato:
                    db.execute("INSERT INTO match (id_usuario, id_busco, id_busco_operacion, id_tengo, id_tengo_operacion, estado) VALUES (?, ?, ?, ?, ?, ?)",
                                session["user_id"], idCategoria, id_busco_operacion[0]["id"], candidato, candidato_operacion["id"], 1)


def asign_matchClients(matches, busquedas_clientes):
    
    for i in range(len(matches)):
        for busqueda_cliente in busquedas_clientes:
            
            if matches[i]["id_busco"] == busqueda_cliente["id"]:
                matches[i]["comprador"] = {
                    "ci": busqueda_cliente["ci"],
                    "nombre": busqueda_cliente["nombre"],
                    "apellido": busqueda_cliente["apellido"],
                    "telefono": busqueda_cliente["telefono"],
                    "email": busqueda_cliente["email"]
                }
                break
    
    return matches


def asign_matchListings(matches, propiedades):
    
    for i in range(len(matches)):
        for propiedad in propiedades:

            if matches[i]["id_tengo"] == propiedad["id"]:
                matches[i]["propiedad"] = {
                    "calle": propiedad["calle"],
                    "numero": propiedad["numero"],
                    "depto": propiedad["depto"],
                    "region": propiedad["region"],
                    "comuna": propiedad["comuna"],
                    "dormitorios": propiedad["dormitorios"],
                    "banos": propiedad["banos"],
                    "estacionamientos": propiedad["estacionamientos"],
                    "bodegas": propiedad["bodegas"],
                    "superficie_u": propiedad["superficie_u"],
                    "superficie_t": propiedad["superficie_t"]
                }
                break
    
    return matches


def asign_matchPropertyTypes(matches, tipos_propiedad_propiedades, tipos_propiedad_requerimientos):
    
    for i in range(len(matches)):

        propiedad = list()
        requerimiento = list()
        matches[i]["tipos propiedad"] = list()
        
        for tipo_propiedad_propiedad in tipos_propiedad_propiedades:
            if matches[i]["id_tengo"] == tipo_propiedad_propiedad["id_tengo"]:
                propiedad.append(tipo_propiedad_propiedad["tipo"])

        for tipo_propiedad_requerimiento in tipos_propiedad_requerimientos:
            if matches[i]["id_busco"] == tipo_propiedad_requerimiento["id_busco"]:
                requerimiento.append(tipo_propiedad_requerimiento["tipo"])

        for tipo_propiedad in propiedad:
            if tipo_propiedad in requerimiento:
                if tipo_propiedad == "departamento":
                    matches[i]["tipos propiedad"].append("Apartment")
                elif tipo_propiedad == "casa":
                    matches[i]["tipos propiedad"].append("House")
                elif tipo_propiedad == "oficina":
                    matches[i]["tipos propiedad"].append("Office")
                elif tipo_propiedad == "comercial":
                    matches[i]["tipos propiedad"].append("Commercial")
                elif tipo_propiedad == "terreno":
                    matches[i]["tipos propiedad"].append("Land")
                elif tipo_propiedad == "industrial":
                    matches[i]["tipos propiedad"].append("Industrial")

    return matches


def asign_matchOperations(matches, operaciones_propiedades):
    
    for i in range(len(matches)):
        for operacion_propiedad in operaciones_propiedades:
            if matches[i]["id_tengo_operacion"] == operacion_propiedad["id"]:
                if operacion_propiedad["tipo"] == "venta":
                    tipo = "Sale"
                else:
                    tipo = "Lease"
                matches[i]["operacion"] = {
                    "tipo": tipo,
                    "precio": f"{operacion_propiedad['precio']:,}".replace(",",".")
                }

    return matches


def count_matchStatus(matches):
    
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
    
    for match in matches:
        
        if match["operacion"]["tipo"] == "Sale":
            if match["estado"] == 1:
                resumen["activos_compra"] += 1
            elif match["estado"] == 3:
                resumen["concretados_compra"] += 1
            elif match["estado"] == 0:
                resumen["nodisponibles_compra"] += 1
            else: 
                resumen["inactivos_compra"] += 1
        
        elif match["operacion"]["tipo"] == "Lease":
            if match["estado"] == 1:
                resumen["activos_arriendo"] += 1
            elif match["estado"] == 3:
                resumen["concretados_arriendo"] += 1
            elif match["estado"] == 0:
                resumen["nodisponibles_arriendo"] += 1
            else:
                resumen["inactivos_arriendo"] += 1
        
    return resumen

#--------------------------------- INSERT -----------------------------------------
def insert_client():
    db = SQL("sqlite:///renection.db")
    db.execute("INSERT INTO clientes (id_usuario, ci, nombre, apellido, telefono, email) VALUES (?, ?, ?, ?, ?, ?)",
                session["user_id"], request.form.get("client_id"), request.form.get("client_name"), 
                request.form.get("client_last_name"), request.form.get("client_phone"), request.form.get("client_email"))


def insert_tengo(idDueno, idUbicacion):
    db = SQL("sqlite:///renection.db")
    db.execute("INSERT INTO tengo (calle, numero, depto, id_usuario, id_cliente, id_ubicacion) VALUES (:calle, :numero, :depto, :usuario, :dueno, :ubicacion)",
                calle=request.form.get("street"), numero=request.form.get("street_number"), depto=request.form.get("apartment_number"), 
                usuario=session["user_id"], dueno=idDueno, ubicacion=idUbicacion)


def insert_busco(idCliente):
    db = SQL("sqlite:///renection.db")
    db.execute("INSERT INTO busco (id_usuario, id_cliente) VALUES (:usuario, :cliente)",
                usuario=session["user_id"], cliente=idCliente)

def insert_location(idbusco):
    location_counter = 1
    db = SQL("sqlite:///renection.db")
    while len(request.form.getlist("communes" + str(location_counter) + "[]")) >= 1:
        communes = request.form.getlist("communes" + str(location_counter) + "[]")    
        
        for commune in communes:
            # Seleccionar id de comuna
            id_ubicacion = db.execute("SELECT id FROM ubicacion WHERE region = :region AND provincia = :provincia AND comuna = :comuna", 
            region=request.form.get("region" + str(location_counter)), provincia=request.form.get("district" + str(location_counter)), 
            comuna=commune.replace('\n','').replace('\r', ''))
            # Ingresar id de comuna
            db.execute("INSERT INTO config_busco_ubicacion (id_busco, id_ubicacion) VALUES (:buscoid, :ubicacionid)",
                        buscoid=idbusco, ubicacionid=id_ubicacion[0]["id"])
        
        location_counter += 1

def insert_operacion(tabla, modalidad, idCategoria):
    db = SQL("sqlite:///renection.db")
    
    if tabla == "tengo_operacion":
        if modalidad == "venta":
            precio = request.form.get("sell_price")
        elif modalidad == "arriendo":
            precio = request.form.get("rent_price")
        db.execute("INSERT INTO tengo_operacion (id_tengo, tipo, precio, activo) VALUES (?, ?, ?, ?)",
                    idCategoria, modalidad, precio, 1)

    elif tabla == "busco_operacion":
        if modalidad == "venta":
            min_budget = request.form.get("min_buy_budget")
            max_budget = request.form.get("max_buy_budget")
        elif modalidad == "arriendo":
            min_budget = request.form.get("min_rent_budget")
            max_budget = request.form.get("max_rent_budget")
        db.execute("INSERT INTO busco_operacion (id_busco, tipo, precio_min, precio_max, activo) VALUES (?, ?, ?, ?, ?)", 
                    idCategoria, modalidad, min_budget, max_budget, 1)

def insert_nuevaOperacion(modalidad, id_tengo):
    db = SQL("sqlite:///renection.db")
    if modalidad == "venta":
        precio = request.form.get("sell_price" + id_tengo)
    elif modalidad == "arriendo":
        precio = request.form.get("rent_price" + id_tengo)
    db.execute("INSERT INTO tengo_operacion (id_tengo, tipo, precio, activo) VALUES (?, ?, ?, ?)",
                id_tengo, modalidad, precio, 1)


def insert_caracteristicas(tabla, idCategoria):
    db = SQL("sqlite:///renection.db")
    
    if tabla == "tengo_tipo_de_propiedad" or tabla == "busco_tipo_de_propiedad":
        if tabla == "tengo_tipo_de_propiedad":
            id_columna = "id_tengo"
        elif tabla == "busco_tipo_de_propiedad":
            id_columna = "id_busco"
        tipos = get_caracteristicas(tabla)
        for tipo in tipos:
            if request.form.get(tipo):
                db.execute("INSERT INTO ? (?, tipo) VALUES (?, ?)", 
                            tabla, id_columna, idCategoria, tipo)
    
    elif tabla == "tengo_caracteristicas_rangos":
        db.execute("INSERT INTO ? (id_tengo, dormitorios, banos, banos_suite, estacionamientos, bodegas, superficie_u, superficie_t, ggcc, contribuciones, rentabilidad, estado, ano_construccion, pisos_construidos, piso) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    tabla, idCategoria, request.form.get("bedrooms"), request.form.get("bathrooms"), 
                    request.form.get("on_suites"), request.form.get("parking"), request.form.get("storage"), 
                    request.form.get("surface"), request.form.get("total_surface"), request.form.get("common_expenses"), 
                    request.form.get("taxation"), request.form.get("potential_rent_fee"), int(request.form.get("condition")), 
                    request.form.get("construction_year"), request.form.get("built_floors"), request.form.get("on_floor"))
    
    elif tabla == "tengo_caracteristicas_opciones":
        db.execute("INSERT INTO ? (id_tengo, orientacion, tipo_vista, estructura, piso_dormitorios, piso_banos, piso_living_comedor, piso_cocina, living_comedor, tipo_cocina, distribucion_cocina, encimera, agua_caliente, calefaccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    tabla, idCategoria, request.form.get("orientation"), request.form.get("view_type"), 
                    request.form.get("construction_material"), request.form.get("flooring_bedroom"), 
                    request.form.get("flooring_bathroom"), request.form.get("flooring_living"), request.form.get("flooring_kitchen"), 
                    request.form.get("living_dining_layout"), request.form.get("kitchen_type"), request.form.get("kitchen_layout"), 
                    request.form.get("kitchen_heating"), request.form.get("water_heating"), request.form.get("heating"))
    
    elif tabla == "tengo_equipamiento":
        db.execute("INSERT INTO ? (id_tengo, amoblado, logia, comedor_diario, condominio, conserje, ascensor, estacionamiento_visitas, lavanderia, gas_caneria, conexion_lavadora, termopanel, ventana_bano, quincho, gimnasio, salon_multiuso, piscina, azotea_privada, sauna) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    tabla, idCategoria, request.form.get("furnished"), request.form.get("on_site_laundry"), 
                    request.form.get("daily_dining"), request.form.get("condominium"), request.form.get("janitor"), 
                    request.form.get("elevator"), request.form.get("visitor_parking"), request.form.get("laundry"), 
                    request.form.get("pipe_gas"), request.form.get("wm_connection"), request.form.get("double_glazed"), 
                    request.form.get("bathroom_window"), request.form.get("barbeque"), request.form.get("gym"), 
                    request.form.get("lounge_room"), request.form.get("pool"), request.form.get("rooftop"), 
                    request.form.get("sauna"))
    
    elif tabla == "busco_caracteristicas_opciones":
        caracteristicas = get_caracteristicas(tabla)
        for caracteristica in caracteristicas:
            opciones = request.form.getlist(caracteristica)
            if len(opciones) >= 1:
                for opcion in opciones:
                    db.execute("INSERT INTO ? (id_busco, columna, valor) VALUES (?, ?, ?)", 
                                tabla, idCategoria, caracteristica, opcion)    
    
    elif tabla == "busco_caracteristicas_rangos":
        caracteristicas = get_caracteristicas(tabla)
        for caracteristica in caracteristicas:
            if request.form.get(caracteristica):
                    db.execute("INSERT INTO ? (id_busco, columna, valor) VALUES (?, ?, ?)", 
                                tabla, idCategoria, caracteristica, request.form.get(caracteristica))
    
    elif tabla == "busco_equipamiento":
        caracteristicas = get_caracteristicas(tabla)
        for caracteristica in caracteristicas:
            if request.form.get(caracteristica):
                db.execute("INSERT INTO ? (id_busco, columna) VALUES (?, ?)", 
                            tabla, idCategoria, caracteristica)

