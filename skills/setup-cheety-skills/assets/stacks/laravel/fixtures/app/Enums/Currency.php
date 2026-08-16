<?php

declare(strict_types=1);

namespace App\Enums;

enum Currency: string
{
    case Euro = 'EUR';
    case Franc = 'CHF';

    public function symbol(): string
    {
        return match ($this) {
            self::Euro => 'EUR',
            self::Franc => 'CHF',
        };
    }

    public function decimals(): int
    {
        return match (true) {
            $this === self::Euro => 2,
            default => 2,
        };
    }
}
