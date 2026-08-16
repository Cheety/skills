import type { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.alterTable('invoices', (t) => {
    t.timestamptz('dunned_at').nullable();
    t.index(['status', 'sent_at']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.alterTable('invoices', (t) => {
    t.dropIndex(['status', 'sent_at']);
    t.dropColumn('dunned_at');
  });
}
