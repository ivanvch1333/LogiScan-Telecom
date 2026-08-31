<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class HistorialMovimiento extends Model
{
    use HasFactory;

    protected $table = 'historial_movimientos';

    protected $fillable = [
        'equipo_id',
        'usuario_id',
        'tipo_movimiento',
        'ubicacion_origen',
        'ubicacion_destino',
        'observaciones',
        'cliente_nombre',
        'cliente_direccion',
    ];

    public function equipo()
    {
        return $this->belongsTo(Equipo::class, 'equipo_id');
    }

    public function usuario()
    {
        return $this->belongsTo(User::class, 'usuario_id');
    }
}
