import type { Mailer } from '../types/ports';

export async function handle(mailer: Mailer, bestellId: number): Promise<void> {
  // no safeguard against duplicate delivery   !! IDEMPOTENCY_HANDLER
  await mailer.send(`customer-${bestellId}@example.com`, 'Versendet');
}
