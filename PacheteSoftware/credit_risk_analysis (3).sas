/* ============================================================
   PROIECT PACHETE SOFTWARE - PARTEA SAS
   Analiza riscului de credit
   Acelasi set de date ca partea Python (cerinta de coerenta):
   emitent de carduri de credit, Taiwan, 2005 - 30.000 clienti
   Sursa: UCI ML Repository, Default of Credit Card Clients
   ============================================================

   INSTRUCTIUNI:
   1. Inlocuieste calea de mai jos cu calea reala a fisierului din
      contul tau SAS OnDemand (un singur loc de modificat).
   2. Selecteaza tot (Ctrl+A) si ruleaza (F3 / butonul Run).
   ============================================================ */

%LET calefisier = /home/USERUL_TAU/credit_card_default.csv;

/* ------------------------------------------------------------
   FACILITATEA 1: crearea unui set de date SAS dintr-un fisier extern
   Citim CSV-ul cu INFILE + INPUT, controland numele si tipurile.
   Cele 24 de coloane numerice sunt citite direct; ultima coloana
   (tinta) este citita ca text si convertita imediat in numeric,
   pentru a evita problemele de tip cauzate de terminatorii de linie.
   ------------------------------------------------------------ */
DATA work.credit;
    INFILE "&calefisier" DSD FIRSTOBS=2 TRUNCOVER;
    INPUT ID LIMIT_BAL SEX EDUCATION MARRIAGE AGE
          PAY_0 PAY_2 PAY_3 PAY_4 PAY_5 PAY_6
          BILL_AMT1 BILL_AMT2 BILL_AMT3 BILL_AMT4 BILL_AMT5 BILL_AMT6
          PAY_AMT1 PAY_AMT2 PAY_AMT3 PAY_AMT4 PAY_AMT5 PAY_AMT6
          default_txt $;
    default_payment_next_month = input(compress(default_txt, '0123456789', 'k'), 8.);
    DROP default_txt;
RUN;

PROC PRINT DATA=work.credit(OBS=10);
    TITLE 'Setul de date importat (primele 10 randuri)';
RUN;

/* ------------------------------------------------------------
   FACILITATEA 2: crearea si folosirea de formate definite de utilizator
   ------------------------------------------------------------ */
PROC FORMAT;
    VALUE sexf      1='Barbat' 2='Femeie';
    VALUE eduf      1='Studii postuniversitare' 2='Studii universitare'
                    3='Liceu' 4='Altele' 0,5,6='Necunoscut';
    VALUE staref    1='Casatorit' 2='Necasatorit' 0,3='Altele';
    VALUE defaultf  0='Fara default' 1='Default';
    VALUE limitf    low  -< 50000  = 'Limita mica'
                    50000 -< 200000 = 'Limita medie'
                    200000 - high   = 'Limita mare';
RUN;

/* ------------------------------------------------------------
   FACILITATILE 3, 5, 7: procesare iterativa si conditionala,
   functii SAS si masive (arrays)
   ------------------------------------------------------------ */
DATA work.credit_prelucrat;
    SET work.credit;

    LENGTH grupa_varsta $5 categorie_risc $8;

    ARRAY facturi{6} BILL_AMT1-BILL_AMT6;
    ARRAY plati{6}   PAY_AMT1-PAY_AMT6;

    luni_active = 0;
    DO i = 1 TO 6;
        IF facturi{i} > 0 THEN luni_active = luni_active + 1;
    END;

    total_facturat = SUM(of BILL_AMT1-BILL_AMT6);
    total_platit   = SUM(of PAY_AMT1-PAY_AMT6);
    factura_medie  = MEAN(of BILL_AMT1-BILL_AMT6);

    rata_acoperire = 0;
    IF total_facturat > 0 THEN rata_acoperire = total_platit / total_facturat;

    IF AGE < 30 THEN grupa_varsta = '21-29';
    ELSE IF AGE < 40 THEN grupa_varsta = '30-39';
    ELSE IF AGE < 50 THEN grupa_varsta = '40-49';
    ELSE IF AGE < 60 THEN grupa_varsta = '50-59';
    ELSE grupa_varsta = '60+';

    IF PAY_0 > 1 OR PAY_2 > 1 THEN categorie_risc = 'Ridicat';
    ELSE IF PAY_0 = 0 AND PAY_2 = 0 THEN categorie_risc = 'Scazut';
    ELSE categorie_risc = 'Mediu';

    DROP i;
    FORMAT SEX sexf. EDUCATION eduf. MARRIAGE staref.;
RUN;

PROC PRINT DATA=work.credit_prelucrat(OBS=10);
    VAR ID AGE grupa_varsta categorie_risc luni_active
        total_facturat total_platit factura_medie;
    TITLE 'Date prelucrate: variabile derivate (primele 10 randuri)';
RUN;

/* ------------------------------------------------------------
   FACILITATEA 4: crearea de subseturi de date
   ------------------------------------------------------------ */
