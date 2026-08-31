<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AdminSeeder extends Seeder
{
    /**
     * Sembrado del Superusuario Inicial
     */
    public function run()
    {
        if (User::count() === 0) {
            User::create([
                'nombre_completo' => 'Administrador Principal',
                'username' => 'ectronix_log_amb',
                'email' => 'admin@logiscan.com',
                'password' => Hash::make('Macara@13'),
                'rol' => 'admin',
            ]);
        }
    }
}
