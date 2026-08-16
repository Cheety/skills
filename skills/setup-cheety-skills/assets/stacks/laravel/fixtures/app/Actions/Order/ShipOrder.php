<?php

declare(strict_types=1);

namespace App\Actions\Order;

use App\Jobs\SendOrderMail;
use App\Models\Order;
use Illuminate\Http\Request;   // !! BOUNDARY_ACTION_HTTP
use Illuminate\Support\Facades\Cache;   // !! BOUNDARY_ACTION_FACADE
use Illuminate\Support\Facades\DB;

class ShipOrder   // !! FORM_ACTION_FINAL
{
    public function run(Request $request): void   // !! FORM_ACTION_HANDLE
    {
        DB::transaction(function () use ($request) {
            $order = Order::find($request->input('id'));
            $order->update(['status' => 'sent']);

            SendOrderMail::dispatch($order);   // !! TRANSACTION_DISPATCH
        });

        Cache::forget('orders');
        dump($order);   // !! DEBUG_OUTPUT
    }
}
