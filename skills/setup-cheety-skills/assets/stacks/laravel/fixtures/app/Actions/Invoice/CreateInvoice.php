<?php

declare(strict_types=1);

namespace App\Actions\Invoice;

use App\Data\InvoiceData;
use App\Enums\InvoiceStatus;
use App\Models\Invoice;
use Illuminate\Support\Facades\DB;

final readonly class CreateInvoice
{
    public function handle(InvoiceData $data): Invoice
    {
        return DB::transaction(fn () => Invoice::create([
            'kunde_id' => $data->kundeId,
            'amount_cents' => $data->amountCents,
            'status' => InvoiceStatus::Entwurf,
        ]));
    }
}
