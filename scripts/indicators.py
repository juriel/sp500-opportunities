import sys
from pathlib import Path

import numpy as np
import pandas as pd
import talib
import yfinance as yf
from scipy.signal import find_peaks
from tabulate import tabulate


def register(subparsers):
    p = subparsers.add_parser(
        "indicators",
        help="Calcula indicadores técnicos para una o varias acciones",
        description=(
            "Descarga datos históricos y calcula más de 50 indicadores técnicos "
            "agrupados por categoría: tendencia, momentum, volatilidad, volumen, "
            "ciclos, estadística y patrones de velas."
        ),
    )
    p.add_argument(
        "tickers",
        help="Ticker(s) separados por coma: NVDA,IBM,TSLA",
    )
    p.add_argument(
        "--period",
        default="1y",
        choices=["3mo", "6mo", "1y", "2y", "5y"],
        metavar="PERIODO",
        help="Período histórico: 3mo, 6mo, 1y (default), 2y, 5y",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Muestra los resultados en tabla formateada",
    )
    p.add_argument(
        "--pivots",
        action="store_true",
        help="Añade análisis de máximos/mínimos locales (período, fractales de Williams y scipy)",
    )
    p.add_argument(
        "--output",
        metavar="ARCHIVO",
        help="Exporta a .csv (ticker como columna) o .xlsx (una hoja por ticker)",
    )
    p.set_defaults(func=run)


def run(args):
    tickers = [t.strip().upper() for t in args.tickers.split(",")]
    all_rows = []

    for ticker in tickers:
        print(f"Descargando {ticker}...", file=sys.stderr)
        df = _download(ticker, args.period)
        if df is None:
            continue
        rows = _calculate(ticker, df)
        if getattr(args, "pivots", False):
            rows.extend(_calculate_pivots(ticker, df))
        all_rows.extend(rows)

    if not all_rows:
        print("No se obtuvieron resultados.", file=sys.stderr)
        sys.exit(1)

    result = pd.DataFrame(all_rows)

    if getattr(args, "output", None):
        _export(result, args.output, tickers)
    elif getattr(args, "pretty", False):
        _print_pretty(result, tickers)
    else:
        _print_plain(result, tickers)


# ─── Descarga ─────────────────────────────────────────────────────────────────

def _download(ticker: str, period: str) -> pd.DataFrame | None:
    try:
        data = yf.download(ticker, period=period, auto_adjust=True, progress=False, multi_level_index=False)
        if data.empty:
            print(f"Sin datos para {ticker}", file=sys.stderr)
            return None
        return data
    except Exception as e:
        print(f"Error descargando {ticker}: {e}", file=sys.stderr)
        return None


# ─── Cálculo de indicadores ───────────────────────────────────────────────────

