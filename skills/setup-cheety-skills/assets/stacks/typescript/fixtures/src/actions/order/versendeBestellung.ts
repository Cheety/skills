import { PrismaClient } from '@prisma/client';   // !! BOUNDARY_ACTION_DB
import type { Request } from 'express';          // !! BOUNDARY_ACTION_HTTP

const prisma = new PrismaClient();

export default async function versenden(req: Request): Promise<any> {   // !! STRICT_TYPES
  const id = req.body.id as any;

  await prisma.$transaction(async (tx) => {
    await tx.order.update({ where: { id }, data: { status: 'sent' } });
    await enqueue('versendeBestellMail', id);   // !! TRANSACTION_SIDE_EFFECT
  });

  try {
    await pruefe(id);
  } catch (e) {}   // !! ERROR_SWALLOWED

  console.log('sent', id);   // !! DEBUG_OUTPUT
  return { ok: true };
}
// !! FORM_ACTION_EXPORT
// !! FORM_ACTION_DEFAULT_EXPORT

async function enqueue(_n: string, _i: number): Promise<void> {}
async function pruefe(_i: number): Promise<void> {}
