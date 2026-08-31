<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    /**
     * Iniciar sesión y retornar token Sanctum Bearer
     */
    public function login(Request $request)
    {
        $request->validate([
            'username' => 'required|string',
            'password' => 'required|string',
        ]);

        $user = User::where('username', $request->username)->first();

        if (!$user || !Hash::check($request->password, $user->password)) {
            return response()->json([
                'detail' => 'Usuario o contraseña incorrectos'
            ], 401);
        }

        $token = $user->createToken('logiscan-token')->plainTextToken;

        return response()->json([
            'access_token' => $token,
            'token_type' => 'bearer'
        ]);
    }

    /**
     * Retornar usuario autenticado actual
     */
    public function me(Request $request)
    {
        return response()->json($request->user());
    }
}
