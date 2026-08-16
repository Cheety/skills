<?php

declare(strict_types=1);

namespace App\Enums;

enum InvoiceStatus: string
{
    case Entwurf = 'draft';
    case Versendet = 'sent';
    case Dunning = 'dunning';
    case Bezahlt = 'paid';
    case Storniert = 'cancelled';

    /** @return array<self> */
    public function allowedTransitions(): array
    {
        return match ($this) {
            self::Entwurf => [self::Versendet, self::Storniert],
            self::Versendet => [self::Dunning, self::Bezahlt, self::Storniert],
            self::Dunning => [self::Bezahlt, self::Storniert],
            self::Bezahlt, self::Storniert => [],
        };
    }

    public function canTransitionTo(self $ziel): bool
    {
        return in_array($ziel, $this->allowedTransitions(), strict: true);
    }
}
