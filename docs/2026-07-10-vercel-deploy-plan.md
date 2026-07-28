# Deploy uz Vercel — vercel.json commit + push

## Konteksts

Lietotājs grib deploy'ot cube-solving projektu uz Vercel no GitHub repo
(https://github.com/Kanjepe/cube-solving). Projekts ir statisks HTML — Vercel
build nav vajadzīgs, bet saknes URL `/` pēc noklusējuma meklē `index.html`,
kura projektā nav (galvenais fails ir `cube-solving.html`).

`vercel.json` jau ir izveidots un stage'ots (iepriekšējā solī, pirms plan mode):

```json
{
  "rewrites": [
    { "source": "/", "destination": "/cube-solving.html" }
  ]
}
```

Lietotājs jau apstiprināja commit + push (AskUserQuestion atbilde: "Jā, commit + push").

## Soļi

1. Commit stage'oto `vercel.json` ar ziņojumu:
   `Add Vercel config to serve cube-solving.html at root`
2. Push uz `origin/main` (github.com/Kanjepe/cube-solving)

## Verifikācija

- `git log --oneline -2` — commits redzams
- Push izvade rāda `main -> main`
- Pēc tam lietotājs Vercel dashboardā importē GitHub repo (Add New → Project →
  izvēlas Kanjepe/cube-solving, Framework Preset: "Other", bez build komandas) —
  Vercel automātiski deploy'os un `/` rādīs cube-solving.html
