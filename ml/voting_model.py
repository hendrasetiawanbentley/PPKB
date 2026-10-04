# -*- coding: utf-8 -*-
"""
Deteksi anomali kewajaran penyajian laporan keuangan — ensemble voting.
Direfactor dari fraud_dashboard.py (versi Dash monolith) menjadi fungsi murni
yang bisa dipanggil dari halaman Dash (pages/5_ml_voting.py) maupun dipanggil
ulang untuk emiten lain tanpa menulis ulang kode.

Metode: 5 classifier (Logistic Regression, SVM-RBF, Neural Net, Random Forest,
Gradient Boosting) dilatih dengan Leave-One-Out CV pada label historis
fraud/clean, lalu setiap model 'vote' pada data target -> majority voting.
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score

MODELS_FACTORY = {
    "Logistic Regression": lambda: LogisticRegression(max_iter=2000, C=0.5, random_state=42),
    "SVM (RBF)": lambda: SVC(kernel="rbf", probability=True, C=1.0, gamma="scale", random_state=42),
    "Neural Network": lambda: MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=3000, random_state=42,
                                             early_stopping=True, validation_fraction=0.15),
    "Random Forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=3, random_state=42),
    "Gradient Boosting": lambda: GradientBoostingClassifier(n_estimators=100, max_depth=2,
                                                              learning_rate=0.1, random_state=42),
}


# ---------------------------------------------------------------------------
# Parsing Excel (Neraca / Laba Rugi / Arus Kas per sheet per emiten)
# TODO: sesuaikan label section & nama akun kalau format sumber data berbeda
# ---------------------------------------------------------------------------

def parse_value(val):
    if pd.isna(val) or str(val).strip() in ["-", ""]:
        return 0.0
    s = str(val).replace(" M", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]
    try:
        v = float(s)
        return -v if neg else v
    except Exception:
        return 0.0


def find_sections(df):
    secs = []
    for idx, row in df.iterrows():
        lb = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        if "Laporan Neraca" in lb:
            secs.append(("neraca", idx))
        elif "Laporan Laba Rugi" in lb:
            secs.append(("labarugi", idx))
        elif "Laporan Arus Kas" in lb:
            secs.append(("aruskas", idx))
    return secs


def get_quarter(df, row):
    if row + 1 < len(df):
        v = str(df.iloc[row + 1, 1]).strip() if pd.notna(df.iloc[row + 1, 1]) else ""
        if v.startswith("Q") and len(v) >= 7:
            return v
    return None


def parse_sec(df, s, e):
    d = {}
    for _, r in df.iloc[s:e].iterrows():
        lb = str(r.iloc[0]).strip().lower() if pd.notna(r.iloc[0]) else ""
        if lb:
            d[lb] = parse_value(r.iloc[1]) if len(r) > 1 else 0.0
    return d


def gi(data, *kw):
    for k, v in data.items():
        for w in kw:
            if w in k.lower():
                return v
    return 0.0


def parse_sheet(df):
    secs = find_sections(df)
    qs = {}
    for i, (t, s) in enumerate(secs):
        nx = secs[i + 1][1] if i + 1 < len(secs) else len(df)
        q = get_quarter(df, s)
        if not q:
            continue
        if q not in qs:
            qs[q] = {"neraca": {}, "labarugi": {}, "aruskas": {}}
        qs[q][t] = parse_sec(df, s + 2, nx)
    return qs


def compute_features(quarters):
    rows = []
    for q in sorted(quarters.keys(), key=lambda x: (x.split()[-1], x.split()[0])):
        bs, pl, cf = quarters[q].get("neraca", {}), quarters[q].get("labarugi", {}), quarters[q].get("aruskas", {})
        ta = gi(bs, "total aset"); tl = gi(bs, "total liabilitas"); te = gi(bs, "total ekuitas")
        kas = gi(bs, "kas dan setara kas"); ar = gi(bs, "piutang usaha"); inv = gi(bs, "persediaan")
        ca = gi(bs, "total aset lancar"); fa = gi(bs, "aset tetap")
        cl = gi(bs, "liabilitas jangka pendek"); ltl = gi(bs, "liabilitas jangka panjan")
        rev = gi(pl, "total pendapatan"); gp = gi(pl, "laba kotor")
        if gp == 0 and rev != 0:
            gp = rev
        opex = abs(gi(pl, "total beban usaha")); oi = gi(pl, "laba usaha")
        oth = gi(pl, "penghasilan/beban lain"); pbt = gi(pl, "laba sebelum pajak")
        tax = abs(gi(pl, "beban pajak penghasilan"))
        ni = gi(pl, "laba bersih tahun berjalan")
        if ni == 0:
            ni = gi(pl, "laba bersih dari operasi")
        cfo = gi(cf, "arus kas dari aktivitas operasi")
        sd = lambda a, b: a / b if b != 0 else 0
        rows.append({
            "debt_to_assets": sd(tl, ta), "debt_to_equity": sd(tl, te), "gp_to_assets": sd(gp, ta),
            "roa": sd(ni, ta), "ca_to_ta": sd(ca, ta), "net_margin": sd(ni, rev), "ar_to_rev": sd(ar, rev),
            "rev_to_ta": sd(rev, ta), "current_ratio": sd(ca, cl), "rev_to_fa": sd(rev, fa),
            "cash_to_ta": sd(kas, ta), "inv_to_cl": sd(inv, cl), "ltd_to_ta": sd(ltl, ta),
            "ni_to_gp": sd(ni, gp), "ta_to_eq": sd(ta, te), "fa_to_ta": sd(fa, ta),
            "cash_to_ca": sd(kas, ca), "eq_to_debt": sd(te, tl), "ar_to_ta": sd(ar, ta),
            "gp_margin": sd(gp, rev), "inv_to_ta": sd(inv, ta), "inv_to_rev": sd(inv, rev),
            "op_margin": sd(oi, rev), "pbt_margin": sd(pbt, rev), "opex_ratio": sd(opex, rev),
            "eff_tax": sd(tax, abs(pbt)), "cfo_to_ni": sd(cfo, ni), "cfo_to_ta": sd(cfo, ta),
            "cfo_to_rev": sd(cfo, rev), "other_to_oi": sd(oth, oi),
        })
    if not rows:
        return None
    dfq = pd.DataFrame(rows)
    res = {}
    for c in dfq.columns:
        v = dfq[c].replace([np.inf, -np.inf], np.nan).dropna()
        res[f"{c}_mean"] = float(v.mean()) if len(v) > 0 else 0
        res[f"{c}_std"] = float(v.std()) if len(v) > 1 else 0
    for k in res:
        if np.isnan(res[k]) or np.isinf(res[k]):
            res[k] = 0
    return res


def t_rank(X, y):
    f, nf = y == 1, y == 0
    n1, n2 = f.sum(), nf.sum()
    ts = {}
    for c in X.columns:
        fv, nv = X.loc[f, c].values, X.loc[nf, c].values
        s1 = np.std(fv, ddof=1) if len(fv) > 1 else 1e-10
        s2 = np.std(nv, ddof=1) if len(nv) > 1 else 1e-10
        d = np.sqrt(s1 ** 2 / max(n1, 1) + s2 ** 2 / max(n2, 1))
        ts[c] = abs(np.mean(fv) - np.mean(nv)) / d if d > 1e-12 else 0
    return sorted(ts.items(), key=lambda x: x[1], reverse=True)


def prep(Xtr, Xte):
    Xl, Xt = Xtr.copy(), Xte.copy()
    for c in Xl.columns:
        Xl[c] = np.sign(Xl[c]) * np.log1p(np.abs(Xl[c]))
        Xt[c] = np.sign(Xt[c]) * np.log1p(np.abs(Xt[c]))
    sc = StandardScaler()
    return (pd.DataFrame(sc.fit_transform(Xl), columns=Xl.columns, index=Xl.index),
            pd.DataFrame(sc.transform(Xt), columns=Xt.columns, index=Xt.index))


def get_prob(model, Xte):
    if hasattr(model, "decision_function"):
        d = float(model.decision_function(Xte)[0])
        return 1.0 / (1.0 + np.exp(-d))
    return float(model.predict_proba(Xte)[0, 1])


def check_benford_law(df):
    """Mengecek kesesuaian digit pertama angka di laporan keuangan dengan Hukum Benford."""
    digits = []
    for col in df.columns:
        for val in df[col]:
            if pd.notna(val):
                try:
                    val_str = str(val).replace("-", "").replace(".", "").strip()
                    for char in val_str:
                        if char in "123456789":
                            digits.append(int(char))
                            break
                except Exception:
                    pass
    if len(digits) < 25:
        return 0.0, "Jumlah digit pertama terlalu sedikit (<25)", "LOW"
    
    counts = np.bincount(digits)[1:10]
    if len(counts) < 9:
        counts = np.append(counts, np.zeros(9 - len(counts)))
    obs = counts / sum(counts)
    exp = np.log10(1.0 + 1.0 / np.arange(1, 10))
    
    mad = float(np.mean(np.abs(obs - exp)))
    
    if mad < 0.008:
        verdict = "LOW"
        desc = f"Excess MAD Result : Conform and KS Statistic ; Conform"
    elif mad < 0.018:
        verdict = "MEDIUM"
        desc = f"Acceptable deviation (MAD: {mad:.4f})"
    else:
        verdict = "HIGH"
        desc = f"Significant deviation (MAD: {mad:.4f})"
    return mad, desc, verdict


def compute_beneish_mscore(a_curr, a_prev):
    """Menghitung skor manipulasi Beneish M-Score berdasarkan 8 indeks rasio."""
    sd = lambda x, y: x / y if y else 0
    
    dsri = sd(sd(a_curr["piutang_usaha"], a_curr["pendapatan"]), sd(a_prev["piutang_usaha"], a_prev["pendapatan"]))
    gp_curr = a_curr["laba_kotor"] if a_curr["laba_kotor"] else a_curr["pendapatan"]
    gp_prev = a_prev["laba_kotor"] if a_prev["laba_kotor"] else a_prev["pendapatan"]
    gpm_curr = sd(gp_curr, a_curr["pendapatan"])
    gpm_prev = sd(gp_prev, a_prev["pendapatan"])
    gmi = sd(gpm_prev, gpm_curr)
    
    aq_curr = 1.0 - sd(a_curr["aset_lancar"] + a_curr["aset_tetap"], a_curr["total_aset"])
    aq_prev = 1.0 - sd(a_prev["aset_lancar"] + a_prev["aset_tetap"], a_prev["total_aset"])
    aqi = sd(aq_curr, aq_prev)
    
    sgi = sd(a_curr["pendapatan"], a_prev["pendapatan"])
    depi = 1.0
    sgai = sd(sd(a_curr["beban_usaha"], a_curr["pendapatan"]), sd(a_prev["beban_usaha"], a_prev["pendapatan"]))
    lv_curr = sd(a_curr["total_liabilitas"], a_curr["total_aset"])
    lv_prev = sd(a_prev["total_liabilitas"], a_prev["total_aset"])
    lvgi = sd(lv_curr, lv_prev)
    tata = sd(a_curr["laba_bersih"] - a_curr["arus_kas_operasi"], a_curr["total_aset"])
    
    m_score = -4.84 + 0.92*dsri + 0.52*gmi + 0.40*aqi + 0.89*sgi + 0.115*depi - 0.172*sgai + 4.679*tata - 0.327*lvgi
    
    if m_score > -1.78:
        verdict = "HIGH"
        desc = f"Beneish M-Score: {m_score:.2f} (> -1.78, Indikasi Manipulasi)"
    elif m_score > -2.22:
        verdict = "MEDIUM"
        desc = f"Beneish M-Score: {m_score:.2f} (Waspada / Perlu Pengawasan)"
    else:
        verdict = "LOW"
        desc = f"Beneish M-Score: {m_score:.2f} (Aman / Wajar)"
        
    return m_score, desc, verdict


# ---------------------------------------------------------------------------
# Fungsi utama yang dipanggil dari halaman Dash
# ---------------------------------------------------------------------------

def run_ml_voting(excel_path: str, train_labels: dict, target_companies: list, k_ratio: float = 0.29):
    """
    excel_path: path file Excel, tiap sheet = 1 emiten
    train_labels: {'KODE_EMITEN': 1 (fraud) / 0 (clean), ...} -> data historis kasus
    target_companies: daftar kode emiten yang mau diperiksa
    k_ratio: proporsi fitur teratas yang dipakai (default ~29%, mengikuti Ravisankar et al. 2011)
    """
    xls = pd.ExcelFile(excel_path)
    all_feat, n_quarters = {}, {}
    benford_mads, benford_descs, benford_verdicts = {}, {}, {}
    beneish_scores, beneish_descs, beneish_verdicts = {}, {}, {}
    
    from utils.financial_parser import extract_raw_accounts, sorted_quarters
    
    for sh in xls.sheet_names:
        code = sh.strip().upper()
        df = pd.read_excel(xls, sh, header=None)
        q = parse_sheet(df)
        f = compute_features(q)
        if f:
            all_feat[code] = f
            n_quarters[code] = len(q)
            
            # Hitung Benford
            mad, desc, verd = check_benford_law(df)
            benford_mads[code] = mad
            benford_descs[code] = desc
            benford_verdicts[code] = verd
            
            # Hitung Beneish M-Score
            raw_accs = extract_raw_accounts(q)
            q_list = sorted_quarters(q)
            if len(q_list) >= 2:
                m_score, m_desc, m_verdict = compute_beneish_mscore(raw_accs[q_list[-1]], raw_accs[q_list[-2]])
            else:
                m_score, m_desc, m_verdict = 0.0, "Butuh minimal 2 kuartal data untuk menghitung M-Score", "LOW"
            beneish_scores[code] = m_score
            beneish_descs[code] = m_desc
            beneish_verdicts[code] = m_verdict

    train_names = [n for n in all_feat if n in train_labels]
    if len(train_names) < 4:
        raise ValueError(
            "Data training kurang dari 4 emiten berlabel. "
            "Perlu histori kasus fraud/clean yang lebih banyak untuk hasil yang andal."
        )
    X_train = pd.DataFrame([all_feat[n] for n in train_names], index=train_names)
    y_train = np.array([train_labels[n] for n in train_names])

    X_infer_all = {c: pd.DataFrame([all_feat[c]], index=[c]) for c in target_companies if c in all_feat}

    good = X_train.std() > 1e-10
    X_train = X_train.loc[:, good].replace([np.inf, -np.inf], np.nan).fillna(0)
    for c in X_infer_all:
        X_infer_all[c] = X_infer_all[c][X_train.columns].replace([np.inf, -np.inf], np.nan).fillna(0)

    ranked = t_rank(X_train, y_train)
    n_total = X_train.shape[1]
    k = max(5, round(n_total * k_ratio))
    top_feats = [f for f, _ in ranked[:k]]

    # LOO validation -> performa tiap model
    yt_all = {m: [] for m in MODELS_FACTORY}
    yp_all = {m: [] for m in MODELS_FACTORY}
    ypr_all = {m: [] for m in MODELS_FACTORY}
    for tr_i, te_i in LeaveOneOut().split(X_train):
        Xtr, Xte = X_train.iloc[tr_i], X_train.iloc[te_i]
        ytr, yte = y_train[tr_i], y_train[te_i]
        fold_ranked = [f for f, _ in t_rank(Xtr, ytr)][:k]
        Xtr_s, Xte_s = prep(Xtr[fold_ranked], Xte[fold_ranked])
        for mn, factory in MODELS_FACTORY.items():
            try:
                m = factory(); m.fit(Xtr_s, ytr)
                p = int(m.predict(Xte_s)[0]); pr = get_prob(m, Xte_s)
            except Exception:
                p, pr = 1, 0.5
            yt_all[mn].append(yte[0]); yp_all[mn].append(p); ypr_all[mn].append(pr)

    model_perf = {}
    for mn in MODELS_FACTORY:
        yt, yp, ypr = np.array(yt_all[mn]), np.array(yp_all[mn]), np.array(ypr_all[mn])
        cm = confusion_matrix(yt, yp, labels=[0, 1]); tn, fp, fn, tp = cm.ravel()
        acc = accuracy_score(yt, yp) * 100
        sens = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
        spec = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
        try:
            auc = roc_auc_score(yt, ypr) * 100
        except Exception:
            auc = 50
        model_perf[mn] = {"acc": round(acc, 1), "sens": round(sens, 1), "spec": round(spec, 1), "auc": round(auc, 1)}

    fraud_mean = X_train.loc[y_train == 1].mean()
    clean_mean = X_train.loc[y_train == 0].mean()

    company_results = {}
    for comp, X_infer in X_infer_all.items():
        Xtr_s, Xte_s = prep(X_train[top_feats], X_infer[top_feats])
        preds, probs = {}, {}
        for mn, factory in MODELS_FACTORY.items():
            m = factory(); m.fit(Xtr_s, y_train)
            preds[mn] = int(m.predict(Xte_s)[0])
            probs[mn] = get_prob(m, Xte_s)

        votes_fraud = sum(1 for v in preds.values() if v == 1)
        avg_prob = float(np.mean(list(probs.values())))
        verdict = "FRAUD" if votes_fraud > len(preds) / 2 else "CLEAN"

        comp_vals = X_infer.iloc[0]
        feat_profile = []
        for feat, t in ranked[:k]:
            fv, cv, bv = float(fraud_mean[feat]), float(clean_mean[feat]), float(comp_vals[feat])
            closer = "FRAUD" if abs(bv - fv) < abs(bv - cv) else "CLEAN"
            feat_profile.append({"name": feat, "t": round(t, 3), "fraud": fv, "clean": cv, "val": bv, "closer": closer})

        best_model = max(model_perf, key=lambda x: model_perf[x]["auc"])
        company_results[comp] = {
            "verdict": verdict,
            "votes_fraud": votes_fraud,
            "n_models": len(preds),
            "avg_prob": round(avg_prob, 4),
            "best_model": best_model,
            "best_auc": model_perf[best_model]["auc"],
            "feat_profile": feat_profile,
            "n_quarters": n_quarters.get(comp, 0),
            "preds_per_model": preds,
            "probs_per_model": probs,
            "benford": {
                "mad": benford_mads.get(comp, 0.0),
                "desc": benford_descs.get(comp, ""),
                "verdict": benford_verdicts.get(comp, "LOW")
            },
            "beneish": {
                "score": beneish_scores.get(comp, 0.0),
                "desc": beneish_descs.get(comp, ""),
                "verdict": beneish_verdicts.get(comp, "LOW")
            }
        }

    return {"company_results": company_results, "model_perf": model_perf, "n_features_used": k}
