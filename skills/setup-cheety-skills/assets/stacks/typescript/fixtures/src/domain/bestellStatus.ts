import { PrismaClient } from '@prisma/client';   // !! BOUNDARY_DOMAIN_PURE

type Status = 'new' | 'sent' | 'paid';

export function label(s: Status): string {
  switch (s) {
    case 'new': return 'Neu';
    default: return 'Unbekannt';   // !! STATE_SWITCH_DEFAULT
  }
}

export function load(p: PrismaClient) {
  return p.order.findMany().then((r) => r.length);   // !! ERROR_FLOATING_PROMISE
}
