<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Invoice\SendDunning;
use App\Http\Resources\RechnungResource;
use Illuminate\Http\JsonResponse;

final class InvoiceController
{
    public function mahnen(int $invoice, SendDunning $action): JsonResponse
    {
        return RechnungResource::make($action->handle($invoice))->response();
    }
}
