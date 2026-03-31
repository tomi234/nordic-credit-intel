# 📡 Nordic Credit Intel — Gratis versjon

Systemet skanner Newsweb og GlobeNewswire hvert 15. minutt.
Når det finner noe relevant, sender det deg en epost med nyheten.
Du limer den inn i Claude.ai (gratis) for å få full credit-analyse.

**Ingen API-nøkler. Ingen kostnad. Null kroner.**

---

## Du trenger bare to ting

1. **GitHub-konto** → github.com (gratis)
2. **Railway-konto** → railway.app (gratis)
3. **Gmail App-passord** (tar 3 minutter)

---

## STEG 1 — Last opp filene til GitHub (5 min)

1. Gå til **github.com** → logg inn eller lag konto
2. Klikk **"New"** (grønn knapp øverst til venstre)
3. Navn: `nordic-credit-intel` → velg **Private** → klikk **"Create repository"**
4. Klikk **"uploading an existing file"**
5. Dra alle filene fra denne mappen inn i nettleseren
6. Klikk **"Commit changes"**

---

## STEG 2 — Lag Gmail App-passord (3 min)

Du må lage et eget passord for appen — du bruker ikke ditt vanlige Gmail-passord.

1. Gå til **myaccount.google.com**
2. Klikk **"Sikkerhet"** i venstremenyen
3. Klikk **"2-trinnsbekreftelse"** → aktiver hvis ikke allerede på
4. Gå tilbake → søk etter **"App-passord"** → klikk det
5. Velg **"E-post"** og **"Annen enhet"** → skriv "Credit Intel"
6. Klikk **"Generer"** → kopier de 16 tegnene (f.eks. `abcdefghijklmnop`)
   - **Fjern mellomrommene når du bruker dem**

---

## STEG 3 — Deploy på Railway (7 min)

1. Gå til **railway.app**
2. Klikk **"Login with GitHub"**
3. Klikk **"New Project"** → **"Deploy from GitHub repo"**
4. Velg `nordic-credit-intel`
5. Klikk på prosjektet → klikk **"Variables"** i toppmenyen
6. Legg inn disse (klikk "New Variable" for hver):

| Navn | Verdi |
|---|---|
| `GMAIL_USER` | din@gmail.com |
| `GMAIL_APP_PASSWORD` | de16tegnene (uten mellomrom) |
| `RECIPIENT_EMAIL` | din@gmail.com |
| `SCAN_INTERVAL_SEC` | 900 |

7. Railway deployer automatisk. Ferdig.

---

## STEG 4 — Sjekk at det virker

1. Klikk **"Deployments"** i Railway
2. Klikk siste deployment → **"View Logs"**
3. Du skal se:
```
🚀 Nordic Credit Intel (gratis versjon) startet
📋 Følger 120 selskaper | 45 triggere
📬 Sender til: din@gmail.com
⏱️  Skanner hvert 15. minutt
```

Ser du dette — kjører systemet. Du trenger aldri røre det igjen.

---

## Slik bruker du det i praksis

1. Du får epost med nyhet og ingress
2. I bunnen av eposten er det en ferdig tekstboks
3. Kopier teksten → lim inn på **claude.ai** (gratis)
4. Claude gir deg full credit flash på sekunder

---

## Feilsøking

**Får ikke epost?**
→ Sjekk spam-mappen
→ Sjekk at App-passordet ikke har mellomrom
→ Klikk "View Logs" i Railway og se etter feilmeldinger

**"Authentication failed"?**
→ Generer nytt Gmail App-passord

**Ingen nyheter på lenge?**
→ Normalt — systemet sender kun ved relevante treff
→ Sjekk logs — skal se "💤 Neste skanning om 15 min..." regelmessig

---

*Nordic Credit Intel · Nordea Markets Securities Advisory · Oslo*
*Ikke investeringsrådgivning. For profesjonelle investorer.*
