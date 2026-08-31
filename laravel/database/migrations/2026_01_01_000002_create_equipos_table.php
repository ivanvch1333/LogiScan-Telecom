<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
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
    }

    public function down()
    {
        Schema::dropIfExists('equipos');
    }
};
