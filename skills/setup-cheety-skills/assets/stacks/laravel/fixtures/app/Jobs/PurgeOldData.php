<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Actions\Invoice\PurgeInvoices;
use Illuminate\Contracts\Queue\ShouldQueue;

final class PurgeOldData implements ShouldQueue
{
    public function __construct(public int $tage) {}

    public function handle(PurgeInvoices $action): void
    {
        if ($this->tage < 1) {
            return;
        }

        $action->handle($this->tage);
    }
}
