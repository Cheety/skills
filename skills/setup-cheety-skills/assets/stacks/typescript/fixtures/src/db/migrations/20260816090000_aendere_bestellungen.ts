import type { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.alterTable('orders', (t) => {
    t.renameColumn('amount', 'betrag_cents');   // !! MIGRATION_RENAME
    t.dropColumn('old_status');                 // !! MIGRATION_DROP
    t.string('shipping_method').notNullable();       // !! MIGRATION_NOT_NULL
    t.timestamp('sent_at');                // !! MIGRATION_TIMEZONE
  });

  await knex('orders').update({ shipping_method: 'standard' });   // !! MIGRATION_BULK_UPDATE
}
// !! MIGRATION_DOWN
