<?php

declare(strict_types=1);

namespace App\Models;

use App\Actions\Order\ShipOrder;   // !! BOUNDARY_MODEL_LOGIC
use Illuminate\Database\Eloquent\Model;

final class Order extends Model
{
    protected $guarded = [];   // !! STATE_MASS_ASSIGNMENT

    public function versenden(): void
    {
        app(ShipOrder::class)->handle($this->id);
    }
}
