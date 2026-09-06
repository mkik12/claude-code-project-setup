# Zadání konfigurace

## Cíl

Vytvořit konfiguraci `.claude` pro Claude Code, která bude uložená na GitHubu.
Kdokoliv z firmy si ji může zkopírovat do svého projektu, nebo nechat být. Do
budoucna se počítá s tím, že se stane součástí komponenty na CodeNOW.

GitHub Copilot se v této konfiguraci neřeší. Copilot si svou konfiguraci
vybuduje samostatně.

## Pro koho to je

Pro **technického vývojáře**. Umí programovat a potřebuje jen znalosti navíc:
CodeNOW, LDWH1, práci s dokumenty a bankovní pojmy.

Z toho plyne, co konfigurace nemá obsahovat: úvodní rozhovor o projektu, vodicí
příkazy ani ochranné zábradlí. Vývojář sedí u toho a čte, co se děje.

## Požadavky

1. **Komunikovat jazykem uživatele.** Mluvit tím jazykem, který uživatel použije.
   Všechny soubory psát anglicky.
2. **Psát podle ASD-STE100** (Simplified Technical English) a bez dlouhých
   pomlček.
3. **Vysvětlovat cizí a byznysové pojmy** jako kontokorent nebo bonita. Jednou za
   konverzaci, jednou větou. Nevysvětlovat slovo, které použil sám uživatel.
4. **Programovat webové aplikace ve Flasku.**
5. **Spolupracovat s platformou CodeNOW:** rozumět jejím specifikům, umět
   vytvořit vlastní databázi a připojit se k datovému skladu LDWH1.
6. **Pracovat se soubory MS Office** a s PDF.
7. **Pamatovat si, o čem projekt je a co se v něm rozhodlo.**
8. **Zkontrolovat práci před commitem.**

## Struktura

Repozitář konfigurace:

```
ai-configuration/
  README.md          jak konfiguraci zkopírovat do projektu
  CHANGELOG.md       co se změnilo mezi verzemi
  task.md            tento soubor
  memory.md          prázdná šablona, kopíruje se do projektu
  .claude/
    CLAUDE.md        jádro konfigurace
    settings.json    oprávnění
    rules/           writing.md  code-style.md  flask.md  codenow.md
    agents/          codenow-reviewer.md
    skills/          docx  pptx  xlsx  pdf  ldwh1  app-database
    scripts/         ste-lint.py  check_tools.py
```

Do projektu se kopíruje `.claude/` **a** `memory.md`. Obojí, ne jen složka.

### Co je v CLAUDE.md

`CLAUDE.md` je jádro konfigurace. Neobsahuje toto zadání. Obsahuje:

- číslo verze konfigurace
- seznam toho, co má AI používat, a jak to má používat: pravidla, skilly, skripty
- seznam agentů a jejich popis
- tvar odpovědi uživateli
- pravidlo o jazyce a o vysvětlování pojmů
- import `memory.md`

### Pravidla, skilly a skripty

Rozdíl je v tom, kdy se to načte:

| Vrstva | Kdy se načte | Co tam patří |
| :--- | :--- | :--- |
| `rules/` | vždy, v každém sezení | co platí pro většinu práce |
| `skills/` | až když úloha odpovídá popisu | jeden druh úlohy |
| `scripts/` | nikdy, jen se spouští | nástroj, který si AI zavolá sama |

Skripty spouští AI, ne uživatel. `ste-lint.py` zkontroluje styl napsaného textu,
`check_tools.py` vypíše, co na stroji je a co chybí.

Skilly obsahují **jen znalost**, žádné skripty ani schémata. Ze vzorových skillů
se bere to podstatné: ověřené postupy a pasti, do kterých se dá spadnout.

### Agent

Jeden: **`codenow-reviewer`**. Spustí se před commitem, dostane diff a vrátí
seznam nálezů. Kontroluje:

- kontrakt CodeNOW: `/health`, port, CI, tracing hlavičky
- pravidla stylu z `code-style.md`
- že v diffu neskončilo heslo, token ani connection string
- že aplikace nezapisuje do svého adresáře

Čte jen. Nastavení `tools` mu zápis neumožní, takže to není slib v textu.

Planner ani coder v konfiguraci nejsou. U technického vývojáře řeší problém,
který nemá: plán chce vidět celý a u implementace sedí. Vrátí se, až bude
konkrétní důvod, například že dlouhý refaktoring zaplevelí kontext.

## Paměť projektu

Jeden soubor `memory.md` v kořeni projektu, mimo `.claude/`. Důvod je technický:
`.claude/` je chráněná cesta, zápis do ní se pokaždé ptá na potvrzení a nejde
povolit dopředu. Cokoliv AI píše za běhu, musí ležet jinde.

Dvě sekce:

- **About the project** — jeden až dva odstavce o tom, co aplikace dělá, kdo ji
  používá a jaké externí systémy potřebuje. Mění se zřídka.
