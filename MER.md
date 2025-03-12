
## 📌 **Tablas y Relaciones**

### 🔹 **1. Usuarios**
📌 Almacena los datos de todos los usuarios del sistema (clientes, barberos, administradores).  

| Atributo        | Tipo de dato     | Descripción |
|----------------|----------------|-------------|
| `idUsuario`    | INT (PK, AI)    | Identificador único del usuario |
| `nombre_completo`       | VARCHAR(254)    | Nombre Completo del usuario |
| `telefono`       | VARCHAR(200)    | telefono del usuario |
| `f_nacimiento`       | DATE()    | fecha nacimiento del usuario |
| `correo`       | VARCHAR(100)    | Correo electrónico (único) |
| `contraseña`   | VARCHAR(255)    | Contraseña encriptada |
| `tipoUsuario`  | ENUM('Administrador', 'Barbero', 'Cliente') | Rol del usuario |

✅ **Restricción:**  
- Un usuario solo puede ser **Administrador, Barbero o Cliente (no más de uno).**  

---

### 🔹 **2. Administradores**
📌 Solo almacena los administradores registrados.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idAdmin`   | INT (PK, AI) | Identificador único del administrador |
| `idUsuario` | INT (FK)     | Relación con `Usuarios(idUsuario)` |

✅ **Relación:**  
- `Usuarios (1 : 1) Administradores`  

---

### 🔹 **3. Barberos**
📌 Contiene los barberos activos en la barbería.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idBarbero` | INT (PK, AI) | Identificador único del barbero |
|  `especialidad`       | VARCHAR(254)    | especialidad del usuario |
|  `horario_trabajo`       | VARCHAR(254)    | horario  del usuario |
|   `Creador_admin`       | INT(FK)    | Relación con `Adminis(idAdmin)` |
| `idUsuario` | INT (FK)     | Relación con `Usuarios(idUsuario)` |

✅ **Relación:**  
- `Usuarios (1 : 1) Barberos`  

---

### 🔹 **4. Clientes**
📌 Almacena información de los clientes registrados.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idCliente` | INT (PK, AI) | Identificador único del cliente |
| `idUsuario` | INT (FK)     | Relación con `Usuarios(idUsuario)` |

✅ **Relación:**  
- `Usuarios (1 : 1) Clientes`  

---

### 🔹 **5. Servicios**
📌 Lista de servicios ofrecidos en la barbería.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idServicio` | INT (PK, AI) | Identificador del servicio |
| `nombre`    | VARCHAR(100)  | Nombre del servicio |
| `precio`    | DECIMAL(10,2) | Precio del servicio |

✅ **Sin relaciones externas.**  

---

### 🔹 **6. Citas**
📌 Controla las citas agendadas por los clientes.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idCita`    | INT (PK, AI) | Identificador de la cita |
| `idCliente` | INT (FK)     | Relación con `Clientes(idCliente)` |
| `idBarbero` | INT (FK)     | Relación con `Barberos(idBarbero)` |
| `idServicio` | INT (FK)    | Relación con `Servicios(idServicio)` |
| `fechaHora` | DATETIME     | Fecha y hora de la cita |
| `estado`    | ENUM('Pendiente', 'Confirmada', 'Cancelada', 'Completada') | Estado de la cita |

✅ **Relaciones:**  
- `Clientes (1 : N) Citas`  
- `Barberos (1 : N) Citas`  
- `Servicios (1 : N) Citas`  

---

### 🔹 **7. Productos**
📌 Almacena los productos disponibles para la venta.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idProducto` | INT (PK, AI) | Identificador del producto |
| `nombre`    | VARCHAR(100)  | Nombre del producto |
| `precio`    | DECIMAL(10,2) | Precio de venta |
| `stock`     | INT          | Cantidad en inventario |

✅ **Sin relaciones externas.**  

---

### 🔹 **8. Ventas**
📌 Controla las ventas realizadas por barberos o administradores.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idVenta`   | INT (PK, AI) | Identificador de la venta |
| `idCliente` | INT (FK)     | Relación con `Clientes(idCliente)` |
| `idVendedor` | INT (FK)    | Relación con `Usuarios(idUsuario)` |
| `fecha`     | DATETIME     | Fecha de la venta |
| `total`     | DECIMAL(10,2) | Monto total de la venta |

✅ **Relaciones:**  
- `Clientes (1 : N) Ventas`  
- `Usuarios (1 : N) Ventas` *(Un barbero o administrador puede hacer ventas).*  

---

### 🔹 **9. DetalleVenta**
📌 Controla los productos vendidos en cada venta.  

| Atributo     | Tipo de dato  | Descripción |
|-------------|--------------|-------------|
| `idDetalleVenta` | INT (PK, AI) | Identificador del detalle |
| `idVenta`  | INT (FK)     | Relación con `Ventas(idVenta)` |
| `idProducto` | INT (FK)   | Relación con `Productos(idProducto)` |
| `cantidad` | INT         | Cantidad vendida |
| `subtotal` | DECIMAL(10,2) | Precio total por producto |

✅ **Relaciones:**  
- `Ventas (1 : N) DetalleVenta`  
- `Productos (1 : N) DetalleVenta`  

---

## 🎯 **Resumen de Relaciones**
✅ `Usuarios (1 : 1) Administradores`  
✅ `Usuarios (1 : 1) Barberos`  
✅ `Usuarios (1 : 1) Clientes`  
✅ `Clientes (1 : N) Citas`  
✅ `Barberos (1 : N) Citas`  
✅ `Servicios (1 : N) Citas`  
✅ `Clientes (1 : N) Ventas`  
✅ `Usuarios (1 : N) Ventas` *(Un vendedor puede ser barbero o admin).*  
✅ `Ventas (1 : N) DetalleVenta`  
✅ `Productos (1 : N) DetalleVenta`  

---


