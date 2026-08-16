<?php

declare(strict_types=1);

namespace App\Actions\Invoice;

use App\Enums\InvoiceStatus;
use App\Exceptions\InvalidStatusTransition;
use App\Jobs\SendDunningMail;
use App\Models\Invoice;
use Illuminate\Support\Facades\DB;

final readonly class SendDunning
{
    public function handle(int $rechnungId): Invoice
    {
        $invoice = DB::transaction(function () use ($rechnungId) {
            $invoice = Invoice::lockForUpdate()->findOrFail($rechnungId);

            if (! $invoice->status->canTransitionTo(InvoiceStatus::Dunning)) {
                throw new InvalidStatusTransition();
            }

            $invoice->update([
                'status' => InvoiceStatus::Dunning,
                'dunned_at' => now(),
            ]);

            return $invoice;
        });

        SendDunningMail::dispatch($invoice->id);

        return $invoice;
    }
}
