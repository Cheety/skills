<?php

declare(strict_types=1);

namespace App\Actions\Order;

final readonly class ErrorHandling
{
    public function handle(int $id): void
    {
        try {
            $this->work($id);
        } catch (\RuntimeException $e) {
        }   // !! ERROR_SWALLOWED

        $inhalt = @file_get_contents('/tmp/x');   // !! ERROR_SUPPRESSED
    }

    private function work(int $id): void {}
}
