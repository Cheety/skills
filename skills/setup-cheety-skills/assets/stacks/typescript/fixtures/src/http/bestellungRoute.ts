import { PrismaClient } from '@prisma/client';   // !! BOUNDARY_ROUTE_DB
import type { Request, Response } from 'express';

const prisma = new PrismaClient();

export async function index(req: Request, res: Response): Promise<void> {
  const limit = process.env.BESTELL_LIMIT;   // !! ENV_OUTSIDE_CONFIG

  // @ts-ignore   !! HYGIENE_TS_IGNORE
  const rows = await prisma.order.findMany({ take: limit });

  res.json(rows);
}
