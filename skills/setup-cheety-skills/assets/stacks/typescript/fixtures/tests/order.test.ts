import { vi, it, expect } from 'vitest';

it('sent eine Order', async () => {
  const mailer = { send: vi.fn() };
  await handle(mailer as never, 1);
  expect(mailer.send).toHaveBeenCalledTimes(1);   // !! TEST_MOCK_CALL
});

async function handle(_m: never, _i: number): Promise<void> {}
