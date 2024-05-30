
time durations for reverse wfc city creation

| size | total    | place tile | find most ceartain start | find most ceartain end | propagate entropies |
| ---- | -------- | ---------- | ------------------------ | ---------------------- | ------------------- |
| 2    | 61.344s  | 0.667s     | 0.002s                   | 0.001s                 | 0.001s              |
| 5    | 146.627s | 0.758s     | 0.005s                   | 0.001s                 | 0.0s                |
| 10   | 486.604s | 0.886s     | 0.012s                   | 0.001s                 | 0.0s                |
### Rules:

| Changes    | River   | Highway | Road    | Industrial | House | park |
| ---------- | ------- | ------- | ------- | ---------- | ----- | ---- |
| River      | 1x +0,6 | 0,2     |         |            |       | 0,1  |
| Highway    | -0.1    | 1x +0,7 |         |            | -0.1  | 0,1  |
| Road       | -0.1    | 0,2     | 1x +0,7 | 0,1        |       |      |
| Industrial | -0.1    | 0,2     |         | 0,4        | -0.1  |      |
| House      | -0.1    | 0,2     | 0,2     | -0,1       | 0,3   |      |
| park       |         | 0,2     |         |            | 0,2   | 0,05 |
