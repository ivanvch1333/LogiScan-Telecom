<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Equipo extends Model
{
    use HasFactory;

    protected $table = 'equipos';

    protected $fillable = [
        'nombre',
        'marca',
        'modelo',
        'numero_serie',
        'plant',
        'material',
        'asset_tag',
        'qty_sap',
        'qty_eaim',
        'cliente_nombre',
        'cliente_direccion',
        'categoria',
        'estado',
        'ubicacion_actual',
    ];

    /**
     * Atributo dinámico de desviación: Qty_SAP - Qty_EAIM
     */
    protected $appends = ['desviacion'];

    public function getDesviacionAttribute()
    {
        return $this->qty_eaim - $this->qty_sap;
    }

    /**
     * Relación Eloquent: Un equipo tiene muchos movimientos en su historial
     */
    public function historial()
    {
        return $this->hasMany(HistorialMovimiento::class, 'equipo_id')->orderBy('created_at', 'desc');
    }
}
