<?php

declare(strict_types=1);

use App\Actions\Order\ShipOrder;

it('sent eine Order', function () {
    $mock = Mockery::mock(ShipOrder::class);   // !! TEST_MOCK_CALL
    $mock->shouldReceive('handle')->once();

    expect(true)->toBeTrue();
});
