<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
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
    }

    public function down()
    {
        Schema::dropIfExists('historial_movimientos');
    }
};
