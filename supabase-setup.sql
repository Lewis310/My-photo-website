-- Run this once in Supabase: SQL Editor > New query > paste > Run.
-- STEP 1: replace YOUR_EMAIL@example.com (3 places below use it) with the email of the owner account you will create.

-- Content table (one row holding all site content)
create table if not exists public.portfolio (
  id int primary key,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.portfolio enable row level security;

create policy "Anyone can read portfolio" on public.portfolio
  for select using (true);

create policy "Owner can insert portfolio" on public.portfolio
  for insert to authenticated
  with check ((auth.jwt() ->> 'email') = 'YOUR_EMAIL@example.com');

create policy "Owner can update portfolio" on public.portfolio
  for update to authenticated
  using ((auth.jwt() ->> 'email') = 'lewis.eom31@gmail.com')
  with check ((auth.jwt() ->> 'email') = 'lewis.eom31@gmail.com');

-- Photo storage (public bucket so visitors can see images)
insert into storage.buckets (id, name, public)
values ('photos', 'photos', true)
on conflict (id) do nothing;

create policy "Owner can upload photos" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'photos' and (auth.jwt() ->> 'email') = 'lewis.eom31@gmail.com');

create policy "Owner can update photos" on storage.objects
  for update to authenticated
  using (bucket_id = 'photos' and (auth.jwt() ->> 'email') = 'lewis.eom31@gmail.com');

create policy "Owner can delete photos" on storage.objects
  for delete to authenticated
  using (bucket_id = 'photos' and (auth.jwt() ->> 'email') = 'lewis.eom31@gmail.com');
