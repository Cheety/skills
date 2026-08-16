<?php

declare(strict_types=1);

namespace App\Data;

final readonly class InvoiceData
{
    public function __construct(
        public int $kundeId,
        public int $amountCents,
    ) {}
}
