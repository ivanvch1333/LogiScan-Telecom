# INSTITUTO TECNOLÓGICO SUPERIOR UNIVERSITARIO ESPAÑA
## CARRERA DE TECNOLOGÍA SUPERIOR UNIVERSITARIA EN SISTEMAS DE INFORMACIÓN Y CIBERSEGURIDAD
### PROYECTOS WEB — MODALIDAD VIRTUAL

**PROYECTO INTEGRADOR / MACROACTIVIDAD**  
**SISTEMA WEB MOBILE DE CONTROL DE INVENTARIOS, CONCILIACIÓN DE ACTIVOS Y TRAZABILIDAD DE TELECOMUNICACIONES**  

* **Nombre del Sistema:** LogiScan Telecom  
* **Estudiante:** Klever Iván Valle Chérrez  
* **Nivel:** Quinto Nivel  
* **Docente:** Ing. Luis Geovanny Cacuango, Mg.  
* **Año:** 2026  

---

# TABLA DE CONTENIDOS
1. [FASE 1: SEMANAS 1 Y 2 — Conceptos Básicos y Herramientas de Diseño de Interfaces (UI/UX)](#fase-1-semanas-1-y-2--conceptos-básicos-y-herramientas-de-diseño-de-interfaces-uiux)
   - 1.1 Definición del Proyecto
   - 1.2 Problemática y Justificación
   - 1.3 Objetivos General y Específicos
   - 1.4 Requerimientos Funcionales (RF) y No Funcionales (RNF)
   - 1.5 Arquitectura de Información y Wireframes (UI/UX)
2. [FASE 2: SEMANAS 3 Y 4 — Herramientas Front-End y Fundamentos de Tailwind CSS](#fase-2-semanas-3-y-4--herramientas-front-end-y-fundamentos-de-tailwind-css)
   - 2.1 Enfoque Utility-First con Tailwind CSS
   - 2.2 Configuración del Sistema de Diseño (Design System)
   - 2.3 Estructura HTML Responsive y Componentes UI
3. [FASE 3: SEMANA 5 — Fundamentos de SASS para Desarrollo Web Responsive](#fase-3-semana-5--fundamentos-de-sass-para-desarrollo-web-responsive)
   - 3.1 Arquitectura SASS Modular (7-1 Pattern)
   - 3.2 Partials, Variables, Mixins y Nesting
   - 3.3 Estrategia de Responsividad y Animaciones
4. [FASE 4: SEMANAS 6, 7 Y 8 — Frameworks y Herramientas Backend con Laravel (PHP)](#fase-4-semanas-6-7-y-8--frameworks-y-herramientas-backend-con-laravel-php)
   - 4.1 Arquitectura del Servidor Backend en Laravel (MVC)
   - 4.2 Esquema de Base de Datos y Migraciones Eloquent
   - 4.3 Modelos y Relaciones Eloquent ORM
   - 4.4 Autenticación JWT / Sanctum y Roles (RBAC)
   - 4.5 Controladores API REST y Mapeo de Rutas
5. [MANUAL DE INSTALACIÓN Y EJECUCIÓN](#manual-de-instalación-y-ejecución)

---

# FASE 1: SEMANAS 1 Y 2 — Conceptos Básicos y Herramientas de Diseño de Interfaces (UI/UX)

## 1.1 Definición del Proyecto
**LogiScan Telecom** es una Single Page Application (SPA) móvil y web orientada a la conciliación física vs. teórica de activos de infraestructura de telecomunicaciones (routers, switches, OLTs, EDFAs, enlaces de radio). Permite la trazabilidad auditada de equipos entre almacenes centrales, ubicaciones técnicas SAP (SLOC 1000, 2000, 1010) y clientes finales instalados.

## 1.2 Problemática y Justificación
En la gestión operativa de bodegas y cuadrillas de telecomunicaciones en campo, existen discrepancias entre el stock teórico de SAP y el stock físico real (EAIM). La falta de un mecanismo de validación dinámica genera:
- **Descalce de Inventarios:** Pérdida de trazabilidad al momento de retirar o instalar equipos en clientes.
- **Tiempos de Auditoría Elevados:** Dificultad para consultar historiales de novedades en campo.
- **Falta de Estandarización:** Uso de hojas de cálculo aisladas sin control de roles ni inmutabilidad de datos.

La solución unifica el escaneo directo de códigos QR/Barras con la cámara del dispositivo móvil, la conciliación automática ($Qty_{SAP} - Qty_{EAIM}$), el control de acceso por roles (RBAC) y la exportación de reportes inmutables en Excel y PDF.

## 1.3 Objetivos
* **Objetivo General:** Desarrollar un sistema web móvil integral para el control de inventarios, conciliación de activos y trazabilidad de telecomunicaciones mediante tecnologías web modernas.
* **Objetivos Específicos:**
  1. Diseñar una interfaz móvil responsiva basada en principios de UX/UI dark mode con glassmorphism.
  2. Implementar la maquetación frontend utilizando Tailwind CSS y el preprocesador SASS.
  3. Desarrollar una API REST robusta bajo el framework Laravel (PHP) con autenticación JWT/Sanctum y ORM Eloquent.

## 1.4 Requerimientos del Sistema

### Requerimientos Funcionales (RF)
* **RF-01 (Autenticación y RBAC):** Inicio de sesión con usuario y contraseña (superusuario: `ectronix_log_amb` / `Macara@13`). Validación de contraseñas de al menos 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial.
* **RF-02 (Gestión de Activos):** Registro de equipos con Material SAP, Asset Tag, Número de Serie, Plant, SLOC (`1000`, `2000`, `1010`, `Almacén Central`), $Qty_{SAP}$ y $Qty_{EAIM}$.
* **RF-03 (Conciliación Automática):** Cálculo dinámico de la desviación ($Qty_{SAP} - Qty_{EAIM}$).
* **RF-04 (Trazabilidad y Movimientos):** Registro de traslados e instalaciones asociando nombre del cliente y dirección.
* **RF-05 (Escáner QR en Móvil):** Lectura directa de códigos QR/Barras mediante la cámara web/móvil usando `html5-qrcode`.
* **RF-06 (Reportes Auditables):** Exportación del stock filtrado a formatos Excel (`.xlsx`) y PDF horizontal (A4 landscape) con resumen estadístico.

### Requerimientos No Funcionales (RNF)
* **RNF-01 (Desempeño):** Respuestas de la API REST inferiores a 1.5 segundos en búsquedas por serial.
* **RNF-02 (Responsividad):** Diseño adaptable a dispositivos móviles (320px+), tablets y computadoras de escritorio.
* **RNF-03 (Seguridad):** Hashing de contraseñas con algoritmo Bcrypt y protección de rutas mediante tokens Bearer.

## 1.5 Arquitectura de Información y Wireframes (UI/UX)

El diseño de interfaz sigue un patrón **SPA (Single Page Application)** con panel lateral desplegable (`Sidebar`) en móviles y barra superior estática (`TopBar`).

```
+-----------------------------------------------------------------------------------+
| LOGISCAN TELECOM                                            [Usuario Admin] [Salir]|
+-------------------+---------------------------------------------------------------+
| 📊 Dashboard       |  +-------------+  +-------------+  +-------------+            |
| 📡 Equipos        |  | TOTAL: 24   |  | DISPO: 18   |  | ASIGNADO: 4 |            |
| 🔄 Movimientos    |  +-------------+  +-------------+  +-------------+            |
| 🔍 Lector QR      |                                                               |
| 👥 Usuarios (Admin)|  [Filtros: Planta | SLOC (1000, 2000, 1010) | Estado | Buscar ] |
| ⚙️ Ajustes (Admin) |  +---------------------------------------------------------+ |
|                   |  | Material | Asset Tag | Serie | SAP | EAIM | Desviación| |
|                   |  +---------------------------------------------------------+ |
+-------------------+---------------------------------------------------------------+
```

---

# FASE 2: SEMANAS 3 Y 4 — Herramientas Front-End y Fundamentos de Tailwind CSS

## 2.1 Enfoque Utility-First con Tailwind CSS
Se utiliza **Tailwind CSS** como motor de estilos utilitarios principal. Esto permite construir una interfaz moderna, rápida e inmune a hojas de estilo infladas, aplicando clases directamente en los elementos del DOM.

## 2.2 Configuración del Sistema de Diseño (Design System)
```javascript
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bgPrimary: 'hsl(220, 25%, 8%)',
        bgSecondary: 'hsl(225, 22%, 12%)',
        bgSidebar: 'hsl(230, 25%, 11%)',
        bgSurface: 'hsla(225, 25%, 16%, 0.6)',
        cyanAccent: 'hsl(175, 80%, 45%)',
        indigoAccent: 'hsl(230, 70%, 58%)',
        stateOperativo: '#2ecc71',
        stateMantenimiento: '#e67e22',
        stateEmergencia: '#e74c3c',
        stateBaja: '#95a5a6'
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif']
      }
    }
  }
}
```

## 2.3 Catálogo de Clases Utilitarias Implementadas

| Elemento UI | Clases Utilitarias Tailwind CSS |
|-------------|----------------------------------|
| **Fondo General** | `bg-[hsl(220,25%,8%)] text-slate-100 font-inter min-h-screen` |
| **Tarjetas Glassmorphism** | `bg-slate-800/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 shadow-xl` |
| **Botón Primario (Cian)** | `bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-2 rounded-lg transition-all duration-200 shadow-lg shadow-emerald-500/20` |
| **Badges de Estado** | `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold tracking-wide` |
| **Tabla de Datos** | `w-full text-left text-sm text-slate-300 border-collapse` |
| **Inputs de Formulario** | `w-full px-3 py-2 bg-slate-900/80 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-emerald-400 focus:ring-1 focus:ring-emerald-400` |

---

# FASE 3: SEMANA 5 — Fundamentos de SASS para Desarrollo Web Responsive

## 3.1 Arquitectura SASS Modular (7-1 Pattern)
Para mantener un código limpio y escalable, los estilos avanzados, mixins, animaciones e integraciones con librerías externas (como el lector QR de cámara) se organizan en componentes **SASS (SCSS)**.

```
resources/sass/
├── app.scss                # Archivo principal que compila la hoja final
├── _variables.scss         # Variables SASS ($colors, $fonts, $breakpoints)
├── _mixins.scss            # Mixins reutilizables (@mixin glassmorphism, @mixin responsive)
├── _animations.scss        # Keyframes (@keyframes fadeInUp, slideToast, scaleIn)
├── _components.scss        # Componentes personalizados con nesting SASS
└── _qr-scanner.scss        # Estilos específicos para la cámara del escáner QR
```

## 3.2 Ejemplos de Implementación SASS

### Mixins y Nesting (`_mixins.scss` y `_components.scss`)
```scss
@import 'variables';

@mixin glassmorphism($opacity: 0.6) {
  background: hsla(225, 25%, 16%, $opacity);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid hsla(220, 20%, 30%, 0.4);
}

@mixin responsive($breakpoint) {
  @if $breakpoint == mobile {
    @media (max-width: 768px) { @content; }
  } @else if $breakpoint == tablet {
    @media (max-width: 1024px) { @content; }
  }
}

// Timeline con Nesting SASS
.timeline {
  position: relative;
  padding-left: 1.5rem;

  &::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: hsla(220, 20%, 30%, 0.4);
  }

  .timeline-item {
    position: relative;
    padding-bottom: 1.25rem;

    &::before {
      content: '';
      position: absolute;
      left: calc(-1.5rem + 4px);
      top: 4px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: $color-cyan;
    }

    .timeline-content {
      @include glassmorphism(0.4);
      border-radius: 8px;
      padding: 0.75rem;
    }
  }
}
```

---

# FASE 4: SEMANAS 6, 7 Y 8 — Frameworks y Herramientas Backend con Laravel (PHP)

## 4.1 Arquitectura MVC en Laravel
El backend fue implementado sobre el framework **Laravel (PHP)** siguiendo el patrón **Modelo-Vista-Controlador (MVC)** y exponiendo una arquitectura de servicios API REST.

```
logiscan-telecom/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── AuthController.php        # Autenticación, Login, Profile
│   │   │   ├── EquipoController.php      # CRUD Inventario, Filtros, QR PNG
│   │   │   ├── MovimientoController.php  # Traslados y datos de Cliente
│   │   │   ├── UsuarioController.php     # Gestión RBAC de Usuarios
│   │   │   └── ConfigController.php      # Configuración de Marca (Logo/Banner)
│   │   └── Middleware/
│   │       └── AdminMiddleware.php       # Verificación de Rol Administrador
│   ├── Models/
│   │   ├── User.php                      # Modelo Usuario Eloquent
│   │   ├── Equipo.php                    # Modelo Equipo de Telecomunicaciones
│   │   └── HistorialMovimiento.php       # Modelo Trazabilidad / Movimientos
├── database/
│   ├── migrations/                       # Esquemas SQL de PostgreSQL / MySQL
│   └── seeders/
│       └── AdminSeeder.php               # Sembrado automático del Superusuario
├── routes/
│   ├── api.php                           # Rutas API REST protegidas
│   └── web.php                           # Despliegue de la vista Blade principal
```

## 4.2 Migraciones de Base de Datos (Eloquent Migrations)

### Tabla `usuarios` (`0001_01_01_000000_create_users_table.php`)
```php
Schema::create('usuarios', function (Blueprint $table) {
    $table->id();
    $table->string('nombre_completo', 100);
    $table->string('username', 50)->unique();
    $table->string('email', 100)->unique();
    $table->string('password');
    $table->enum('rol', ['admin', 'tecnico'])->default('tecnico');
    $table->timestamps();
});
```

### Tabla `equipos` (`0002_01_01_000000_create_equipos_table.php`)
```php
Schema::create('equipos', function (Blueprint $table) {
    $table->id();
    $table->string('nombre', 100);
    $table->string('marca', 50);
    $table->string('modelo', 50);
    $table->string('numero_serie', 100)->unique()->index();
    $table->string('plant', 50)->default('Planta Latacunga');
    $table->string('material', 50);
    $table->string('asset_tag', 50)->unique()->index();
    $table->integer('qty_sap')->default(1);
    $table->integer('qty_eaim')->default(0);
    $table->string('cliente_nombre', 100)->nullable();
    $table->string('cliente_direccion', 200)->nullable();
    $table->enum('categoria', ['router', 'switch', 'olt', 'edfa', 'enlace_radio', 'otro']);
    $table->enum('estado', ['disponible', 'asignado', 'en_mantenimiento', 'baja'])->default('disponible');
    $table->enum('ubicacion_actual', ['1000', '2000', '1010', 'Almacén Central'])->default('Almacén Central');
    $table->timestamps();
});
```

### Tabla `historial_movimientos` (`0003_01_01_000000_create_historial_movimientos_table.php`)
```php
Schema::create('historial_movimientos', function (Blueprint $table) {
    $table->id();
    $table->foreignId('equipo_id')->constrained('equipos')->cascadeOnDelete();
    $table->foreignId('usuario_id')->constrained('usuarios');
    $table->enum('tipo_movimiento', ['ingreso_almacen', 'instalacion_nodo', 'retiro_mantenimiento', 'reemplazo_emergencia']);
    $table->enum('ubicacion_origen', ['1000', '2000', '1010', 'Almacén Central'])->nullable();
    $table->enum('ubicacion_destino', ['1000', '2000', '1010', 'Almacén Central']);
    $table->text('observaciones')->nullable();
    $table->string('cliente_nombre', 100)->nullable();
    $table->string('cliente_direccion', 200)->nullable();
    $table->timestamps();
});
```

## 4.3 Modelos Eloquent ORM

### Modelo `Equipo` (`app/Models/Equipo.php`)
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Equipo extends Model
{
    protected $table = 'equipos';

    protected $fillable = [
        'nombre', 'marca', 'modelo', 'numero_serie',
        'plant', 'material', 'asset_tag', 'qty_sap', 'qty_eaim',
        'cliente_nombre', 'cliente_direccion',
        'categoria', 'estado', 'ubicacion_actual'
    ];

    // Cálculo dinámico de la desviación en JSON: Qty_SAP - Qty_EAIM
    protected $appends = ['desviacion'];

    public function getDesviacionAttribute()
    {
        return $this->qty_sap - $this->qty_eaim;
    }

    public function historial()
    {
        return $this->hasMany(HistorialMovimiento::class, 'equipo_id')->orderBy('created_at', 'desc');
    }
}
```

## 4.4 Mapeo de Rutas API REST (`routes/api.php`)

```php
use App\Http\Controllers\AuthController;
use App\Http\Controllers\EquipoController;
use App\Http\Controllers\MovimientoController;
use App\Http\Controllers\UsuarioController;
use App\Http\Controllers\ConfigController;
use Illuminate\Support\Facades\Route;

// Rutas Públicas
Route::post('/usuarios/login', [AuthController::class, 'login']);
Route::get('/config', [ConfigController::class, 'show']);
Route::get('/equipos/{id}/qr', [EquipoController::class, 'generarQR']);

// Rutas Protegidas por Sanctum Token (Técnicos y Admins)
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/usuarios/me', [AuthController::class, 'me']);
    Route::get('/equipos', [EquipoController::class, 'index']);
    Route::post('/equipos', [EquipoController::class, 'store']);
    Route::get('/equipos/serie/{numero_serie}', [EquipoController::class, 'showBySerie']);
    Route::post('/movimientos', [MovimientoController::class, 'store']);
    Route::get('/movimientos/equipo/{equipo_id}', [MovimientoController::class, 'historial']);

    // Rutas Exclusivas para Administrador (RBAC Middleware)
    Route::middleware('admin')->group(function () {
        Route::get('/usuarios', [UsuarioController::class, 'index']);
        Route::post('/usuarios/registro', [UsuarioController::class, 'store']);
        Route::put('/usuarios/{id}/rol', [UsuarioController::class, 'updateRol']);
        Route::delete('/usuarios/{id}', [UsuarioController::class, 'destroy']);
        Route::post('/config', [ConfigController::class, 'update']);
    });
});
```

---

# MANUAL DE INSTALACIÓN Y EJECUCIÓN

### 1. Requisitos Previos
* PHP 8.1+ y Composer
* PostgreSQL o MySQL / MariaDB
* Node.js & NPM (para compilación Vite/SASS)

### 2. Clonación e Instalación de Dependencias
```bash
git clone https://github.com/ivanvch1333/LogiScan-Telecom.git
cd LogiScan-Telecom
composer install
npm install
```

### 3. Configuración de Entorno y Base de Datos
Copiar el archivo `.env.example` a `.env`:
```ini
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=teletrack_db
DB_USERNAME=postgres
DB_PASSWORD=tu_contraseña
```

Ejecutar migraciones y sembrado de datos:
```bash
php artisan migrate --seed
```

### 4. Ejecución del Servidor
```bash
# Compilar recursos CSS/SASS
npm run build

# Iniciar servidor Laravel
php artisan serve
```
El sistema estará disponible inmediatamente en `http://127.0.0.1:8000`.

**Credenciales de acceso iniciales:**
* **Usuario:** `ectronix_log_amb`
* **Contraseña:** `Macara@13`
