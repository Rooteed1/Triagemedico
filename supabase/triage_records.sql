-- Run this script in the Supabase SQL Editor for the project.
create table if not exists public.triage_records (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null default auth.uid()
        references auth.users (id) on delete cascade,
    patient_name text not null,
    created_at timestamptz not null default now(),
    temperature numeric not null check (temperature between 30 and 45),
    heart_rate integer not null check (heart_rate between 30 and 220),
    pain integer not null check (pain between 0 and 10),
    urgency_score numeric not null check (urgency_score between 0 and 100),
    priority_label text not null,
    summary text
);

-- Add the new ownership/timestamp columns when upgrading an older table.
-- Existing rows without an owner remain inaccessible under RLS; assign them
-- manually only after verifying which authenticated account owns each record.
alter table public.triage_records
    add column if not exists user_id uuid default auth.uid()
        references auth.users (id) on delete cascade;
alter table public.triage_records
    add column if not exists created_at timestamptz not null default now();
alter table public.triage_records
    add column if not exists patient_name text not null default 'Sin identificar';
alter table public.triage_records
    add column if not exists temperature numeric;
alter table public.triage_records
    add column if not exists heart_rate integer;
alter table public.triage_records
    add column if not exists pain integer;
alter table public.triage_records
    add column if not exists urgency_score numeric;
alter table public.triage_records
    add column if not exists priority_label text;
alter table public.triage_records
    add column if not exists summary text;
alter table public.triage_records
    alter column user_id set default auth.uid();
alter table public.triage_records
    alter column created_at set default now();

-- Older versions wrote a separate required `timestamp` column. Keep its old
-- values, but allow new records to use the server-managed `created_at` column.
do $$
begin
    if exists (
        select 1
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'triage_records'
          and column_name = 'timestamp'
    ) then
        alter table public.triage_records alter column "timestamp" drop not null;
    end if;
end;
$$;

create index if not exists triage_records_user_created_at_idx
    on public.triage_records (user_id, created_at desc);

alter table public.triage_records enable row level security;
revoke all on public.triage_records from anon;
grant select, insert on public.triage_records to authenticated;

drop policy if exists "Users read their own triage records"
    on public.triage_records;
create policy "Users read their own triage records"
    on public.triage_records
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists "Users insert their own triage records"
    on public.triage_records;
create policy "Users insert their own triage records"
    on public.triage_records
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);
