-- YA EN SISTEMA
CREATE TABLE 'usuarios' (
    'id' INTEGER NOT NULL,
    'email' TEXT NOT NULL,
    'hash' TEXT NOT NULL,
    'nombre' TEXT,
    'apellido' TEXT,
    'empresa' TEXT,
    'ciudad' TEXT, 
    'telefono' TEXT,
    PRIMARY KEY ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'clientes' (
    'id' INTEGER NOT NULL, 
    'id_usuario' INTEGER NOT NULL,
    'ci' TEXT NOT NULL, 
    'nombre' TEXT NOT NULL,
    'apellido' TEXT NOT NULL,
    'telefono' TEXT,
    'email' TEXT,
    'fecha' DATE NOT NULL DEFAULT (date('now', 'localtime')),
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_usuario')  REFERENCES 'usuarios' ('id'),
    CHECK ('telefono' IS NOT NULL OR 'email' IS NOT NULL)
);
-- YA EN SISTEMA
CREATE TABLE 'tengo' (
    'id' INTEGER NOT NULL,
    'calle' TEXT NOT NULL,
    'numero' TEXT NOT NULL,
    'depto' TEXT,
    'id_usuario' INTEGER NOT NULL,
    'id_cliente' INTEGER NOT NULL,
    'id_ubicacion' INTEGER,
    'fecha' DATE NOT NULL DEFAULT (date('now', 'localtime')),
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_usuario') REFERENCES 'usuarios' ('id'),
    FOREIGN KEY ('id_cliente') REFERENCES 'clientes' ('id'),
    FOREIGN KEY ('id_ubicacion') REFERENCES 'ubicacion' ('id')
);

-- YA EN SISTEMA
CREATE TABLE 'busco' (
    'id' INTEGER NOT NULL,
    'id_usuario' INTEGER NOT NULL,
    'id_cliente' INTEGER NOT NULL,
    'fecha' DATE NOT NULL DEFAULT (date('now', 'localtime')),
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_usuario') REFERENCES 'usuarios' ('id'),
    FOREIGN KEY ('id_cliente') REFERENCES 'clientes' ('id')
);
-- YA EN SISTEMA
-- estado: 0 no disponible, 1 generado, 2 desactivado por usuario, 3 concretado
CREATE TABLE 'match' (
    'id' INTEGER NOT NULL,
    'id_usuario' INTEGER NOT NULL,
    'id_busco' INTEGER NOT NULL,
    'id_busco_operacion' INTEGER NOT NULL,
    'id_tengo' INTEGER NOT NULL,
    'id_tengo_operacion' INTEGER NOT NULL,
    'estado' INTEGER NOT NULL,
    PRIMARY KEY ('id'), 
    FOREIGN KEY ('id_usuario') REFERENCES 'usuarios' ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id'),
    FOREIGN KEY ('id_busco_operacion') REFERENCES 'busco_operacion' ('id'),
    FOREIGN KEY ('id_tengo') REFERENCES 'tengo' ('id'),
    FOREIGN KEY ('id_tengo_operacion') REFERENCES 'tengo_operacion' ('id')
);

-------------------------------------- FILTROS -----------------------------------------


-- YA EN SISTEMA
-- activo: 0 inactivo; 1 activo;
CREATE TABLE 'tengo_operacion' (
    'id' INTEGER NOT NULL,
    'id_tengo' INTEGER,
    'tipo' TEXT,
    'precio' INTEGER,
    'activo' INTEGER NOT NULL, 
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_tengo') REFERENCES 'tengo' ('id')
);
-- YA EN SISTEMA
-- activo: 0 inactivo; 1 activo;
CREATE TABLE 'busco_operacion' (
    'id' INTEGER NOT NULL,
    'id_busco' INTEGER,
    'tipo' TEXT,
    'precio_min' INTEGER,
    'precio_max' INTEGER NOT NULL,
    'activo' INTEGER NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'ubicacion' (
    'id' INTEGER NOT NULL,
    'region' TEXT NOT NULL,
    'provincia' TEXT NOT NULL,
    'comuna' TEXT NOT NULL, 
    PRIMARY KEY ('id')
);
--YA EN SISTEMA
CREATE TABLE 'config_busco_ubicacion' (
    'id' INTEGER NOT NULL,
    'id_busco' INTEGER NOT NULL,
    'id_ubicacion' INTEGER NOT NULL,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id'),
    FOREIGN KEY ('id_ubicacion') REFERENCES 'ubicacion' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'tengo_tipo_de_propiedad' (
    'id' INTEGER NOT NULL,
    'id_tengo' INTEGER NOT NULL,
    'tipo' TEXT,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_tengo') REFERENCES 'tengo' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'busco_tipo_de_propiedad' (
    'id' INTEGER NOT NULL,
    'id_busco' INTEGER NOT NULL,
    'tipo' TEXT,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'tengo_caracteristicas_rangos' (
    'id' INTEGER NOT NULL,
    'id_tengo' INTEGER,
    'dormitorios' INTEGER,
    'banos' INTEGER,
    'banos_suite' INTEGER,
    'estacionamientos' INTEGER,
    'bodegas' INTEGER,
    'superficie_u' INTEGER,
    'superficie_t' INTEGER,
    'ggcc' INTEGER,
    'contribuciones' INTEGER,
    'rentabilidad' INTEGER,
    'estado' INTEGER,
    'ano_construccion' INTEGER,
    'pisos_construidos' INTEGER,
    'piso' INTEGER,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_tengo') REFERENCES 'tengo' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'busco_caracteristicas_rangos' (
    'id' INTEGER NOT NULL,
    'id_busco' INTEGER NOT NULL,
    'columna' TEXT,
    'valor' INTEGER,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'tengo_caracteristicas_opciones' (
    'id' INTEGER NOT NULL,
    'id_tengo' INTEGER,
    'orientacion' TEXT,
    'tipo_vista' TEXT,
    'estructura' TEXT,
    'piso_dormitorios' TEXT,
    'piso_banos' TEXT,
    'piso_living_comedor' TEXT,
    'piso_cocina' TEXT,
    'living_comedor' TEXT,
    'tipo_cocina' TEXT,
    'distribucion_cocina' TEXT,
    'encimera' TEXT,
    'agua_caliente' TEXT,
    'calefaccion' TEXT,
    PRIMARY KEY ('id'), 
    FOREIGN KEY ('id_tengo') REFERENCES 'tengo' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'busco_caracteristicas_opciones' (
    'id' INTEGER NOT NULL,
    'id_busco' INTEGER NOT NULL,
    'columna' TEXT, 
    'valor' TEXT,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'tengo_equipamiento' (
    'id' INTEGER NOT NULL,
    'id_tengo' INTEGER,
    'amoblado' INTEGER,
    'logia' INTEGER,
    'comedor_diario' INTEGER,
    'condominio' INTEGER,
    'conserje' INTEGER,
    'ascensor' INTEGER,
    'estacionamiento_visitas' INTEGER,
    'lavanderia' INTEGER,
    'gas_caneria' INTEGER,
    'conexion_lavadora' INTEGER,
    'termopanel' INTEGER,
    'ventana_bano' INTEGER,
    'quincho' INTEGER,
    'gimnasio' INTEGER,
    'salon_multiuso' INTEGER,
    'piscina' INTEGER,
    'azotea_privada' INTEGER,
    'sauna' INTEGER,
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_tengo') REFERENCES 'tengo' ('id')
);
-- YA EN SISTEMA
CREATE TABLE 'busco_equipamiento' (
    'id' INTEGER NOT NULL,
    'id_busco' INTEGER NOT NULL,
    'columna' TEXT, 
    PRIMARY KEY ('id'),
    FOREIGN KEY ('id_busco') REFERENCES 'busco' ('id')
);

---------------------------------------------------------
DELETE FROM usuarios;
DELETE FROM clientes;
DELETE FROM tengo;
DELETE FROM busco;
DELETE FROM match;
DELETE FROM tengo_operacion;
DELETE FROM busco_operacion;
DELETE FROM config_busco_ubicacion;
DELETE FROM tengo_tipo_de_propiedad;
DELETE FROM busco_tipo_de_propiedad;
DELETE FROM tengo_caracteristicas_rangos;
DELETE FROM busco_caracteristicas_rangos;
DELETE FROM tengo_caracteristicas_opciones;
DELETE FROM busco_caracteristicas_opciones;
DELETE FROM tengo_equipamiento;
DELETE FROM busco_equipamiento;
