<?php

declare(strict_types=1);

namespace App\Models;

use App\Enums\InvoiceStatus;
use Illuminate\Database\Eloquent\Model;

final class Invoice extends Model
{
    protected $fillable = ['kunde_id', 'amount_cents', 'status', 'dunned_at'];

    protected $casts = [
        'status' => InvoiceStatus::class,
        'dunned_at' => 'immutable_datetime',
    ];

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }
}
