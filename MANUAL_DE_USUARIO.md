# MANUAL DE USUARIO POR ROLES Y FUNCIONES
## LOGISCAN TELECOM — SISTEMA WEB MOBILE DE CONTROL DE INVENTARIOS Y CONCILIACIÓN DE ACTIVOS

---

# TABLA DE CONTENIDOS
1. [Introducción y Acceso al Sistema](#1-introducción-y-acceso-al-sistema)
2. [Matriz General de Permisos y Roles (RBAC)](#2-matriz-general-de-permisos-y-roles-rbac)
3. [Manual para el Rol: ADMINISTRADOR](#3-manual-para-el-rol-administrador)
   - 3.1 Credenciales y Acceso Inicial
   - 3.2 Monitoreo del Dashboard y Conciliación
   - 3.3 Gestión de Inventario y Conciliación SAP vs EAIM
   - 3.4 Registro de Movimientos e Instalaciones a Clientes
   - 3.5 Uso del Lector QR de Cámara Móvil
   - 3.6 Exportación de Auditorías (Excel y PDF)
   - 3.7 Administración de Usuarios y Roles (RBAC)
   - 3.8 Personalización de Marca (Logo, Banner, Nombre)
4. [Manual para el Rol: TÉCNICO / BODEGUERO](#4-manual-para-el-rol-técnico--bodeguero)
   - 4.1 Acceso al Sistema
   - 4.2 Consulta del Dashboard
   - 4.3 Registro de Materiales y Conciliación en Bodega
   - 4.4 Traslados de Equipos e Instalación en Campo
   - 4.5 Escáner QR Móvil en Bodega/Campo
   - 4.6 Exportación de Reportes Auditables
   - 4.7 Restricciones de Seguridad Visibles
5. [Preguntas Frecuentes y Solución de Problemas](#5-preguntas-frecuentes-y-solución-de-problemas)

---

# 1. INTRODUCCIÓN Y ACCESO AL SISTEMA

**LogiScan Telecom** es una plataforma web móvil diseñada para controlar el inventario técnico, realizar la conciliación entre el stock teórico registrados en SAP y el stock físico real (EAIM), y mantener la trazabilidad de equipos de telecomunicaciones (routers, switches, OLTs, EDFAs, enlaces de radio).

### Acceso a la Plataforma
* **Dirección Web:** `http://localhost:8000` (o servidor asignado)
* **Compatibilidad:** Navegadores web en computadoras PC/Mac y navegadores en smartphones (Android / iOS) con soporte para cámara web.

---

# 2. MATRIZ GENERAL DE PERMISOS Y ROLES (RBAC)

El sistema opera bajo un **Control de Acceso Basado en Roles (RBAC)** que garantiza que cada usuario solo acceda a los módulos autorizados:

| Módulo / Función | Rol Administrador | Rol Técnico / Bodeguero |
|------------------|:-----------------:|:-----------------------:|
| Inicio de Sesión y Perfil | ✅ | ✅ |
| Dashboard de Métricas y Estadísticas | ✅ | ✅ |
| Visualizar Inventario (Filtros por SLOC `1000`, `2000`, `1010`, Planta, Estado, Mes, Año, Serie) | ✅ | ✅ |
| Registrar Nuevo Activo (Material, Asset Tag, Serie, Qty SAP, Qty EAIM) | ✅ | ✅ |
| Registrar Movimientos / Traslados entre SLOCs | ✅ | ✅ |
| Registrar Instalación a Cliente (Nombre y Dirección del Cliente) | ✅ | ✅ |
| Escáner de Códigos QR/Barras con Cámara Móvil | ✅ | ✅ |
| Exportación de Auditoría a Excel (`.xlsx`) y PDF (A4 Landscape) | ✅ | ✅ |
| **Gestión de Usuarios (Crear, cambiar rol, eliminar usuarios)** | ✅ | ❌ *(Bloqueado)* |
| **Ajustes de Marca (Nombre de empresa, Logo oficial, Banner)** | ✅ | ❌ *(Bloqueado)* |

---

# 3. MANUAL PARA EL ROL: ADMINISTRADOR

El **Administrador** tiene control operativo completo del sistema, además de las atribuciones exclusivas de gobernanza (usuarios, roles y personalización corporativa).

## 3.1 Credenciales y Acceso Inicial
* **Usuario por defecto:** `ectronix_log_amb`
* **Contraseña por defecto:** `Macara@13`

1. Ingrese a la pantalla de inicio de sesión.
2. Escriba su usuario y contraseña.
3. Haga clic en **"Iniciar Sesión"**.

## 3.2 Monitoreo del Dashboard y Conciliación
Al ingresar verá 5 tarjetas de resumen dinámico:
* **Total Materiales:** Suma global de activos en base de datos.
* **Disponible:** Equipos listos en almacén para asignación.
* **Asignado:** Equipos instalados en clientes o asignados a nodos.
* **En Mantenimiento:** Equipos en revisión técnica o reparación.
* **De Baja:** Equipos desincorporados por avería irrecuperable.

Además, incluye gráficos de distribución por categoría (Router, Switch, OLT, etc.) y por ubicación SLOC (`1000`, `2000`, `1010`, `Almacén Central`), junto con la tabla de materiales recientemente ingresados.

## 3.3 Gestión de Inventario y Conciliación SAP vs EAIM
En la sección **📡 Equipos**:
1. **Filtros Avanzados:** Filtre en tiempo real por palabra clave (Serie, Asset Tag, Material), Planta, Ubicación SLOC (`1000`, `2000`, `1010`, `Almacén Central`), Estado, Mes y Año de registro.
2. **Cálculo de Desviación:** El sistema calcula automáticamente la fórmula:
   $$\text{Desviación} = Qty_{SAP} - Qty_{EAIM}$$
   * Si la desviación es **0**, se muestra en verde (inventario conciliado).
   * Si la desviación es diferente de 0, se resalta en rojo (alerta de descalce).
3. **Registrar Nuevo Equipo:**
   - Haga clic en **"+ Nuevo Equipo"**.
   - Ingrese los datos obligatorios: Nombre, Código Material SAP, Nº Serie, Asset Tag (Placa), Marca, Modelo, Plant, SLOC, Qty SAP, Qty EAIM y Categoría.
   - *(Opcional)* Si el equipo se registra ya instalado, complete Nombre y Dirección del Cliente.
   - Haga clic en **"Registrar Activo"**.

## 3.4 Registro de Movimientos e Instalaciones a Clientes
En la sección **🔄 Movimientos**:
1. Seleccione el equipo desde el desplegable.
2. Elija el **Tipo de Movimiento**:
   - `Ingreso Almacén`
   - `Instalación Nodo`
   - `Retiro Mantenimiento`
   - `Reemplazo Emergencia`
3. Elija el **SLOC Destino** (`1000`, `2000`, `1010`, `Almacén Central`).
4. **Si el tipo de movimiento es `Instalación Nodo`:** Se desplegarán automáticamente los campos obligatorios para ingresar el **Nombre del Cliente / Empresa** y la **Dirección de Instalación**.
5. *(Opcional)* Cambie el estado del equipo o agregue observaciones técnicas.
6. Haga clic en **"Registrar Movimiento"**.

## 3.5 Uso del Lector QR de Cámara Móvil
En la sección **🔍 Lector QR / Cámara**:
1. En teléfonos móviles o computadoras con cámara web, presione **"📷 Iniciar Escáner de Cámara"**.
2. Apunte la cámara hacia el código QR o código de barras del equipo.
3. El sistema detectará el serial automáticamente y desplegará la ficha completa del activo, su ubicación actual, cliente asignado y el historial cronológico de movimientos.

## 3.6 Exportación de Auditorías (Excel y PDF)
En la parte superior de la sección **Equipos**:
* **Boton 📊 Excel:** Genera un libro `.xlsx` con todas las columnas de inventario, stock SAP, stock EAIM, Desviación, datos del Cliente y fecha de registro.
* **Boton 📄 PDF:** Genera un documento PDF horizontal (formato A4 Landscape) con encabezados institucionales, resumen estadístico por estados, líneas de separación y paginado automático.

## 3.7 Administración de Usuarios y Roles (RBAC) *(Exclusivo Admin)*
En la sección **👥 Usuarios**:
1. **Crear Usuario:** Haga clic en **"+ Nuevo Usuario"**, ingrese el nombre, username, correo, rol (`admin` o `tecnico`) y una contraseña que cumpla las políticas de seguridad (mínimo 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial).
2. **Cambiar Rol:** Presione el botón 🔄 en la fila correspondiente para alternar el rol entre Administrador y Técnico.
3. **Eliminar Usuario:** Presione el botón 🗑 para eliminar un usuario. *(El sistema no permite que un admin se elimine o cambie de rol a sí mismo)*.

## 3.8 Personalización de Marca (Logo, Banner, Nombre) *(Exclusivo Admin)*
En la sección **⚙️ Ajustes**:
1. Cambie el **Nombre del Proyecto / Empresa**.
2. Suba el **Logotipo Oficial** (PNG o JPG). Podrá ver la vista previa al instante.
3. Suba el **Banner de Bienvenida** horizontal para el Dashboard.
4. Haga clic en **"Guardar Configuración"**. El sistema actualizará el branding en toda la aplicación.

---

# 4. MANUAL PARA EL ROL: TÉCNICO / BODEGUERO

El **Técnico o Bodeguero** cuenta con un entorno optimizado para la operación en campo y bodega, enfocado en el registro de inventario, conciliación, transferencias entre SLOCs, lectura QR y exportación de reportes.

## 4.1 Acceso al Sistema
Ingrese con las credenciales entregadas por el administrador de la plataforma.

## 4.2 Consulta del Dashboard
Permite visualizar los totales de stock, equipos disponibles, asignados, en mantenimiento y de baja, garantizando visibilidad de la disponibilidad de materiales.

## 4.3 Registro de Materiales y Conciliación en Bodega
1. Ingrese a **📡 Equipos**.
2. Puede realizar ingresos físicos de nuevos equipos especificando las cantidades $Qty_{SAP}$ y $Qty_{EAIM}$.
3. Realice búsquedas rápidas por placa o serial al momento de recibir o despachar mercancía.

## 4.4 Traslados de Equipos e Instalaciones en Campo
1. Ingrese a **🔄 Movimientos**.
2. Registre el movimiento de un equipo hacia los SLOCs autorizados (`1000`, `2000`, `1010`, `Almacén Central`).
3. En instalaciones domiciliarias o empresariales, seleccione `Instalación Nodo` e ingrese los datos del cliente y la dirección exacta.

## 4.5 Escáner QR Móvil en Bodega/Campo
1. Desde su teléfono móvil, abra **🔍 Lector QR**.
2. Active la cámara para escanear etiquetas pegadas en los chasis de los equipos.
3. Verifique al instante el historial de mantenimientos o transferencias anteriores del equipo.

## 4.6 Exportación de Reportes Auditables
Los técnicos pueden generar descargas de reportes en **Excel** y **PDF** para adjuntarlos a las actas de entrega-recepción o respaldos de cuadrilla.

## 4.7 Restricciones de Seguridad Visibles
Por seguridad del sistema, el rol Técnico **no visualiza** en el menú lateral las pestañas de **Usuarios** ni **Ajustes de Marca**. Si un técnico intenta acceder directamente mediante peticiones API a estas rutas, el servidor retornará un código de error `403 Forbidden` (Acceso denegado).

---

# 5. PREGUNTAS FRECUENTES Y SOLUCIÓN DE PROBLEMAS

### ¿Qué ocurre si la contraseña no cumple los requisitos al crear un usuario?
El sistema rechazará el formulario tanto en el frontend como en el servidor, mostrando la alerta: `"La contraseña debe tener al menos 8 caracteres, incluir una mayúscula, un número y un carácter especial"`.

### ¿Qué hago si la cámara del móvil no abre en el lector QR?
Verifique que le ha otorgado permisos de cámara al navegador web en la configuración del smartphone. El sitio debe ejecutarse sobre `localhost` o en una conexión segura `https://`.

### ¿Cómo se desvincula un cliente de un equipo si el equipo se retira por falla?
Al registrar un movimiento de tipo `Retiro Mantenimiento` o mover el equipo de regreso a un almacén (`1000`, `2000`, `1010`, `Almacén Central`), el sistema desvincula automáticamente al cliente del equipo activo y conserva el dato histórico en la línea de tiempo de auditoría.
