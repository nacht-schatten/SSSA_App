
import random
import math
from itertools import combinations

def is_prim(r):
    """
    Ueberprueft auf Primzahlen.

    Parameters
    ----------
    r (int/float): beliebige Zahl

    Returns
    -------
    (boolean): Wahrheitswert "True" bei Primzahl, sonst "False".

    """
    if r != int(r): #6.33 keine Primzahl
        return False
    else:
        r = int(r) #7.0 = 7
        
    if r <= 1:
        return False
    if r == 2:
        return True
    for i in range(2, int(math.sqrt(r)) + 1): #49 = 7*7; range(2, 7) prüft alle x mit 2<=x<7 (7 ausgeschlossen), daher +1
        if r % i == 0:
            return False #return-Aufruf beendet sofort die gesamte Funktion
    return True




def next_prim(s, n, k):
    """
    Bestimmt neachste Primzahl nach s, damit s im Primkörper (mod p) als Restklasse existiert. k ist die minimale Anzahl
    der verschiedenen Punkte, die fuer die spaetere Rekonstruktion benoetigt werden. n ist die tatsaechliche Anzahl
    der Punkte, die vergeben werden.
    
    Werden mehr tuples vergeben, als benoetigt, erhoeht sich die Ausfallsicherheit, denn es bleiben genuegend tuples verfuegbar.
    
    Ein Angreifer benoetigt mindestens k Punkte gleichzeitig, demnach sollte k groß gewaehlt werden. Jedoch steigt somit
    auch die Laufzeit.
    
    Parameters
    ----------
    s (int/float): beliebige Zahl
    n (int): Anzahl der Informationen, wobei [0] nicht vergeben werden kann, da f([0]) = s.
    k (int): Anzahl der benötigten tupels

    Returns
    -------
    cand (int): naechsthoehere Primzahl passend zu s und n

    """
    if n < k:
        return
    
    cand = int(s) + 1 #sonst s % s == 0; float-Eingabe durch Typumwandlung "int()" moeglich
    while True:
        if is_prim(cand) and cand > n:
            return cand
        else:
            cand = cand + 1



def generiere_funktion(s, k, p):
    '''
    Generiert eine Koeffizientenliste für ein Polynom k-ten Grades. Der erste Koeffizient wird zufaellig generiert, darf dabei nicht Null sein,
    dass Grad k erhalten bleibt. Der letzte Koeffizinet ist s. Alle anderen Koeffizienten werden zufaellig generiert und duerfen auch Null sein.

    Parameters
    ----------
    s (int): das Geheimnis
    k (int): Anzahl der benoetigten tupels
    p (int): naechsthoehere Primzahl passend zu s und n

    Returns
    -------
    koeff (list): beispielsweise [a, b, c, s] fuer a * x^3 + b * x^2 + c * x + s

    '''
    koeff = [random.randint(1, p - 1)]  # Höchstkoeffizinet nicht 0
    koeff += [random.randint(0, p - 1) for _ in range(k - 2)] #alle anderen Koeffizineten mit Ausnahme des letzen dürfen 0 annehmen
    koeff.append(s) #letzter Koeffizient ist s
    return koeff

def anteile_generieren(s, k, n, p):
    '''
    Generiert eine Liste mit n verschiedenen Wertepaaren, wobei [0, f(0)] nicht vergeben wird, da f(0)=s

    Parameters
    ----------
    s (int): das Geheimnis
    k (int): Anzahl der benoetigten tupels
    n (int): Gesamtanzahl der Wertepaare, die verteilt werden
    p (int): naechsthoehere Primzahl passend zu s und n

    Returns
    -------
    (list[Tuple[int, int]]): n verschiedenen Wertepaaren


    '''
    koeff = generiere_funktion(s, k, p)
    x_werte = random.sample(range(1, p), n) #0 darf nicht vergeben werden, da f(0)=s
    #random.sample verhindert, dass x-Werte mehr als einmal vorkommen, was zu identischen Wertepaaren führen würde
    
    y_werte = []
    for x in x_werte:
        y = sum([koeff[i] * (x ** (k - 1 - i)) for i in range(k)]) % p
        y_werte.append(y)
    return list(zip(x_werte, y_werte))




def lagrange_interpolation_mod(x_vals, y_vals, p, k):
    '''
    Bestimmt aus k Wertepaaren ein Polynom vom Grad k-1 mittels Lagrange_Interpolation.
    Liegen mehr als k Wertepaare vor, werden mithilfe von random.sample zufeallig k verschiedene Wertepaare ausgewaehlt.

    Parameters
    ----------
    x_vals (list): Die x-Werte der vergebenen Anteile
    y_vals (list): Die zu x zugehoerigen y-Werte der vergebenen Anteile
    p (int): naechsthoehere Primzahl passend zu s und n
    k (int): Anzahl der benoetigten tupels 

    Raises
    ------
    ValueError
    Da mindestens k Punkte noetig sind, um ein Polynom k-1-ten Grades zu bestimmen, wird ein Fehler ausgegeben,
    wenn weniger als k Werte vorliegen.

    Returns
    -------
    total (int): Rekonstruiertes s in modulo p
    '''
    if len(x_vals) < k:
        raise ValueError(f"Mindestens {k} Punkte nötig, aber nur {len(x_vals)} gegeben.")

    # Zufällige Auswahl von k Punkten
    indices = random.sample(range(len(x_vals)), k)
    x = [x_vals[i] for i in indices]
    y = [y_vals[i] for i in indices]

    total = 0
    for j in range(k):
        num = 1
        den = 1
        for m in range(k):
            if m != j:
                num = (num * -x[m]) % p
                den = (den * (x[j] - x[m])) % p
        inv_den = pow(den, -1, p)
        total = (total + y[j] * num * inv_den) % p

    return total

   

