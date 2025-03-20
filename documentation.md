
## **📌 Índice**  
- [**� Índice**](#-índice)
- [**🔹 Introducción**](#-introducción)
- [**🔹 Función `register(request)`**](#-función-registerrequest)
  - [**📌 Características**](#-características)
  - [**📌 Flujo de la Función**](#-flujo-de-la-función)
- [**🔹 Manejo de Errores**](#-manejo-de-errores)
- [**🔹 Consideraciones Adicionales**](#-consideraciones-adicionales)

---

## **🔹 Introducción**  
Este documento describe el funcionamiento de la función **`register(request)`**, utilizada para gestionar el registro de usuarios en **Ziara App**.  

A diferencia de los registros tradicionales con múltiples formularios y vistas separadas, esta función **unifica el proceso de registro** para usuarios, barberos y administradores, evitando código redundante y mejorando la eficiencia del sistema.  

---

## **🔹 Función `register(request)`**  

### **📌 Características**  
✅ Unifica el registro para **Clientes, Barberos y Administradores**.  
✅ Solo el **Administrador** puede crear cuentas de **Barberos y Administradores**.  
✅ **Evita múltiples formularios** al usar un `dropdown` para seleccionar el tipo de cuenta.  
✅ **Soporte para foto de perfil**, la cual se procesa automáticamente para ser redonda.  
✅ **Envía un correo de bienvenida** al usuario registrado (si el correo es válido).  

### **📌 Flujo de la Función**  
1. **Verifica que la solicitud sea POST**.  
2. **Obtiene los datos del formulario** (email, contraseña, rol y foto).  
3. **Cifra la contraseña** antes de guardarla.  
4. **Guarda el usuario en la base de datos**.  
5. **Procesa la foto de perfil** (redonda o predeterminada si no se sube ninguna).  
6. **Asigna el rol**:
   - Si es **Barbero**, lo registra en la tabla `Barberos`.  
   - Si es **Administrador**, lo registra en la tabla `Administradores`.  
   - Si es **Cliente**, no requiere una tabla extra.  
7. **Envía un correo de bienvenida** con los datos de la cuenta.  
8. **Manejo de errores**:  
   - Si el correo ya está en uso, muestra un mensaje de error.  
   - Si hay problemas con la base de datos o el correo, lo notifica.  
9. **Redirecciona según el tipo de usuario**:
   - Administradores y Barberos → `listar_usuarios`  
   - Clientes → `login`  

---

## **🔹 Manejo de Errores**  
| Error Detectado | Acción Tomada |
|----------------|--------------|
| Correo ya registrado | Muestra un mensaje de error y redirige según el rol. |
| Falla en el envío de correo | Notifica al usuario pero mantiene el registro exitoso. |
| Problema general en la base de datos | Muestra un mensaje de error genérico y redirige. |

---

## **🔹 Consideraciones Adicionales**  
- La función solo permite registros desde el **login** o el **panel de administración**.  
- Si alguien intenta acceder a la URL `/register` sin un `POST`, será redirigido al `index`.  
- **Mejora la experiencia del usuario** al no mostrar opciones innecesarias según el rol.  
- La foto de perfil se guarda automáticamente en formato redondo sin intervención del usuario.  