def _calculate(ticker: str, df: pd.DataFrame) -> list[dict]:
    o = df["Open"].to_numpy(dtype=float)
    h = df["High"].to_numpy(dtype=float)
    l = df["Low"].to_numpy(dtype=float)
    c = df["Close"].to_numpy(dtype=float)
    v = df["Volume"].to_numpy(dtype=float)

    rows = []

    def add(category, name, value, signal=""):
        if value is None:
            return
        if isinstance(value, (float, np.floating)) and np.isnan(value):
            return
        rows.append({
            "ticker": ticker,
            "category": category,
            "indicator": name,
            "value": round(float(value), 4),
            "signal": signal,
        })

    def bull_bear(v):
        return "Alcista" if v > 0 else "Bajista"

    def above_below(price, ref):
        return "▲ Precio > ref" if price > ref else "▼ Precio < ref"

    def overbought(v, high=70, low=30):
        return "Sobrecomprado" if v > high else ("Sobrevendido" if v < low else "Neutral")

    # ── Precio ─────────────────────────────────────────────────────────────────
    daily_changes = np.diff(c)
    daily_up = daily_changes > 0

    # Cierre y variación del día
    day_chg = c[-1] - c[-2]
    day_pct = (day_chg / c[-2]) * 100
    add("Precio", "Cierre",       c[-1],   f"{day_chg:+.2f} ({day_pct:+.2f}%)")
    add("Precio", "Apertura",     o[-1])
    add("Precio", "High del día", h[-1])
    add("Precio", "Low del día",  l[-1])

    # Racha consecutiva actual
    streak = 1
    direction = daily_up[-1]
    for chg in reversed(daily_up[:-1]):
        if chg == direction:
            streak += 1
        else:
            break
    streak_label = f"{'Alza' if direction else 'Baja'}"
    add("Precio", "Racha actual", streak, f"días en {streak_label}")

    # Días al alza/baja por período
    for n, label in [(5, "5D"), (20, "20D"), (60, "60D")]:
        if len(daily_up) < n:
            continue
        window = daily_up[-n:]
        up_days   = int(window.sum())
        down_days = n - up_days
        up_pct    = (up_days / n) * 100
        add("Precio", f"Días alza  {label}", up_days,   f"{up_pct:.0f}% de {n} días")
        add("Precio", f"Días baja  {label}", down_days, f"{100 - up_pct:.0f}% de {n} días")

    # ── Tendencia ──────────────────────────────────────────────────────────────
    for period, label in [(20, "SMA20"), (50, "SMA50"), (200, "SMA200")]:
        val = talib.SMA(c, timeperiod=period)[-1]
        add("Tendencia", label, val, above_below(c[-1], val))

    for period, label in [(9, "EMA9"), (12, "EMA12"), (21, "EMA21"), (26, "EMA26"), (50, "EMA50")]:
        val = talib.EMA(c, timeperiod=period)[-1]
        add("Tendencia", label, val, above_below(c[-1], val))

    add("Tendencia", "DEMA21",      talib.DEMA(c, timeperiod=21)[-1])
    add("Tendencia", "TEMA21",      talib.TEMA(c, timeperiod=21)[-1])
    add("Tendencia", "KAMA",        talib.KAMA(c)[-1])
    add("Tendencia", "T3_21",        talib.T3(c, timeperiod=21)[-1])
    add("Tendencia", "HT_TRENDLINE", talib.HT_TRENDLINE(c)[-1])

    ht_mode = talib.HT_TRENDMODE(c)[-1]
    add("Tendencia", "HT_TRENDMODE", ht_mode, "Tendencia" if ht_mode == 1 else "Ciclo")

    # ── Momentum ───────────────────────────────────────────────────────────────
    rsi = talib.RSI(c, timeperiod=14)[-1]
    add("Momentum", "RSI14", rsi, overbought(rsi))

    macd, macd_sig, macd_hist = talib.MACD(c, 12, 26, 9)
    add("Momentum", "MACD",       macd[-1],      bull_bear(macd[-1] - macd_sig[-1]))
    add("Momentum", "MACD Signal", macd_sig[-1])
    add("Momentum", "MACD Hist",  macd_hist[-1], bull_bear(macd_hist[-1]))

    sk, sd = talib.STOCH(h, l, c)
    add("Momentum", "STOCH %K", sk[-1], overbought(sk[-1], 80, 20))
    add("Momentum", "STOCH %D", sd[-1])

    srsi_k, srsi_d = talib.STOCHRSI(c)
    add("Momentum", "STOCHRSI %K", srsi_k[-1], overbought(srsi_k[-1], 80, 20))
    add("Momentum", "STOCHRSI %D", srsi_d[-1])

    willr = talib.WILLR(h, l, c)[-1]
    add("Momentum", "WILLR", willr, overbought(willr, -20, -80))

    cci = talib.CCI(h, l, c)[-1]
    add("Momentum", "CCI14", cci, overbought(cci, 100, -100))

    cmo = talib.CMO(c)[-1]
    add("Momentum", "CMO", cmo, overbought(cmo, 50, -50))

    aroon_d, aroon_u = talib.AROON(h, l)
    add("Momentum", "AROON Up",   aroon_u[-1])
    add("Momentum", "AROON Down", aroon_d[-1])
    add("Momentum", "AROONOSC",   talib.AROONOSC(h, l)[-1], bull_bear(talib.AROONOSC(h, l)[-1]))

    ultosc = talib.ULTOSC(h, l, c)[-1]
    add("Momentum", "ULTOSC", ultosc, overbought(ultosc))

    add("Momentum", "ROC10",  talib.ROC(c,  timeperiod=10)[-1])
    add("Momentum", "ROCP10", talib.ROCP(c, timeperiod=10)[-1])
    add("Momentum", "TRIX",   talib.TRIX(c)[-1], bull_bear(talib.TRIX(c)[-1]))
    add("Momentum", "PPO",    talib.PPO(c)[-1],  bull_bear(talib.PPO(c)[-1]))

    bop = talib.BOP(o, h, l, c)[-1]
    add("Momentum", "BOP", bop, bull_bear(bop))

    adx = talib.ADX(h, l, c)[-1]
    add("Momentum", "ADX14",    adx, "Fuerte" if adx > 25 else "Débil")
    add("Momentum", "ADXR",     talib.ADXR(h, l, c)[-1])
    add("Momentum", "DX14",     talib.DX(h, l, c)[-1])
    add("Momentum", "PLUS_DI",  talib.PLUS_DI(h, l, c)[-1])
    add("Momentum", "MINUS_DI", talib.MINUS_DI(h, l, c)[-1])

    mfi = talib.MFI(h, l, c, v)[-1]
    add("Momentum", "MFI14", mfi, overbought(mfi, 80, 20))

    # ── Volatilidad ────────────────────────────────────────────────────────────
    upper, mid, lower = talib.BBANDS(c, timeperiod=20, nbdevup=2, nbdevdn=2)
    if c[-1] > upper[-1]:
        bb_sig = "Sobrecomprado"
    elif c[-1] < lower[-1]:
        bb_sig = "Sobrevendido"
    else:
        bb_sig = "Dentro de banda"

    add("Volatilidad", "BB Upper",  upper[-1], bb_sig)
    add("Volatilidad", "BB Middle", mid[-1])
    add("Volatilidad", "BB Lower",  lower[-1])
    add("Volatilidad", "BB Width",  ((upper[-1] - lower[-1]) / mid[-1]) * 100)
    add("Volatilidad", "ATR14",     talib.ATR(h, l, c)[-1])
    add("Volatilidad", "NATR14",    talib.NATR(h, l, c)[-1])
    add("Volatilidad", "TRANGE",    talib.TRANGE(h, l, c)[-1])

    # ── Volumen ────────────────────────────────────────────────────────────────
    add("Volumen", "OBV",   talib.OBV(c, v)[-1])
    add("Volumen", "AD",    talib.AD(h, l, c, v)[-1])
    adosc = talib.ADOSC(h, l, c, v)[-1]
    add("Volumen", "ADOSC", adosc, bull_bear(adosc))

    # ── Ciclos (Hilbert Transform) ─────────────────────────────────────────────
    add("Ciclos", "HT_DCPERIOD", talib.HT_DCPERIOD(c)[-1])
    add("Ciclos", "HT_DCPHASE",  talib.HT_DCPHASE(c)[-1])
    sine, leadsine = talib.HT_SINE(c)
    add("Ciclos", "HT_SINE",     sine[-1])
    add("Ciclos", "HT_LEADSINE", leadsine[-1])

    # ── Estadística ────────────────────────────────────────────────────────────
    slope = talib.LINEARREG_SLOPE(c)[-1]
    add("Estadística", "LINEARREG_SLOPE", slope, bull_bear(slope))
    add("Estadística", "STDDEV20", talib.STDDEV(c, timeperiod=20)[-1])
    add("Estadística", "BETA5",    talib.BETA(h, l, timeperiod=5)[-1])
    add("Estadística", "TSF",      talib.TSF(c)[-1])
    add("Estadística", "VAR20",    talib.VAR(c, timeperiod=20)[-1])

    # ── Patrones de velas ──────────────────────────────────────────────────────
    patterns = {
        "DOJI":             talib.CDLDOJI(o, h, l, c)[-1],
        "HAMMER":           talib.CDLHAMMER(o, h, l, c)[-1],
        "ENGULFING":        talib.CDLENGULFING(o, h, l, c)[-1],
        "MORNING STAR":     talib.CDLMORNINGSTAR(o, h, l, c)[-1],
        "EVENING STAR":     talib.CDLEVENINGSTAR(o, h, l, c)[-1],
        "3 WHITE SOLDIERS": talib.CDL3WHITESOLDIERS(o, h, l, c)[-1],
        "3 BLACK CROWS":    talib.CDL3BLACKCROWS(o, h, l, c)[-1],
        "HARAMI":           talib.CDLHARAMI(o, h, l, c)[-1],
        "SHOOTING STAR":    talib.CDLSHOOTINGSTAR(o, h, l, c)[-1],
    }
    for name, val in patterns.items():
        if val != 0:
            add("Patrones", name, val, bull_bear(val))

    return rows


