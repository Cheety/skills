<?php

declare(strict_types=1);

namespace App\Actions\Traps;

final readonly class WordTrapAction
{
    /**
     * Note: this comment used to contain a dump() and an env() call.
     * var_dump() and dd() are only mentioned here.
     */
    public function handle(): string
    {
        $hint = 'Please use neither dump() nor env(APP_KEY).';
        $environment = $this->environment();

        return $hint.$environment;
    }

    private function environment(): string
    {
        return 'produktion';
    }
}
