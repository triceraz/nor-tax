# LinkedIn-post: DIA-TAX v0.1

Format: Norwegian (Bokmål). No em dashes. Tone: direct, technical-but-readable,
ends with concrete CTA. Lead with the surprising fact. Embed the skyline figure
as the main visual.

---

## Variant 1 — short hook + surprising finding

**Hovedversjon:**

Samme spørsmål. Samme modell. Norsk koster 30 % mer enn engelsk.

Vi målte tokenization-skatten på fire språkmodeller med 200 parallelle setninger fra FLORES-200. Resultatet:

- GPT-4o: 348 sider engelsk i 128K-vinduet, 256 sider norsk. Minus 27 %.
- GPT-4 (legacy): 347 sider engelsk, 222 sider norsk. Minus 36 %.
- Qwen 2.5 1.5B: 337 sider engelsk, 218 sider norsk. Minus 35 %.

Hvorfor? BPE-tokenisering belønner sekvenser som repeteres ofte i treningsdataen. Engelsk dominerer korpuset, så engelske ord komprimeres til få tokens. Norske ord fragmenteres.

Men her er det interessante: tren tokenisereren på norsk, og skatten reverseres.

NorMistral 7B (trent på norsk korpus) får 295 sider norsk i samme 128K-vindu, mot 249 sider engelsk. Pluss 18 % i norsk favør.

[SKYLINE-FIGUR]

Det betyr for norske SMB-er som bruker engelsk-trente modeller via API:

1. 1.3 til 1.6 ganger høyere token-kostnad per spørring
2. Kortere effektivt context-vindu (kan ikke prosessere like lange kontrakter, regnskap, eller juridiske tekster på én gang)
3. Modellen lærte engelsk bedre under pre-training — bedre svar på samme datavolum

Det er ikke et argument mot å bruke API-modeller. Det er et argument for å vite hva det koster.

Råddata, kode og full reproducerbarhet på github.com/triceraz/dia-tax. v0.1 av et lite prosjekt jeg gjør under Tenki Labs.

#norskKI #lokalKI #NLP #tokenisering

---

## Variant 2 — pure hook, billboard style

Samme 128K context-vindu.
348 sider engelsk innhold.
256 sider norsk.
295 sider norsk på norsk-trent modell.

Tokenisering er ikke nøytral infrastruktur. Den er en skatt på språkets representasjon i treningsdataen.

DIA-TAX v0.1, Tenki Labs.
Kode + data: github.com/triceraz/dia-tax

[SKYLINE-FIGUR]

---

## Variant 3 — story-driven open

For 18 måneder siden begynte jeg å lure: hvorfor merker norske kunder at GPT-er "føles tregere" og "dyrere" enn engelske team beskriver?

Svaret ligger i tokenisering. Måling viser at norsk koster 1.3 til 1.6 ganger så mye som engelsk på de samme modellene, for samme innhold.

[SKYLINE-FIGUR]

Detaljer i kommentarfeltet eller på github.com/triceraz/dia-tax.

---

## Notater for visualen

Bruk `paper/figures/skyline.png` som hovedvisual. Den er allerede LinkedIn-format
(16:9 horisontalt, høy kontrast, leselig på mobil). Sett som første vedlegg.

Hvis post-en blir lang: del i to slides — `tokenization_tax.png` for grunnregnskapet,
`skyline.png` for punchline.

## Hashtags (Norwegian LinkedIn)

#norskKI #lokalKI #NLP #språkteknologi #KIforSMB #tokenisering #ML

## Mention-strategi

- Tag NorMistral-teamet (NORA-LLM / Universitetet i Oslo) hvis de er på LinkedIn
- Tag Tenki Labs offisiell side
- Ikke tag konkurrenter eller spesifikke kundeselskap
