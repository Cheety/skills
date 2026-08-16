<?php
// !! STRICT_TYPES

namespace App\Enums;

use App\Models\Order;   // !! BOUNDARY_ENUM_PURE

enum OrderStatus: string
{
    case Neu = 'new';
    case Versendet = 'sent';

    public function label(): string
    {
        return match ($this) {
            self::Neu => 'Neu',
            default => 'Unbekannt',   // !! STATE_MATCH_DEFAULT
        };
    }
}
