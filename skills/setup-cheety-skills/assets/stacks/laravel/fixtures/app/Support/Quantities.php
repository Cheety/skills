<?php

declare(strict_types=1);

namespace App\Support;

use App\Data\InvoiceData;

final readonly class Quantities
{
    public function __construct(public float $count, public float $weight) {}

    public function fromData(InvoiceData $data): float
    {
        return (float) $data->amountCents;
    }
}
