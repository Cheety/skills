import type { RechnungRepository, Mailer } from '../types/ports';

export async function handle(
  repo: RechnungRepository,
  mailer: Mailer,
  rechnungId: number,
): Promise<void> {
  const invoice = await repo.find(rechnungId);

  if (invoice.dunningSentAt !== null) {
    return;
  }

  await mailer.send(invoice.email, 'Zahlungserinnerung');
  await repo.update(rechnungId, { dunningSentAt: new Date() });
}
