<?php

declare(strict_types=1);

namespace App\Actions\Traps;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

final readonly class ActionWithLog
{
    public function handle(int $id): int
    {
        $count = DB::transaction(fn () => $id);

        Log::info('traps.ausgefuehrt', ['count' => $count]);

        return $count;
    }
}
