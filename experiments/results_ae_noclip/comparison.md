# Porównanie: results_ae_noclip vs results

Średnie F1 po spółkach; Δ = results_ae_noclip − results.

| Scenariusz | Tryb | Model | results | results_ae_noclip | Δ |
|---|---|---|---|---|---|
| basic | batch | isolation_forest | 0.769 | 0.769 | +0.000 |
| basic | batch | lof | 0.618 | 0.618 | +0.000 |
| basic | batch | ocsvm | 0.356 | 0.356 | +0.000 |
| basic | batch | autoencoder | 0.569 | 0.368 | -0.201 |
| basic | batch | ensemble | 0.577 | 0.472 | -0.105 |
| basic | walk_forward | isolation_forest | 0.653 | 0.653 | +0.000 |
| basic | walk_forward | lof | 0.534 | 0.534 | +0.000 |
| basic | walk_forward | ocsvm | 0.498 | 0.498 | +0.000 |
| basic | walk_forward | autoencoder | 0.481 | 0.415 | -0.066 |
| basic | walk_forward | ensemble | 0.481 | 0.484 | +0.003 |
| extended | batch | isolation_forest | 0.356 | 0.356 | +0.000 |
| extended | batch | lof | 0.506 | 0.506 | +0.000 |
| extended | batch | ocsvm | 0.238 | 0.238 | +0.000 |
| extended | batch | autoencoder | 0.477 | 0.411 | -0.066 |
| extended | batch | ensemble | 0.497 | 0.468 | -0.029 |
| extended | walk_forward | isolation_forest | 0.344 | 0.344 | +0.000 |
| extended | walk_forward | lof | 0.368 | 0.368 | +0.000 |
| extended | walk_forward | ocsvm | 0.349 | 0.349 | +0.000 |
| extended | walk_forward | autoencoder | 0.389 | 0.359 | -0.031 |
| extended | walk_forward | ensemble | 0.390 | 0.383 | -0.008 |
