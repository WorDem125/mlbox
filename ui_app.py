import os
import io
import json
import numpy as np
import pandas as pd
import requests
import streamlit as st

# =========================
# Transaction Risk UI (4.2)
# ✅ Uses the developed API (Module G / 4.1)
# - Upload CSV (raw transactions)
# - Build minimal features (hour + flow)
# - Call API /predict_batch
# - Show results + download
# - Button with reference/help info
# =========================

# ============================================================
# SETTINGS (change here if needed)
# ============================================================
# API base URL (Flask). You can override via env: API_URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Endpoints
EP_HEALTH = f"{API_URL}/health"
EP_PREDICT_BATCH = f"{API_URL}/predict_batch"

# Base date for parsing 'tr_datetime' format: '0 10:23:26'
BASE_DATE = pd.Timestamp("2020-01-01")

# Required columns in uploaded CSV (raw)
REQUIRED_RAW = ["customer_id", "tr_datetime", "mcc_code", "tr_type", "amount"]

# Minimal features expected by API (your API currently supports these)
API_FEATURES = ["amount", "mcc_code", "tr_type", "flow", "hour"]

# ============================================================
# HELPERS
# ============================================================

def read_csv_safely(uploaded_file) -> pd.DataFrame:
    """Read CSV robustly (comma/semicolon, python engine autodetect + fallback)."""
    raw_bytes = uploaded_file.getvalue()

    df = None
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes), sep=None, engine="python")
    except Exception:
        df = None

    if df is None:
        df = pd.read_csv(io.BytesIO(raw_bytes), sep=";")

    # If everything collapsed into one column and header contains ';' => retry with ';'
    if df.shape[1] == 1 and ";" in str(df.columns[0]):
        df = pd.read_csv(io.BytesIO(raw_bytes), sep=";")

    df.columns = df.columns.astype(str).str.strip()
    return df


def parse_tr_datetime(series: pd.Series) -> pd.Series:
    """Parse format: '0 10:23:26' (day_index + time)."""

    def _parse_one(x):
        if pd.isna(x):
            return pd.NaT
        s = str(x).strip()
        parts = s.split()
        if len(parts) != 2:
            return pd.NaT
        try:
            day_idx = int(parts[0])
            t = pd.to_timedelta(parts[1])
            return BASE_DATE + pd.Timedelta(days=day_idx) + t
        except Exception:
            return pd.NaT

    return series.apply(_parse_one)


def build_api_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Build minimal feature set for API from raw CSV.

    Raw columns (typical):
      customer_id, tr_datetime, mcc_code, tr_type, amount, term_id (optional)

    Output features for API:
      amount, mcc_code, tr_type, flow, hour
    """
    df = df_raw.copy()

    # numeric coercions
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    for c in ["mcc_code", "tr_type", "customer_id"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # hour from tr_datetime
    if "hour" not in df.columns:
        if "tr_datetime" in df.columns:
            dt = parse_tr_datetime(df["tr_datetime"])
            df["hour"] = dt.dt.hour.fillna(0).astype(int)
        else:
            df["hour"] = 0

    # flow from amount sign
    if "flow" not in df.columns:
        if "amount" in df.columns:
            df["flow"] = np.where(df["amount"].fillna(0) >= 0, "income", "spend")
        else:
            df["flow"] = "spend"

    # keep only what API needs
    out = df[API_FEATURES].copy()

    # fill NaNs safely
    out["amount"] = out["amount"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    out["mcc_code"] = out["mcc_code"].replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
    out["tr_type"] = out["tr_type"].replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
    out["hour"] = out["hour"].replace([np.inf, -np.inf], np.nan).fillna(0).astype(int)
    out["flow"] = out["flow"].astype(str).fillna("spend")

    # normalize flow values
    out["flow"] = out["flow"].str.lower().replace({"расход": "spend", "доход": "income"})
    out.loc[~out["flow"].isin(["income", "spend"]), "flow"] = "spend"

    return out


def api_healthcheck(timeout: float = 2.5) -> tuple[bool, str]:
    try:
        r = requests.get(EP_HEALTH, timeout=timeout)
        if r.status_code == 200:
            return True, "OK"
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def call_predict_batch(rows: list[dict], timeout: float = 30.0) -> dict:
    payload = {"rows": rows}
    r = requests.post(EP_PREDICT_BATCH, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def df_to_download_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


# ============================================================
# STREAMLIT UI
# ============================================================
st.set_page_config(page_title="Transaction Risk App", layout="wide")

st.title("💳 Классификация транзакций по риску (через API)")

with st.expander("ℹ️ Справка (как это работает)", expanded=False):
    st.markdown(
        f"""