# ─── Pivots: máximos y mínimos locales ───────────────────────────────────────

def _calculate_pivots(ticker: str, df: pd.DataFrame) -> list[dict]:
    c = df["Close"].to_numpy(dtype=float)
    current = c[-1]
    rows = []

    def pct(level):
        return f"{((level - current) / current) * 100:+.2f}%"

    def add(category, name, value, signal=""):
        rows.append({
            "ticker": ticker,
            "category": category,
            "indicator": name,
            "value": round(float(value), 4),
            "signal": signal,
        })

    # ── A: Máximos/mínimos por período ────────────────────────────────────────
    periods = [(20, "20D"), (60, "60D"), (252, "52W")]
    for n, label in periods:
        if len(c) < n:
            continue
        hi = talib.MAX(c, timeperiod=n)[-1]
        lo = talib.MIN(c, timeperiod=n)[-1]
        add("Período", f"High {label}", hi, pct(hi))
        add("Período", f"Low  {label}", lo, pct(lo))

    # ── B: Fractales de Williams (ventana 5 barras) ───────────────────────────
    h = df["High"].to_numpy(dtype=float)
    l = df["Low"].to_numpy(dtype=float)

    fractal_highs, fractal_lows = [], []
    for i in range(2, len(c) - 2):
        if h[i] > h[i-1] and h[i] > h[i-2] and h[i] > h[i+1] and h[i] > h[i+2]:
            fractal_highs.append((i, h[i]))
        if l[i] < l[i-1] and l[i] < l[i-2] and l[i] < l[i+1] and l[i] < l[i+2]:
            fractal_lows.append((i, l[i]))

    dates = df.index
    for rank, (idx, price) in enumerate(reversed(fractal_highs[-5:]), 1):
        dias = len(c) - 1 - idx
        add("Fractales · Resistencia", f"R{rank} ({dias}d atrás)", price, pct(price))

    for rank, (idx, price) in enumerate(reversed(fractal_lows[-5:]), 1):
        dias = len(c) - 1 - idx
        add("Fractales · Soporte",     f"S{rank} ({dias}d atrás)", price, pct(price))

    # ── C: scipy find_peaks ───────────────────────────────────────────────────
    prominence = current * 0.03  # mínimo 3% de movimiento para considerarlo pivot

    peaks, props = find_peaks(c, prominence=prominence, distance=5)
    troughs, tprops = find_peaks(-c, prominence=prominence, distance=5)

    for rank, idx in enumerate(reversed(peaks[-5:]), 1):
        dias = len(c) - 1 - idx
        prom = props["prominences"][list(peaks).index(idx)]
        add("Scipy · Resistencia", f"P{rank} ({dias}d atrás)", c[idx],
            f"{pct(c[idx])} | prom={prom:.2f}")

    for rank, idx in enumerate(reversed(troughs[-5:]), 1):
        dias = len(c) - 1 - idx
        prom = tprops["prominences"][list(troughs).index(idx)]
        add("Scipy · Soporte", f"V{rank} ({dias}d atrás)", c[idx],
            f"{pct(c[idx])} | prom={prom:.2f}")

    return rows


