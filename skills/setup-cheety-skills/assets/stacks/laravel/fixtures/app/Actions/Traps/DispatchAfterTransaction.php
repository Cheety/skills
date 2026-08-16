<?php

declare(strict_types=1);

namespace App\Actions\Traps;

use App\Jobs\SendDunningMail;
use Illuminate\Support\Facades\DB;

final readonly class DispatchAfterTransaction
{
    public function handle(int $id): int
    {
        $new = DB::transaction(
            function () use ($id) {
                $wert = $id * 2;

                return $wert;
            }
        );

        SendDunningMail::dispatch($new);

        return $new;
    }
}