- **Decisions** — deník rozhodnutí. Nejnovější nahoře.

**Deník není changelog.** Co se změnilo, už umí git. Do deníku patří to, co git
neumí: proč jsme se rozhodli takhle, co jsme zavrhli, co je rozdělané a na jakou
past někdo narazil. Strop 100 řádků, starší záznam se stlačí na jednu řádku s
datem.

Soubor patří do gitu, je to sdílená paměť týmu. Píše se anglicky.

**Jak vznikne.** Prázdná šablona se kopíruje spolu s konfigurací, takže import v
`CLAUDE.md` funguje od prvního sezení. Šablona si nese vlastní návod. Obsah do ní
píše vždy AI, nikdy uživatel ručně.

**Kdy se ukládá.** Dvěma způsoby, oba platí zároveň:

1. pravidlo v `CLAUDE.md`: po dokončení práce, která mění, co projekt umí nebo
   jak funguje, přidej záznam
2. uživatel si o to řekne

## Distribuce a verzování

Kopie do projektu. Kolega si stáhne repozitář a zkopíruje `.claude/` a
`memory.md` do svého projektu.

Kopie tím zmrzne a oprava se do ní sama nedostane. Proto:

- **číslo verze** v `CLAUDE.md`, hned pod nadpisem, formát `MAJOR.MINOR.PATCH`
- **`CHANGELOG.md`** v repozitáři konfigurace, nejnovější verze nahoře

| Číslo | Kdy povyskočí |
| :--- | :--- |
| PATCH `0.1.1` | oprava, nic nového |
| MINOR `0.2.0` | přibylo něco, staré funguje dál |
| MAJOR `1.0.0` | přepsání staré složky novou něco rozbije |

Changelog odpovídá na jedinou otázku: mám verzi 0.1.0, na GitHubu je 0.3.0,
vyplatí se mi kopírovat znovu?

Pozor na jeden důsledek: jakmile je konfigurace commitnutá v projektu, dostane ji
každý, kdo projekt naklonuje. Volba „stáhnu, nebo nestáhnu" existuje jednou, při
zavedení do projektu, ne u každého člověka zvlášť.

## Omezení

| Omezení | Odkud se vzalo |
| :--- | :--- |
| jen Python a git; žádný Node, LibreOffice, zip, pandoc ani tesseract | změřeno na cílovém stroji |
| celá konfigurace do 200 kB | požadavek na jednoduchost |
| trvale načtený kontext kolem 545 řádků | součet `CLAUDE.md`, `rules/` a `memory.md` |
| žádné hooky, žádné příkazy, jeden agent | rozhodnuto v návrhu |

Bez Node a LibreOffice se dokumenty vytvářejí knihovnami `python-docx`,
`python-pptx` a `openpyxl`. Co knihovna neumí, jde dodělat zásahem do XML přes ni
samotnou, bez rozbalování souboru na disk.

## Jak poznáme, že to funguje

Tohle v původním zadání chybělo a stálo to celou jednu iteraci. Validace souboru
neznamená, že se skill spustí.

1. **Každý ze šesti skillů se načte na správný dotaz** v živém sezení. Dvojice
   `ldwh1` a `app-database` je nejnáchylnější k tomu, aby si vzaly cizí práci.
2. **Vytvořený `.docx` a `.pptx` jde otevřít** ve Wordu a v PowerPointu.
3. **`ste-lint.py` projde pod hodnotou 2,5** na vlastních souborech konfigurace.
4. **Import `memory.md` se chová rozumně** i v projektu, kde soubor chybí.

## Co se z prototypů nebere

Z `flask_template` a z dodaných vzorových skillů se bere jen to, co funguje.
Vědomě se nechává stranou:

| Nebere se | Proč |
| :--- | :--- |
| příkazy `/start`, `/spawn`, `/kill`, `/end` | stínily netechnického uživatele |
| agenti `planner` a `coder` | u technického vývojáře nemají problém k řešení |
| `PROJECT.md`, `PROJECT.local.md`, `session-memory.md` | tři soubory tam, kde stačí jeden |
| skill `skill-creator` | jeho hodnota stojí na subagentech |
| skill `asd-ste100` | styl musí platit vždy, skill se načte jen někdy |
| hooky | volají `python3`, který na Windows není, a mohou odpověď poslat dvakrát |
| `validate.py` a schémata ECMA-376 | 1,2 MB proti stropu 200 kB |
| `repack.py` | zásah do XML jde přes knihovnu, bez rozbalování |

## Otevřené otázky

1. **Název konfigurace a repozitáře.** Zatím nerozhodnuto.
2. **Chování chybějícího importu.** Ověřit v živém sezení, jestli `CLAUDE.md` s
   importem na neexistující `memory.md` vypíše varování.
3. **Slovníček interních pojmů.** Model zná kontokorent i bonitu, ale nezná
   interní kódy produktů a zkratky útvarů. Doplnit, až bude potřeba.
