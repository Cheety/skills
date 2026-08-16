<?php

declare(strict_types=1);

namespace App\Support;

final readonly class Money
{
    public function __construct(public int $cent) {}

    public function formatted(): string
    {
        return number_format($this->cent / 100, 2, ',', '.').' EUR';
    }
}
