<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->renameColumn('amount', 'amount_cents');   // !! MIGRATION_RENAME
            $table->dropColumn('old_status');   // !! MIGRATION_DROP
            $table->string('shipping_method')->nullable(false);   // !! MIGRATION_NOT_NULL
            $table->timestamp('sent_at')->nullable();   // !! MIGRATION_TIMEZONE
            $table->index('status');
        });

        DB::table('orders')->update(['shipping_method' => 'standard']);   // !! MIGRATION_BULK_UPDATE
    }
    // !! MIGRATION_DOWN
};
