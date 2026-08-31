<?php

namespace App\Http\Controllers;

use App\Models\Equipo;
use App\Models\HistorialMovimiento;
use Illuminate\Http\Request;

class MovimientoController extends Controller
{
    /**
     * Registrar un movimiento de traslado o instalación
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'equipo_id' => 'required|exists:equipos,id',
            'tipo_movimiento' => 'required|in:ingreso_almacen,instalacion_nodo,retiro_mantenimiento,reemplazo_emergencia',
            'ubicacion_destino' => 'required|in:1000,2000,1010,Almacén Central',
            'nuevo_estado' => 'nullable|in:disponible,asignado,en_mantenimiento,baja',
            'observaciones' => 'nullable|string',
            'cliente_nombre' => 'nullable|string|max:100',
            'cliente_direccion' => 'nullable|string|max:200',
        ]);

        $equipo = Equipo::findOrFail($validated['equipo_id']);
        $ubicacionOrigen = $equipo->ubicacion_actual;

        // Actualizar datos del equipo
        $equipo->ubicacion_actual = $validated['ubicacion_destino'];
        if (!empty($validated['nuevo_estado'])) {
            $equipo->estado = $validated['nuevo_estado'];
        }

        if ($validated['tipo_movimiento'] === 'instalacion_nodo') {
            $equipo->cliente_nombre = $validated['cliente_nombre'] ?? null;
            $equipo->cliente_direccion = $validated['cliente_direccion'] ?? null;
        } else {
            // Limpiar datos de cliente si regresa a un almacén técnico
            $equipo->cliente_nombre = null;
            $equipo->cliente_direccion = null;
        }

        $equipo->save();

        // Crear registro en la bitácora
        $movimiento = HistorialMovimiento::create([
            'equipo_id' => $equipo->id,
            'usuario_id' => $request->user()->id,
            'tipo_movimiento' => $validated['tipo_movimiento'],
            'ubicacion_origen' => $ubicacionOrigen,
            'ubicacion_destino' => $validated['ubicacion_destino'],
            'observaciones' => $validated['observaciones'] ?? null,
            'cliente_nombre' => $validated['cliente_nombre'] ?? null,
            'cliente_direccion' => $validated['cliente_direccion'] ?? null,
        ]);

        return response()->json($movimiento, 201);
    }

    /**
     * Consultar historial completo de trazabilidad de un equipo
     */
    public function historial($equipo_id)
    {
        $historial = HistorialMovimiento::where('equipo_id', $equipo_id)
            ->with('usuario:id,nombre_completo,username')
            ->orderBy('created_at', 'desc')
            ->get();

        return response()->json($historial);
    }
}
