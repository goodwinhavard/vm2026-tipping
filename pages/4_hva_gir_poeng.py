import streamlit as st

# Set page config
st.set_page_config(
    page_title="Poenggiving",
    page_icon="🎯",
    layout="wide"
)

st.markdown("# 🎯 Poenggiving")
st.markdown("---")

st.markdown("""
## Følgende poengsystem :

### 📋 Gruppespill
**72 kamper totalt**

- **1 poeng ** for riktig utfall (Hjemme, Uavgjort, Borte)
- **+2 bonuspoeng ** for også riktig resultat
- **Maksimum: 3 poeng per kamp**

---

### 🏆 Sluttspill

#### Round of 32
- **2 poeng per riktig lag**
- Du predikerer 32 lag → poeng gis for hvert lag som faktisk går videre

#### Round of 16  
- **4 poeng per riktig lag**
- Du predikerer 16 lag → poeng gis for hvert lag som faktisk går videre

#### Kvartfinaler
- **8 poeng per riktig lag**
- Du predikerer 8 lag → poeng gis for hvert lag som faktisk går videre

#### Semi Finals
- **16 poeng per riktig lag**
- Du predikerer 4 lag → poeng gis for hvert lag som faktisk går videre

#### Finals Teams (Before Winner)
- **32 poeng per riktig lag**
- Du predikerer 2 lag → poeng gis for hvert lag som faktisk går til finalen

---

### 🥇 Finale

#### Finalevinnere
- **64 poeng per riktig lag**
- Du predikerer 1 lag → poeng gis hvis du har riktig vinner av VM 2026

---

## Point Summary Table

| VM | Score | Poeng |
|-------|------|--------|
| Gruppespill - Riktig utfall | per kamp | 1 |
| Gruppespill - Eksakt resultat | per kamp | +2 |
| Round of 32 | per riktig lag | 2 |
| Round of 16 | per riktig lag | 4 |
| Kvartfinaler | per riktig lag | 8 |
| Semifinale | per riktig lag | 16 |
| Finale | per riktig lag | 32 |
| Finalevinner | engang | 64 |

---

## Maksimumspoeng

- **Gruppespill:** 72 kamper × 3 poeng = 216 poeng 
- **Round of 32:** 32 teams × 2 poeng = 64 poeng
- **Round of 16:** 16 teams × 4 poeng = 64 poeng
- **Kvartfinaler:** 8 teams × 8 poeng = 64 poeng
- **Semi Finals:** 4 teams × 16 poeng = 64 poeng
- **Finals Teams:** 2 teams × 32 poeng = 64 poeng
- **Finals Winner:** 1 × 64 poeng = 64 poeng

**🎉 Maksimum: 600 poeng**

---

""")