#-----------------------------------
#Autor: Johanna Vogel


def konsistenzpruefung(punkte, k, p):
    '''
    Die Lagrange-Interpolation erstellt ein Polynom k-1-ten Grades zu k gegbenen Wertepaaren. Dabei kann ein fehlerhaftes
    Wertepaar zu einem falsch rekonstruierten s führen. Dies kann aber nicht erkannt werden.
    Sobald k+1 oder mehr Werte vorliegen, kann man erkennen, ob alle Punkte zusammenpassen, wenn auch die Werte, die nicht
    zu Bestimmung des Polynoms beigetragen haben, dessen Bedingungen erfuellen.
    
    "konsistenzpruefung" rekonstruiert s (mittels der Funktion lagrange_interpolation_mod(x_vals, y_vals, p, k))aus allen 
    k-großen Teilmengen der eingegebenen Wertepaare und zaehlt die Haeufigkeit der berechneten s. Stimmt diese mit der
    Anzahl der Wertepaare überein, gilt die Rekonstruktion als konsistent.
    
    Werden verschiedene s berechnet, wird deren Haeufigkeit gezaehlt und das s mit der groeßten Haeufigkeit als Vermutung ausgegeben.
    
    Je mehr zusaetzliche (nicht fehlerhafte) Wertepaare vorliegen, desto zuverlaessiger wird diese Vermutung.
    
    Parameters
    ----------
    punkte (list): die eingegebenen Wertepaare
    k (int): Anzahl der benoetigten tupels
    p (int): naechsthoehere Primzahl passend zu s und n

    Returns
    -------
    best_guess (int): das s, das beim Prüfen aller k-großen Teilmengen der eingegebenen Werte am haeufigsten vorkam
    konsistent (boolean): Wahrheitswert, "True", wenn alle k-großen Teilmengen zum gleichen s fuehren, "False" sonst.
    haeufigkeiten (dict[int, int]): Ein Dictionary, das für jedes rekonstruierte Geheimnis zaehlt, wie oft es bei den k-großen Teilmengen vorkam.
    '''
    geheime_kandidaten = []

    for subset in combinations(punkte, k):
        x_vals, y_vals = zip(*subset)
        s = lagrange_interpolation_mod(x_vals, y_vals, p, k)
        geheime_kandidaten.append(s % p)

    # Zähle, welches Ergebnis wie oft vorkommt
    haeufigkeiten = {}
    for s in geheime_kandidaten:
        haeufigkeiten[s] = haeufigkeiten.get(s, 0) + 1

    # Finde das häufigste Ergebnis
    best_guess = max(haeufigkeiten, key=haeufigkeiten.get)
    anzahl = haeufigkeiten[best_guess]

    konsistent = (anzahl == len(geheime_kandidaten))
    return best_guess, konsistent, haeufigkeiten


import streamlit
import streamlit as st

st.set_page_config(page_title="Geheimnisteilung", layout="centered")
st.title("🔐 Shamir’s Secret Sharing")

tab1, tab2 = st.tabs(["➕ Anteile generieren", "🔍 Rekonstruktion"])




    # 🎯 Tab 1 – Anteilerzeugung
with tab1:
        


    st.subheader("➕ Anteile generieren")

    s = st.number_input("Geheimnis (s)", min_value=0, value=123)
    k = st.number_input("Benötigte Anteile (k)", min_value=2, value=3)
    n = st.number_input("Gesamtanzahl Anteile (n)", min_value=1, value=5)
    d = n-k

    def zeige_k_warnung(k, n):
        if k > n:
            st.error("❌ k darf nicht größer als n sein!")
            return False
        elif k <= n * 0.3:
            st.warning("⚠️ Angreiferrisiko: k ist sehr klein!\n\n" + f"\n Ein Angreifer braucht nur **{k}** von **{n}** Anteilen, um das Geheimnis zu erfahren!")
        
        elif k >= n - 2:
            st.warning("⚠️ Ausfallsrisiko: k ist sehr groß!\n\n" + "Verlorene oder fehlerhafte Anteile gefährden hier schnell die Rekonstruierbarkeit des Geheimnisses!")
                       
        else:
            st.success("✅ k ist gut gewählt. Eine gute Balance zwischen Sicherheit und Verfügbarkeit!")
        return True

    weiter = zeige_k_warnung(k, n)

    eigene_p_gueltig = True
    p = None
    validierungsfehler = ""

    if weiter:
        verwende_eigene_p = st.checkbox("📌 Ich möchte eine eigene Primzahl verwenden")

        if verwende_eigene_p:
            p_input = st.number_input("Eigene Primzahl (p)", value=0, step=1)
            if p_input > 0:
                if not is_prim(p_input):
                    eigene_p_gueltig = False
                    validierungsfehler = "❌ Die Zahl ist keine Primzahl."
                elif p_input <= max(s, n):
                    eigene_p_gueltig = False
                    validierungsfehler = f"❌ Die Primzahl muss größer als s = {s} und n = {n} sein."
                else:
                    p = p_input
            else:
                eigene_p_gueltig = False
                validierungsfehler = "🪶 Bitte gib eine Primzahl ein."

            if not eigene_p_gueltig:
                st.error(validierungsfehler)
        else:
            p = next_prim(s, n, k)
            st.info(f"💡 Automatisch berechnete Primzahl: p = {p}")
    else:
        p = None
        eigene_p_gueltig = False


       
        
        

