import { canTransitionTo } from '../../domain/stateTransition';
import type { RechnungRepository } from '../../types/ports';

export async function execute(
  repo: RechnungRepository,
  enqueue: (name: string, id: number) => Promise<void>,
  rechnungId: number,
): Promise<void> {
  const gewechselt = await repo.transaction(async (tx) => {
    const invoice = await tx.findForUpdate(rechnungId);
    if (!canTransitionTo(invoice.status, 'dunning')) {
      throw new Error(`Wechsel von ${invoice.status} nach dunning ist nicht erlaubt.`);
    }
    await tx.update(rechnungId, { status: 'dunning', dunnedAt: new Date() });
    return true;
  });

  if (gewechselt) {
    await enqueue('versendeMahnungsMail', rechnungId);
  }
}
