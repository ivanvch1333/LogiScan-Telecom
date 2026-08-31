<?php

namespace App\Http\Controllers;

use App\Models\Equipo;
use App\Models\HistorialMovimiento;
use Illuminate\Http\Request;
use SimpleSoftwareIO\QrCode\Facades\QrCode;

class EquipoController extends Controller
{
    /**
     * Listar equipos con filtros avanzados
     */
    public function index(Request $request)
    {
        $query = Equipo::query();

        if ($request->has('categoria') && $request->categoria) {
            $query->where('categoria', $request->categoria);
        }
        if ($request->has('estado') && $request->estado) {
            $query->where('estado', $request->estado);
        }
        if ($request->has('ubicacion') && $request->ubicacion) {
            $query->where('ubicacion_actual', $request->ubicacion);
        }
        if ($request->has('plant') && $request->plant) {
            $query->where('plant', 'like', '%' . $request->plant . '%');
        }
        if ($request->has('numero_serie') && $request->numero_serie) {
            $query->where('numero_serie', 'like', '%' . $request->numero_serie . '%');
        }
        if ($request->has('mes') && $request->mes) {
            $query->whereMonth('created_at', $request->mes);
        }
        if ($request->has('anio') && $request->anio) {
            $query->whereYear('created_at', $request->anio);
        }

        return response()->json($query->get());
    }

    /**
     * Registrar un nuevo equipo en el inventario
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'nombre' => 'required|string|max:100',
            'marca' => 'required|string|max:50',
            'modelo' => 'required|string|max:50',
            'numero_serie' => 'required|string|unique:equipos,numero_serie',
            'plant' => 'required|string|max:50',
            'material' => 'required|string|max:50',
            'asset_tag' => 'required|string|unique:equipos,asset_tag',
            'qty_sap' => 'required|integer|min:0',
            'qty_eaim' => 'required|integer|min:0',
            'cliente_nombre' => 'nullable|string|max:100',
            'cliente_direccion' => 'nullable|string|max:200',
            'categoria' => 'required|in:router,switch,olt,edfa,enlace_radio,otro',
            'estado' => 'nullable|in:disponible,asignado,en_mantenimiento,baja',
            'ubicacion_actual' => 'nullable|in:1000,2000,1010,Almacén Central',
        ]);

        $equipo = Equipo::create($validated);

        // Movimiento inicial automático
        HistorialMovimiento::create([
            'equipo_id' => $equipo->id,
            'usuario_id' => $request->user()->id,
            'tipo_movimiento' => 'ingreso_almacen',
            'ubicacion_origen' => null,
            'ubicacion_destino' => $equipo->ubicacion_actual,
            'observaciones' => "Registro inicial de equipo en {$equipo->ubicacion_actual}. Conteo Real: {$equipo->qty_eaim}",
            'cliente_nombre' => $equipo->cliente_nombre,
            'cliente_direccion' => $equipo->cliente_direccion,
        ]);

        return response()->json($equipo, 201);
    }

    /**
     * Consultar equipo por número de serie o asset tag (Lector QR)
     */
    public function showBySerie($numero_serie)
    {
        $equipo = Equipo::where('numero_serie', $numero_serie)
            ->orWhere('asset_tag', $numero_serie)
            ->first();

        if (!$equipo) {
            return response()->json(['detail' => 'Equipo no encontrado.'], 404);
        }

        return response()->json($equipo);
    }

    /**
     * Generar código QR dinámico en formato PNG
     */
    public function generarQR($id)
    {
        $equipo = Equipo::find($id);

        if (!$equipo) {
            return response()->json(['detail' => 'Equipo no encontrado.'], 404);
        }

        $qrImage = QrCode::format('png')
            ->size(300)
            ->margin(1)
            ->generate($equipo->numero_serie);

        return response($qrImage)->header('Content-Type', 'image/png');
    }
}
