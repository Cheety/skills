<?php

declare(strict_types=1);

namespace App\Support;

use App\Models\Order;   // !! BOUNDARY_SUPPORT_PURE

final class OrderHelper
{
    public static function count(): int
    {
        return Order::count();
    }
}
