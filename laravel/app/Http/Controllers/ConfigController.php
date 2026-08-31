<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class ConfigController extends Controller
{
    private function getConfigFilePath()
    {
        return storage_path('app/config.json');
    }

    /**
     * Obtener datos de la marca (Nombre, Logo, Banner)
     */
    public function show()
    {
        $file = $this->getConfigFilePath();

        if (file_exists($file)) {
            $config = json_decode(file_get_contents($file), true);
            return response()->json($config);
        }

        return response()->json([
            'nombre_empresa' => 'LogiScan Telecom',
            'logo_url' => null,
            'banner_url' => null,
        ]);
    }

    /**
     * Actualizar configuración de marca y subir archivos
     */
    public function update(Request $request)
    {
        $file = $this->getConfigFilePath();
        $config = [
            'nombre_empresa' => 'LogiScan Telecom',
            'logo_url' => null,
            'banner_url' => null,
        ];

        if (file_exists($file)) {
            $config = json_decode(file_get_contents($file), true);
        }

        if ($request->has('nombre_empresa') && !empty($request->nombre_empresa)) {
            $config['nombre_empresa'] = $request->nombre_empresa;
        }

        if ($request->hasFile('logo')) {
            $logoPath = $request->file('logo')->store('uploads', 'public');
            $config['logo_url'] = '/storage/' . $logoPath;
        }

        if ($request->hasFile('banner')) {
            $bannerPath = $request->file('banner')->store('uploads', 'public');
            $config['banner_url'] = '/storage/' . $bannerPath;
        }

        if (!file_exists(dirname($file))) {
            mkdir(dirname($file), 0755, true);
        }

        file_put_contents($file, json_encode($config, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

        return response()->json($config);
    }
}
