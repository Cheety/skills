<?php

declare(strict_types=1);

namespace App\Actions\Traps;

use Illuminate\Support\Facades\Log;

final readonly class CleanCatch
{
    public function handle(int $id): string
    {
        // Looks like a violation but is not: the error is handled,
        // not swallowed. And the e-mail address is not an @ operator.
        try {
            return $this->work($id);
        } catch (\RuntimeException $e) {
            Log::warning('work.fehlgeschlagen', ['id' => $id]);

            throw new \DomainException("Arbeit fuer {$id} fehlgeschlagen.", previous: $e);
        }
    }

    public function sender(): string
    {
        return 'noreply@example.com';
    }

    private function work(int $id): string
    {
        return (string) $id;
    }
}
