<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rules\Password;

class UsuarioController extends Controller
{
    /**
     * Listar todos los usuarios del sistema (Admin)
     */
    public function index()
    {
        return response()->json(User::all());
    }

    /**
     * Crear un nuevo usuario técnico o admin (Admin)
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'nombre_completo' => 'required|string|max:100',
            'username' => 'required|string|max:50|unique:usuarios,username',
            'email' => 'required|email|max:100|unique:usuarios,email',
            'password' => ['required', 'string', Password::min(8)->mixedCase()->numbers()->symbols()],
            'rol' => 'required|in:admin,tecnico',
        ]);

        $validated['password'] = Hash::make($validated['password']);

        $user = User::create($validated);

        return response()->json($user, 201);
    }

    /**
     * Cambiar el rol de un usuario (Admin)
     */
    public function updateRol(Request $request, $id)
    {
        $user = User::findOrFail($id);

        if ($user->id === $request->user()->id) {
            return response()->json(['detail' => 'No puede cambiar su propio rol.'], 400);
        }

        $request->validate([
            'rol' => 'required|in:admin,tecnico'
        ]);

        $user->rol = $request->rol;
        $user->save();

        return response()->json($user);
    }

    /**
     * Eliminar un usuario (Admin)
     */
    public function destroy(Request $request, $id)
    {
        $user = User::findOrFail($id);

        if ($user->id === $request->user()->id) {
            return response()->json(['detail' => 'No puede eliminarse a sí mismo.'], 400);
        }

        $user->delete();

        return response()->json(null, 204);
    }
}
