-- Run in Supabase: SQL Editor > New query > paste > Run. Safe to run more than once.
-- No email needs to be edited. Only signed-in users can write, so keep
-- Authentication > Sign In / Providers > "Allow new users to sign up" turned OFF.

-- 1. Content table
create table if not exists public.portfolio (
  id int primary key,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.portfolio enable row level security;

drop policy if exists "Anyone can read portfolio" on public.portfolio;
drop policy if exists "Owner can insert portfolio" on public.portfolio;
drop policy if exists "Owner can update portfolio" on public.portfolio;
drop policy if exists "Signed-in can insert portfolio" on public.portfolio;
drop policy if exists "Signed-in can update portfolio" on public.portfolio;

create policy "Anyone can read portfolio" on public.portfolio
  for select using (true);
create policy "Signed-in can insert portfolio" on public.portfolio
  for insert to authenticated with check (true);
create policy "Signed-in can update portfolio" on public.portfolio
  for update to authenticated using (true) with check (true);

-- 2. Photo storage bucket (public so visitors can see images)
insert into storage.buckets (id, name, public)
values ('photos', 'photos', true)
on conflict (id) do update set public = true;

drop policy if exists "Owner can upload photos" on storage.objects;
drop policy if exists "Owner can update photos" on storage.objects;
drop policy if exists "Owner can delete photos" on storage.objects;
drop policy if exists "Signed-in can upload photos" on storage.objects;
drop policy if exists "Signed-in can update photos" on storage.objects;
drop policy if exists "Signed-in can delete photos" on storage.objects;

create policy "Signed-in can upload photos" on storage.objects
  for insert to authenticated with check (bucket_id = 'photos');
create policy "Signed-in can update photos" on storage.objects
  for update to authenticated using (bucket_id = 'photos') with check (bucket_id = 'photos');
create policy "Signed-in can delete photos" on storage.objects
  for delete to authenticated using (bucket_id = 'photos');
