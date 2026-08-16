<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Actions\Invoice\MarkDunningSent;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;

final class SendDunningMail implements ShouldBeUnique, ShouldQueue
{
    public int $tries = 3;

    public int $uniqueFor = 3600;

    public function __construct(public int $rechnungId) {}

    public function uniqueId(): string
    {
        return (string) $this->rechnungId;
    }

    public function handle(MarkDunningSent $action): void
    {
        $action->handle($this->rechnungId);
    }
}