# ✅ Alles passt? Dann Button zeigen!
    if weiter and (not verwende_eigene_p or eigene_p_gueltig):
        if st.button("🔐 Anteile generieren"):
            shares = anteile_generieren(s, k, n, p)
            st.success(f"✅ Anteile erfolgreich erzeugt! Verwendete Primzahl p = {p}")
            st.code(" ; ".join(f"{x},{y}" for x, y in shares), language="text")

            
           

    # 🔎 Tab 2 – Rekonstruktion
with tab2:
       
        st.subheader("🔎 Geheimnis rekonstruieren")

        punkte_input = st.text_input("📥 Wertepunkte (x,y;x,y;...)", value="1,45;2,63;3,28")
        p = st.number_input("Primzahl (p)", min_value=1, value=89)
        k = st.number_input("Benötigte Anteile (k)", min_value=2, value=3)

        try:
            punkte = [tuple(map(int, pair.split(","))) for pair in punkte_input.split(";") if pair.strip()]
        except:
            st.error("❌ Ungültiges Format bei den Punkten. Bitte als x,y;x,y;... eingeben.")
            punkte = []
            
        def ist_gueltige_primzahl(p, punkte):

            if not is_prim(p):
                return False, "❌ Die eingegebene Zahl ist keine Primzahl."

            werte_flat = [v for tupel in punkte for v in tupel]
            max_val = max(werte_flat, default=0)

            if p <= max_val:
                return False, f"❌ Verdacht auf fehlerhafte Primzahl! p muss größer als {max_val} sein."

            return True, ""
        


        ist_gueltig, fehlertext = ist_gueltige_primzahl(p, punkte)

        if not ist_gueltig:
            st.error(fehlertext)
        elif len(punkte) < k:
            st.warning(f"⚠️ Du brauchst mindestens {k} Anteile für die Rekonstruktion.")
        elif st.button("🧩 Rekonstruktion starten"):
            try:
                s_guess, konsistent, stimmen = konsistenzpruefung(punkte, k, p)
                werte = list(stimmen.values())
                max_h = max(werte)
                max_kandidaten = [s for s, h in stimmen.items() if h == max_h]

            # 🟡 Spezialfall: alle s-Werte gleich oft?
                if len(max_kandidaten) > 1:
                    st.error("🔄 Kein eindeutiges Geheimnis rekonstruierbar: Mehrere s-Werte treten gleich oft auf.")
                    st.write("🧩 Gleich häufige Kandidaten:")
                    st.code(", ".join(str(s) for s in max_kandidaten))
                    st.info("💡 **Tipp:** Füge einen weiteren Anteil hinzu, um eine Entscheidung zu ermöglichen.")
                
                elif konsistent:
                    st.success(f"✅ Geheimnis erfolgreich rekonstruiert: s = {s_guess}")
                else:
                    st.warning(f"⚠️ Nicht eindeutig: häufigstes s = {s_guess}")
                    st.write("Ergebnisse der Häufigkeitsanalyse:")
                    st.json(stimmen)
                    
                
                    # 🕵️‍♂️ Analyse möglicher Störpunkte
                    fehlerbericht = []
                    for i, punkt in enumerate(punkte):
                         ohne_punkt = punkte[:i] + punkte[i+1:]
                         if len(ohne_punkt) >= k:
                             s_test, konsistent_test, _ = konsistenzpruefung(ohne_punkt, k, p)
                             if konsistent_test:
                                 fehlerbericht.append(f"Ohne Punkt {punkt} ergibt sich konsistent **s = {s_test}**")

                    if fehlerbericht:
                         text = "🧯 **Verdächtiger Punkt:**\n\n" + "\n".join(f"- {zeile}" for zeile in fehlerbericht)
                         st.info(text)
                    if not fehlerbericht:
                         tipp = "**Verdacht auf falsche Anteile!**\n\n" + "**Tipp:** Entferne einen Punkt und versuche es erneut!"
                         st.info(tipp)
                
            except Exception as e:
                st.error(f"❌ Fehler bei der Rekonstruktion: {e}")


