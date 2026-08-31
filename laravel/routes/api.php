<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\EquipoController;
use App\Http\Controllers\MovimientoController;
use App\Http\Controllers\UsuarioController;
use App\Http\Controllers\ConfigController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes - LogiScan Telecom
|--------------------------------------------------------------------------
*/

// Rutas Públicas
Route::post('/usuarios/login', [AuthController::class, 'login']);
Route::get('/config', [ConfigController::class, 'show']);
Route::get('/equipos/{id}/qr', [EquipoController::class, 'generarQR']);

// Rutas Autenticadas (Técnico y Admin)
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/usuarios/me', [AuthController::class, 'me']);
    Route::get('/equipos', [EquipoController::class, 'index']);
    Route::post('/equipos', [EquipoController::class, 'store']);
    Route::get('/equipos/serie/{numero_serie}', [EquipoController::class, 'showBySerie']);
    Route::post('/movimientos', [MovimientoController::class, 'store']);
    Route::get('/movimientos/equipo/{equipo_id}', [MovimientoController::class, 'historial']);

    // Rutas Exclusivas Administrador (RBAC)
    Route::middleware('admin')->group(function () {
        Route::get('/usuarios', [UsuarioController::class, 'index']);
        Route::post('/usuarios/registro', [UsuarioController::class, 'store']);
        Route::put('/usuarios/{id}/rol', [UsuarioController::class, 'updateRol']);
        Route::delete('/usuarios/{id}', [UsuarioController::class, 'destroy']);
        Route::post('/config', [ConfigController::class, 'update']);
    });
});