**Что делает приложение (4.2):**
1) Ты загружаешь CSV с *сырыми транзакциями*.
2) Интерфейс считает минимальные признаки (`hour`, `flow`).
3) Интерфейс отправляет данные в API: `{EP_PREDICT_BATCH}`.
4) API возвращает предсказания:
   - `risk_level` (low/medium/high)
   - `verification_complexity` (simple/medium/hard)
5) Ты скачиваешь результат в CSV.

**Важно:**
- Streamlit НЕ обучает модели.
- Streamlit НЕ хранит модели.
- Всё предсказание делает API (Flask) по сохранённым `.joblib`.

**Как запускать (пример):**
- Терминал 1 (API): `python api_app.py` (обычно порт 8000)
- Терминал 2 (UI):  `streamlit run ui_app.py` (обычно порт 8501)

Если API не запущен — UI покажет ошибку.
"""
    )

# Sidebar settings
st.sidebar.header("⚙️ Настройки")
st.sidebar.write("API URL:")
st.sidebar.code(API_URL)

ok, msg = api_healthcheck()
if ok:
    st.sidebar.success("✅ API доступен")
else:
    st.sidebar.error("❌ API недоступен")
    st.sidebar.caption(f"Причина: {msg}")
    st.error(
        "API сейчас недоступен. Сначала запусти API в другом терминале: `python api_app.py`. "
        "Потом обнови страницу Streamlit."
    )
    st.stop()

uploaded = st.file_uploader("Загрузить CSV с транзакциями", type=["csv"])
if uploaded is None:
    st.info("Загрузи CSV, чтобы начать.")
    st.stop()

# Read CSV
try:
    df_raw = read_csv_safely(uploaded)
except Exception as e:
    st.error(f"Не могу прочитать CSV: {e}")
    st.stop()

st.subheader("📄 Preview (сырые данные)")
st.dataframe(df_raw.head(30), use_container_width=True)

missing_raw = [c for c in REQUIRED_RAW if c not in df_raw.columns]
if missing_raw:
    st.error(
        "❌ В загруженном CSV не хватает обязательных колонок: "
        + ", ".join(missing_raw)
        + "\n\nПодсказка: часто на проверке CSV с разделителем `;`."
    )
    st.stop()

with st.expander("⚙️ Настройки расчёта", expanded=False):
    max_rows = st.number_input(
        "Ограничить количество строк (0 = без ограничений)",
        min_value=0,
        value=0,
        step=1000,
    )
    timeout_s = st.number_input(
        "Таймаут запроса к API (сек)",
        min_value=5,
        value=30,
        step=5,
    )

run_btn = st.button("🚀 Рассчитать риск через API", type="primary")
if not run_btn:
    st.stop()

with st.spinner("Считаю признаки и отправляю в API..."):
    df_work = df_raw.copy()
    if max_rows and len(df_work) > int(max_rows):
        df_work = df_work.head(int(max_rows)).copy()

    # Build minimal features for API
    df_feat = build_api_features(df_work)

    # Convert to list of dicts
    rows = df_feat.to_dict(orient="records")

    # Call API
    try:
        resp = call_predict_batch(rows=rows, timeout=float(timeout_s))
    except requests.HTTPError as e:
        st.error(f"API вернул ошибку: {e}\n\n{getattr(e.response, 'text', '')[:500]}")
        st.stop()
    except Exception as e:
        st.error(f"Не удалось вызвать API: {e}")
        st.stop()

    # Parse response
    result = resp.get("result", [])
    if not isinstance(result, list) or len(result) != len(df_work):
        st.error("Ответ API некорректный: длина результата не совпала с входом.")
        st.json(resp)
        st.stop()

    pred_df = pd.DataFrame(result)

    out = df_work.reset_index(drop=True).copy()
    out["risk_level"] = pred_df["risk_level"].astype(str)
    out["verification_complexity"] = pred_df["verification_complexity"].astype(str)

    # Optional: add probabilities if present in API response
    if "risk_proba" in pred_df.columns:
        try:
            proba_df = pd.json_normalize(pred_df["risk_proba"])
            proba_df.columns = [f"proba_{c}" for c in proba_df.columns]
            out = pd.concat([out, proba_df], axis=1)
        except Exception:
            pass

st.subheader("✅ Результат")
st.dataframe(out.head(200), use_container_width=True)

st.download_button(
    label="⬇️ Скачать CSV с результатами",
    data=df_to_download_bytes(out),
    file_name="transactions_scored.csv",
    mime="text/csv",
)

st.caption(
    "Готово. Для больших файлов включай ограничение строк в настройках. "
    "UI зависит от API: если API остановить — новые расчёты не будут работать."
)