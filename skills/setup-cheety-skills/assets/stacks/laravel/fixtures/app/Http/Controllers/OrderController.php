<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Models\Order;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;   // !! BOUNDARY_CONTROLLER_DB

class OrderController   // !! FORM_CONTROLLER_FINAL
{
    public function index(Request $request)
    {
        $query = DB::table('orders');

        if ($request->has('status')) {
            $query->where('status', $request->input('status'));
        }

        if ($request->has('von')) {
            $query->where('created_at', '>=', $request->input('von'));
        }

        if ($request->has('bis')) {
            $query->where('created_at', '<=', $request->input('bis'));
        }

        $ergebnis = $query->orderBy('created_at')->paginate(50);

        foreach ($ergebnis as $zeile) {
            $zeile->kunde_name = Order::find($zeile->id)->customer->name;
        }

        $limit = env('BESTELL_LIMIT', 100);   // !! ENV_OUTSIDE_CONFIG

        return view('orders.index', compact('ergebnis', 'limit'));
    }
}
