# Sito web CFM – Centro Assistenza Caldaie Vaillant Verona

Sito statico per **CFM S.n.c. di Caspani M., Faustini G., Mirandola R.** (San Giovanni Lupatoto, VR).
Ottimizzato per la ricerca locale su Google/Bing e per essere letto e citato dagli assistenti AI
(ChatGPT, Claude, Perplexity, Gemini, Copilot).

## Struttura

```
build.py          generatore (solo Python standard, nessuna dipendenza)
src/layout.html   layout comune (head SEO, header, footer, barra contatti mobile)
src/pages/*.html  contenuti delle pagine, con metadati in testa (<!--meta {...} -->)
src/assets/       CSS, JS, logo, favicon, immagine social
src/llms.txt      scheda sintetica per gli LLM
src/robots.txt    accesso esplicito ai crawler AI
public/           sito generato: è la cartella da pubblicare
```

```bash
python3 build.py                                  # rigenera public/
cd public && python3 -m http.server 8000          # anteprima su http://localhost:8000
```

Tutti i dati aziendali (telefono, indirizzo, orari, dominio, comuni serviti) stanno nel
dizionario `SITE` in `build.py`: si cambiano in un solo punto e si aggiornano in pagine,
dati strutturati, `llms.txt` e sitemap.

## Scelte di design (dall'analisi dei siti del settore)

I siti di assistenza caldaie che convertono meglio hanno elementi in comune; i siti dei
centri assistenza locali in Italia spesso no (template datati, telefono nascosto, nessun contenuto utile).
Il sito adotta quello che funziona:

| Elemento | Perché |
|---|---|
| Telefono sempre visibile (header desktop + barra fissa "Chiama ora" su mobile) | La maggior parte delle ricerche "caldaia rotta" avviene da smartphone e finisce in una chiamata |
| Due percorsi separati: **Chiama** (urgenza) e **Richiedi intervento** (programmato) | Chi ha la caldaia in blocco vuole telefonare; chi prenota la manutenzione preferisce un modulo |
| Hero con promessa chiara + i 3 punti di fiducia (40 anni, specialisti Vaillant, zona) | Si capisce in 3 secondi chi siete, cosa fate e dove |
| Contenuti utili (tabella codici errore Vaillant, obblighi di manutenzione, FAQ) | Portano traffico organico e sono la fonte preferita dagli LLM per le risposte |
| Palette verde petrolio + arancio fiamma | Richiamo al mondo Vaillant senza copiarne l'identità; l'arancio è usato solo per le call to action |
| Nessun framework, nessun font esterno, ~15 KB di CSS | Caricamento quasi istantaneo, ottimi Core Web Vitals |

## SEO locale e visibilità sugli LLM (GEO)

Già implementato:

- **Dati strutturati JSON-LD** su ogni pagina: `HVACBusiness`/`LocalBusiness` (indirizzo, geo,
  orari, zone servite, specializzazione), `WebSite`, `BreadcrumbList`, `Service` sulle pagine
  servizio e `FAQPage` generato automaticamente dalle FAQ.
- **`/llms.txt`** (standard llmstxt.org) e **`/llms-full.txt`** con tutto il testo del sito in
  Markdown: gli assistenti AI ottengono i fatti senza dover interpretare l'HTML.
- **`robots.txt`** che autorizza esplicitamente GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot,
  Google-Extended, Applebot-Extended, Bingbot e altri.
- Blocchi **"In breve"** con i fatti chiave (chi, dove, cosa, contatti) in apertura delle pagine:
  è il formato che gli LLM estraggono e citano più facilmente.
- Contenuto interamente in HTML statico: leggibile anche dai crawler che non eseguono JavaScript.
- URL parlanti con keyword locali, title/description unici, canonical, Open Graph, sitemap.xml.

## ⚠️ Da completare prima della messa online

Dati che non è stato possibile verificare dalle fonti pubbliche (vanno confermati dai titolari):

- [ ] **Dominio** definitivo (`SITE["url"]` in `build.py`, ora è un segnaposto)
- [ ] **Partita IVA** (`SITE["vat"]`, obbligatoria nel footer)
- [ ] **Orari**: le directory online riportano dati discordanti (07:30–18:30 vs 08:30–20:30)
- [ ] **Email**: `cfmsnc1@virgilio.it` è quella presente nelle directory; meglio un indirizzo sul dominio
- [ ] **Coordinate GPS** della sede (`lat`/`lng`, ora approssimate)
- [ ] **Elenco comuni serviti** e affermazioni sui servizi (garanzia, ricambi in magazzino,
      promemoria annuale, caldaie di altre marche, smaltimento)
- [ ] Se CFM è **centro assistenza autorizzato Vaillant**, dirlo esplicitamente: è il segnale più forte
- [ ] Link della scheda **Google Business Profile** (`gbp_url`)
- [ ] Testo **privacy** da far verificare
- [ ] Foto reali (sede, furgoni, tecnici al lavoro): aumentano fiducia e conversioni

## Dopo la pubblicazione (fondamentale per Google e per gli LLM)

1. **Google Business Profile**: verificare che nome, indirizzo e telefono siano identici al sito;
   categoria principale "Servizio di riparazione caldaie", inserire il link al sito, foto, orari.
   Chiedere recensioni ai clienti soddisfatti: per le ricerche locali e per gli LLM sono decisive.
2. **Bing Places** e **Bing Webmaster Tools** (inviare la sitemap): ChatGPT e Copilot usano l'indice Bing.
3. **Google Search Console**: verificare il dominio e inviare `sitemap.xml`.
4. **Apple Business Connect**: per Apple Maps e Siri.
5. **Uniformare le directory** (PagineGialle, Virgilio, MisterImprese, ReteImprese…): molte riportano
   "Fautini" invece di "Faustini" e orari diversi. I dati incoerenti riducono la fiducia di Google e degli LLM.
6. Chiedere l'inserimento/aggiornamento nel **localizzatore centri assistenza Vaillant** con link al sito.

## Pubblicazione

Funziona su qualsiasi hosting statico. Consigliati (gratuiti, HTTPS incluso):
**Cloudflare Pages** o **Netlify** → cartella di pubblicazione `public`, comando di build
`python3 build.py`. Il file `_headers` imposta cache e header di sicurezza.
