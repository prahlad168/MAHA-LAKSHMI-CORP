create extension if not exists pgcrypto;

create table if not exists public.businesses (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  category text not null,
  location text not null,
  website_url text,
  score integer not null check (score between 0 and 100),
  clarity_score integer not null check (clarity_score between 0 and 100),
  trust_score integer not null check (trust_score between 0 and 100),
  contact_score integer not null check (contact_score between 0 and 100),
  actions jsonb not null default '[]'::jsonb,
  source text not null default 'user_input',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.referrals (
  id uuid primary key default gen_random_uuid(),
  referrer_business_id uuid not null references public.businesses(id) on delete cascade,
  referred_business_id uuid references public.businesses(id) on delete set null,
  referral_code text not null,
  status text not null default 'visited' check (status in ('visited','activated','qualified')),
  created_at timestamptz not null default now(),
  activated_at timestamptz
);

create index if not exists idx_businesses_slug on public.businesses(slug);
create index if not exists idx_referrals_code on public.referrals(referral_code);
create index if not exists idx_referrals_referrer on public.referrals(referrer_business_id);

alter table public.businesses enable row level security;
alter table public.referrals enable row level security;

-- Public Passport pages may be read. Writes will be moved behind a server-side API/Edge Function.
create policy "public can read passports"
  on public.businesses for select
  using (true);

create policy "public can read referral status"
  on public.referrals for select
  using (true);

-- No public insert/update/delete policies are intentionally created here.
-- Production writes must be performed by a trusted API/Edge Function after validation/rate limiting.
