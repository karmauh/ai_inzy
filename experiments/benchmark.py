"""
Eksperyment porównawczy modeli detekcji anomalii (materiał do pracy, niezależny od aplikacji).

Kroki:
  1. fetch    – jednorazowe pobranie notowań z API aplikacji i zamrożenie ich w plikach data/<SYMBOL>.json
  2. evaluate – ewaluacja na zamrożonych plikach w 4 wariantach (basic/extended × batch/walk_forward),
                surowe odpowiedzi API zapisywane do results/<SYMBOL>_<scenario>_<mode>.json
  3. summary  – zbiorcze tabele z wyników: results/summary.csv (wszystko) i results/summary.md (do pracy)

Wymaga uruchomionego backendu (domyślnie http://localhost:8000).

Przykład:
  python experiments/benchmark.py fetch
  python experiments/benchmark.py evaluate
  python experiments/benchmark.py summary
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import requests

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

DEFAULT_SYMBOLS = ["AAPL", "NVDA", "JPM", "XOM", "KO", "TSLA"]
SCENARIOS = ["basic", "extended"]
MODES = ["batch", "walk_forward"]
MODELS = ["isolation_forest", "lof", "ocsvm", "autoencoder", "ensemble"]
METRICS = ["precision", "recall", "f1_score"]


def fetch(args: argparse.Namespace) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for symbol in args.symbols:
        path = DATA_DIR / f"{symbol}.json"
        if path.exists() and not args.force:
            # Dane są zamrożone – nadpisanie tylko na wyraźne żądanie (--force)
            print(f"[pomijam] {symbol}: {path.name} już istnieje")
            continue

        response = requests.get(f"{args.api}/api/v1/market/data/{symbol}", params={"period": args.period}, timeout=60)
        response.raise_for_status()
        records = response.json()["data"]

        payload = {
            "symbol": symbol,
            "period": args.period,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "first_date": records[0]["date"],
            "last_date": records[-1]["date"],
            "sessions": len(records),
            "data": records,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=1))
        print(f"[ok] {symbol}: {len(records)} sesji ({records[0]['date']} – {records[-1]['date']})")


def evaluate(args: argparse.Namespace) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        sys.exit("Brak danych w experiments/data – najpierw uruchom: benchmark.py fetch")

    for file in files:
        dataset = json.loads(file.read_text())
        for scenario in SCENARIOS:
            for mode in MODES:
                out = RESULTS_DIR / f"{dataset['symbol']}_{scenario}_{mode}.json"
                if out.exists() and not args.force:
                    print(f"[pomijam] {out.name} już istnieje")
                    continue

                print(f"[...] {dataset['symbol']} {scenario} {mode}", flush=True)
                response = requests.post(
                    f"{args.api}/api/v1/evaluation/evaluate",
                    json={
                        "data": dataset["data"],
                        "fraction": args.fraction,
                        "n_runs": args.n_runs,
                        "scenario": scenario,
                        "mode": mode,
                        "models": MODELS,
                    },
                    timeout=1800,
                )
                response.raise_for_status()

                result = response.json()
                # Opis danych wejściowych – żeby każdy plik wyników był samowystarczalny
                result["dataset"] = {key: dataset[key] for key in ("symbol", "period", "fetched_at", "first_date", "last_date", "sessions")}
                out.write_text(json.dumps(result, ensure_ascii=False, indent=1))


def _load_rows() -> list:
    rows = []
    for path in sorted(RESULTS_DIR.glob("*_*_*.json")):
        result = json.loads(path.read_text())
        meta, dataset = result["metadata"], result["dataset"]
        for model, values in result["evaluation"].items():
            if "error" in values:
                print(f"[błąd] {path.name} / {model}: {values['error']}")
                continue
            row = {
                "symbol": dataset["symbol"], "scenario": meta["scenario"], "mode": meta["mode"], "model": model,
                "n_runs": meta["n_runs"], "scored_sessions": meta["scored_records"],
            }
            for metric in METRICS:
                row[f"{metric}_mean"] = values["metrics"][metric]
                row[f"{metric}_std"] = values["metrics_std"][metric]
            for anomaly_type, stats in values["by_type"].items():
                row[f"detect_{anomaly_type}"] = stats["detection_rate"]
            rows.append(row)
    return rows


def summary(_: argparse.Namespace) -> None:
    rows = _load_rows()
    if not rows:
        sys.exit("Brak wyników w experiments/results – najpierw uruchom: benchmark.py evaluate")

    # 1) Pełna tabela (spółka × wariant × model) do dalszej obróbki, np. w Excelu
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with open(RESULTS_DIR / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    # 2) Tabele do pracy: F1 (średnia ± odch. std. z n_runs) per spółka oraz średnia po spółkach
    symbols = sorted({row["symbol"] for row in rows})
    lines = []
    for scenario in SCENARIOS:
        for mode in MODES:
            variant = [row for row in rows if row["scenario"] == scenario and row["mode"] == mode]
            if not variant:
                continue
            lines += [f"## Scenariusz: {scenario}, tryb: {mode}", "",
                      "| Model | " + " | ".join(symbols) + " | Średnia F1 | Śr. precision | Śr. recall |",
                      "|---|" + "---|" * (len(symbols) + 3)]
            for model in MODELS:
                cells = {row["symbol"]: row for row in variant if row["model"] == model}
                if not cells:
                    continue
                per_symbol = [f"{cells[s]['f1_score_mean']:.3f} ± {cells[s]['f1_score_std']:.3f}" if s in cells else "–"
                              for s in symbols]
                averages = [mean(row[f"{metric}_mean"] for row in cells.values()) for metric in ("f1_score", "precision", "recall")]
                lines.append(f"| {model} | " + " | ".join(per_symbol) + " | " + " | ".join(f"**{v:.3f}**" if i == 0 else f"{v:.3f}"
                                                                                    for i, v in enumerate(averages)) + " |")
            lines.append("")

    n_runs = rows[0]["n_runs"]
    lines += [f"Wartości w komórkach: F1 jako średnia ± odchylenie standardowe z {n_runs} przebiegów "
              "(różne losowania wstrzykniętych anomalii, te same dla wszystkich modeli). "
              "Kolumny „Średnia” to średnia arytmetyczna po spółkach."]
    (RESULTS_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(f"Zapisano {RESULTS_DIR / 'summary.csv'} i {RESULTS_DIR / 'summary.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api", default="http://localhost:8000", help="adres backendu")
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="pobierz i zamroź notowania")
    p_fetch.add_argument("--symbols", nargs="+", default=DEFAULT_SYMBOLS)
    p_fetch.add_argument("--period", default="1y")
    p_fetch.add_argument("--force", action="store_true", help="nadpisz istniejące pliki danych")
    p_fetch.set_defaults(func=fetch)

    p_eval = sub.add_parser("evaluate", help="uruchom ewaluację w 4 wariantach")
    p_eval.add_argument("--n-runs", type=int, default=10)
    p_eval.add_argument("--fraction", type=float, default=0.05)
    p_eval.add_argument("--force", action="store_true", help="nadpisz istniejące wyniki")
    p_eval.set_defaults(func=evaluate)

    sub.add_parser("summary", help="zbuduj tabele zbiorcze").set_defaults(func=summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
