<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class AdminMiddleware
{
    /**
     * Middleware de verificación de rol administrador (RBAC)
     */
    public function handle(Request $request, Closure $next)
    {
        if ($request->user() && $request->user()->rol === 'admin') {
            return $next($request);
        }

        return response()->json([
            'detail' => 'No tiene permisos de administrador para esta acción.'
        ], 403);
    }
}
