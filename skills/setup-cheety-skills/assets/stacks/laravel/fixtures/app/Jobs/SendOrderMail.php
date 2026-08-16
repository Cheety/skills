<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Models\Order;   // !! IDEMPOTENCY_JOB_MODEL
use Illuminate\Contracts\Queue\ShouldQueue;

class SendOrderMail implements ShouldQueue   // !! FORM_JOB_FINAL
{
    public function __construct(public Order $order) {}

    public function handle(): void
    {
        // no idempotency check   !! IDEMPOTENCY_JOB
        mail($this->order->email, 'Versendet', 'Ihre Order ist unterwegs.');
    }
}
