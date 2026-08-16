<?php

declare(strict_types=1);

namespace App\Data;

class OrderData   // !! FORM_DATA_IMMUTABLE
{
    public float $amount;   // !! STATE_MONEY_FLOAT

    public function __construct(float $amount)
    {
        $this->amount = $amount;
    }
}
