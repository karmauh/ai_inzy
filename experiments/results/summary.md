## Scenariusz: basic, tryb: batch

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.748 ± 0.065 | 0.744 ± 0.080 | 0.772 ± 0.090 | 0.764 ± 0.085 | 0.732 ± 0.080 | 0.768 ± 0.102 | **0.755** | 0.755 | 0.755 |
| lof | 0.568 ± 0.084 | 0.580 ± 0.060 | 0.616 ± 0.129 | 0.548 ± 0.076 | 0.584 ± 0.086 | 0.548 ± 0.076 | **0.574** | 0.574 | 0.574 |
| ocsvm | 0.320 ± 0.047 | 0.296 ± 0.109 | 0.304 ± 0.074 | 0.428 ± 0.078 | 0.352 ± 0.073 | 0.384 ± 0.102 | **0.347** | 0.347 | 0.347 |
| autoencoder | 0.596 ± 0.077 | 0.628 ± 0.088 | 0.648 ± 0.091 | 0.572 ± 0.067 | 0.592 ± 0.084 | 0.588 ± 0.088 | **0.604** | 0.604 | 0.604 |
| ensemble | 0.608 ± 0.078 | 0.644 ± 0.097 | 0.652 ± 0.091 | 0.584 ± 0.072 | 0.596 ± 0.075 | 0.592 ± 0.091 | **0.613** | 0.613 | 0.613 |

## Scenariusz: basic, tryb: walk_forward

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.535 ± 0.068 | 0.643 ± 0.116 | 0.590 ± 0.080 | 0.704 ± 0.061 | 0.648 ± 0.091 | 0.656 ± 0.095 | **0.629** | 0.523 | 0.802 |
| lof | 0.492 ± 0.068 | 0.586 ± 0.115 | 0.559 ± 0.104 | 0.520 ± 0.094 | 0.453 ± 0.057 | 0.534 ± 0.128 | **0.524** | 0.416 | 0.734 |
| ocsvm | 0.471 ± 0.078 | 0.570 ± 0.126 | 0.489 ± 0.109 | 0.503 ± 0.092 | 0.420 ± 0.075 | 0.505 ± 0.102 | **0.493** | 0.394 | 0.689 |
| autoencoder | 0.482 ± 0.062 | 0.539 ± 0.058 | 0.539 ± 0.056 | 0.474 ± 0.099 | 0.563 ± 0.067 | 0.496 ± 0.075 | **0.515** | 0.421 | 0.682 |
| ensemble | 0.473 ± 0.054 | 0.560 ± 0.089 | 0.539 ± 0.082 | 0.505 ± 0.086 | 0.505 ± 0.058 | 0.511 ± 0.081 | **0.516** | 0.410 | 0.711 |

## Scenariusz: extended, tryb: batch

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.316 ± 0.083 | 0.344 ± 0.072 | 0.452 ± 0.072 | 0.324 ± 0.068 | 0.352 ± 0.050 | 0.416 ± 0.065 | **0.367** | 0.367 | 0.367 |
| lof | 0.464 ± 0.082 | 0.492 ± 0.112 | 0.468 ± 0.116 | 0.524 ± 0.103 | 0.516 ± 0.114 | 0.512 ± 0.129 | **0.496** | 0.496 | 0.496 |
| ocsvm | 0.220 ± 0.060 | 0.244 ± 0.070 | 0.216 ± 0.074 | 0.276 ± 0.068 | 0.260 ± 0.082 | 0.256 ± 0.054 | **0.245** | 0.245 | 0.245 |
| autoencoder | 0.480 ± 0.107 | 0.524 ± 0.127 | 0.444 ± 0.133 | 0.528 ± 0.087 | 0.556 ± 0.128 | 0.540 ± 0.132 | **0.512** | 0.512 | 0.512 |
| ensemble | 0.472 ± 0.093 | 0.536 ± 0.132 | 0.508 ± 0.120 | 0.552 ± 0.111 | 0.524 ± 0.114 | 0.552 ± 0.135 | **0.524** | 0.524 | 0.524 |

## Scenariusz: extended, tryb: walk_forward

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.260 ± 0.096 | 0.385 ± 0.143 | 0.363 ± 0.071 | 0.354 ± 0.072 | 0.389 ± 0.079 | 0.302 ± 0.076 | **0.342** | 0.273 | 0.465 |
| lof | 0.340 ± 0.145 | 0.380 ± 0.145 | 0.406 ± 0.132 | 0.372 ± 0.087 | 0.336 ± 0.118 | 0.379 ± 0.124 | **0.369** | 0.276 | 0.566 |
| ocsvm | 0.301 ± 0.111 | 0.391 ± 0.146 | 0.403 ± 0.128 | 0.356 ± 0.090 | 0.311 ± 0.085 | 0.342 ± 0.124 | **0.351** | 0.260 | 0.551 |
| autoencoder | 0.358 ± 0.148 | 0.425 ± 0.145 | 0.433 ± 0.134 | 0.378 ± 0.100 | 0.442 ± 0.119 | 0.356 ± 0.140 | **0.399** | 0.319 | 0.542 |
| ensemble | 0.343 ± 0.120 | 0.441 ± 0.158 | 0.462 ± 0.133 | 0.406 ± 0.087 | 0.403 ± 0.126 | 0.376 ± 0.136 | **0.405** | 0.310 | 0.593 |

Wartości w komórkach: F1 jako średnia ± odchylenie standardowe z 10 przebiegów (różne losowania wstrzykniętych anomalii, te same dla wszystkich modeli). Kolumny „Średnia” to średnia arytmetyczna po spółkach.

## Model zespołowy vs najlepszy pojedynczy model (F1)

| Scenariusz | Tryb | vs najlepszy na danej spółce (wygrane / remisy / przegrane) | Najlepszy pojedynczy średnio | vs ten model (wygrane / remisy / przegrane) |
|---|---|---|---|---|
| basic | batch | 0 / 0 / 6 | isolation_forest | 0 / 0 / 6 |
| basic | walk_forward | 0 / 0 / 6 | isolation_forest | 0 / 0 / 6 |
| extended | batch | 4 / 0 / 2 | autoencoder | 4 / 0 / 2 |
| extended | walk_forward | 3 / 0 / 3 | autoencoder | 4 / 0 / 2 |

Liczba spółek: 6. Remis = identyczne średnie F1.

## Uwagi metodologiczne

- **Tryb batch – precision ≈ recall ≈ F1.** Parametr contamination jest równy prawdziwemu udziałowi wstrzykniętych anomalii, więc model oznacza dokładnie tyle sesji, ile anomalii wstrzyknięto: każdy fałszywy alarm odpowiada jednej przeoczonej anomalii (FP = FN). To założenie optymistyczne – w praktyce udział anomalii nie jest znany. W trybie walk-forward próg jest kalibrowany na przeszłości, stąd wartości się różnią.
- **Zaniżona precyzja.** Rzeczywiste anomalie obecne w notowaniach przed wstrzyknięciem nie mają etykiety, więc ich wykrycie jest liczone jako fałszywy alarm. Podana precyzja jest zatem dolnym oszacowaniem.
