## Scenariusz: basic, tryb: batch

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.768 ± 0.075 | 0.772 ± 0.100 | 0.780 ± 0.100 | 0.748 ± 0.084 | 0.732 ± 0.098 | 0.812 ± 0.074 | **0.769** | 0.769 | 0.769 |
| lof | 0.616 ± 0.109 | 0.636 ± 0.075 | 0.668 ± 0.158 | 0.580 ± 0.090 | 0.616 ± 0.078 | 0.592 ± 0.098 | **0.618** | 0.618 | 0.618 |
| ocsvm | 0.384 ± 0.084 | 0.308 ± 0.054 | 0.324 ± 0.094 | 0.380 ± 0.057 | 0.332 ± 0.074 | 0.408 ± 0.087 | **0.356** | 0.356 | 0.356 |
| autoencoder | 0.328 ± 0.143 | 0.312 ± 0.107 | 0.420 ± 0.221 | 0.408 ± 0.106 | 0.392 ± 0.154 | 0.348 ± 0.217 | **0.368** | 0.368 | 0.368 |
| ensemble | 0.392 ± 0.129 | 0.444 ± 0.107 | 0.544 ± 0.166 | 0.488 ± 0.069 | 0.508 ± 0.096 | 0.456 ± 0.164 | **0.472** | 0.472 | 0.472 |

## Scenariusz: basic, tryb: walk_forward

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.586 ± 0.061 | 0.663 ± 0.120 | 0.631 ± 0.083 | 0.700 ± 0.071 | 0.641 ± 0.088 | 0.695 ± 0.109 | **0.653** | 0.543 | 0.834 |
| lof | 0.505 ± 0.086 | 0.594 ± 0.121 | 0.577 ± 0.102 | 0.528 ± 0.105 | 0.438 ± 0.061 | 0.562 ± 0.142 | **0.534** | 0.418 | 0.772 |
| ocsvm | 0.472 ± 0.077 | 0.574 ± 0.133 | 0.492 ± 0.108 | 0.510 ± 0.091 | 0.421 ± 0.084 | 0.516 ± 0.109 | **0.498** | 0.397 | 0.701 |
| autoencoder | 0.381 ± 0.085 | 0.422 ± 0.077 | 0.421 ± 0.074 | 0.431 ± 0.075 | 0.435 ± 0.096 | 0.398 ± 0.084 | **0.415** | 0.334 | 0.564 |
| ensemble | 0.467 ± 0.070 | 0.517 ± 0.090 | 0.470 ± 0.092 | 0.501 ± 0.065 | 0.468 ± 0.089 | 0.479 ± 0.098 | **0.484** | 0.382 | 0.683 |

## Scenariusz: extended, tryb: batch

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.284 ± 0.077 | 0.336 ± 0.054 | 0.464 ± 0.086 | 0.300 ± 0.074 | 0.320 ± 0.067 | 0.432 ± 0.080 | **0.356** | 0.356 | 0.356 |
| lof | 0.488 ± 0.080 | 0.504 ± 0.127 | 0.460 ± 0.123 | 0.548 ± 0.116 | 0.520 ± 0.109 | 0.516 ± 0.122 | **0.506** | 0.506 | 0.506 |
| ocsvm | 0.272 ± 0.069 | 0.268 ± 0.086 | 0.236 ± 0.088 | 0.204 ± 0.085 | 0.212 ± 0.067 | 0.236 ± 0.058 | **0.238** | 0.238 | 0.238 |
| autoencoder | 0.368 ± 0.061 | 0.420 ± 0.065 | 0.356 ± 0.075 | 0.464 ± 0.100 | 0.396 ± 0.081 | 0.460 ± 0.120 | **0.411** | 0.411 | 0.411 |
| ensemble | 0.408 ± 0.078 | 0.444 ± 0.070 | 0.464 ± 0.109 | 0.520 ± 0.088 | 0.452 ± 0.078 | 0.520 ± 0.128 | **0.468** | 0.468 | 0.468 |

## Scenariusz: extended, tryb: walk_forward

| Model | AAPL | JPM | KO | NVDA | TSLA | XOM | Średnia F1 | Śr. precision | Śr. recall |
|---|---|---|---|---|---|---|---|---|---|
| isolation_forest | 0.280 ± 0.078 | 0.389 ± 0.160 | 0.363 ± 0.088 | 0.365 ± 0.074 | 0.372 ± 0.101 | 0.294 ± 0.084 | **0.344** | 0.272 | 0.476 |
| lof | 0.353 ± 0.140 | 0.382 ± 0.144 | 0.404 ± 0.117 | 0.368 ± 0.091 | 0.325 ± 0.123 | 0.376 ± 0.126 | **0.368** | 0.275 | 0.566 |
| ocsvm | 0.312 ± 0.106 | 0.390 ± 0.138 | 0.395 ± 0.132 | 0.350 ± 0.084 | 0.305 ± 0.079 | 0.343 ± 0.115 | **0.349** | 0.258 | 0.551 |
| autoencoder | 0.310 ± 0.113 | 0.355 ± 0.122 | 0.381 ± 0.096 | 0.357 ± 0.101 | 0.410 ± 0.143 | 0.339 ± 0.116 | **0.359** | 0.276 | 0.520 |
| ensemble | 0.331 ± 0.109 | 0.412 ± 0.148 | 0.428 ± 0.125 | 0.399 ± 0.079 | 0.364 ± 0.115 | 0.362 ± 0.119 | **0.383** | 0.288 | 0.580 |

Wartości w komórkach: F1 jako średnia ± odchylenie standardowe z 10 przebiegów (różne losowania wstrzykniętych anomalii, te same dla wszystkich modeli). Kolumny „Średnia” to średnia arytmetyczna po spółkach.

## Model zespołowy vs najlepszy pojedynczy model (F1)

| Scenariusz | Tryb | vs najlepszy na danej spółce (wygrane / remisy / przegrane) | Najlepszy pojedynczy średnio | vs ten model (wygrane / remisy / przegrane) |
|---|---|---|---|---|
| basic | batch | 0 / 0 / 6 | isolation_forest | 0 / 0 / 6 |
| basic | walk_forward | 0 / 0 / 6 | isolation_forest | 0 / 0 / 6 |
| extended | batch | 1 / 1 / 4 | lof | 2 / 0 / 4 |
| extended | walk_forward | 3 / 0 / 3 | lof | 4 / 0 / 2 |

Liczba spółek: 6. Remis = identyczne średnie F1.

## Uwagi metodologiczne

- **Tryb batch – precision ≈ recall ≈ F1.** Parametr contamination jest równy prawdziwemu udziałowi wstrzykniętych anomalii, więc model oznacza dokładnie tyle sesji, ile anomalii wstrzyknięto: każdy fałszywy alarm odpowiada jednej przeoczonej anomalii (FP = FN). To założenie optymistyczne – w praktyce udział anomalii nie jest znany. W trybie walk-forward próg jest kalibrowany na przeszłości, stąd wartości się różnią.
- **Zaniżona precyzja.** Rzeczywiste anomalie obecne w notowaniach przed wstrzyknięciem nie mają etykiety, więc ich wykrycie jest liczone jako fałszywy alarm. Podana precyzja jest zatem dolnym oszacowaniem.