# ─── Salida ───────────────────────────────────────────────────────────────────

def _print_plain(df: pd.DataFrame, tickers: list[str]) -> None:
    for ticker in tickers:
        sub = df[df["ticker"] == ticker]
        if sub.empty:
            continue
        print(f"\n{'=' * 52}\n {ticker}\n{'=' * 52}")
        print(sub[["category", "indicator", "value", "signal"]].to_string(index=False))


def _print_pretty(df: pd.DataFrame, tickers: list[str]) -> None:
    for ticker in tickers:
        sub = df[df["ticker"] == ticker]
        if sub.empty:
            continue
        print(f"\n{'=' * 52}\n {ticker}\n{'=' * 52}")
        print(tabulate(
            sub[["category", "indicator", "value", "signal"]],
            headers=["Categoría", "Indicador", "Valor", "Señal"],
            tablefmt="rounded_outline",
            showindex=False,
        ))


def _export(df: pd.DataFrame, filepath: str, tickers: list[str]) -> None:
    path = Path(filepath)
    ext = path.suffix.lower()
    path.parent.mkdir(parents=True, exist_ok=True)

    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in (".xlsx", ".xls"):
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for ticker in tickers:
                sub = df[df["ticker"] == ticker]
                if not sub.empty:
                    sub[["category", "indicator", "value", "signal"]].to_excel(
                        writer, sheet_name=ticker, index=False
                    )
    else:
        print(f"Error: extensión '{ext}' no soportada. Usa .csv o .xlsx", file=sys.stderr)
        sys.exit(1)

    print(f"Guardado en {path}")
