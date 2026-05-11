# Norsk koster mer

## En måling av tokenization-skatten på Bokmål, Nynorsk og engelsk

Hvis du har brukt ChatGPT eller en annen KI-modell på norsk og engelsk, har du kanskje merket at den norske versjonen "føles tregere" eller "rusler treigere på lengre dokumenter". Det er ikke fantasi. Det er målbart, og det handler om noe som kalles tokenization.

Vi målte det.

## Hvordan KI ser teksten din

En språkmodell leser ikke ord. Den leser tokens.

Et token er en biter av tekst som modellen får et eget oppslag på i sin interne ordbok. For engelsk er typisk *the*, *and*, *is* hver sitt enkelt-token. For sjeldnere ord brytes de opp i flere tokens (*tokenization* kan bli *token* + *ization*).

Tokenizer-en, som er det som gjør om bokstaver til tokens, lager ordboken sin ved å se på treningsdataen. Bytes som gjentar seg ofte får sitt eget korte token. Bytes som forekommer sjelden blir fragmentert.

Engelsk dominerer all treningsdata for de store kommersielle modellene (GPT-4, Claude, Gemini). Det betyr at engelske ord blir komprimert effektivt. Norske ord blir det ikke.

## Måling: 200 parallelle setninger

For å måle dette tok vi 200 parallelle setninger fra FLORES-200, et standardisert datasett for maskinoversettelse vedlikeholdt av Meta AI. Hver setning finnes i identisk meningsinnhold på engelsk og norsk Bokmål. I tillegg brukte vi 200 Bokmål-til-Nynorsk-par fra Wikipedia oversatt med Apertium (samme innhold, bare dialektendringer).

Vi kjørte alle setningene gjennom fire tokenizere:

- GPT-4o (`o200k_base`, OpenAIs nyeste tokenizer)
- GPT-4 (`cl100k_base`, OpenAIs eldre tokenizer)
- Qwen 2.5 1.5B (kinesisk-fokusert open source, mye brukt i forskning)
- NorMistral 7B (en åpen modell fra NORA-LLM-prosjektet ved Universitetet i Oslo, trent på norsk korpus)

For hver setning telte vi hvor mange tokens den brukte i hver tokenizer.

## Resultatet: 27 til 36 prosent skatt

På de tre engelsk-trente modellene betaler norsk mellom 27 og 36 prosent mer enn engelsk for å si nøyaktig det samme.

Konkret: ta GPT-4os 128K context-vindu, det maksimale antallet tokens modellen kan lese om gangen. Det høres mye ut. Men i sider med tekst (cirka 300 ord per side) holder vinduet:

- 348 sider på engelsk
- 256 sider på norsk Bokmål
- 210 sider på norsk Nynorsk

På GPT-4 (den eldre tokenizeren som fortsatt brukes av mange systemer):

- 347 sider på engelsk  
- 222 sider på Bokmål
- 184 sider på Nynorsk

For en norsk advokat som vil prosessere en kontraktsamling, eller en regnskapsfører som vil analysere et stort årsregnskap, betyr det at en stor del av dokumentet rett og slett ikke får plass. Modellen må kuttes ned eller deles opp.

[FIGURE: skyline.png]

## Bokmål og Nynorsk pays the same

Vi forventet at Nynorsk ville være verre tokenisert enn Bokmål. Det er det færre treningsdata for Nynorsk, og strukturen er ulik nok til at vi tenkte BPE ville fragmentere det mer.

Men nei. Parret BM/NN-måling viser nesten ingen forskjell mellom Bokmål og Nynorsk. På GPT-4o er ratio NN/BM = 1.00x. På Qwen 2.5 er den 1.02x. Skatten ligger i å være norsk, ikke i hvilken målform du skriver.

Det er litt overraskende, men det gir mening når du ser på hva som skjer på token-nivå. Forskjellene mellom *en* (BM) og *ein* (NN), eller mellom *ikke* (BM) og *ikkje* (NN), gir små forskjeller i absoluttall, men siden begge er fragmenterte uansett, blir den relative forskjellen liten.

## Det interessante: norsk-trent tokenizer reverserer alt

Her kommer det som overrasket oss mest. Vi inkluderte NorMistral 7B i målingen som en kontrast, en modell trent eksplisitt på norsk korpus. Tokenizeren er bygget med norsk som førsteprioritet.

Resultatet:

- 249 sider engelsk i 128K-vinduet
- 295 sider Bokmål i 128K-vinduet  
- 200 sider Nynorsk i 128K-vinduet

Norsk får mer plass enn engelsk. 18 prosent mer for Bokmål spesifikt.

Tokenisering er ikke en lov av naturen. Den er et resultat av hva tokenizeren ble trent på. Tren den på norsk, og norsk blir billig.

[FIGURE: tokenization_tax.png]

## Hva det betyr i praksis

Hvis du bruker en kommersiell engelsk-dominant modell (GPT-4, Claude, Gemini) til å prosessere norske dokumenter, betaler du:

1. Mellom 1.3 og 1.6 ganger mer per spørring (siden API-er priser per token, ikke per ord)
2. Mistet kontekstkapasitet for lange dokumenter (du får inn mindre av en kontrakt eller en rapport per kall)
3. Mulig dårligere kvalitet på modellsvar, siden modellen så norsk i fragmentert form under trening

Hvis bruksmønsteret ditt har lav norsk-andel, eller du primært stiller korte spørsmål, betyr det lite. Men hvis du er en advokat, regnskapsfører, eller rådgiver som ofte vil prosessere lange norske tekster, blir det dyrt fort.

Et alternativ er en norsk-trent modell, enten en åpen kandidat som NorMistral, eller en lokalt finetuned variant. Det går glipp av det kommersielle øko-systemet rundt GPT-4 og Claude, men du får en infrastruktur som faktisk er bygget for språket du bruker.

## Begrensninger og forbehold

Dette er ikke et komplett bilde. Noen ting vi ikke har målt enda:

- **Modellkvalitet**. Tokenisering er kostnadssiden. Hvor godt modellen faktisk svarer på norsk er en separat måling.
- **Claude**. Anthropic publiserer ikke sin tokenizer offentlig, så vi har ikke målt den direkte (men estimater fra deres SDK indikerer lignende mønster som GPT-4).
- **Gemma**. Tenki kjører Gemma 3 4B i produksjon for Hugin-chat-tjenesten, men vi måtte hoppe over den i denne v0.1-en på grunn av HF auth-krav. Kommer i v0.2.
- **Lengre dokumenter**. 200 FLORES-setninger er rundt 20 ord hver. Vi gjør antakelser om hvordan dette skalerer til hele bedriftsdokumenter. Sannsynlig konservativt, men ikke bekreftet.

## Hvor finner du dataene

All rådata, koden og figurene ligger åpent på [github.com/triceraz/dia-tax](https://github.com/triceraz/dia-tax). Klon, kjør, mål på dine egne setninger.

Dette er v0.1 av et lite forskningsprosjekt vi gjør under Tenki Labs. To søsterpapirer er [DIA-LOC](https://github.com/triceraz/dia-loc) (hvor i Qwen-modellen norsk dialekt-signalet bor) og [DIA-INT](https://github.com/triceraz/dia-int) (hvor LoRA-intervensjon bør skje for å påvirke dialekt-output).

Når vi bygger lokal KI for norske SMB-er hos Tenki, er det ikke bare en ideologisk preferanse for at data skal bli i Norge. Det er også et regnestykke. Modellene som er trent på norsk koster mindre per spørring, gir mer kontekst, og forstår språket bedre.

Skatten på å være norsk kan unngås. Den må bare bygges bort.