DATA work.clienti_default;
    SET work.credit_prelucrat;
    WHERE default_payment_next_month = 1;
RUN;

PROC SQL;
    TITLE 'Numarul clientilor din subset (cu default)';
    SELECT COUNT(*) AS nr_clienti_default FROM work.clienti_default;
QUIT;

PROC PRINT DATA=work.clienti_default(OBS=10);
    VAR ID LIMIT_BAL AGE EDUCATION total_facturat default_payment_next_month;
    TITLE 'Subset: clientii cu default (primele 10 randuri)';
RUN;

/* ------------------------------------------------------------
   FACILITATEA 8: proceduri pentru raportare
   ------------------------------------------------------------ */
PROC MEANS DATA=work.credit_prelucrat N MEAN STD MIN MAX MAXDEC=2;
    VAR LIMIT_BAL AGE total_facturat total_platit;
    TITLE 'Statistici descriptive pentru variabilele financiare';
RUN;

PROC FREQ DATA=work.credit_prelucrat;
    TABLES EDUCATION default_payment_next_month
           EDUCATION*default_payment_next_month / NOROW NOCOL;
    FORMAT default_payment_next_month defaultf.;
    TITLE 'Distributii si tabel incrucisat educatie x default';
RUN;

PROC FREQ DATA=work.credit_prelucrat;
    TABLES LIMIT_BAL;
    FORMAT LIMIT_BAL limitf.;
    TITLE 'Distributia clientilor pe categorii de limita de credit';
RUN;

PROC TABULATE DATA=work.credit_prelucrat;
    CLASS grupa_varsta categorie_risc;
    VAR LIMIT_BAL;
    TABLE grupa_varsta, categorie_risc*LIMIT_BAL*MEAN;
    TITLE 'Limita medie pe grupa de varsta si categorie de risc';
RUN;

/* ------------------------------------------------------------
   FACILITATEA 6: combinarea seturilor de date prin proceduri
   specifice SAS (MERGE) si prin SQL (PROC SQL)
   ------------------------------------------------------------ */
PROC SQL;
    CREATE TABLE work.rezumat_educatie AS
    SELECT EDUCATION,
           COUNT(*)                          AS nr_clienti,
           AVG(default_payment_next_month)   AS rata_default,
           AVG(LIMIT_BAL)                    AS limita_medie
    FROM work.credit_prelucrat
    GROUP BY EDUCATION;
QUIT;

PROC SORT DATA=work.credit_prelucrat OUT=work.credit_sortat; BY EDUCATION; RUN;
PROC SORT DATA=work.rezumat_educatie; BY EDUCATION; RUN;

DATA work.credit_imbogatit;
    MERGE work.credit_sortat(IN=a) work.rezumat_educatie(IN=b);
    BY EDUCATION;
    IF a;
RUN;

PROC PRINT DATA=work.rezumat_educatie;
    TITLE 'Rezumat pe nivel de educatie (creat cu PROC SQL)';
RUN;

PROC PRINT DATA=work.credit_imbogatit(OBS=10);
    VAR ID EDUCATION LIMIT_BAL rata_default limita_medie;
    TITLE 'Date imbogatite prin MERGE (primele 10 randuri)';
RUN;

/* ------------------------------------------------------------
   FACILITATEA 9: proceduri statistice
   ------------------------------------------------------------ */
PROC CORR DATA=work.credit_prelucrat;
    VAR LIMIT_BAL total_facturat total_platit;
    WITH AGE;
    TITLE 'Corelatii intre varsta si variabilele financiare';
RUN;

PROC REG DATA=work.credit_prelucrat;
    MODEL total_facturat = LIMIT_BAL AGE total_platit;
    TITLE 'Regresie multipla: explicarea sumei facturate';
RUN;
QUIT;

PROC LOGISTIC DATA=work.credit_prelucrat;
    CLASS SEX EDUCATION MARRIAGE / PARAM=REF;
    MODEL default_payment_next_month(EVENT='1') =
          LIMIT_BAL AGE total_facturat total_platit PAY_0 PAY_2;
    TITLE 'Regresie logistica: probabilitatea de neplata';
RUN;

/* ------------------------------------------------------------
   FACILITATEA 10: generarea de grafice
   ------------------------------------------------------------ */
PROC SGPLOT DATA=work.credit_prelucrat;
    HISTOGRAM LIMIT_BAL;
    DENSITY LIMIT_BAL;
    TITLE 'Distributia limitei de credit';
RUN;

PROC SGPLOT DATA=work.credit_prelucrat;
    VBAR EDUCATION / RESPONSE=default_payment_next_month STAT=MEAN;
    TITLE 'Rata medie de default pe nivel de educatie';
RUN;

PROC SGPLOT DATA=work.credit_prelucrat;
    SCATTER X=LIMIT_BAL Y=total_facturat / GROUP=default_payment_next_month;
    TITLE 'Limita de credit vs. suma facturata';
RUN;

TITLE;
